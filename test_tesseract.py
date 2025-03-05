import pytesseract
from PIL import Image
# Пример изображения с текстом
image = Image.open('images/test_image-text.jpeg')
# text = pytesseract.image_to_string(image) /latin by default
text = pytesseract.image_to_string(image, lang='rus')
print(text)