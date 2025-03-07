# Функция сохранения JSON
# modules/json_handler.py

import json

def save_to_json(data, output_file="output.json"):
    """Сохраняет структуру данных в JSON-файл с отступами и кодировкой UTF-8."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Данные сохранены в файл {output_file}")
