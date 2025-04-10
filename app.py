import streamlit as st
import json
import cv2
import numpy as np

from modules.opencv_processing import find_blocks_and_build_tree
from modules.color_processing import detect_colors
from modules.text_recognition_processing import extract_text
from modules.render_bboxes import annotate_image
from modules.html_processing import generate_html
from ui_panel import render_control_panel

def main():
    
    # Если ещё нет ключей для хранения результата, создадим
    if "result_json" not in st.session_state:
        st.session_state.result_json = None
    if "original_image" not in st.session_state:
        st.session_state.original_image = None

    st.title("Layout Mapper")
    st.subheader("Based on: OpenCV, EasyOSR, Scikit-learn")

    # 1. Загрузка изображения
    uploaded_img = st.file_uploader("Загрузите изображение", type=["png", "jpg", "jpeg"])
    if uploaded_img is not None:
        uploaded_img_uint8 = np.frombuffer(uploaded_img.getvalue(), np.uint8)
        uploaded_img_rgb = cv2.imdecode(uploaded_img_uint8, cv2.IMREAD_COLOR)
        st.session_state.original_image = uploaded_img_rgb
        st.image(cv2.cvtColor(uploaded_img_rgb, cv2.COLOR_BGR2RGB), caption="Uploaded image", use_container_width=True)

    # 2. Отрисовка панели настроек и выгрузка параметров из панели управления (через форму)
    render_control_panel()

    # 3. Получаем актуальные параметры (объединение дефолтных и пользовательских)
    def get_params():
        return {**st.session_state.params_defaults, **st.session_state.params}

    # 4. Кнопка "Process Image"
    if st.session_state.original_image is not None:
        if st.button("Process Image"):

            def extract_text_and_color(block, image, parent_key=""):
                for key, data in block.items():
                    # Определяем фон
                    bg_info = detect_colors(data, image)
                    data.update(bg_info)
                    
                    # Распознаем текст
                    text_info = extract_text(data, image)
                    data.update(text_info)
                    
                    # Обрабатываем детей
                    if data["children"]:
                        extract_text_and_color(data["children"], image, f"{parent_key}_{key}")

            # Считываем изображение и идентифицируем структурные блоки
            result_json = find_blocks_and_build_tree(st.session_state.original_image, get_params())
            # Для каждого блока - определяем фон, распознаём текст
            extract_text_and_color(result_json["block_00"]["children"], st.session_state.original_image)
            st.session_state.result_json = result_json

            # Сохраняем JSON локально
            with open("output-coordinates.json", "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            st.success("JSON успешно сохранён в output-coordinates.json")

    # 5. Вывод JSON
    if st.session_state.result_json is not None:
        st.subheader("Сгенерированный JSON")
        st.json(st.session_state.result_json)

    # 6. Кнопка Render Bboxes
    if st.session_state.result_json is not None:
        if st.button("Render Bboxes"):
            if st.session_state.original_image is None:
                st.warning("Нет исходного изображения в session_state.original_image")
            else:
                # Аннотируем
                annotated_img = annotate_image(st.session_state.original_image, st.session_state.result_json, (255, 0, 127), 1) # BGR
                cv2.imwrite("annotated_result.png", annotated_img)
                st.success("Результат сохранён в файл annotated_result.png")

                st.image(
                    cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB),
                    caption="Annotated image",
                    use_container_width=True
                )

    # 7. Кнопка "Generate HTML Collection"
    if st.session_state.result_json is not None:
        if st.button("Generate HTML Collection"):
            if 'result_json' in st.session_state:
                # Генерируем HTML файл
                generate_html(st.session_state.result_json)
                
                # Показываем превью
                st.success("HTML файл успешно сгенерирован!")
                st.subheader("Preview blocks.html")
                
                # Читаем и отображаем содержимое файла
                with open("blocks.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                    st.html(html_content)
            else:
                st.warning("Сначала обработайте изображение через 'Process Image'!")

if __name__ == "__main__":
    main()
