from datetime import datetime

import stripe

from sms import Sms
from backend.db_functions import insert_array_to_table, get_table_columns

table_name = 'goalsms'
sign_up_sms_text = '{name}, you have successfully signed up for goal updates from {team}!'


def add_data_and_send_sms(db, values_dic, email, teams_dic):
    # Add to data base and send sms.

    rev_teams_dic = dict((v, k) for k, v in teams_dic.iteritems())

    dt = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    text_row = [str(values_dic['phone_number']),
                str(email),
                dt,
                str(rev_teams_dic[str(values_dic['team'])]),
                str(values_dic['name'])]

    # Add message to table
    insert_array_to_table(table_name, db,
                          get_table_columns('tables/' + table_name + '_table.json'),
                          text_row)

    # Send message that it is over now
    sign_up_sms = Sms(content=sign_up_sms_text.format(name=str(values_dic['name']),
                                                      team=str(values_dic['team'])),
                      receiver=str(values_dic['phone_number']))
    sign_up_sms.send()
    return None


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
