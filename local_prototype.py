# local_prototype.py

import cv2
import numpy as np

# Импорт функций из модулей
from modules import image_processing, ocr_processing, json_handler, html_generator

def process_image(image_path):
    # Загрузка и конвертация изображения
    image = image_processing.load_image(image_path)
    image = image_processing.convert_color(image)
    
    # Предобработка: преобразование в черно-белое изображение
    binary = image_processing.preprocess_image(image)
    
    # Поиск контуров
    contours = image_processing.get_contours(binary)

    elements = []
    for i, contour in enumerate(contours):
        roi, (x, y, w, h) = image_processing.extract_roi(image, contour)
        text = ocr_processing.extract_text(roi)

        elements.append({
            "type": "div",
            "id": f"block_{i}",
            "position": {"x": x, "y": y, "width": w, "height": h},
            "styles": {
                "background_color": "#FFFFFF",  # Будет улучшено на следующих шагах
                "border_radius": "0px",
                "padding": "0px"  # Будет вычисляться далее
            },
            "children": [
                {
                    "type": "text",
                    "content": text,
                    "styles": {
                        "font_size": "16px",  # Оценка параметров шрифта будет добавлена позже
                        "font_family": "Arial",
                        "color": "#000000",
                        "text_align": "left"
                    }
                }
            ]
        })

    layout = {
        "layout": {
            "width": image.shape[1],
            "height": image.shape[0],
            "background_color": "#FFFFFF",
            "elements": elements
        }
    }
    return layout

if __name__ == '__main__':
    image_path = 'images/website_template.png'  # Замените на нужное изображение
    layout = process_image(image_path)
    
    # Сохранение результата в JSON
    json_handler.save_to_json(layout)
    
    # Генерация HTML и запись в файл
    html_code = html_generator.generate_html_css(layout)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_code)
