class Activity:
    training_date = None
    distance = None

    def __init__(self, training_date, distance):
        self.training_date = training_date[:10]
        self.distance = round(distance / 1000.0, 2)
