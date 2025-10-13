# Streamlit Gym Tracker

## Descripción
Streamlit Gym Tracker es una aplicación web diseñada para ayudar a los usuarios a llevar un registro de sus ejercicios en el gimnasio. Permite a los usuarios anotar la cantidad de peso levantado, repeticiones y series, así como revisar su historial de entrenamientos.

## Estructura del Proyecto
El proyecto está organizado de la siguiente manera:

```
streamlit-gym-tracker
├── app.py                     # Punto de entrada principal de la aplicación Streamlit
├── requirements.txt           # Dependencias necesarias para el proyecto
├── .streamlit
│   └── config.toml           # Configuración de la aplicación Streamlit
├── src
│   ├── pages
│   │   ├── A_home.py         # Página de inicio de la aplicación
│   │   ├── B_log_exercise.py  # Página para registrar ejercicios
│   │   └── C_history.py      # Página para ver el historial de ejercicios
│   ├── components
│   │   └── exercise_form.py   # Componente para el formulario de ejercicios
│   └── utils
│       ├── db.py             # Manejo de conexiones y consultas a la base de datos
│       ├── models.py         # Definición de modelos de datos
│       └── helpers.py        # Funciones utilitarias
├── scripts
│   └── init_db.py            # Script para inicializar la base de datos
├── data
│   └── schema.sql            # Esquema SQL para la base de datos
├── tests
│   ├── test_db.py            # Pruebas unitarias para funciones de la base de datos
│   └── test_app.py           # Pruebas unitarias para la lógica de la aplicación
├── .gitignore                 # Archivos y directorios a ignorar por el control de versiones
└── README.md                  # Documentación del proyecto
```

## Instalación
1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd streamlit-gym-tracker
   ```

2. Crea un entorno virtual y actívalo:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Inicializa la base de datos:
   ```
   python scripts/init_db.py
   ```

## Uso
Para ejecutar la aplicación, utiliza el siguiente comando:
```
streamlit run app.py
```

Accede a la aplicación a través de tu navegador en `http://localhost:8501`.

## Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.
