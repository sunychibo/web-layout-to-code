"""
yolo_processing.py
Пример использования YOLO (ultralytics) для детекции элементов.
"""

import numpy as np
import cv2
# Для примера используем ultralytics
# pip install ultralytics
from ultralytics import YOLO

def detect_elements_with_yolo(image, model_path='yolov8n.pt', conf_threshold=0.5):
    """
    Загружает модель YOLO, прогоняет изображение, возвращает список детектированных объектов.
    
    :param image: np.ndarray (BGR)
    :param model_path: путь к весам YOLO (или название модели)
    :param conf_threshold: порог уверенности
    :return: список словарей:
     [
       {
         "class_id": int,
         "class_name": str,
         "confidence": float,
         "bbox": [x, y, w, h]
       },
       ...
     ]
    """
    # Загружаем модель
    model = YOLO(model_path)

    # Прогоняем inference
    results = model.predict(source=image, conf=conf_threshold)

    detected = []
    # results – объект ultralytics, обычно results[0] – список боксов
    boxes = results[0].boxes
    names = model.names  # словарь или список с названиями классов

    for box in boxes:
        cls_id = int(box.cls[0].item())  # класс
        conf   = float(box.conf[0].item())
        # xyxy формат
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        w = x2 - x1
        h = y2 - y1
        class_name = names[cls_id] if cls_id in names else f"class_{cls_id}"

        detected.append({
            "class_id": cls_id,
            "class_name": class_name,
            "confidence": conf,
            "bbox": [int(x1), int(y1), int(w), int(h)]
        })

    return detected
