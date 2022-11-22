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
import io
import logging
import json
import zlib
import gzip
import base64

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

def elicit_slot_without_message(session_attributes, intent_name, slots, slot_to_elicit):
    return {
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

def encode_data(json_data):
    text = json.dumps(json_data)
    bytes = text.encode('utf-8')
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(bytes)
    return base64.b64encode(out.getvalue()).decode('utf8')


def decode_data(encoded_str):
    data = base64.b64decode(encoded_str)
    striodata = io.BytesIO(data)
    with gzip.GzipFile(fileobj=striodata, mode='r') as f:
        data = json.loads(f.read())
    return data

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def interpreted_value(slot):
    """
    Retrieves interprated value from slot object
    """
    if slot is not None:
        return slot["value"]["interpretedValue"]
    return slot

""" --- Functions that control the bot's behavior --- """


def order_flowers(intent_request):
    source = intent_request['invocationSource']
    if source == 'DialogCodeHook':
        flower_type = get_slots(intent_request)["FlowerType"]
        date = get_slots(intent_request)["PickupDate"]
        pickup_time = get_slots(intent_request)["PickupTime"]
        source = intent_request['invocationSource']

        ###
        # store the original event and handler for the callback step
        ###
        sessionState = intent_request.get('sessionState', {})
        session_attributes = sessionState.get("sessionAttributes", {})
        session_attributes['callback_event'] = encode_data(intent_request)
        ###

        if flower_type is None:
            return elicit_slot_without_message(session_attributes,
                intent_request['sessionState']['intent']['name'],
                 get_slots(intent_request),
                'FlowerType')
        if date is None:
            return elicit_slot_without_message(session_attributes,
                intent_request['sessionState']['intent']['name'],
                 get_slots(intent_request),
                'PickupDate')
        if pickup_time is None:
            return elicit_slot_without_message(session_attributes,
                intent_request['sessionState']['intent']['name'],
                 get_slots(intent_request),
                'PickupTime')

        return delegate(session_attributes, intent_request['sessionState']['intent']['name'], get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return close(intent_request['sessionState']['sessionAttributes'],
                 intent_request['sessionState']['intent']['name'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks, your order for {} has been placed and will be ready for pickup by {} on {}'.format(interpreted_value(flower_type), interpreted_value(pickup_time), interpreted_value(date))})

""" Logic to handle repeat intent. Repeat intent will extract 'callback_event' from sessiona ttribute and repplay the previous event  """
def repeat_intent(intent_request):

    # extract previous event from the session state
    callback_event = decode_data( intent_request['sessionState']['sessionAttributes']['callback_event'].encode('utf-8'))
    return dispatch(callback_event)

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
    if intent_name == 'RepeatIntent':
        return repeat_intent(intent_request)

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
    logger.debug('Input={}'.format(json.dumps(event)))

    output = dispatch(event)

    logger.debug('Output={}'.format(json.dumps(output)))
    return output