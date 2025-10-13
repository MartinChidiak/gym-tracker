# ...existing code...
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
    import re
    nums = list(map(int, re.findall(r"\d+", cell)))
    if len(nums) == 0:
        return 0, 1
    if len(nums) == 1:
        # si solo hay un número lo tomamos como reps
        return nums[0], 1
    # si hay dos números: (series, reps) o (reps, descanso) -> asumimos (reps, series) según formato
    return nums[-1], nums[0]

# --- NUEVAS FUNCIONES: render HTML y generar PDF ---
def _render_routine_html(modified: list, title: str, subtitle: str = "") -> str:
    """Genera HTML responsivo para la rutina (útil para convertir a PDF)."""
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

def _html_to_pdf_bytes(html: str) -> bytes | None:
    """Intenta convertir HTML a PDF. Usa WeasyPrint si está disponible; si no, ReportLab como fallback."""
    # Intentar WeasyPrint
    try:
        from weasyprint import HTML, CSS
        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 10mm }')])
        return pdf
    except Exception:
        pass

    # Fallback simple con ReportLab (más limitado en estilo)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=18)
        styles = getSampleStyleSheet()
        elems = []
        # título simple
        elems.append(Paragraph("Rutina exportada", styles['Heading2']))
        elems.append(Spacer(1, 6))
        # parse minimal table from HTML rows (simple approach: re-create from html string)
        # Para mantenerlo robusto, el caller puede pasar 'modified' directamente a una función separada.
        # Aquí simplemente extraemos filas con tags <tr>... (básico, pero suficiente como fallback).
        import re
        trs = re.findall(r"<tr>(.*?)</tr>", html, flags=re.S)
        # construir data (tomar texto entre <td>)
        data = []
        for tr in trs[1:]:  # skip header
            tds = re.findall(r"<td>(.*?)</td>", tr, flags=re.S)
            data.append([td.strip() for td in tds])
        if not data:
            data = [["No hay ejercicios", "", "", "", ""]]
        table = Table([["#", "Ejercicio", "Peso (kg)", "Series", "Reps/Tiempo"]] + data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f7f7f7')),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elems.append(table)
        doc.build(elems)
        buffer.seek(0)
        return buffer.read()
    except Exception:
        return None

def load_routines(path: Path) -> Dict[str, pd.DataFrame]:
    if not path.exists():
        return {}
    # lee todas las hojas; cada hoja -> una rutina
    try:
        sheets = pd.read_excel(path, sheet_name=None)
        return sheets
    except Exception:
        # intenta leer primera hoja como fallback
        df = pd.read_excel(path, sheet_name=0)
        return {"Rutina": df}

# ...existing code...
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

    # Nuevo: detectar columna de día y permitir filtrar por día
    day_col = next((c for c in df.columns if c.lower() in ("día", "dia", "day")), None)
    if day_col is not None:
        # obtener valores únicos (como strings) y ofrecer opción "Todos"
        unique_days = sorted(df[day_col].dropna().astype(str).unique().tolist())
        day_options = ["Todos"] + unique_days
        selected_day = st.selectbox("Filtrar por día", day_options, index=0)
        if selected_day != "Todos":
            df_filtered = df[df[day_col].astype(str) == selected_day].copy()
        else:
            df_filtered = df.copy()
    else:
        # si no existe columna día, no filtrar
        selected_day = None
        df_filtered = df.copy()

    # Normalizar nombres de columnas esperadas
    # Esperamos columnas como: Día, Categoría, Ejercicio, Series, Reps/Tiempo, Peso
    # Mantenemos todo visible y añadimos inputs para peso, series y reps/tiempo.
    df_cols = df_filtered.columns.tolist()
    st.write("Vista previa de la rutina:")
    st.dataframe(df_filtered)

    st.markdown("### Ajustes rápidos por ejercicio")
    with st.form(key="routine_form"):
        modified = []
        for idx, row in df_filtered.iterrows():
            # columnas: Día | Categoría | Ejercicio | Peso | Series | Reps/Tiempo
            cols = st.columns([1, 2, 3, 1, 1, 1])

            # obtener valores de día usando la columna detectada para coherencia con el filtro
            day_val = str(row.get(day_col, row.get('Día', row.get('Dia', '')))) if day_col else str(row.get('Día', row.get('Dia', '')))
            cat_val = str(row.get('Categoría', row.get('Categoria', '')))
            ex_val = str(row.get('Ejercicio', row.get('Exercise', '')))

            # Campos editables en la misma fila
            day = cols[0].text_input("Día", value=day_val, key=f"day_{idx}")
            category = cols[1].text_input("Categoría", value=cat_val, key=f"cat_{idx}")
            exercise_name = cols[2].text_input("Ejercicio", value=ex_val, key=f"ex_{idx}")

            # obtener valores por defecto desde columnas dedicadas (Series y Reps/Tiempo)
            raw_series = row.get('Series', row.get('Series ', None))
            raw_reps_time = row.get('Reps/Tiempo', row.get('Reps', row.get('Reps/Time', row.get('Reps/Tiempo ', None))))

            # Si no vienen, intentar extraer desde una columna combinada
            if raw_series is None or (isinstance(raw_series, float) and pd.isna(raw_series)):
                # intenta parsear desde una columna combinada como 'Series/Reps/Descanso'
                combined = row.get('Series/Reps/Descanso', row.get('Series/Reps/Desc', None))
                _, fallback_series = _parse_reps_series(combined if isinstance(combined, str) else str(combined) if combined is not None else "")
                default_series = int(fallback_series)
            else:
                try:
                    default_series = int(raw_series)
                except Exception:
                    # si viene como texto con números
                    import re
                    nums = re.findall(r"\d+", str(raw_series))
                    default_series = int(nums[0]) if nums else 1

            # Reps/Tiempo puede ser número o texto (ej. "10", "30s", "0:45"). Usaremos text_input para permitir ambos.
            if raw_reps_time is None or (isinstance(raw_reps_time, float) and pd.isna(raw_reps_time)):
                # fallback: intentar parsear desde columna combinada
                combined = row.get('Series/Reps/Descanso', row.get('Series/Reps/Desc', None))
                fallback_reps, _ = _parse_reps_series(combined if isinstance(combined, str) else str(combined) if combined is not None else "")
                default_reps_text = str(fallback_reps) if fallback_reps else ""
            else:
                default_reps_text = str(raw_reps_time)

            # inputs para peso/series/reps-time en la misma fila (nuevo orden)
            weight = cols[3].number_input(f"Peso (kg) #{idx}", min_value=0.0, step=0.5, value=float(row.get('Peso', 0.0)), key=f"w_{idx}")
            series = cols[4].number_input(f"Series #{idx}", min_value=1, step=1, value=int(default_series), key=f"s_{idx}")
            reps_time = cols[5].text_input(f"Reps/Tiempo #{idx}", value=default_reps_text, key=f"rt_{idx}")

            modified.append({
                "exercise_name": exercise_name,
                "weight": float(weight),
                "repetitions_or_time": reps_time,
                "repetitions": int(next(iter(__import__('re').findall(r"\d+", reps_time)), 0)) if isinstance(reps_time, str) else int(reps_time) if reps_time else 0,
                "series": int(series),
                "day": day,
                "category": category,
                "description": row.get('Descripción', row.get('Description', '')),
            })

        save_to_history = st.checkbox("Guardar ejercicios en historial (base de datos) al enviar", value=True)

        # Dos botones dentro del form: uno para guardar+registrar y otro para vista previa/exportar
        submit_save = st.form_submit_button("Aplicar y registrar")
        submit_export = st.form_submit_button("Vista previa y exportar (PDF/CSV)")

    # Manejo cuando el usuario eligió guardar y registrar
    if submit_save:
        st.success("Rutina procesada.")
        if save_to_history:
            for item in modified:
                try:
                    # registra cada ejercicio en la BD usando la función central
                    # usamos 'repetitions' (entero) para la BD; 'repetitions_or_time' conserva el texto si aplica
                    log_exercise(weight=item["weight"], repetitions=item["repetitions"], series=item["series"], exercise_name=item["exercise_name"])
                except Exception as e:
                    st.error(f"Error al guardar {item['exercise_name']}: {e}")
            st.success("Ejercicios guardados en historial.")

        # permitir descargar la versión modificada (CSV)
        export_df = pd.DataFrame(modified)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar rutina modificada (CSV)", csv, file_name=f"{selected}_modified.csv", mime="text/csv")

        # generar y ofrecer descarga de PDF de la rutina
        pdf_title = f"Rutina - {selected}" + (f" - {selected_day}" if selected_day and selected_day != "Todos" else "")
        html = _render_routine_html(modified, pdf_title, subtitle=f"Rutina: {selected}")
        pdf_bytes = _html_to_pdf_bytes(html)
        if pdf_bytes:
            st.download_button("Descargar rutina (PDF)", data=pdf_bytes, file_name=f"{selected}_rutina_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
        else:
            st.info("No fue posible generar PDF (WeasyPrint/ReportLab no instalados). Descarga CSV o instala weasyprint/reportlab.")

    # Manejo cuando el usuario quiere solo vista previa / exportar sin guardar en historial
    elif submit_export:
        st.info("Generando vista previa y archivos de exportación (no se guardará en historial).")

        export_df = pd.DataFrame(modified)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar rutina modificada (CSV) — vista previa", csv, file_name=f"{selected}_modified_preview.csv", mime="text/csv")

        pdf_title = f"Rutina - {selected}" + (f" - {selected_day}" if selected_day and selected_day != "Todos" else "")
        html = _render_routine_html(modified, pdf_title, subtitle=f"Rutina: {selected}")

        # Mostrar vista previa HTML responsiva en la app (útil en móvil)
        st.markdown("#### Vista previa")
        try:
            st.components.v1.html(html, height=600, scrolling=True)
        except Exception:
            st.markdown("Vista previa no disponible en este entorno.")

        pdf_bytes = _html_to_pdf_bytes(html)
        if pdf_bytes:
            st.download_button("Descargar rutina (PDF) — vista previa", data=pdf_bytes, file_name=f"{selected}_rutina_preview_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
        else:
            st.info("No fue posible generar PDF (WeasyPrint/ReportLab no instalados). Descarga CSV o instala weasyprint/reportlab.")

# alias esperado por app/tests
def show_routine():
    show()
# ...existing code...