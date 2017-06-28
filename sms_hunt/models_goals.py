from datetime import datetime
import stripe

from sms import Sms
from sms_hunt import sms_content
from backend.db_functions import insert_array_to_table, get_table_columns
from sms_hunt import team_data, app_config

sign_up_sms_text = sms_content['sign_up_sms_text']
teams_dic = team_data['club_teams']
leagues_dic = team_data['leagues']
teams = teams_dic.values()
teams.sort()

# Create an ordered league list to be passed to the templates
leagues_order = team_data['leagues_order']
country_leagues = team_data['country_leagues']
league_currencies = app_config['league_currencies']
leagues_list = []
for league_key in leagues_order:
    entry = {'league_id': league_key,
             'league_name': leagues_dic[league_key]}
    leagues_list.append(entry)

# Create a team list dictionary to be passed to the templates. It includes currency values by native league
teams_list = []
for league_key in leagues_dic:
    team_keys = team_data[league_key]
    team_keys.sort()
    for team_id in team_keys:

        # Find native league
        native_league = ''
        if league_key in country_leagues:
            native_league = league_key
        else:
            for entry in country_leagues:
                if team_id in team_data[entry]:
                    native_league = entry

        # Make entry and append
        entry = {'league_id': league_key,
                 'team_id': team_id,
                 'team_name': teams_dic[team_id],
                 'currency': league_currencies[native_league]
                 }
        teams_list.append(entry)

# goal sms configuration settings
variable_names = ['phone_number']  # used to contain 'names', but that's now obtained from stripe checkout.
country_codes = app_config['country_codes'].split(',')  # all accepted codes
default_country_code = country_codes[0]  # default code, used to complete numbers
payments = app_config['payments']
currencies = app_config['currencies']

default_dic = {'valid': True,
               'value': ''
               }


def add_data_and_send_sms(db, name, email, phone_number, team_id_name, team_name, league_id, service_id):
    # Add to data base and send sms.
    table_name = 'goalsms'
    service = service_id.split('_')[1]

    # Convert unicode to utf-8 string
    name = str(name.encode('utf-8'))
    team_name = team_name.encode('utf-8')

    mode = 0
    if service == 'bronze':
        mode = 1
    elif service == 'silver':
        mode = 2
    elif service == 'gold':
        mode = 3

    dt = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    text_row = [str(phone_number),
                str(email),
                dt,
                str(team_id_name),
                str(league_id),
                name,
                mode]

    # Add message to table
    insert_array_to_table(table_name, db,
                          get_table_columns('tables/' + table_name + '_table.json'),
                          text_row)

    # Get content string
    content = sign_up_sms_text.format(name=name, team=team_name)

    # Send message that you are signed up
    sign_up_sms = Sms(content=content,
                      receiver=str(phone_number))
    sign_up_sms.send()


def charge_stripe(payment, email, secret_key, stripe_token, phone_number):
    # Connecting with stripe and charge if successful
    stripe.api_key = secret_key

    # print(payment, secret_key, stripe_token, email, phone_number)
    # print('make user  ----------------------')

    try:
        customer = stripe.Customer.create(
            email=str(email),
            source=str(stripe_token)
        )
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err = body['error']

        print "Status is: %s" % e.http_status
        print "Type is: %s" % err['type']
        print "Code is: %s" % err['code']
        # param is '' in this case
        print "Param is: %s" % err['param']
        print "Message is: %s" % err['message']
        return False
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        print('RateLimitError -----------')
        return False
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        print('InvalidRequestError -----------')
        return False
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        print('AuthenticationError -----------')
        return False
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        print('APIConnectionError -----------')
        return False
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        print('StripeError -----------')
        return False
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        print('Exception - something else! -----------')
        return False

    # print('made user ----------')
    # print(customer, '=---------')
    # print('make charge  ----------------------')
    # print(str(stripe_token), int(payment['amount_integer']), str(payment['currency']), (str(phone_number) + ' charge'),
    #      'goalsms.com fee')
    try:
        # create the charge on stripe's servers - this will charge the user's card
        charge = stripe.Charge.create(
            amount=int(payment['amount_integer']),
            currency=str(payment['currency']),
            # source=str(stripe_token),
            customer=customer.id,
            description=str(phone_number) + ' charge',
            statement_descriptor='goalsms.com fee'
        )
        return True
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err = body['error']

        print "Status is: %s" % e.http_status
        print "Type is: %s" % err['type']
        print "Code is: %s" % err['code']
        # param is '' in this case
        print "Param is: %s" % err['param']
        print "Message is: %s" % err['message']
        return False
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        print('RateLimitError -----------')
        return False
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        print('InvalidRequestError -----------')
        return False
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        print('AuthenticationError -----------')
        return False
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        print('APIConnectionError -----------')
        return False
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        print('StripeError -----------')
        return False
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        print('Exception - something else! -----------')
        return False
