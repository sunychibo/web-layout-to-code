import cv2
import pytesseract
from PIL import Image
import numpy as np
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image(image_path):
    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка: Не удалось загрузить изображение. Проверьте путь к файлу.")
        return {"layout": {"width": 0, "height": 0, "elements": []}}

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Преобразуем изображение в черно-белое
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Применяем пороговую обработку
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    # Находим контуры блоков
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Создаем список для хранения элементов
    elements = []

    # Обрабатываем каждый контур
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        
        # Вырезаем область изображения, соответствующую контуру
        roi = image[y:y+h, x:x+w]
        
        # Распознаем текст в области
        text = pytesseract.image_to_string(roi)

        # Добавляем элемент в список
        elements.append({
            "type": "div",
            "id": f"block_{i}",  # Уникальный идентификатор
            "position": {"x": x, "y": y, "width": w, "height": h},
            "styles": {
                "background_color": "#FFFFFF",  # Белый цвет по умолчанию
                "border_radius": "0px",  # Скругление углов
                "padding": "0px"  # Отступы внутри элемента
            },
            "children": [
                {
                    "type": "text",
                    "content": text.strip(),  # Распознанный текст
                    "styles": {
                        "font_size": "16px",
                        "font_family": "Arial",
                        "color": "#000000",
                        "text_align": "left"
                    }
                }
            ]
        })

    # Возвращаем структуру данных
    return {
        "layout": {
            "width": image.shape[1],
            "height": image.shape[0],
            "background_color": "#FFFFFF",  # Цвет фона макета
            "elements": elements
        }
    }

def save_to_json(data, output_file="output.json"):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Данные сохранены в файл {output_file}")

def generate_html_css(layout):
    html = []
    css = []

    # Проверка наличия ключа "elements"
    if "elements" not in layout["layout"]:
        print("Ошибка: Ключ 'elements' отсутствует в структуре layout.")
        return ""

    for element in layout["layout"]["elements"]:
        # Генерация HTML
        html.append(f'<div id="{element["type"]}_{element["position"]["x"]}_{element["position"]["y"]}"></div>')

        # Генерация CSS
        css.append(
            f'#div_{element["position"]["x"]}_{element["position"]["y"]} {{\n'
            f'  position: absolute;\n'
            f'  left: {element["position"]["x"]}px;\n'
            f'  top: {element["position"]["y"]}px;\n'
            f'  width: {element["position"]["width"]}px;\n'
            f'  height: {element["position"]["height"]}px;\n'
            f'  background-color: {element["styles"]["background_color"]};\n'
            f'}}\n'
        )

    # Объединяем HTML и CSS
    html_code = "<!DOCTYPE html>\n<html>\n<head>\n<style>\n" + "\n".join(css) + "</style>\n</head>\n<body>\n" + "\n".join(html) + "\n</body>\n</html>"
    return html_code

if __name__ == '__main__':
    # Путь к изображению
    image_path = 'images/website_template.png' # Замените на путь к вашему изображению

    # Обработка изображения
    layout = process_image(image_path)

    # Сохранение результата в JSON
    save_to_json(layout)