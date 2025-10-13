class Exercise:
    def __init__(self, name, weight, repetitions, sets):
        self.name = name
        self.weight = weight
        self.repetitions = repetitions
        self.sets = sets

    def __repr__(self):
        return f"Exercise(name={self.name}, weight={self.weight}, repetitions={self.repetitions}, sets={self.sets})"

class Workout:
    def __init__(self, date, exercises):
        self.date = date
        self.exercises = exercises

    def __repr__(self):
        return f"Workout(date={self.date}, exercises={self.exercises})"