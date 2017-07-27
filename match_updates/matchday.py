import re

from match_updates.get_daily_matches import (get_matches_from_db,
                                             compare_matches_and_update,
                                             format_message_and_send_sms,
                                             eod_ft_message_and_send)
from match_updates.functions.db_functions import all_games_finished, get_ft_standings
from sms_hunt import team_data
from match_updates.match import look_up_teams_print


def format_ft_string(results):
    # Improve formatting and make changes to eod ft string
    ft_string = results.to_string(header=False, index=False)
    ft_string = re.sub(' +', ' ', ft_string)
    ft_string = ft_string.replace(' \n', '\n')
    print(ft_string)
    return ft_string


class MatchDay:
    def __init__(self, date_str, comp_id, league):
        self.date_str = date_str

        self.db_matches = []
        self.live_matches = []
        self.updated_matches = []

        self.comp_id = comp_id
        self.league = league
        self.all_games_finished = False
        self.ft_standings_str = ''

    def get_db_matches(self, db):
        self.db_matches = get_matches_from_db(db, self.date_str, self.comp_id)

    def set_live_matches(self, live_matches):
        self.live_matches = live_matches

    def find_updated_matches(self, db):
        self.updated_matches = compare_matches_and_update(db, self.db_matches, self.live_matches)
        self.all_games_finished = all_games_finished(db, self.date_str, self.comp_id)
        if self.all_games_finished:
            self.ft_standings_str = self.ft_standings(db)

    def ft_standings(self, db):
        results = get_ft_standings(db, self.date_str, self.comp_id)

        if len(results) > 0:
            results['localteam_name'] = results['localteam_name'].apply(look_up_teams_print, team_data=team_data)
            results['visitorteam_name'] = results['visitorteam_name'].apply(look_up_teams_print, team_data=team_data)
            return format_ft_string(results)
        else:
            self.all_games_finished = False
            return ''

    def send_sms_updates(self, db):
        if len(self.updated_matches) > 0:
            print('matches with an update found!')
            for match in self.updated_matches:
                format_message_and_send_sms(db, match, self.league)
        else:
            print('no update in any match')

    def send_sms_eod_ft(self, db):
        # If all matches are finished, then send end of day full time standings.
        if self.all_games_finished:
            eod_ft_message_and_send(self.league, self.ft_standings_str, db)

    def is_eligible(self):
        # Need a function to see if a match day is eligible (see stop_update_function)
        pass

    def stop_updates(self):
        # Need a function to stop updates when EOD FT is reached. How about saving to a file?
        pass
