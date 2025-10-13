import streamlit as st


def main():
    st.title("Gym Tracker")
    st.header("Welcome to the Gym Tracker App!")
    st.write("This application helps you keep track of your workouts.")
    
    st.subheader("Navigation")
    st.write("Use the sidebar to log your exercises and view your workout history.")
    
    # st.sidebar.title("Menu")
    # st.sidebar.markdown("Select an option:")
    # st.sidebar.markdown("- [Log Exercise](B_log_exercise) ")
    # st.sidebar.markdown("- [View History](C_history) ")

# Alias functions expected by other modules/tests
def show():
    main()

def show_home():
    main()

if __name__ == "__main__":
    main()
