# ...existing code...
import re
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict
from src.utils.db import log_exercise
import io
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROUTINES_PATH = PROJECT_ROOT / "data" / "routines.xlsx"

def _parse_reps_series(cell: str):
    # Intenta extraer números simples (ej. "10 reps", "3x10", "3 series x 10 reps")
    if not isinstance(cell, str):
        return 0, 1
    nums = list(map(int, re.findall(r"\d+", cell)))
    if len(nums) == 0:
        return 0, 1
    if len(nums) == 1:
        return nums[0], 1
    return nums[-1], nums[0]

def _safe_key(value: str, suffix: str = "") -> str:
    s = str(value)
    s = re.sub(r"[^a-zA-Z0-9_-]", "_", s)
    if suffix:
        return f"{s}_{suffix}"
    return s

def _render_routine_html(modified: list, title: str, subtitle: str = "") -> str:
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    styles = """
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial; padding:10px; }
      .container { max-width:720px; margin:0 auto; }
      h1 { font-size:20px; margin-bottom:6px; }
      h2 { font-size:14px; color:#666; margin-top:0; margin-bottom:12px; }
      table { width:100%; border-collapse:collapse; font-size:13px; }
      th, td { padding:8px 6px; border-bottom:1px solid #eee; text-align:left; }
      th { background:#f7f7f7; font-weight:600; }
      .meta { font-size:12px; color:#666; margin-bottom:8px; }
      @media (max-width:420px) {
        h1 { font-size:18px; }
        th, td { padding:8px 4px; font-size:12px; }
      }
    </style>
    """
    rows_html = ""
    for i, it in enumerate(modified, 1):
        rows_html += f"<tr><td>{i}</td><td>{it.get('exercise_name','')}</td><td>{it.get('weight','')}</td><td>{it.get('series','')}</td><td>{it.get('repetitions_or_time','')}</td></tr>"

    html = f"""<!doctype html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <meta charset="utf-8"/>
      {styles}
    </head>
    <body>
      <div class="container">
        <h1>{title}</h1>
        <div class="meta">{subtitle} · Generado: {date_str}</div>
        <table>
          <thead><tr><th>#</th><th>Ejercicio</th><th>Peso (kg)</th><th>Series</th><th>Reps/Tiempo</th></tr></thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """
    return html

def load_routines(path: Path) -> Dict[str, pd.DataFrame]:
    if not path.exists():
        return {}
    try:
        sheets = pd.read_excel(path, sheet_name=None)
        return sheets
    except Exception:
        df = pd.read_excel(path, sheet_name=0)
        return {"Rutina": df}

