from match_updates.get_daily_matches import (check_for_daily_file, get_matches_from_db,
                                             get_live_matches, compare_matches_and_update,
                                             get_phone_numbers_and_send_sms)


class MatchDay:
    def __init__(self, date_str, db, login_goal_api):
        self.date_str = date_str
        self.db = db
        self.login_goal_api = login_goal_api

        self.is_match_day = False
        self.trigger_times = []

        self.db_matches = []
        self.live_matches = []
        self.updated_matches = []

        self.competitions = []
        self.final_day_whistle_time = ''

    def check_match_day_trigger_times(self, file_path, competition):

        self.is_match_day, self.trigger_times = check_for_daily_file(self.db,
                                                                     file_path,
                                                                     self.date_str,
                                                                     competition,
                                                                     self.login_goal_api)

    def get_db_matches(self):
        self.db_matches = get_matches_from_db(self.db, self.date_str)

    def get_live_matches(self, competition):
        self.live_matches = get_live_matches(self.date_str, competition, self.login_goal_api)

    def get_updated_matches(self):
        self.updated_matches = compare_matches_and_update(self.db, self.db_matches, self.live_matches)

    def send_sms_updates(self):

        if len(self.updated_matches) > 0:
            print('matches with an update found!')
            for match in self.updated_matches:
                get_phone_numbers_and_send_sms(self.db, match)
            else:
                print('no update in any match')
