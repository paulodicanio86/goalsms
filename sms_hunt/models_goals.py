from datetime import datetime

import stripe

from sms import Sms
from sms_hunt import key_config
from backend.db_functions import insert_array_to_table, get_table_columns

stripe.api_key = key_config['stripe_secret_key']
table_name = 'eurosms'
sign_up_sms_text = '{name}, you have successfully signed up for goal updates from {team}!'


def add_data_and_send_sms(db, values_dic, name):
    # Add to data base and send sms

    dt = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    text_row = [str(values_dic['phone_number']),
                str(values_dic['email']),
                dt,
                str(values_dic['team']),
                str(name)]

    # Add message to table
    insert_array_to_table(table_name, db,
                          get_table_columns('tables/' + table_name + '_table.json'),
                          text_row)

    # Send message that it is over now
    sign_up_sms = Sms(content=sign_up_sms_text.format(name=name, team=str(values_dic['team'])),
                      receiver=str(values_dic['phone_number']))
    sign_up_sms.send()
    return None


def charge_stripe(payment, stripe_email, stripe_token, phone_number):
    # Connecting with stripe and charge if successful
    try:

        customer = stripe.Customer.create(
            email=stripe_email,
            source=stripe_token
        )

        # create the charge on stripe's servers - this will charge the user's card
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=payment['amount_integer'],
            currency=payment['currency'],
            description=phone_number + ' charge'
        )

        success = True
        name = customer.cards.data[0].name
        return success, name

    except stripe.CardError, e:  # The card has been declined.
        success = False
        name = '[no name]'
        return success, name
