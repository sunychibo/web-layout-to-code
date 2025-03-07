import streamlit as st
import json
import cv2
import numpy as np

from processing import find_blocks_and_build_tree
from render_bboxes import annotate_image
from ui_panel import render_control_panel

def main():
    st.title("Web Layout Prototype (OpenCV + Streamlit)")

    # 1. Загрузка изображения
    uploaded_file = st.file_uploader("Загрузите изображение", type=["png", "jpg", "jpeg"])

    # 2. Панель управления (через форму)
    params = render_control_panel()

    # Если ещё нет ключей для хранения результата, создадим
    if "result_json" not in st.session_state:
        st.session_state.result_json = None
    if "original_image" not in st.session_state:
        st.session_state.original_image = None

    # 3. Кнопка "Process Image"
    if st.button("Process Image"):
        if uploaded_file is None:
            st.warning("Сначала загрузите изображение!")
        else:
            # Считываем изображение
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            st.session_state.original_image = image

            # Вызываем нашу функцию с текущими params
            result_json = find_blocks_and_build_tree(image, params=params)
            st.session_state.result_json = result_json

            # Показываем JSON
            st.subheader("Сгенерированный JSON")
            st.json(result_json)

            # Сохраняем локально
            with open("output-coordinates.json", "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            st.success("JSON успешно сохранён в output-coordinates.json")

    # 4. Если result_json уже есть — показываем повторно (даже если кнопка не нажата)
    if st.session_state.result_json is not None:
        st.subheader("Сгенерированный JSON")
        st.json(st.session_state.result_json)

        # Кнопка Render Bboxes
        if st.button("Render Bboxes"):
            if st.session_state.original_image is None:
                st.warning("Нет исходного изображения!")
            else:
                annotated_img = annotate_image(
                    st.session_state.original_image,
                    st.session_state.result_json,
                    color=(0, 0, 255),
                    thickness=2
                )
                cv2.imwrite("annotated_result.png", annotated_img)
                st.success("Результат сохранён в файл annotated_result.png")

                st.image(
                    cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB),
                    caption="Annotated image",
                    use_column_width=True
                )

    # 5. Превью загруженного изображения
    if uploaded_file is not None:
        st.subheader("Preview загруженного изображения")
        file_bytes2 = np.frombuffer(uploaded_file.getvalue(), np.uint8)
        img2 = cv2.imdecode(file_bytes2, cv2.IMREAD_COLOR)
        st.image(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB), use_column_width=True)

if __name__ == "__main__":
    main()
