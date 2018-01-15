from datetime import datetime
import stripe

from sms import Sms
from goalsms import sms_content
from backend.db_functions import insert_array_to_table, get_table_columns
from goalsms import team_data, app_config

sign_up_sms_text = sms_content['sign_up_sms_text']
teams_dic = team_data['club_teams']
leagues_dic = team_data['leagues']
teams = teams_dic.values()
teams.sort()

# Create an ordered league list to be passed to the templates
leagues_order = team_data['leagues_order']
leagues_list = []
for league_key in leagues_order:
    entry = {'league_id': league_key,
             'league_name': leagues_dic[league_key]}
    leagues_list.append(entry)


# Create a team list dictionary to be passed to the templates.
teams_list = []
for league_key in leagues_dic:
    team_keys = team_data[league_key]
    team_keys.sort()
    for team_id in team_keys:
        # Make entry and append
        entry = {'league_id': league_key,
                 'team_id': team_id,
                 'team_name': teams_dic[team_id]
                 }
        teams_list.append(entry)


# Create a prefixes list
prefixes = app_config['prefixes']
prefix_currencies = app_config['prefix_currencies']
prefix_label = app_config['prefix_label']
currencies = prefix_currencies.values()
prefixes_list = []
for prefix in prefixes:
    # Make entry and append
    entry = {'prefix_value': prefix,
             'prefix_name': prefix_label[prefix],
             'prefix_currency': prefix_currencies[prefix]}
    prefixes_list.append(entry)


# goal sms configuration and payment settings
variable_names = ['phone_number']  # used to contain 'names', but that's now obtained from stripe checkout.
payment_matrix = app_config['payments']
currency_html = app_config['currency_html']
prefix_order = payment_matrix['prefix_order']
service_order = payment_matrix['service_order']
payments = []

for league_key in leagues_order:
    prices_order = payment_matrix[league_key]

    for entry in range(0, len(prefix_order)):
        entry_prefix = prefix_order[entry]
        entry_currency = prefix_currencies[entry_prefix]
        entry_service = service_order[entry]

        entry_name = [entry_currency, entry_service, league_key, entry_prefix]

        payment = {"name": "_".join(entry_name),
                   "value_int": prices_order[entry],
                   "currency_html": currency_html[entry_currency],
                   "prefix": entry_prefix
                   }
        payments.append(payment)

services_dic = app_config['services']

default_dic = {'valid': True,
               'value': ''
               }


def add_data_and_send_sms(db, name, email, phone_number, team_id_name, team_name, league_id, service_id,
                          table_name='goalsms'):
    # Add to data base and send sms.
    service = str(service_id)

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
                str(name.encode('utf-8')),
                mode]

    # Add message to table
    insert_array_to_table(table_name, db,
                          get_table_columns('tables/' + table_name + '_table.json'),
                          text_row)

    # Convert unicode to utf-8 string
    content = sign_up_sms_text.format(name=name, team=team_name)

    # Send message that you are signed up
    sign_up_sms = Sms(content=content,
                      receiver=str(phone_number))
    sign_up_sms.encode_content()
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
