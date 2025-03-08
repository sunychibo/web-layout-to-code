import streamlit as st
import json
import os

DEFAULTS_FILE = "defaults.json"

def load_defaults():
    """Загружаем словарь с параметрами по умолчанию из defaults.json."""
    if not os.path.exists(DEFAULTS_FILE):
        return {}
    with open(DEFAULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def render_control_panel():
    """
    Отрисовывает панель управления всеми параметрами через st.form,
    чтобы изменения UI не применялись мгновенно, а лишь после нажатия «Apply changes».
    """

    st.subheader("Настройки распознавания (OpenCV)")
    
    # Если params нет в session_state, загружаем их из defaults.json
    if "params" not in st.session_state:
        st.session_state.params = load_defaults()

    # Достаём словарь params из session_state (для удобства обращения)
    p = st.session_state.params

    # Создаём форму
    with st.form("params_form"):
        st.write("Измените нужные параметры, затем нажмите 'Apply changes'")
        
        threshold_method = st.selectbox(
            "Метод бинаризации (threshold_method)",
            options=["fixed", "otsu", "triangle", "adaptive_mean", "adaptive_gaussian"],
            index=["fixed", "otsu", "triangle", "adaptive_mean", "adaptive_gaussian"].index(p.get("threshold_method", "fixed"))
        )

        threshold_value = st.slider(
            "Порог (threshold_value), если метод = fixed",
            min_value=0, max_value=255, step=1,
            value=p.get("threshold_value", 127)
        )

        max_value = st.slider(
            "Максимальное значение (max_value)",
            min_value=1, max_value=255, step=1,
            value=p.get("max_value", 255)
        )

        adaptive_block_size = st.slider(
            "adaptive_block_size (для adaptiveThreshold)",
            min_value=3, max_value=51, step=2,
            value=p.get("adaptive_block_size", 11)
        )

        adaptive_C = st.slider(
            "adaptive_C (для adaptiveThreshold)",
            min_value=-10, max_value=10, step=1,
            value=p.get("adaptive_C", 2)
        )

        morphology_kernel_size = st.slider(
            "Размер ядра для морфологии (morphology_kernel_size)",
            min_value=1, max_value=31, step=2,
            value=p.get("morphology_kernel_size", 3)
        )

        morphology_iterations = st.slider(
            "Кол-во итераций морф. операций (morphology_iterations)",
            min_value=0, max_value=5, step=1,
            value=p.get("morphology_iterations", 1)
        )

        min_block_width = st.number_input(
            "min_block_width",
            min_value=0, max_value=500, step=1,
            value=p.get("min_block_width", 20)
        )

        min_block_height = st.number_input(
            "min_block_height",
            min_value=0, max_value=500, step=1,
            value=p.get("min_block_height", 20)
        )

        retrieval_mode = st.selectbox(
            "retrieval_mode",
            ["RETR_EXTERNAL", "RETR_TREE", "RETR_CCOMP", "RETR_LIST"],
            index=["RETR_EXTERNAL", "RETR_TREE", "RETR_CCOMP", "RETR_LIST"].index(
                p.get("retrieval_mode", "RETR_EXTERNAL")
            )
        )

        approx_method = st.selectbox(
            "approx_method (аппроксимация контуров)",
            ["CHAIN_APPROX_SIMPLE", "CHAIN_APPROX_NONE", "CHAIN_APPROX_TC89_L1", "CHAIN_APPROX_TC89_KCOS"],
            index=["CHAIN_APPROX_SIMPLE", "CHAIN_APPROX_NONE", "CHAIN_APPROX_TC89_L1", "CHAIN_APPROX_TC89_KCOS"].index(
                p.get("approx_method", "CHAIN_APPROX_SIMPLE")
            )
        )

        min_area = st.number_input(
            "min_area",
            min_value=0, max_value=9999999, step=10,
            value=p.get("min_area", 0)
        )

        max_area = st.number_input(
            "max_area",
            min_value=1, max_value=99999999, step=100,
            value=p.get("max_area", 999999)
        )

        approx_polygons = st.checkbox(
            "approx_polygons (аппроксимация многоугольников)",
            value=p.get("approx_polygons", False)
        )

        # Кнопка отправки формы
        submitted = st.form_submit_button("Apply changes")

        if submitted:
            # Обновляем session_state.params
            st.session_state.params["threshold_method"] = threshold_method
            st.session_state.params["threshold_value"] = threshold_value
            st.session_state.params["max_value"] = max_value
            st.session_state.params["adaptive_block_size"] = adaptive_block_size
            st.session_state.params["adaptive_C"] = adaptive_C
            st.session_state.params["morphology_kernel_size"] = morphology_kernel_size
            st.session_state.params["morphology_iterations"] = morphology_iterations
            st.session_state.params["min_block_width"] = min_block_width
            st.session_state.params["min_block_height"] = min_block_height
            st.session_state.params["retrieval_mode"] = retrieval_mode
            st.session_state.params["approx_method"] = approx_method
            st.session_state.params["min_area"] = min_area
            st.session_state.params["max_area"] = max_area
            st.session_state.params["approx_polygons"] = approx_polygons

            st.success("Параметры обновлены!")

    # Для отладки отобразим текущее состояние params
    st.write("Текущие параметры:", st.session_state.params)
    return st.session_state.params
