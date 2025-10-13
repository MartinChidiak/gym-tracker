import streamlit as st
from src.utils import db

def show():
    st.title("Registrar Ejercicio")

    with st.form(key="exercise_form"):
        exercise_name = st.text_input("Nombre del ejercicio")
        weight = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
        repetitions = st.number_input("Repeticiones", min_value=1, step=1)
        series = st.number_input("Series", min_value=1, step=1)
        submit = st.form_submit_button("Registrar Ejercicio")

        if submit:
            try:
                db.log_exercise(weight=weight, repetitions=repetitions, series=series, exercise_name=exercise_name)
                st.success(f"Ejercicio registrado: {exercise_name}, Peso: {weight}kg, Repeticiones: {repetitions}, Series: {series}")
            except Exception as e:
                st.error(f"Ocurrió un error al registrar: {e}")

# Backwards compatibility: export the helper functions/tests expect
get_connection = db.get_connection
create_exercise_table = db.create_exercise_table
insert_exercise = db.insert_exercise
get_exercise_history = db.get_exercise_history
log_exercise = db.log_exercise
