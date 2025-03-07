import cv2
import numpy as np

def find_blocks_and_build_tree(image, params=None):
    """
    Функция учитывает параметры из 'params' (dict):
      - threshold_method: 'fixed', 'otsu', 'adaptive'
      - threshold_value: (int) [0..255]
      - max_value: (int) значение заливки [1..255]
      - adaptive_block_size: (int) размер окна при adaptiveThreshold
      - adaptive_C: (int) константа при adaptiveThreshold
      - morphology_kernel_size: (int) размер ядра морфологии
      - morphology_iterations: (int) кол-во итераций морфологических оп-й
      - min_block_width, min_block_height
      - retrieval_mode: 'RETR_EXTERNAL' / 'RETR_TREE' / ...
      - approx_method: 'CHAIN_APPROX_SIMPLE', ...
      - min_area, max_area
      - approx_polygons: (bool) аппроксимация контуров cv2.approxPolyDP

    Возвращает dict с иерархией найденных блоков.
    """
    if params is None:
        params = {}

    # Извлекаем
    threshold_method = params.get("threshold_method", "fixed")
    threshold_value = params.get("threshold_value", 127)
    max_value = params.get("max_value", 255)
    adaptive_block_size = params.get("adaptive_block_size", 11)
    adaptive_C = params.get("adaptive_C", 2)
    morphology_kernel_size = params.get("morphology_kernel_size", 3)
    morphology_iterations = params.get("morphology_iterations", 1)
    min_block_width = params.get("min_block_width", 20)
    min_block_height = params.get("min_block_height", 20)
    retrieval_mode_str = params.get("retrieval_mode", "RETR_EXTERNAL")
    approx_method_str = params.get("approx_method", "CHAIN_APPROX_SIMPLE")
    min_area = params.get("min_area", 0)
    max_area = params.get("max_area", 999999)
    approx_polygons = params.get("approx_polygons", False)

    # Конвертация retrieval_mode_str в константу OpenCV
    if retrieval_mode_str == "RETR_EXTERNAL":
        retrieval_mode = cv2.RETR_EXTERNAL
    elif retrieval_mode_str == "RETR_TREE":
        retrieval_mode = cv2.RETR_TREE
    elif retrieval_mode_str == "RETR_CCOMP":
        retrieval_mode = cv2.RETR_CCOMP
    else:
        retrieval_mode = cv2.RETR_LIST

    # Конвертация approx_method_str в константу OpenCV
    if approx_method_str == "CHAIN_APPROX_NONE":
        approx_method = cv2.CHAIN_APPROX_NONE
    elif approx_method_str == "CHAIN_APPROX_TC89_L1":
        approx_method = cv2.CHAIN_APPROX_TC89_L1
    elif approx_method_str == "CHAIN_APPROX_TC89_KCOS":
        approx_method = cv2.CHAIN_APPROX_TC89_KCOS
    else:
        approx_method = cv2.CHAIN_APPROX_SIMPLE

    print("[processing.py] DEBUG: Started find_blocks_and_build_tree with params =", params)
    
    # 1) Перевод в grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2) Выбор метода пороговой бинаризации
    if threshold_method == "fixed":
        # Простой фиксированный порог
        _, thresh = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY_INV)

    elif threshold_method == "otsu":
        # OTSU автоматически определяет оптимальный порог
        _, thresh = cv2.threshold(gray, 0, max_value, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    else:  # "adaptive"
        # Адаптивный метод (GAUSSIAN_C или MEAN_C)
        # Ниже – пример с GAUSSIAN_C
        thresh = cv2.adaptiveThreshold(
            gray,
            max_value,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # можно поменять на MEAN_C
            cv2.THRESH_BINARY_INV,
            adaptive_block_size,
            adaptive_C
        )

    # 3) Морфология (например, закрытие разрывов)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morphology_kernel_size, morphology_kernel_size))
    # Можно применять dilate, erode, open, close – по задаче, сейчас делаем close итерации раз
    for _ in range(morphology_iterations):
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 4) Поиск контуров с заданным retrieval_mode и approx_method
    contours, _ = cv2.findContours(thresh, retrieval_mode, approx_method)

    # 5) Проходимся по контурам
    blocks = []
    for c in contours:
        # Если включена аппроксимация многоугольников
        if approx_polygons:
            epsilon = 0.01 * cv2.arcLength(c, True)
            c = cv2.approxPolyDP(c, epsilon, True)

        x, y, w, h = cv2.boundingRect(c)

        # Фильтрация по ширине/высоте
        if w >= min_block_width and h >= min_block_height:
            area = w * h
            if area >= min_area and area <= max_area:
                corners = [
                    [int(x), int(y)],
                    [int(x + w), int(y)],
                    [int(x + w), int(y + h)],
                    [int(x), int(y + h)]
                ]
                blocks.append({
                    "coordinatesXY": corners,
                    "bbox": (x, y, w, h)
                })

    # 6) layout = boundingRect всего изображения
    h_img, w_img = image.shape[:2]
    layout_corners = [[0, 0], [w_img, 0], [w_img, h_img], [0, h_img]]
    layout_dict = {
        "coordinatesXY": layout_corners,
        "children": {}
    }

    # Вложенность (логика, как прежде)
    def is_inside(bbox_a, bbox_b):
        Ax, Ay, Aw, Ah = bbox_a
        Bx, By, Bw, Bh = bbox_b
        return (Ax >= Bx and Ay >= By 
                and (Ax + Aw) <= (Bx + Bw) 
                and (Ay + Ah) <= (By + Bh))

    # Сортируем по убыванию площади
    blocks = sorted(blocks, key=lambda b: b["bbox"][2] * b["bbox"][3], reverse=True)

    final_blocks = []

    def add_block_recursively(block, parents_list):
        for p in parents_list:
            if is_inside(block["bbox"], p["bbox"]):
                added = add_block_recursively(block, p["children_list"])
                if not added:
                    p["children_list"].append({
                        "coordinatesXY": block["coordinatesXY"],
                        "bbox": block["bbox"],
                        "children_list": []
                    })
                return True
        return False

    root_blocks = []
    for block in blocks:
        if is_inside(block["bbox"], (0, 0, w_img, h_img)):
            added = add_block_recursively(block, root_blocks)
            if not added:
                root_blocks.append({
                    "coordinatesXY": block["coordinatesXY"],
                    "bbox": block["bbox"],
                    "children_list": []
                })

    def convert_to_json_structure(blocks_list, prefix="block"):
        result = {}
        idx = 0
        for b in blocks_list:
            block_name = f"{prefix}_{idx:02d}"
            children_dict = convert_to_json_structure(b["children_list"], prefix=f"{block_name}")
            result[block_name] = {
                "coordinatesXY": b["coordinatesXY"],
                "children": children_dict
            }
            idx += 1
        return result

    children_json = convert_to_json_structure(root_blocks, prefix="block")
    layout_dict["children"] = children_json

    final_json = {
        "layout": layout_dict
    }

    return final_json
