class Activity:
    start_date = None
    distance = None

    def __init__(self, start_date, distance):
        self.start_date = start_date[:10]
        self.distance = round(distance / 1000.0, 2)