def show():
    st.title("Rutinas predefinidas")
    st.write("Selecciona una rutina y ajusta solo peso/repeticiones/series antes de registrar.")

    routines = load_routines(ROUTINES_PATH)
    if not routines:
        st.info(f"No se encontró {ROUTINES_PATH}. Coloca tu archivo Excel en data/routines.xlsx")
        return

    routine_names = list(routines.keys())
    selected = st.selectbox("Selecciona una rutina", routine_names)
    df = routines[selected].copy()

    day_col = next((c for c in df.columns if c.lower() in ("día", "dia", "day")), None)
    if day_col is not None:
        unique_days = sorted(df[day_col].dropna().astype(str).unique().tolist())
        day_options = ["Todos"] + unique_days
        selected_day = st.selectbox("Filtrar por día", day_options, index=0)
        if selected_day != "Todos":
            df_filtered = df[df[day_col].astype(str) == selected_day].copy()
        else:
            df_filtered = df.copy()
    else:
        selected_day = None
        df_filtered = df.copy()

    st.write("Vista previa de la rutina:")
    st.dataframe(df_filtered)

    st.markdown("### Ajustes rápidos por ejercicio")
    category_col = next((c for c in df_filtered.columns if c.lower() in ("categoría", "categoria", "category")), None)

    with st.form(key="routine_form"):
        modified = []
        if category_col is None:
            groups = [("Sin categoría", df_filtered.reset_index())]
        else:
            groups = [(str(cat) if pd.notna(cat) else "Sin categoría", grp.reset_index()) for cat, grp in df_filtered.groupby(df_filtered[category_col])]

        for cat_name, grp_df in groups:
            st.markdown(f"### {cat_name}")
            with st.container():
                for local_i, row in grp_df.iterrows():
                    idx = row["index"]
                    day_val = str(row.get(day_col, row.get('Día', row.get('Dia', '')))) if day_col else str(row.get('Día', row.get('Dia', '')))
                    cat_val = str(row.get(category_col, row.get('Categoría', row.get('Categoria', cat_name))))
                    ex_val = str(row.get('Ejercicio', row.get('Exercise', '')))

                    raw_series = row.get('Series', row.get('Series ', None))
                    raw_reps_time = row.get('Reps/Tiempo', row.get('Reps', row.get('Reps/Time', row.get('Reps/Tiempo ', None))))
                    if raw_series is None or (isinstance(raw_series, float) and pd.isna(raw_series)):
                        combined = row.get('Series/Reps/Descanso', row.get('Series/Reps/Desc', None))
                        _, fallback_series = _parse_reps_series(combined if isinstance(combined, str) else str(combined) if combined is not None else "")
                        default_series = int(fallback_series)
                    else:
                        try:
                            default_series = int(raw_series)
                        except Exception:
                            nums = re.findall(r"\d+", str(raw_series))
                            default_series = int(nums[0]) if nums else 1

                    if raw_reps_time is None or (isinstance(raw_reps_time, float) and pd.isna(raw_reps_time)):
                        combined = row.get('Series/Reps/Descanso', row.get('Series/Reps/Desc', None))
                        fallback_reps, _ = _parse_reps_series(combined if isinstance(combined, str) else str(combined) if combined is not None else "")
                        default_reps_text = str(fallback_reps) if fallback_reps else ""
                    else:
                        default_reps_text = str(raw_reps_time)

                    exp_label = f"{local_i + 1}. {ex_val}"
                    key_suffix = f"{idx}_{local_i}"
                    ex_key = _safe_key(f"{ex_val}_{cat_name}", key_suffix)

                    with st.expander(exp_label, expanded=False):
                        # encabezado reducido (sin Día ni Categoría)
                        header_cols = st.columns([3, 1, 1, 1])
                        headers = ["Ejercicio", "Peso (kg)", "Series", "Reps/Tiempo"]
                        for c, h in zip(header_cols, headers):
                            c.markdown(f"**{h}**")

                        cols = st.columns([3, 1, 1, 1])
                        exercise_name = cols[0].text_input("", value=ex_val, key=f"ex_{ex_key}")
                        weight = cols[1].number_input("", min_value=0.0, step=0.5, value=float(row.get('Peso', 0.0) or 0.0), key=f"w_{ex_key}")
                        series = cols[2].number_input("", min_value=1, step=1, value=int(default_series), key=f"s_{ex_key}")
                        reps_time = cols[3].text_input("", value=default_reps_text, key=f"rt_{ex_key}")
                        # descripción en una fila aparte (ancho completo)
                        description = st.text_area("Descripción", value=row.get('Descripción', row.get('Description', '')), key=f"desc_{ex_key}", height=80)

                    reps_int = int(next(iter(re.findall(r"\d+", str(reps_time))), 0)) if isinstance(reps_time, str) else int(reps_time) if reps_time else 0
                    modified.append({
                        "exercise_name": exercise_name,
                        "weight": float(weight),
                        "repetitions_or_time": reps_time,
                        "repetitions": reps_int,
                        "series": int(series),
                        "day": day_val,
                        "category": cat_val,
                        "description": description,
                    })

        save_to_history = st.checkbox("Guardar ejercicios en historial (base de datos) al enviar", value=True)
        submit_save = st.form_submit_button("Aplicar y registrar")
        submit_export = st.form_submit_button("Vista previa y exportar (CSV)")

    if submit_save:
        st.success("Rutina procesada.")
        if save_to_history:
            for item in modified:
                try:
                    log_exercise(weight=item["weight"], repetitions=item["repetitions"], series=item["series"], exercise_name=item["exercise_name"])
                except Exception as e:
                    st.error(f"Error al guardar {item['exercise_name']}: {e}")
            st.success("Ejercicios guardados en historial.")

        export_df = pd.DataFrame(modified)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar rutina modificada (CSV)", csv, file_name=f"{selected}_modified.csv", mime="text/csv")

        # mostrar vista previa HTML de la rutina (solo CSV/HTML, sin PDF)
        pdf_title = f"Rutina - {selected}" + (f" - {selected_day}" if selected_day and selected_day != "Todos" else "")
        html = _render_routine_html(modified, pdf_title, subtitle=f"Rutina: {selected}")
        st.markdown("#### Vista previa")
        try:
            st.components.v1.html(html, height=600, scrolling=True)
        except Exception:
            st.markdown("Vista previa no disponible en este entorno.")

    elif submit_export:
        st.info("Generando vista previa y archivos de exportación (no se guardará en historial).")
        export_df = pd.DataFrame(modified)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar rutina modificada (CSV) — vista previa", csv, file_name=f"{selected}_modified_preview.csv", mime="text/csv")

        pdf_title = f"Rutina - {selected}" + (f" - {selected_day}" if selected_day and selected_day != "Todos" else "")
        html = _render_routine_html(modified, pdf_title, subtitle=f"Rutina: {selected}")

        st.markdown("#### Vista previa")
        try:
            st.components.v1.html(html, height=600, scrolling=True)
        except Exception:
            st.markdown("Vista previa no disponible en este entorno.")

def show_routine():
    show()
# ...existing code...