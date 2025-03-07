import cv2
import numpy as np

def find_blocks_and_build_tree(image):
    """
    Наивная функция:
    1) Переводит изображение в серый формат.
    2) Применяет простую бинарную сегментацию (threshold).
    3) Находит контуры (cv2.findContours).
    4) Для каждого контура вычисляет boundingRect и сохраняет в список.
    5) Строит иерархию (layout -> children).
    
    Возвращает структуру данных, которую потом сериализуем в JSON.
    """
    # Шаг 1: перевод в grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Шаг 2: простое бинарное пороговое преобразование
    # Обычно порог ~127, но можно подбирать в зависимости от яркости
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Шаг 3: ищем контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Для хранения результатов (bounding box каждой найденной области)
    blocks = []

    # Шаг 4: извлекаем boundingRect у каждого контура
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        # Фильтруем слишком маленькие блоки (можно подбирать порог)
        if w > 20 and h > 20:
            # Сохраняем координаты углов (x,y) (x+w,y) (x+w, y+h) (x, y+h)
            corners = [
                [int(x), int(y)],
                [int(x + w), int(y)],
                [int(x + w), int(y + h)],
                [int(x), int(y + h)]
            ]
            blocks.append({
                "coordinatesXY": corners,
                "bbox": (x, y, w, h)  # Для удобства определения вложенности
            })

    # Для упрощения считаем, что "layout" - это boundingRect по всему изображению
    # (или самый большой блок, если хочется). Здесь пойдём по пути boundingRect всего изображения:
    h_img, w_img = image.shape[:2]
    layout_corners = [[0, 0], [w_img, 0], [w_img, h_img], [0, h_img]]
    layout_dict = {
        "coordinatesXY": layout_corners,
        "children": {}
    }

    # Шаг 5: определение вложенности
    # У нас есть блоки, у каждого блок-а bbox. 
    # Проверим, какие блоки находятся целиком в layout, а потом иерархически распределим.
    
    # Функция проверки, что все углы A внутри углов B (здесь можно сделать проверку точек внутри bbox).
    def is_inside(bbox_a, bbox_b):
        """
        Проверяем, все ли углы bbox_a внутри bbox_b (по boundingRect).
        """
        (Ax, Ay, Aw, Ah) = bbox_a
        (Bx, By, Bw, Bh) = bbox_b
        if Ax >= Bx and Ay >= By and (Ax + Aw) <= (Bx + Bw) and (Ay + Ah) <= (By + Bh):
            return True
        return False

    # Разместим все блоки, которые реально внутри layout.
    # Можно строить дерево на основе сортировки по размеру bbox.
    # Для простоты сделаем одноуровневую вложенность: все блоки -> children layout.
    # И/или рекурсивно распределять: если один блок внутри другого.
    
    # Отсортируем блоки по убыванию площади, чтобы сначала обрабатывать большие.
    blocks = sorted(blocks, key=lambda b: b["bbox"][2] * b["bbox"][3], reverse=True)

    # Чтобы хранить итоговую структуру
    final_blocks = []

    # Функция рекурсивного добавления
    def add_block_recursively(block, parents_list):
        """
        Пытается добавить блок как потомка к уже имеющимся элементам,
        если он полностью внутри. Иначе возвращается, что не добавлен.
        """
        for p in parents_list:
            # Если все углы этого блока внутри p
            if is_inside(block["bbox"], p["bbox"]):
                # Ищем дальше среди детей p (p["children"])
                added = add_block_recursively(block, p["children_list"])
                if not added:
                    # Не получилось добавить глубже, значит добавим его прямо здесь
                    p["children_list"].append({
                        "coordinatesXY": block["coordinatesXY"],
                        "bbox": block["bbox"],
                        "children_list": []
                    })
                return True
        return False

    # Будем формировать список "корневых" блоков
    root_blocks = []

    # Последовательно пытаемся вставить каждый блок в уже существующую иерархию
    for block in blocks:
        # Проверяем, лежит ли он внутри layout
        if is_inside(block["bbox"], (0, 0, w_img, h_img)):
            # Пробуем добавить его рекурсивно в root_blocks
            added = add_block_recursively(block, root_blocks)
            # Если не добавлен, значит он сам становится root (не вложен ни в один из уже имеющихся)
            if not added:
                root_blocks.append({
                    "coordinatesXY": block["coordinatesXY"],
                    "bbox": block["bbox"],
                    "children_list": []
                })

    # Теперь у нас есть список "root_blocks", которые целиком лежат в layout
    # но при этом они могут иметь рекурсивные children. Нужно превратить это в JSON-структуру.

    def convert_to_json_structure(blocks_list, prefix="block"):
        """
        Превращаем вложенные списки в структуру вида:
        {
          "block_00": {
            "coordinatesXY": ...,
            "children": {
              ...
            }
          }
        }
        """
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

    # Окончательная структура
    final_json = {
        "layout": layout_dict
    }

    return final_json
