from backend.db_functions import insert_array_to_table, get_table_columns
from match_updates.functions.db_functions import update_matches_table


class Match:
    def __init__(self, localteam_name, visitorteam_name, time_str, date_str, status, timer,
                 localteam_score, visitorteam_score, comp_id):
        self.localteam_name = str(localteam_name)
        self.visitorteam_name = str(visitorteam_name)
        self.localteam_name_print = str(localteam_name)
        self.visitorteam_name_print = str(visitorteam_name)

        self.localteam_score = str(localteam_score)  # "0"
        self.visitorteam_score = str(visitorteam_score)  # "1"

        self.time_str = str(time_str)  # "13:30"
        self.date_str = str(date_str)  # "03.01.2016"

        self.status = str(status)  # "FT"
        self.timer = str(timer)

        self.comp_id = str(comp_id)

    def change_names(self, team_data):
        self.localteam_name = look_up_teams(self.localteam_name, team_data)
        self.visitorteam_name = look_up_teams(self.visitorteam_name, team_data)
        self.localteam_name_print = look_up_teams_print(self.localteam_name, team_data)
        self.visitorteam_name_print = look_up_teams_print(self.visitorteam_name, team_data)

    def change_time(self):
        # Function to convert kick off times back by one hour for BST from ECT
        adjusted_time = int(self.time_str[:-3]) + 1
        self.time_str = str(adjusted_time) + self.time_str[-3:]

    def save_to_db(self, db, table_name='matches'):
        text_row = [self.date_str, self.localteam_name, self.visitorteam_name,
                    self.localteam_score, self.visitorteam_score, self.time_str,
                    self.status, self.timer, self.comp_id]

        # Add match to table
        insert_array_to_table(table_name, db, get_table_columns('tables/' + table_name + '_table.json'), text_row)

    def update_on_db(self, db):
        update_matches_table(db, 'localteam_score', self.localteam_score, self.date_str, self.localteam_name)
        update_matches_table(db, 'visitorteam_score', self.visitorteam_score, self.date_str, self.localteam_name)
        update_matches_table(db, 'status_str', self.status, self.date_str, self.localteam_name)
        update_matches_table(db, 'timer_str', self.timer, self.date_str, self.localteam_name)

    def get_score_message_text(self):
        message = '{timer}. New score: {localteam_name_print} {localteam_score} -'
        message += ' {visitorteam_score} {visitorteam_name_print}'
        message = message.format(timer=self.timer,
                                 localteam_name_print=self.localteam_name_print,
                                 localteam_score=self.localteam_score,
                                 visitorteam_name_print=self.visitorteam_name_print,
                                 visitorteam_score=self.visitorteam_score)
        return message

    def get_full_time_message_text(self):
        message = 'FT. Final score: {localteam_name_print} {localteam_score} -'
        message += ' {visitorteam_score} {visitorteam_name_print}'
        message = message.format(localteam_name_print=self.localteam_name_print,
                                 localteam_score=self.localteam_score,
                                 visitorteam_name_print=self.visitorteam_name_print,
                                 visitorteam_score=self.visitorteam_score)
        return message

    def get_kick_off_message_text(self):
        message = 'Kick off: {localteam_name_print} -'
        message += ' {visitorteam_name_print}'
        message = message.format(localteam_name_print=self.localteam_name_print,
                                 visitorteam_name_print=self.visitorteam_name_print)
        return message

    def __eq__(self, match2):
        return ((self.localteam_name == match2.localteam_name) &
                (self.visitorteam_name == match2.visitorteam_name) &
                # (self.time_str == match2.time_str) &
                (self.date_str == match2.date_str))


def look_up_teams(team_name, team_data):
    # First check if team name is in look up table
    if team_name in team_data['team_name_lookup'].keys():
        return str(team_data['team_name_lookup'][team_name])
    # else look up in master table. If team is not known at all then it stays just unchanged
    elif team_name in team_data['club_teams'].values():
        rev_team_data = dict((v, k) for k, v in team_data['club_teams'].iteritems())
        return str(rev_team_data[team_name])
    else:
        return team_name


def look_up_teams_print(team_name, team_data):
    # First check if team name is in look up table
    if team_name in team_data['club_teams'].keys():
        team_str = team_data['club_teams'][team_name]
        team_str = unicode(team_str).encode("utf-8")
        return str(team_str)
    else:
        return team_name


def has_qm(match):
    if match.localteam_score == '?' or match.visitorteam_score == '?':
        return True
    else:
        return False


def is_score(match, score_local, score_visitor):
    if match.localteam_score == score_local and match.visitorteam_score == score_visitor:
        return True
    else:
        return False


def are_digits(match):
    if match.localteam_score.isdigit() and match.visitorteam_score.isdigit():
        return True
    else:
        return False


def compare_matches(db_matches, live_matches):
    changed_matches = []

    for db_match in db_matches:
        for live_match in live_matches:
            if db_match == live_match:
                print_flag = False

                # kick off:
                if has_qm(db_match) and are_digits(live_match):
                    changed_matches.append(live_match)
                    print_flag = True
                # full time
                elif (db_match.status != 'FT') and (live_match.status == 'FT'):
                    changed_matches.append(live_match)
                    print_flag = True
                # score change
                elif are_digits(db_match) and are_digits(live_match):
                    # visitor team has scored
                    if int(live_match.visitorteam_score) > int(db_match.visitorteam_score) and int(
                            live_match.localteam_score) >= int(db_match.localteam_score):
                        changed_matches.append(live_match)
                        print_flag = True
                    # local team has scored
                    elif int(live_match.localteam_score) > int(db_match.localteam_score) and int(
                            live_match.visitorteam_score) >= int(db_match.visitorteam_score):
                        changed_matches.append(live_match)
                        print_flag = True

                if print_flag:
                    print('match & updated score found! DB: ',
                          db_match.date_str, db_match.localteam_name, db_match.visitorteam_name,
                          db_match.localteam_score, db_match.visitorteam_score, db_match.status, db_match.timer,
                          'LIVE: ',
                          live_match.date_str, live_match.localteam_name, live_match.visitorteam_name,
                          live_match.localteam_score, live_match.visitorteam_score, live_match.status,
                          live_match.timer)

    return changed_matches
