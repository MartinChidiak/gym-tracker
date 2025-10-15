import streamlit as st
import streamlit.components.v1 as components
from src.pages import A_home, B_log_exercise, C_history, D_routine

def main():
    st.set_page_config(page_title="Gym Tracker", layout="wide")
    
    # Ajuste del viewport para "zoom out" por defecto en móviles.
    # Cambia initial-scale (ej. 0.75 - 0.95) según lo necesites.
    components.html(
        """
        <script>
        (function() {
          try {
            var m = document.querySelector('meta[name="viewport"]');
            if (!m) {
              m = document.createElement('meta');
              m.name = 'viewport';
              document.head.appendChild(m);
            }
            m.setAttribute('content', 'width=device-width, initial-scale=0.85, maximum-scale=5, minimum-scale=0.5, user-scalable=yes');
          } catch(e) {
            // Ignorar errores de inyección
          }
        })();
        </script>
        """,
        height=1,
    )

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