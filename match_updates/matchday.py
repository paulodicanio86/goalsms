from match_updates.get_daily_matches import (get_matches_from_db,
                                             compare_matches_and_update,
                                             get_phone_numbers_and_send_sms)
from match_updates.functions.db_functions import number_of_live_matches


class MatchDay:
    def __init__(self, db, date_str, competition_str):
        self.date_str = date_str
        self.db = db

        self.db_matches = []
        self.live_matches = []
        self.updated_matches = []

        self.competition_str = competition_str
        self.all_games_finished = False

    def get_db_matches(self):
        self.db_matches = get_matches_from_db(self.db, self.date_str, self.competition_str)

    def set_live_matches(self, live_matches):
        self.live_matches = live_matches

    def find_updated_matches(self):
        self.updated_matches = compare_matches_and_update(self.db, self.db_matches, self.live_matches)
        if number_of_live_matches(self.db, self.date_str, self.competition_str) == 0:
            self.all_games_finished = True

    def send_sms_updates(self):

        if len(self.updated_matches) > 0:
            print('matches with an update found!')
            for match in self.updated_matches:
                get_phone_numbers_and_send_sms(self.db, match)
        else:
            print('no update in any match')
