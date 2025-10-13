def validate_exercise_data(weight, repetitions, series):
    if weight <= 0:
        raise ValueError("El peso debe ser mayor que cero.")
    if repetitions <= 0:
        raise ValueError("Las repeticiones deben ser mayores que cero.")
    if series <= 0:
        raise ValueError("Las series deben ser mayores que cero.")
    return True

def format_exercise_entry(weight, repetitions, series):
    return f"Peso: {weight} kg, Repeticiones: {repetitions}, Series: {series}"

def calculate_total_weight(weight, repetitions, series):
    return weight * repetitions * series

def get_current_date():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")