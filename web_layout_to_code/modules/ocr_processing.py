# Функции для распознавания текста
# modules/ocr_processing.py

import pytesseract

# Укажите путь к Tesseract, если это необходимо для вашей системы
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(roi):
    """Распознаёт текст на вырезанной области (ROI) и возвращает его без лишних пробелов."""
    text = pytesseract.image_to_string(roi)
    return text.strip()
