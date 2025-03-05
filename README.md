# Web Layout to Code

## Описание
Этот проект позволяет преобразовать дизайн веб-страницы (изображение) в HTML и CSS код. 
Используются библиотеки OpenCV для обработки изображений и Tesseract для распознавания текста.

## Автор
- Имя: Aleksandr Chebaev
- Email: sunychibo@gmail.com
- GitHub: [sunychibo](https://github.com/sunychibo)

## Версия
Текущая версия: 1.0.0

## Установка
1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/ваш-username/web-layout-to-code.git
    ```
    
2. Перейдите в папку проекта:
    ```bash
    cd web-layout-to-code
    ```
    
3. Создайте новое локальное окружение и активируйте его:
    ```bash
    python -m venv weblayoutenv
    ```
    ```bash
    weblayoutenv\Scripts\activate
    ```
    
4. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
## Использование
Запустите скрипт:
```bash
python local_prototype.py
```
Результат будет сохранен в файл `output.html`.

## Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).