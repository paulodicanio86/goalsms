import urllib2
import json
import os as os

from match_updates.functions.db_functions import get_matches, date_in_table, get_kick_off_times, get_phone_numbers
from match import Match, compare_matches
from sms_hunt.sms import Sms
from sms_hunt import meta_data


def map_to_match_object(entry):
    match = Match(entry['localteam_name'],
                  entry['visitorteam_name'],
                  entry['time_str'],
                  entry['date_str'],
                  entry['status_str'],
                  entry['localteam_score'],
                  entry['visitorteam_score'])
    return match


def get_matches_from_db(db, date_str):
    matches = get_matches(db, date_str)
    result = matches.apply(map_to_match_object, axis=1)
    return result.values


def get_live_matches(date_str, competition, login_goal_api):
    # Web query matches
    query = ("http://api.football-api.com/2.0/matches?comp_id=" + competition + "&match_date=" + date_str +
             "&Authorization=" + login_goal_api)
    try:
        result = urllib2.urlopen(query).read()
    except urllib2.HTTPError:
        result = '{}'

    result_test = '[{"id":"1921980","comp_id":"1204","formatted_date":"' + date_str + \
                  '","season":"2015\\/2016",' \
                  '"week":"20","venue":"Selhurst Park (London)","venue_id":"1265","venue_city":"London","status":"FT",' \
                  '"timer":"","time":"12:30","localteam_id":"9127","localteam_name":"Leicester",' \
                  '"localteam_score":"15","visitorteam_id":"9092","visitorteam_name":"Chelsea","visitorteam_score":"3",' \
                  '"ht_score":"[0-1]","ft_score":"[0-3]","et_score":null,"penalty_local":null,' \
                  '"penalty_visitor":null,"events":[{"id":"21583631","type":"yellowcard","minute":"13",' \
                  '"extra_min":"","team":"localteam","player":"D. Delaney","player_id":"15760","assist":"",' \
                  '"assist_id":"","result":""},{"id":"21583632","type":"goal","minute":"29","extra_min":"",' \
                  '"team":"visitorteam","player":"Oscar","player_id":"57860","assist":"D. Costa","assist_id":"60977",' \
                  '"result":"[0-1]"},{"id":"21583633","type":"yellowcard","minute":"57","extra_min":' \
                  '"","team":"localteam","player":"M. Jedinak","player_id":"17515","assist":"","assist_id":""' \
                  ',"result":""},{"id":"21583634","type":"goal","minute":"60","extra_min":"","team":"visitorteam",' \
                  '"player":"Willian","player_id":"9051","assist":"Oscar","assist_id":"57860","result":"[0-2]"},' \
                  '{"id":"21583635","type":"goal","minute":"66","extra_min":"","team":"visitorteam","player":' \
                  '"D. Costa","player_id":"60977","assist":"Willian","assist_id":"9051","result":"[0-3]"},' \
                  '{"id":"21583636","type":"yellowcard","minute":"80","extra_min":"","team":"localteam","player":' \
                  '"S. Dann","player_id":"26006","assist":"","assist_id":"","result":""}]},{"id":"1921987","comp_id":' \
                  '"1204","formatted_date":"' + date_str + \
                  '","season":"2015\\/2016","week":"20","venue":"Goodison Park (Liverpool)","venue_id":"1252",' \
                  '"venue_city":"Liverpool","status":"FT","timer":"","time":"12:30","localteam_id":"9158",' \
                  '"localteam_name":"Bayern","localteam_score":"1","visitorteam_id":"9406","visitorteam_name":' \
                  '"Sunderland","visitorteam_score":"0","ht_score":"[1-1]","ft_score":"[1-1]","et_score":null,' \
                  '"penalty_local":null,"penalty_visitor":null,"events":[{"id":"21583651","type":"goal","minute":"22",' \
                  '"extra_min":"","team":"localteam","player":"A. Lennon","player_id":"","assist":"R. Lukaku","assist_id":' \
                  '"79495","result":"[1-0]"},{"id":"21583652","type":"yellowcard","minute":"35","extra_min":"","team":' \
                  '"localteam","player":"S. Coleman","player_id":"7158","assist":"","assist_id":"","result":""},' \
                  '{"id":"21583653","type":"goal","minute":"45","extra_min":"1","team":"visitorteam","player":"D. Alli",' \
                  '"player_id":"217739","assist":"T. Alderweireld","assist_id":"70508","result":"[1-1]"},{"id":"21583654",' \
                  '"type":"yellowcard","minute":"68","extra_min":"","team":"visitorteam","player":"E. Lamela",' \
                  '"player_id":"81992","assist":"","assist_id":"","result":""},{"id":"21583655","type":"yellowcard",' \
                  '"minute":"72","extra_min":"","team":"visitorteam","player":"T. Carroll","player_id":"173621",' \
                  '"assist":"","assist_id":"","result":""}]}]'

    # Make Match objects
    matches_json = json.loads(result)
    matches = []
    if (len(matches_json) > 0) and ('code' not in matches_json):
        for entry in matches_json:
            match = Match(entry['localteam_name'],
                          entry['visitorteam_name'],
                          entry['time'],
                          entry['formatted_date'],
                          entry['status'],
                          entry['localteam_score'],
                          entry['visitorteam_score'])
            match.change_time()
            matches.append(match)

    return matches


