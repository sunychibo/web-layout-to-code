# text_recognition_processing.py
import cv2
import easyocr
import numpy as np

# Инициализация модели при первом вызове
_reader = None

def init_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(
            ['ru', 'en'],  # Поддерживаемые языки
            gpu=False,      # Для использования CPU установите False
            model_storage_directory='./model_storage',
            download_enabled=True
        )

def extract_text(block_dict, image):
    """
    Извлекает текст из блока с помощью EasyOCR
    """
    init_reader()
    
    coords = block_dict["coordinatesXY"]
    
    # Получаем ограничивающий прямоугольник
    x_values = [p[0] for p in coords]
    y_values = [p[1] for p in coords]
    x1, x2 = int(min(x_values)), int(max(x_values))
    y1, y2 = int(min(y_values)), int(max(y_values))
    
    # Проверка валидности координат
    h, w = image.shape[:2]
    x1 = max(0, min(x1, w-1))
    x2 = max(0, min(x2, w-1))
    y1 = max(0, min(y1, h-1))
    y2 = max(0, min(y2, h-1))
    
    if x2 <= x1 or y2 <= y1:
        return {"text": ""}
    
    # Вырезаем ROI и конвертируем в RGB
    roi = image[y1:y2, x1:x2]
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    
    # Распознавание текста
    results = _reader.readtext(roi_rgb, paragraph=True)
    
    # Собираем все тексты
    texts = [detection[1] for detection in results]
    full_text = "\n".join(texts)
    
    return {"text": full_text.strip()}