import pytesseract
from PIL import Image

# Укажите путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Пример изображения с текстом
image = Image.open('images/test_image-text.jpeg')
# text = pytesseract.image_to_string(image) /latin by default
text = pytesseract.image_to_string(image, lang='rus')
print(text)