class Match:
    def __init__(self):
        self.localteam_name = ""
        self.visitorteam_name = ""

        self.localteam_score_str = "0"
        self.localteam_score = int(self.localteam_score_str)

        self.visitorteam_score_str = "1"
        self.visitorteam_score = int(self.visitorteam_score_str)

        self.time_str = "13:30"
        self.date_str = "03.01.2016"

        self.status = "FT"

    def load_from_file(self):
        return False

    def save_to_file(self):
        return False
