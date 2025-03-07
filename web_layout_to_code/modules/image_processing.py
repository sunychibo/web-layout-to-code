# Функции для загрузки, предобработки и выделения контуров
# modules/image_processing.py

import cv2
import numpy as np

def load_image(image_path):
    """Загружает изображение по указанному пути. Выбрасывает ошибку, если изображение не найдено."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")
    return image

def convert_color(image):
    """Преобразует изображение из BGR в RGB."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def preprocess_image(image):
    """
    Преобразует изображение в оттенки серого и затем в бинарное (черно-белое) с помощью пороговой обработки.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return binary

def get_contours(binary):
    """Находит контуры в бинарном изображении."""
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def extract_roi(image, contour):
    """
    Извлекает область интереса (ROI) по контуру.
    Возвращает вырезанный регион и кортеж с координатами и размерами (x, y, w, h).
    """
    x, y, w, h = cv2.boundingRect(contour)
    roi = image[y:y+h, x:x+w]
    return roi, (x, y, w, h)

def get_dominant_color(image, x, y, w, h):
    """
    Определяет доминирующий цвет фона блока.
    Использует среднее значение всех пикселей внутри блока.

    :param image: Исходное изображение (RGB).
    :param x, y, w, h: Координаты и размер блока.
    :return: Цвет фона в формате HEX.
    """
    roi = image[y:y+h, x:x+w]  # Вырезаем область блока
    avg_color = np.mean(roi, axis=(0, 1))  # Средний цвет в формате BGR
    avg_color_rgb = avg_color[::-1]  # Переводим в RGB

    # Конвертация в HEX-формат
    return "#{:02x}{:02x}{:02x}".format(int(avg_color_rgb[0]), int(avg_color_rgb[1]), int(avg_color_rgb[2]))

def get_text_color(image, x, y, w, h):
    """
    Определяет цвет текста в блоке.
    Если текст тёмный — возвращает чёрный, если светлый — белый.

    :param image: Исходное изображение (RGB).
    :param x, y, w, h: Координаты и размер блока.
    :return: Цвет текста в формате HEX.
    """
    roi = image[y:y+h, x:x+w]  # Вырезаем область блока
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)  # Преобразуем в оттенки серого

    # Определяем среднее значение яркости пикселей
    avg_brightness = np.mean(gray_roi)

    # Если яркость высокая — текст скорее тёмный, иначе светлый
    if avg_brightness > 127:
        return "#000000"  # Чёрный текст
    else:
        return "#FFFFFF"  # Белый текст


