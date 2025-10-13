import streamlit as st

def exercise_form():
    st.header("Registro de Ejercicio")
    
    with st.form(key='exercise_form'):
        exercise_name = st.text_input("Nombre del ejercicio")
        weight = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
        repetitions = st.number_input("Repeticiones", min_value=1, step=1)
        sets = st.number_input("Series", min_value=1, step=1)
        
        submit_button = st.form_submit_button(label='Registrar Ejercicio')
        
        if submit_button:
            # Aquí se puede agregar la lógica para guardar los datos en la base de datos
            st.success(f"Ejercicio registrado: {exercise_name}, Peso: {weight}kg, Repeticiones: {repetitions}, Series: {sets}")