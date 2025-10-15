# ...existing code...
import streamlit as st
from src.utils import db
import re

def show():
    st.title("Registrar Ejercicio")

    with st.form(key="exercise_form"):
        day = st.text_input("Día")
        category = st.text_input("Categoría")
        exercise_name = st.text_input("Ejercicio")
        weight = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
        series = st.number_input("Series", min_value=1, step=1)
        reps_time = st.text_input("Reps/Tiempo (ej. 10, 30s, 0:45)")

        submit = st.form_submit_button("Registrar Ejercicio")

        if submit:
            # intentar extraer un número de 'reps_time' para guardar en la BD
            found = re.findall(r"\d+", str(reps_time))
            repetitions = int(found[0]) if found else 0
            try:
                db.log_exercise(weight=weight, repetitions=repetitions, series=series, exercise_name=exercise_name)
                st.success(
                    f"Ejercicio registrado: {exercise_name} | Día: {day} | Categoría: {category} | "
                    f"Peso: {weight}kg | Series: {series} | Reps/Tiempo: {reps_time}"
                )
            except Exception as e:
                st.error(f"Ocurrió un error al registrar: {e}")

# Backwards compatibility: export the helper functions/tests expect
get_connection = db.get_connection
create_exercise_table = db.create_exercise_table
insert_exercise = db.insert_exercise
get_exercise_history = db.get_exercise_history
log_exercise = db.log_exercise
# ...existing code...