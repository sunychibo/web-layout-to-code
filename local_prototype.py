import cv2
import pytesseract
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

# Укажите путь к Tesseract, если он не добавлен в PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        elements.append({
            "type": "div",
            "position": {"x": x, "y": y, "width": w, "height": h},
            "styles": {"background_color": "#FFFFFF"}  # Белый цвет по умолчанию
        })

    # Отладочная информация
    print(f"Найдено контуров: {len(contours)}")
    print(f"Элементы: {elements}")

    # Возвращаем структуру данных
    return {
        "layout": {
            "width": image.shape[1],
            "height": image.shape[0],
            "elements": elements  # Убедитесь, что элементы добавлены в ключ "elements"
        }
    }

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
    image_path = 'images/website_template.png'  # Замените на путь к вашему изображению

    # Обработка изображения
    layout = process_image(image_path)

    # Генерация HTML и CSS
    html_css = generate_html_css(layout)

    # Сохранение результата в файл
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(html_css)

    print("HTML и CSS успешно сгенерированы и сохранены в файл output.html")