import streamlit as st
from src.pages import A_home, B_log_exercise, C_history, D_routine

def main():
    st.set_page_config(page_title="Gym Tracker", layout="wide")
    
    st.sidebar.title("Navegación")
    page = st.sidebar.radio("Selecciona una página:", ("Inicio", "Registrar Ejercicio", "Historial", "Rutinas"))

    if page == "Inicio":
        A_home.show()
    elif page == "Registrar Ejercicio":
        B_log_exercise.show()
    elif page == "Historial":
        C_history.show()
    elif page == "Rutinas":
        D_routine.show()


def show():
    # Adapter para que app.py pueda llamar A_home.show()
    main()

if __name__ == "__main__":
    main()