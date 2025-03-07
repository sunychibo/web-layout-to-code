# Функция генерации HTML и CSS
# modules/html_generator.py

def generate_html_css(layout):
    """Генерирует HTML и CSS на основе переданной структуры layout."""
    html = []
    css = []

    if "elements" not in layout["layout"]:
        print("Ошибка: Ключ 'elements' отсутствует в структуре layout.")
        return ""

    for element in layout["layout"]["elements"]:
        # Генерация HTML с включением распознанного текста (если он есть)
        content = element["children"][0]["content"] if element.get("children") else ""
        html.append(
            f'<div id="{element["type"]}_{element["position"]["x"]}_{element["position"]["y"]}">'
            f'{content}'
            '</div>'
        )

        # Генерация CSS (убедитесь, что id в CSS соответствует id в HTML)
        css.append(
            f'#div_{element["position"]["x"]}_{element["position"]["y"]} {{\n'
            f'  position: absolute;\n'
            f'  left: {element["position"]["x"]}px;\n'
            f'  top: {element["position"]["y"]}px;\n'
            f'  width: {element["position"]["width"]}px;\n'
            f'  height: {element["position"]["height"]}px;\n'
            f'  background-color: {element["styles"]["background_color"]};\n'
            f'}}\n'
        )

    html_code = (
        "<!DOCTYPE html>\n<html>\n<head>\n<style>\n" +
        "\n".join(css) +
        "</style>\n</head>\n<body>\n" +
        "\n".join(html) +
        "\n</body>\n</html>"
    )
    return html_code
