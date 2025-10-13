# ...existing code...
import streamlit as st
import pandas as pd
import time
from src.utils.db import get_exercise_history, delete_exercise

def _safe_rerun():
    """
    Intentar forzar una recarga. Si st.experimental_rerun no existe,
    actualizar params de query usando st.query_params o usar session_state como fallback.
    """
    try:
        st.experimental_rerun()
    except Exception:
        try:
            # Construir copia modificable de los query params y reasignarlos.
            params = dict(st.query_params) if hasattr(st, "query_params") else {}
            params["_refresh"] = str(int(time.time()))
            st.query_params = params
        except Exception:
            st.session_state["_refresh"] = st.session_state.get("_refresh", 0) + 1

def display_exercise_history():
    st.title("Historial de Ejercicios")

    history = get_exercise_history()
    df = pd.DataFrame(history) if history else pd.DataFrame()

    if df.empty:
        st.write("No hay ejercicios registrados aún.")
        return

    # Asegurar columna id y columnas en el orden deseado
    if 'id' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'id'})

    cols_to_show = ['id', 'date', 'exercise_name', 'weight', 'repetitions', 'series']
    # si faltara alguna columna, la creamos para evitar errores al renderizar
    for c in cols_to_show:
        if c not in df.columns:
            df[c] = ""

    st.markdown("Historial (formato tabular). Usa el botón ❌ a la derecha para eliminar un registro.")
    # Header row
    header_cols = st.columns([1, 2, 4, 1, 1, 1, 1])
    headers = ["ID", "Fecha", "Ejercicio", "Peso (kg)", "Reps", "Series", ""]
    for hc, h in zip(header_cols, headers):
        hc.markdown(f"**{h}**")

    # Filas: mostrar cada registro en una fila con botón a la derecha
    for _, row in df.iterrows():
        rec_id = int(row['id']) if str(row['id']).isdigit() else row['id']
        date = row.get('date', "")
        name = row.get('exercise_name', "")
        weight = row.get('weight', "")
        reps = row.get('repetitions', "")
        sets = row.get('series', "")

        rcols = st.columns([1, 2, 4, 1, 1, 1, 1])
        rcols[0].write(rec_id)
        rcols[1].write(str(date))
        rcols[2].write(str(name))
        rcols[3].write(str(weight))
        rcols[4].write(str(reps))
        rcols[5].write(str(sets))

        # botón de eliminar a la derecha
        if rcols[6].button("❌ Eliminar", key=f"del_{rec_id}"):
            try:
                delete_exercise(rec_id)
                st.success(f"Registro {rec_id} eliminado.")
                _safe_rerun()
            except Exception as e:
                st.error(f"Error al eliminar {rec_id}: {e}")

# Backwards-compatible aliases expected by app/tests
def show():
    display_exercise_history()

def show_history():
    display_exercise_history()

if __name__ == "__main__":
    display_exercise_history()
# ...existing code...