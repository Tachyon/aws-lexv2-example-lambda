"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation https://docs.aws.amazon.com/lexv2/latest/dg/what-is.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'messages': [
            message
        ],
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',            
                'slotToElicit': slot_to_elicit
            },
            'intent': {
                'name': intent_name,
                'slots': slots
            }
        }
    }


def close(session_attributes, intent_name, fulfillment_state, message):
    response = {
        'messages': [
            message
        ],
        'sessionState': {
            'dialogAction': {
                'type': 'Close'           
            },
            'sessionAttributes': session_attributes,
            'intent': {
                'name': intent_name,
                'state': fulfillment_state
            }
        }
    }

    return response


def delegate(session_attributes, intent_name, slots):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Delegate'           
            },
            'sessionAttributes': session_attributes,
            'intent': {
                'name': intent_name,
                'slots': slots
            }
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def interpreted_value(slot):
    """
    Retrieves interprated value from slot object
    """
    if slot is not None:
        return slot["value"]["interpretedValue"]
    return slot   

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_order_flowers(flower_type, date, pickup_time):
    flower_types = ['lilies', 'roses', 'tulips']
    if flower_type is not None and interpreted_value(flower_type).lower() not in flower_types:
        return build_validation_result(False,
                                       'FlowerType',
                                       'We do not have {}, would you like a different type of flower?  '
                                       'Our most popular flowers are roses'.format(interpreted_value(flower_type)))

    if date is not None:
        if not isvalid_date(interpreted_value(date)):
            return build_validation_result(False, 'PickupDate', 'I did not understand that, what date would you like to pick the flowers up?')
        elif datetime.datetime.strptime(interpreted_value(date), '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'PickupDate', 'You can pick up the flowers from tomorrow onwards.  What day would you like to pick them up?')

    if pickup_time is not None:
        if len(pickup_time["value"]["resolvedValues"]) != 1:
            return build_validation_result(False, 'PickupTime', 'I did not understand that, what time would you like to pick the flowers up? Please specify AM or PM')
        elif len(interpreted_value(pickup_time)) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'PickupTime', None)

        hour, minute = interpreted_value(pickup_time).split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'PickupTime', None)

        if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(False, 'PickupTime', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def order_flowers(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    flower_type = get_slots(intent_request)["FlowerType"]
    date = get_slots(intent_request)["PickupDate"]
    pickup_time = get_slots(intent_request)["PickupTime"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_order_flowers(flower_type, date, pickup_time)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionState']['sessionAttributes'],
                               intent_request['sessionState']['intent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes  = intent_request['sessionState']['sessionAttributes'] if "sessionAttributes" in intent_request['sessionState'] else {}
        if flower_type is not None:
            output_session_attributes['Price'] = len(interpreted_value(flower_type)) * 5  # Elegant pricing model

        return delegate(output_session_attributes, intent_request['sessionState']['intent']['name'], get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return close(intent_request['sessionState']['sessionAttributes'],
                 intent_request['sessionState']['intent']['name'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks, your order for {} has been placed and will be ready for pickup by {} on {}'.format(interpreted_value(flower_type), interpreted_value(pickup_time), interpreted_value(date))})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch sessionId={}, intentName={}'.format(intent_request['sessionId'], intent_request['sessionState']['intent']['name']))

    intent_name =  intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'OrderFlowers':
        return order_flowers(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
