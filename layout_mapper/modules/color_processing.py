# color_processing.py
import cv2
import numpy as np

def detect_background(block_dict, image, 
                     std_threshold=0.18, 
                     gradient_diff=10,
                     sample_ratio=0.7):
    """
    Определяет фон блока с защитой от ложных градиентов.
    """
    
    # 1. Извлечение координат блока
    coords = block_dict["coordinatesXY"]
    x_values = [p[0] for p in coords]
    y_values = [p[1] for p in coords]
    
    x1, x2 = int(min(x_values)), int(max(x_values))
    y1, y2 = int(min(y_values)), int(max(y_values))
    w, h = x2 - x1, y2 - y1
    
    if w <= 10 or h <= 10:
        return {}

    # 2. Вырезаем центральную область
    margin_w = int(w * (1 - sample_ratio) // 2)
    margin_h = int(h * (1 - sample_ratio) // 2)
    
    roi = image[
        max(0, y1 + margin_h):min(image.shape[0], y2 - margin_h),
        max(0, x1 + margin_w):min(image.shape[1], x2 - margin_w)
    ]
    
    if roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
        return {}

    # 3. Предобработка изображения
    roi_float = roi.astype(np.float32) / 255.0
    roi_filtered = cv2.medianBlur(roi_float, 3)
    
    # 4. Анализ однородности
    median_color = np.median(roi_filtered.reshape(-1, 3), axis=0)
    std_dev = np.std(roi_filtered.reshape(-1, 3), axis=0).mean()
    
    # 5. Проверка на однородный цвет
    if std_dev < std_threshold:
        b, g, r = (median_color * 255).astype(np.uint8)
        return {"background-color": f"#{r:02X}{g:02X}{b:02X}"}

    # 6. Анализ градиента
    top_slice = roi_filtered[0]  # BGR format
    bottom_slice = roi_filtered[-1]
    
    top_color = np.median(top_slice, axis=0) * 255
    bottom_color = np.median(bottom_slice, axis=0) * 255
    
    # Конвертация в целочисленные значения (BGR -> RGB)
    tb, tg, tr = top_color.astype(int)
    bb, bg, br = bottom_color.astype(int)
    
    # 7. Проверка значимости градиента
    color_diff = max(
        abs(tr - br),  # Red
        abs(tg - bg),  # Green
        abs(tb - bb)   # Blue
    )
    
    if color_diff < gradient_diff:
        avg_r = (tr + br) // 2
        avg_g = (tg + bg) // 2
        avg_b = (tb + bb) // 2
        return {"background-color": f"#{avg_r:02X}{avg_g:02X}{avg_b:02X}"}

    # 8. Форматирование градиента
    top_hex = f"#{tr:02X}{tg:02X}{tb:02X}"
    bottom_hex = f"#{br:02X}{bg:02X}{bb:02X}"
    
    return {
        "background-image": f"linear-gradient(to bottom, {top_hex}, {bottom_hex})"
    }