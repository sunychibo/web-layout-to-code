# local_prototype.py

import cv2
import numpy as np
import pytesseract
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Импорт функций из модулей
from modules import image_processing, ocr_processing, json_handler, html_generator
from modules.image_processing import get_dominant_color, get_text_color

def process_image(image_path):
    """Обрабатывает изображение и извлекает структуру интерфейса."""
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка: Не удалось загрузить изображение.")
        return {"layout": {"width": 0, "height": 0, "elements": []}}

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Улучшенная пороговая обработка
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Делаем меньшее увеличение границ, чтобы не соединять ненужные элементы
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.dilate(binary, kernel, iterations=1)

    # Находим контуры
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    elements = []
    parent_map = {}

    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)

        # Отбрасываем слишком маленькие элементы
        if w < 50 or h < 20:
            continue

        # Определяем цвет фона блока
        roi = image[y:y+h, x:x+w]
        avg_color = np.mean(roi, axis=(0,1))  # Средний цвет в BGR
        background_color = "#{:02x}{:02x}{:02x}".format(int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))

        # Распознаём текст в блоке
        text = pytesseract.image_to_string(roi).strip()

        # Проверяем, есть ли родитель (вложенность)
        parent_id = None
        if hierarchy[0][i][3] != -1:  # Если есть родительский элемент
            parent_id = f"block_{hierarchy[0][i][3]}"

        block_data = {
            "type": "div",
            "id": f"block_{i}",
            "position": {"x": x, "y": y, "width": w, "height": h},
            "styles": {
                "background_color": background_color,
                "border_radius": "0px",
                "padding": "5px"
            },
            "children": []
        }

        # Добавляем текст, только если он действительно есть
        if text:
            block_data["children"].append({
                "type": "text",
                "content": text,
                "styles": {
                    "font_size": "16px",
                    "font_family": "Arial",
                    "color": "#000000",
                    "text_align": "left"
                }
            })

        if parent_id:
            # Если есть родитель, добавляем блок в него
            if parent_id in parent_map:
                parent_map[parent_id]["children"].append(block_data)
            else:
                parent_map[parent_id] = {"children": [block_data]}
        else:
            # Если родителя нет, это основной блок
            elements.append(block_data)
            parent_map[block_data["id"]] = block_data

    return {
        "layout": {
            "width": image.shape[1],
            "height": image.shape[0],
            "background_color": "#FFFFFF",
            "elements": elements
        }
    }

def save_to_json(data, output_file="output.json"):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Исправленный JSON сохранён в {output_file}")

if __name__ == '__main__':
    image_path = 'images/website_template_3.png'  # Изображение для теста
    layout = process_image(image_path)
    save_to_json(layout)