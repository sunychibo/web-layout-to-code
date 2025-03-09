import cv2
import json
import numpy as np

# Если ваши данные JSON находятся в файле 'output-coordinates.json':
JSON_FILE = 'output-coordinates.json'
# Исходное изображение (как в примере, используем website_template_3.png):
IMAGE_FILE = 'website_template_3.png'
# Итоговое изображение с нарисованными контурами и подписями
OUTPUT_FILE = 'annotated_result.png'

def draw_block_recursively(image, block_dict, block_name, color, thickness):
    """
    Рекурсивно рисует блок и его вложенные блоки на изображении.
    
    :param image: исходное изображение (NumPy array OpenCV).
    :param block_dict: словарь с ключами 'coordinatesXY' и 'children' (и т.д.).
    :param block_name: строковое имя текущего блока, например "block_00".
    :param color: цвет контура (по умолчанию красный BGR).
    :param thickness: толщина линии.
    """
    # Получаем список координат для данного блока
    coords = block_dict["coordinatesXY"]  # Список списков [[x1,y1],[x2,y2],...]
    coords_array = np.array(coords, dtype=np.int32)

    # Рисуем многоугольник (замкнутый контур)
    cv2.polylines(image, [coords_array], isClosed=True, color=color, thickness=thickness)


    # Чтобы красиво расположить текст, возьмём первую вершину (или любую)
    x_text, y_text = coords[0]

    # Подпишем блок: блок-id + координаты
    # text = f"{block_name} {coords}"
    text = f"{block_name}"
    cv2.putText(
        image,
        text,
        (x_text, y_text - 5),  # чуток выше первой точки
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,       # масштаб шрифта
        color,
        1,         # толщина линии шрифта
        cv2.LINE_AA
    )

    # Рисуем детей (если есть)
    children = block_dict.get("children", {})
    for child_name, child_dict in children.items():
        draw_block_recursively(image, child_dict, child_name, color=color, thickness=thickness)

def annotate_image(image, json_data, color=(0, 255, 0), thickness=2): # можно другой цвет и толщину
    # 1. Загружаем изображение
    if image is None:
        raise FileNotFoundError(f"Не удалось открыть изображение {IMAGE_FILE}")
    
    # Создадим копию, чтобы не портить оригинал
    annotated = image.copy()

    # Предположим, что у нас структура вида {"layout": { ... }}
    layout_dict = json_data.get("layout", {})
    
    # 3. Рисуем layout и всех детей
    draw_block_recursively(annotated, layout_dict, "layout", color, thickness)

    return annotated