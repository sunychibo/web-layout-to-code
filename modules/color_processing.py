# color_processing.py
import cv2
import numpy as np
from sklearn.cluster import KMeans

def detect_colors(block_dict, image, max_colors=3, sample_size=100):
    """
    Определяет доминирующие цвета в блоке и возвращает их в HEX-формате.
    
    Параметры:
    - block_dict: словарь с координатами блока
    - image: исходное изображение в BGR
    - max_colors: максимальное количество определяемых цветов
    - sample_size: размер выборки для анализа
    
    Возвращает: словарь с массивом цветов {"colors": ["#HEX1", "#HEX2"]}
    """
    
    # Извлечение координат блока
    coords = block_dict["coordinatesXY"]
    x_values = [p[0] for p in coords]
    y_values = [p[1] for p in coords]
    
    x1, x2 = int(min(x_values)), int(max(x_values))
    y1, y2 = int(min(y_values)), int(max(y_values))
    w, h = x2 - x1, y2 - y1
    
    if w <= 10 or h <= 10:
        return {"colors": []}

    # Вырезаем область интереса
    roi = image[y1:y2, x1:x2]
    
    if roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
        return {"colors": []}

    # Предобработка изображения
    roi_filtered = cv2.medianBlur(roi, 3)
    pixels = roi_filtered.reshape(-1, 3)
    
    # Уменьшаем выборку для производительности
    if len(pixels) > sample_size:
        pixels = pixels[np.random.choice(pixels.shape[0], sample_size, replace=False)]

    # Кластеризация цветов
    n_clusters = min(max_colors, len(pixels))
    if n_clusters < 1:
        return {"colors": []}

    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    labels = kmeans.fit_predict(pixels)
    
    # Получаем доминирующие цвета
    colors = []
    for center in kmeans.cluster_centers_:
        b, g, r = center.astype(int)
        colors.append(f"#{r:02X}{g:02X}{b:02X}")
    
    # Убираем дубликаты и сортируем по частоте
    unique_colors, counts = np.unique(colors, return_counts=True)
    sorted_colors = [color for _, color in sorted(zip(counts, unique_colors), reverse=True)]
    
    return {"colors": sorted_colors[:max_colors]}