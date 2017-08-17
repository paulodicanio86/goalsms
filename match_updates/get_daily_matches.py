import urllib2
import json
import os as os

from match_updates.functions.db_functions import (get_matches, date_in_table,
                                                  get_kick_off_times, get_phone_numbers)
from match import Match, compare_matches
from sms_hunt.sms import Sms
from sms_hunt import team_data


def map_to_match_object(entry):
    match = Match(entry['localteam_name'],
                  entry['visitorteam_name'],
                  entry['time_str'],
                  entry['date_str'],
                  entry['status_str'],
                  entry['timer_str'],
                  entry['localteam_score'],
                  entry['visitorteam_score'],
                  entry['comp_id_str'])
    return match


def get_matches_from_db(db, date_str, comp_id=''):
    matches = get_matches(db, date_str, comp_id)
    result = matches.apply(map_to_match_object, axis=1)
    return result.values


def get_team_names(db, date_str, comp_id=''):
    matches = get_matches(db, date_str, comp_id)
    if len(matches) > 0:
        return matches.localteam_name.values.tolist() + matches.visitorteam_name.values.tolist()
    else:
        return None


def get_live_matches(date_str, comp_id, login_goal_api, test=False):
    # Web query matches
    query = ("http://api.football-api.com/2.0/matches?comp_id=" + comp_id + "&match_date=" + date_str +
             "&Authorization=" + login_goal_api)
    try:
        result = urllib2.urlopen(query).read()
    except urllib2.HTTPError:
        result = '{}'

    test_localteam = 'Leicester City'
    test_visitorteam = 'Arsenal'
    test_localteam_score = '0'
    test_visitorteam_score = '0'
    test_timer = '0'  # Minute or FT
    test_comp_id = '1204'

    test_result = '''[{{"id":"1921980","comp_id":"{test_comp_id}","formatted_date":"{date_str}","season":"2015\\/2016",
    "week":"20","venue":"Selhurst Park (London)","venue_id":"1265","venue_city":"London","status":"{test_timer}",
    "timer":"{test_timer}","time":"12:30","localteam_id":"9127","localteam_name":"{test_localteam}","localteam_score":
    "{test_localteam_score}","visitorteam_id":"9092","visitorteam_name":"{test_visitorteam}","visitorteam_score":
    "{test_visitorteam_score}","ht_score":"[0-1]","ft_score":"[0-3]","et_score":null,"penalty_local":null,
    "penalty_visitor":null,"events":[{{"id":"21583631","type":"yellowcard","minute":"13","extra_min":"","team":
    "localteam","player":"D. Delaney","player_id":"15760","assist":"","assist_id":"","result":""}},
    {{"id":"21583632","type":"goal","minute":"29","extra_min":"","team":"visitorteam",
    "player":"Oscar","player_id":"57860","assist":"D. Costa","assist_id":"60977","result":"[0-1]"}},
    {{"id":"21583633","type":"yellowcard","minute":"57","extra_min":"","team":"localteam","player":"M. Jedinak",
    "player_id":"17515","assist":"","assist_id":"","result":""}},{{"id":"21583634","type":"goal","minute":"60",
    "extra_min":"","team":"visitorteam","player":"Willian","player_id":"9051","assist":"Oscar",
    "assist_id":"57860","result":"[0-2]"}},{{"id":"21583635","type":"goal","minute":"{test_timer}","extra_min":"",
    "team":"visitorteam","player":"Brgermeister Olaf","player_id":"60977","assist":"Willian","assist_id":"9051",
    "result":"[0-3]"}},{{"id":"21583636","type":"yellowcard","minute":"80","extra_min":"","team":"localteam",
    "player":"S. Dann","player_id":"26006","assist":"","assist_id":"","result":""}}]}}]'''

    test_result = test_result.format(test_comp_id=test_comp_id, date_str=date_str, test_timer=test_timer,
                                     test_localteam=test_localteam, test_localteam_score=test_localteam_score,
                                     test_visitorteam=test_visitorteam, test_visitorteam_score=test_visitorteam_score
                                     )
    if test:
        result = test_result

    # Make Match objects
    matches_json = json.loads(result)

    matches = []
    if (len(matches_json) > 0) and ('code' not in matches_json):  # 'code' was sometimes returned so taking this out.
        for entry in matches_json:
            # add events somewhere here to extract event with highest minute and the player field?

            player = get_event_details(entry)

            match = Match(entry['localteam_name'],
                          entry['visitorteam_name'],
                          entry['time'],
                          entry['formatted_date'],
                          entry['status'],
                          entry['timer'],
                          entry['localteam_score'],
                          entry['visitorteam_score'],
                          entry['comp_id'],
                          player)
            match.change_time(-2)  # Not required as time on server is same as football API times...
            match.change_names(team_data)  # change team names according to dict keys
            matches.append(match)

    return matches


def get_event_details(match_json):
    player = ' '

    if len(match_json['events']) > 0 and str(match_json['timer']).isdigit():

        events = match_json['events']
        timer = int(match_json['timer'])

        for event in events:
            if (int(event['minute']) == timer) and (str(event['type']) == 'goal'):
                player = event['player'].encode('utf8')

    return player


def get_comp_standing(comp_id, login_goal_api):
    # Web query matches
    query = ("http://api.football-api.com/2.0/standings/" + comp_id + "?Authorization=" + login_goal_api)

    try:
        result = urllib2.urlopen(query).read()
    except urllib2.HTTPError:
        result = '{}'

    standing = json.loads(result)

    for entry in standing:
        print entry['team_name']

    return standing


