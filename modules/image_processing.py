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
