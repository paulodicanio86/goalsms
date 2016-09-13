import urllib2
import json

from match_updates.functions.db_functions import get_matches
from match import Match, compare_matches


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


def get_live_matches(date_str, competition):
    # Web query matches
    query = ("http://api.football-api.com/2.0/matches?comp_id=" + competition + "&match_date=" + date_str +
             "&Authorization=565ec012251f932ea4000001393b4115a8bf4bf551672b0543e35683")
    # result = urllib2.urlopen(query).read()
    result = '[{"id":"1921980","comp_id":"1204","formatted_date":"13.09.2016","season":"2015\\/2016","week":"20","venue":"Selhurst Park (London)","venue_id":"1265","venue_city":"London","status":"FT","timer":"","time":"13:30","localteam_id":"9127","localteam_name":"Crystal Palace","localteam_score":"1","visitorteam_id":"9092","visitorteam_name":"Chelsea","visitorteam_score":"3","ht_score":"[0-1]","ft_score":"[0-3]","et_score":null,"penalty_local":null,"penalty_visitor":null,"events":[{"id":"21583631","type":"yellowcard","minute":"13","extra_min":"","team":"localteam","player":"D. Delaney","player_id":"15760","assist":"","assist_id":"","result":""},{"id":"21583632","type":"goal","minute":"29","extra_min":"","team":"visitorteam","player":"Oscar","player_id":"57860","assist":"D. Costa","assist_id":"60977","result":"[0-1]"},{"id":"21583633","type":"yellowcard","minute":"57","extra_min":"","team":"localteam","player":"M. Jedinak","player_id":"17515","assist":"","assist_id":"","result":""},{"id":"21583634","type":"goal","minute":"60","extra_min":"","team":"visitorteam","player":"Willian","player_id":"9051","assist":"Oscar","assist_id":"57860","result":"[0-2]"},{"id":"21583635","type":"goal","minute":"66","extra_min":"","team":"visitorteam","player":"D. Costa","player_id":"60977","assist":"Willian","assist_id":"9051","result":"[0-3]"},{"id":"21583636","type":"yellowcard","minute":"80","extra_min":"","team":"localteam","player":"S. Dann","player_id":"26006","assist":"","assist_id":"","result":""}]},{"id":"1921987","comp_id":"1204","formatted_date":"03.01.2016","season":"2015\\/2016","week":"20","venue":"Goodison Park (Liverpool)","venue_id":"1252","venue_city":"Liverpool","status":"FT","timer":"","time":"16:00","localteam_id":"9158","localteam_name":"Everton","localteam_score":"5","visitorteam_id":"9406","visitorteam_name":"Tottenham Hotspur","visitorteam_score":"1","ht_score":"[1-1]","ft_score":"[1-1]","et_score":null,"penalty_local":null,"penalty_visitor":null,"events":[{"id":"21583651","type":"goal","minute":"22","extra_min":"","team":"localteam","player":"A. Lennon","player_id":"","assist":"R. Lukaku","assist_id":"79495","result":"[1-0]"},{"id":"21583652","type":"yellowcard","minute":"35","extra_min":"","team":"localteam","player":"S. Coleman","player_id":"7158","assist":"","assist_id":"","result":""},{"id":"21583653","type":"goal","minute":"45","extra_min":"1","team":"visitorteam","player":"D. Alli","player_id":"217739","assist":"T. Alderweireld","assist_id":"70508","result":"[1-1]"},{"id":"21583654","type":"yellowcard","minute":"68","extra_min":"","team":"visitorteam","player":"E. Lamela","player_id":"81992","assist":"","assist_id":"","result":""},{"id":"21583655","type":"yellowcard","minute":"72","extra_min":"","team":"visitorteam","player":"T. Carroll","player_id":"173621","assist":"","assist_id":"","result":""}]}]'
    matches_json = json.loads(result)

    # Make Match objects
    matches = []
    if len(matches_json) > 0:
        for entry in matches_json:
            match = Match(entry['localteam_name'],
                          entry['visitorteam_name'],
                          entry['time'],
                          entry['formatted_date'],
                          entry['status'],
                          entry['localteam_score'],
                          entry['visitorteam_score'])
            matches.append(match)

    return matches


def add_daily_matches_to_db(db, date_str, competition):
    matches = get_live_matches(date_str, competition)

    # Save matches to db
    for match in matches:
        match.save_to_db(db)


def compare_matches_and_update(db, db_matched, live_matches):
    changed_matches = compare_matches(db_matched, live_matches)

    # Update matches on db
    for match in changed_matches:
        match.update_score_db(db)

    return changed_matches