def add_daily_matches_to_db(db, date_str, comp_id, login_goal_api):
    matches = get_live_matches(date_str, comp_id, login_goal_api)

    # Save matches to db
    for match in matches:
        match.save_to_db(db)


def compare_matches_and_update(db, db_matches, live_matches):
    changed_matches = compare_matches(db_matches, live_matches)

    # Update matches on db
    for match in changed_matches:
        match.update_on_db(db)

    return changed_matches


def get_trigger_times(db, date_str):
    df = get_kick_off_times(db, date_str)

    df_values = df['time_str'].values
    hours = []
    if len(df_values) > 0:
        for entry in df_values:
            hour = entry.split(':')[0]
            hours.append(hour)

            # add two hours after kick off to be safe:
            hour_int = int(hour)
            hours.append(str(hour_int + 1))
            hours.append(str(hour_int + 2))

        hours = list(set(hours))
        hours.sort()
        return ';'.join(hours)
    else:
        return 'False - no trigger times found'


def daily_file_exists(file_path):
    # File exists
    if os.path.isfile(file_path):
        # print('File exists')
        return True
    else:
        # File does not exist
        return False


def read_daily_file(file_path, false_string):
    match_day = False
    trigger_times = []

    # File exists
    f = open(file_path, 'r')
    content = f.readline()

    if content != false_string:
        match_day = True
        trigger_times = content.split(';')
        # print('Kick of times are: ', content)
    f.close()
    return match_day, trigger_times


def write_daily_file(db, file_path, date_str, comp_id, login_goal_api, false_string):
    date_in_table_bool = date_in_table(db, date_str)

    if not date_in_table_bool:
        add_daily_matches_to_db(db, date_str, comp_id, login_goal_api)

    # Open file
    f = open(file_path, 'w')

    # Now check if there are any matches today:
    if date_in_table_bool:
        # Write extra information here, separated by ';'
        f.write(get_trigger_times(db, date_str))
    else:
        f.write(false_string)

    # Close file
    f.close()


def format_teams(match):
    # format team names
    teams = [match.localteam_name, match.visitorteam_name]
    teams_formatted = []

    for team in teams:
        if team in team_data['club_teams'].keys():
            # teams_formatted.append(str(rev_team_data[team]))
            teams_formatted.append(str(team))

    return teams_formatted


def format_content(match):
    # determine type and content of message
    # 1 = Kickoff, 2 = goal scored, 3 = Full Time
    # FT message
    if match.status == 'FT':
        content = match.get_full_time_message_text()
        msg_type = 3
    # kick off message
    elif match.localteam_score == '0' and match.visitorteam_score == '0':
        content = match.get_kick_off_message_text()
        msg_type = 1
    # score change message
    else:
        content = match.get_score_message_text()
        msg_type = 2

    return content, msg_type


def format_message_and_send_sms(db, match, league):
    teams = format_teams(match)
    content, msg_type = format_content(match)
    sms = Sms(content)

    # now find users who are subscribed to one of the two teams
    if len(teams) > 0:
        # make string readable by SQL
        teams_formatted = str(teams)[1:-1]

        check_cases_and_send(db, teams_formatted, sms, msg_type, league)
    else:
        print('No users found for this match')


def get_numbers(db, teams_formatted, mode, league):
    phone_numbers = get_phone_numbers(db, teams_formatted, mode, league)
    phone_numbers_list = list(phone_numbers['phone_number'].values)
    # only send one sms if a user is subscribed to two teams that play each other
    phone_numbers_list = list(set(phone_numbers_list))
    return phone_numbers_list


def get_numbers_and_send_sms(db, teams_formatted, sms, mode, league):
    phone_numbers_list = get_numbers(db, teams_formatted, mode, league)

    # In future, if there are many many users, the list can be split here and several requests to send sms
    # can me made here.
    if len(phone_numbers_list) > 0:
        sms.set_receiver(phone_numbers_list)
        sms.send()
        print('Sms have been sent for mode ' + str(mode))
    else:
        print('No subscribed users found for mode ' + str(mode))


# send sms to all relevant modes
def check_cases_and_send(db, teams_formatted, sms, msg_type, league):
    # Here special cases can be defined, of whom to send which message depending on message type and league
    # The mode needs to be set in the flask module when signing up
    # mode = 0, all messages
    if msg_type in [3]:
        mode = 1
        get_numbers_and_send_sms(db, teams_formatted, sms, mode, league)

    if msg_type in [1, 3]:
        mode = 2
        get_numbers_and_send_sms(db, teams_formatted, sms, mode, league)

    if msg_type in [1, 2, 3]:
        mode = 3
        get_numbers_and_send_sms(db, teams_formatted, sms, mode, league)


def eod_ft_message_and_send(league, teams, ft_standings_str, db):
    modes = [2, 3]

    for mode in modes:
        teams_formatted = str(teams)[1:-1]
        phone_numbers_list = get_numbers(db, teams_formatted, mode, league)

        # In future, if there are many many users, the list can be split here and several requests to send sms
        # can me made here.

        if len(phone_numbers_list) > 0:
            sms = Sms(ft_standings_str)
            sms.set_receiver(phone_numbers_list)
            sms.send()
            # print('eod FT Sms have been sent')
