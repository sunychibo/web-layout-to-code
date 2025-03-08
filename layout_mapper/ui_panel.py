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

    st.subheader("Настройки распознавания (OpenCV)")

    # Инициализация параметров по умолчанию при первом запуске
    if "params_defaults" not in st.session_state:
        st.session_state.params_defaults = load_defaults()
    
    # Инициализация пользовательских параметров
    if "params" not in st.session_state:
        st.session_state.params = {}

    # Создаём форму
    with st.form("params_form"):
        st.write("Измените нужные параметры, затем нажмите 'Apply changes'")

        current_params = {**st.session_state.params_defaults, **st.session_state.params}
        
        st.selectbox(
            "Метод бинаризации (threshold_method)",
            options=["fixed", "otsu", "triangle", "adaptive_mean", "adaptive_gaussian"],
            index=["fixed", "otsu", "triangle", "adaptive_mean", "adaptive_gaussian"].index(current_params.get("threshold_method")),
            key="threshold_method"
        )

        st.slider(
            "Порог (threshold_value), если метод = fixed",
            min_value=0, max_value=255, step=1,
            value=current_params.get("threshold_value"),
            key="threshold_value"
        )

        st.slider(
            "Максимальное значение (max_value)",
            min_value=1, max_value=255, step=1,
            value=current_params.get("max_value"),
            key="max_value"
        )

        st.slider(
            "adaptive_block_size (для adaptiveThreshold)",
            min_value=3, max_value=51, step=2,
            value=current_params.get("adaptive_block_size"),
            key="adaptive_block_size"
        )

        st.slider(
            "adaptive_C (для adaptiveThreshold)",
            min_value=-10, max_value=10, step=1,
            value=current_params.get("adaptive_C"),
            key="adaptive_C"
        )

        st.slider(
            "Размер ядра для морфологии (morphology_kernel_size)",
            min_value=1, max_value=31, step=2,
            value=current_params.get("morphology_kernel_size"),
            key="morphology_kernel_size"
        )

        st.slider(
            "Кол-во итераций морф. операций (morphology_iterations)",
            min_value=0, max_value=5, step=1,
            value=current_params.get("morphology_iterations"),
            key="morphology_iterations"
        )

        st.number_input(
            "min_block_width",
            min_value=0, max_value=500, step=1,
            value=current_params.get("min_block_width"),
            key="min_block_width"
        )

        st.number_input(
            "min_block_height",
            min_value=0, max_value=500, step=1,
            value=current_params.get("min_block_height"),
            key="min_block_height"
        )

        st.selectbox(
            "retrieval_mode",
            ["RETR_EXTERNAL", "RETR_TREE", "RETR_CCOMP", "RETR_LIST"],
            index=["RETR_EXTERNAL", "RETR_TREE", "RETR_CCOMP", "RETR_LIST"].index(
                current_params.get("retrieval_mode")
            ),
            key="retrieval_mode"
        )

        st.selectbox(
            "approx_method (аппроксимация контуров)",
            ["CHAIN_APPROX_SIMPLE", "CHAIN_APPROX_NONE", "CHAIN_APPROX_TC89_L1", "CHAIN_APPROX_TC89_KCOS"],
            index=["CHAIN_APPROX_SIMPLE", "CHAIN_APPROX_NONE", "CHAIN_APPROX_TC89_L1", "CHAIN_APPROX_TC89_KCOS"].index(
                current_params.get("approx_method")
            ),
            key="approx_method"
        )

        st.number_input(
            "min_area",
            min_value=0, max_value=9999999, step=10,
            value=current_params.get("min_area"),
            key="min_area"
        )

        st.number_input(
            "max_area",
            min_value=1, max_value=99999999, step=100,
            value=current_params.get("max_area"),
            key="max_area"
        )

        st.checkbox(
            "approx_polygons (аппроксимация многоугольников)",
            value=current_params.get("approx_polygons"),
            key="approx_polygons"
        )

        # Кнопка отправки формы
        if st.form_submit_button("Apply"):
            # Получаем ВСЕ параметры из session_state
            updated_params = {
                key: st.session_state[key] 
                for key in st.session_state.params_defaults.keys()
                if key in st.session_state
            }
            
            st.session_state.params = updated_params
            st.rerun()  # Важно для немедленного обновления
            
            print("Updated params:", updated_params)
            print("Params AFTER update:", st.session_state.params)
            st.success("Параметры обновлены!")

    # Для отладки отобразим текущее состояние params
    st.write("Текущие параметры:", {**st.session_state.params_defaults, **st.session_state.params})
