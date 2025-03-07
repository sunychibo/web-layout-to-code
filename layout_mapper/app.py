import streamlit as st
import json
import cv2
import numpy as np
from processing import find_blocks_and_build_tree
from render_bboxes import annotate_image

def main():
    st.title("Web Layout Prototype (OpenCV + Streamlit)")

    uploaded_file = st.file_uploader("Загрузите изображение", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Читаем файл как bytes -> в OpenCV формат
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Показываем превью изображения (конвертация в RGB для корректного отображения)
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Preview of uploaded image", use_column_width=True)

        # Обработка изображения — поиск блоков
        result_json = find_blocks_and_build_tree(image)

        # Выводим JSON в интерфейсе
        st.subheader("Сгенерированный JSON")
        st.json(result_json)

        # Также сохраняем JSON локально
        with open("output-coordinates.json", "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=2)

        st.success("JSON успешно сохранён в output-coordinates.json")

        # Кнопка для отрисовки
        if st.button("Render Bboxes"):
            annotated_img = annotate_image(image, result_json, color=(0, 0, 255), thickness=2)
            # Сохраняем результат в файл (при желании)
            cv2.imwrite("annotated_result.png", annotated_img)
            st.success("Результат сохранён в файл annotated_result.png")

            # Покажем его прямо здесь в интерфейсе
            st.image(
                cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB),
                caption="Annotated image",
                use_column_width=True
            )

if __name__ == "__main__":
    main()