def add_daily_matches_to_db(db, date_str, competition, login_goal_api):
    matches = get_live_matches(date_str, competition, login_goal_api)

    # Save matches to db
    for match in matches:
        match.save_to_db(db)


def compare_matches_and_update(db, db_matches, live_matches):
    changed_matches = compare_matches(db_matches, live_matches)

    # Update matches on db
    for match in changed_matches:
        match.update_score_db(db)

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


def check_for_daily_file(db, file_path, date_str, competition, login_goal_api):
    match_day = False
    trigger_times = []

    # File exists
    if os.path.isfile(file_path):
        f = open(file_path, 'r')
        content = f.readline()

        if content == 'False':
            match_day = False
        else:
            match_day = True
            trigger_times = content.split(';')
            # print('Kick of times are: ', content)
        f.close()
    # File does not exist
    else:
        f = open(file_path, 'w')

        if not date_in_table(db, date_str):
            add_daily_matches_to_db(db, date_str, competition, login_goal_api)

        # Now check if there are any matches today:
        if date_in_table(db, date_str):
            # Write extra information here, separated by ';'
            f.write(get_trigger_times(db, date_str))
        else:
            f.write('False - no matches today')

        f.close()

    return match_day, trigger_times


def get_phone_numbers_and_send_sms(db, match):
    teams = [match.localteam_name, match.visitorteam_name]

    # Reverse team name to make it no capitals and no spaces.
    rev_meta_data = dict((v, k) for k, v in meta_data['club_teams'].iteritems())

    teams_formatted = []
    for team in teams:
        if team in rev_meta_data.keys():
            teams_formatted.append(str(rev_meta_data[team]))
            # teams_formatted.append(str(team)) # Let us only add our key team names and remove this full name

    # now find users who are subscribed to one of the two teams
    if len(teams_formatted) > 0:
        # make string readable by SQL
        teams_formatted = str(teams_formatted)[1:-1]
        phone_numbers = get_phone_numbers(db, teams_formatted)

        phone_numbers_list = list(phone_numbers['phone_number'].values)
        # only send one sms if a user is subscribed to two teams
        phone_numbers_list = list(set(phone_numbers_list))

        # check if any users are subscribed, and send sms
        if len(phone_numbers_list) > 0:
            content = match.get_score_message_text()

            sms = Sms(content, receiver=phone_numbers_list)
            sms.send()
            print('Sms have been sent')
        else:
            print('No subscribed users found')
    else:
        print('No teams found for this match')
