import cv2
import numpy as np

def find_blocks_and_build_tree(image, params=None):
    """
    Функция учитывает параметры из 'params' (dict):
      - threshold_method: 'fixed', 'otsu', 'triangle', 'adaptive_mean', 'adaptive_gaussian'
      - threshold_value: (int) [0..255] (используется при "fixed")
      - max_value: (int) значение заливки [1..255]
      - adaptive_block_size: (int) размер окна при adaptiveThreshold
      - adaptive_C: (int) константа при adaptiveThreshold
      - morphology_kernel_size: (int) размер ядра морфологии
      - morphology_iterations: (int) кол-во итераций морфологических оп-й
      - min_block_width, min_block_height
      - retrieval_mode: 'RETR_EXTERNAL' / 'RETR_TREE' / 'RETR_CCOMP' / 'RETR_LIST'
      - approx_method: 'CHAIN_APPROX_SIMPLE' / 'CHAIN_APPROX_NONE' / ...
      - min_area, max_area
      - approx_polygons: (bool) аппроксимация контуров cv2.approxPolyDP

    Возвращает dict с иерархией найденных блоков:
    {
        "block_00": {
        "coordinatesXY": [[0,0],[W,0],[W,H],[0,H]],
        "children": {
            "block_00_00": {
            "coordinatesXY": [],
            "children": {
                "block_00_00_00": {}
            }
            },
            "block_00_01": {
            "coordinatesXY": [],
            "children": {
                "block_00_01_00": {}
            }
            },
            "block_00_02": {
            "coordinatesXY": [],
            "children": {
                "block_00_02_00": {},
                "block_00_02_01": {
                    "coordinatesXY": [],
                    "children": {
                        "block_00_02_01_00": {},
                        "block_00_02_01_01": {}
                    }
                },
                "block_00_00_02": {}
            }
            }
        }
        }
    }
    """

    if params is None:
        params = {}

    # Извлекаем параметры
    threshold_method      = params.get("threshold_method", "fixed")
    threshold_value       = params.get("threshold_value", 127)
    max_value             = params.get("max_value", 255)
    adaptive_block_size   = params.get("adaptive_block_size", 11)
    adaptive_C            = params.get("adaptive_C", 2)
    morphology_kernel_size = params.get("morphology_kernel_size", 3)
    morphology_iterations  = params.get("morphology_iterations", 1)
    min_block_width       = params.get("min_block_width", 20)
    min_block_height      = params.get("min_block_height", 20)
    retrieval_mode_str    = params.get("retrieval_mode", "RETR_EXTERNAL")
    approx_method_str     = params.get("approx_method", "CHAIN_APPROX_SIMPLE")
    min_area              = params.get("min_area", 0)
    max_area              = params.get("max_area", 999999)
    approx_polygons       = params.get("approx_polygons", False)

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

    # ==============================
    # 1) Перевод в grayscale
    # ==============================
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ==============================
    # 2) Бинаризация
    # ==============================
    if threshold_method == "fixed":
        # Простой фиксированный порог
        _, thresh = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY_INV)

    elif threshold_method == "otsu":
        # OTSU автоматически определяет оптимальный порог
        _, thresh = cv2.threshold(gray, 0, max_value, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    elif threshold_method == "triangle":
        # Автоматический порог методом треугольника
        _, thresh = cv2.threshold(gray, 0, max_value, cv2.THRESH_BINARY_INV | cv2.THRESH_TRIANGLE)

    elif threshold_method == "adaptive_mean":
        thresh = cv2.adaptiveThreshold(
            gray,
            max_value,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            adaptive_block_size,
            adaptive_C
        )

    elif threshold_method == "adaptive_gaussian":
        thresh = cv2.adaptiveThreshold(
            gray,
            max_value,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            adaptive_block_size,
            adaptive_C
        )
    else:
        # Fallback (на всякий случай)
        _, thresh = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY_INV)

    # ==============================
    # 3) Морфологическая обработка
    # ==============================
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morphology_kernel_size, morphology_kernel_size))
    for _ in range(morphology_iterations):
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # ==============================
    # 4) findContours (с иерархией)
    # ==============================
    contours, hierarchy = cv2.findContours(thresh, retrieval_mode, approx_method)

    # Если нет контуров или нет иерархии, возвращаем пустой block_00
    if not contours or hierarchy is None:
        h_img, w_img = image.shape[:2]
        block_00_corners = [[0, 0], [w_img, 0], [w_img, h_img], [0, h_img]]
        return {
            "block_00": {
                "coordinatesXY": block_00_corners,
                "children": {}
            }
        }

    # hierarchy.shape = (1, N, 4) => берем [0], чтобы получить (N, 4)
    hierarchy = hierarchy[0]

    # ==============================
    # 5) Сбор данных о блоках
    # ==============================
    # Для каждого контура проверим размер, получим boundingRect, сохраним в структуре
    # + запишем parent, child, next, prev (из hierarchy).
    blocks_info = []

    for i, c in enumerate(contours):
        if approx_polygons:
            epsilon = 0.01 * cv2.arcLength(c, True)
            c = cv2.approxPolyDP(c, epsilon, True)

        x, y, w, h = cv2.boundingRect(c)
        if w < min_block_width or h < min_block_height:
            continue
        area = w * h
        if area < min_area or area > max_area:
            continue

        # corners = boundingRect (для упрощения, как раньше)
        corners = [
            [x,       y],
            [x + w,   y],
            [x + w,   y + h],
            [x,       y + h]
        ]

        next_i, prev_i, child_i, parent_i = hierarchy[i]

        block_data = {
            "index": i,
            "coordinatesXY": corners,
            "next_idx":   next_i,
            "prev_idx":   prev_i,
            "child_idx":  child_i,
            "parent_idx": parent_i,
        }
        blocks_info.append(block_data)

    # Превращаем список в словарь { i: block_data }
    # Но учтите, что не все контуры попали в blocks_info (из-за фильтра размеров).
    # Значит, доступ по child_i/parent_i может указывать на несуществующий индекс.
    blocks_by_index = { b["index"]: b for b in blocks_info }

    # ==============================
    # 6) Строим иерархию контуров
    # ==============================
    debug_counter = 0

    def build_subtree(idx, parent_id, level):
        nonlocal debug_counter
        current_debug_id = debug_counter
        debug_counter += 1

        if idx not in blocks_by_index:
            return ("missing_block", {})

        node = blocks_by_index[idx]
        children_map = {}

        # Генерация уникального ID на основе parent_id и уровня вложенности
        if "_" in parent_id:
            parts = parent_id.split("_")
            base_id = "_".join(parts[:-1])
            sibling_num = int(parts[-1])
            block_id = f"{base_id}_{sibling_num:02d}"
        else:
            block_id = f"{parent_id}_00"

        sibling_counter = 0  # Локальный счетчик для детей текущего узла

        def traverse_siblings(child_idx, base_id):
            nonlocal sibling_counter
            while child_idx != -1:
                if child_idx not in blocks_by_index:
                    break
                
                child_node = blocks_by_index[child_idx]
                child_unique_id = f"{base_id}_{sibling_counter:02d}"
                
                c_name, c_dict = build_subtree(child_idx, child_unique_id, level+1)
                children_map[c_name] = c_dict
                
                child_idx = child_node["next_idx"]
                sibling_counter += 1

        # Обработка дочерних элементов
        first_child_idx = node["child_idx"]
        if first_child_idx != -1:
            traverse_siblings(first_child_idx, block_id)

        return (f"block_{block_id}", {
            "coordinatesXY": node["coordinatesXY"],
            "children": children_map
        })

    # ==============================
    # 7) Формируем block_00 + children
    # ==============================
    h_img, w_img = image.shape[:2]
    debug_counter = 0

    root_block = {
        "block_00": {
            "coordinatesXY": [[0, 0], [w_img, 0], [w_img, h_img], [0, h_img]],
            "children": {}
        }
    }

    root_counter = 0
    for b in blocks_info:
        if b["parent_idx"] == -1:
            root_child_id = f"00_{root_counter:02d}"
            idx_ = b["index"]
            block_name, block_data = build_subtree(idx_, root_child_id, 0)
            root_block["block_00"]["children"][block_name] = block_data
            root_counter += 1
    
    return root_block