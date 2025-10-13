import streamlit as st
from src.pages import A_home, B_log_exercise, C_history

def test_app():
    # Test the home page
    st.set_page_config(page_title="Gym Tracker", layout="wide")
    st.title("Gym Tracker")

    # Test navigation to home
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ("Home", "Log Exercise", "History"))

    if page == "Home":
        A_home.show_home()
    elif page == "Log Exercise":
        B_log_exercise.log_exercise()
    elif page == "History":
        C_history.show_history()

if __name__ == "__main__":
    test_app()