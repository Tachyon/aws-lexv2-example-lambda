"""
 This code sample demonstrates an implementation of the Lex Code Hook Interface
 in order to serve a bot which manages dentist appointments.
 Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
 as part of the 'MakeAppointment' template.

 For instructions on how to set up and test this bot, as well as additional samples,
 visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'messages': [
            message,
            response_card
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


def confirm_intent(session_attributes, intent_name, slots, message, response_card):
    return {
        'messages': [
            message,
            response_card
        ],
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ConfirmIntent'
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


def build_response_card(title, subtitle, options):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    if options is not None:
        buttons = []
        for i in range(min(5, len(options))):
            buttons.append(options[i])

    return {
        "contentType": "ImageResponseCard",
       "imageResponseCard": {
            "title": title,
            "subtitle": subtitle,
            "imageUrl": "string",
            "buttons": buttons
        }
    }

def build_slot_value(interpreted_value):
    """
    Build a slot object with given interpretedValue.
    """
    return {
        "shape": "Scalar",
        "value": {
            "originalValue": interpreted_value,
            "interpretedValue": interpreted_value,
            "resolvedValues": [interpreted_value]
        }
    }    


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def interpreted_value(slot):
    """
    Retrieves interprated value from slot object
    """
    if slot is not None:
        return slot["value"]["interpretedValue"]
    return slot  

def increment_time_by_thirty_mins(appointment_time):
    hour, minute = list(map(int, appointment_time.split(':')))
    return '{}:00'.format(hour + 1) if minute == 30 else '{}:30'.format(hour)


def get_random_int(minimum, maximum):
    """
    Returns a random integer between min (included) and max (excluded)
    """
    min_int = math.ceil(minimum)
    max_int = math.floor(maximum)

    return random.randint(min_int, max_int - 1)


def get_availabilities(date):
    """
    Helper function which in a full implementation would  feed into a backend API to provide query schedule availability.
    The output of this function is an array of 30 minute periods of availability, expressed in ISO-8601 time format.

    In order to enable quick demonstration of all possible conversation paths supported in this example, the function
    returns a mixture of fixed and randomized results.

    On Mondays, availability is randomized; otherwise there is no availability on Tuesday / Thursday and availability at
    10:00 - 10:30 and 4:00 - 5:00 on Wednesday / Friday.
    """
    day_of_week = dateutil.parser.parse(date).weekday()
    availabilities = []
    available_probability = 0.3
    if day_of_week == 0:
        start_hour = 10
        while start_hour <= 16:
            if random.random() < available_probability:
                # Add an availability window for the given hour, with duration determined by another random number.
                appointment_type = get_random_int(1, 4)
                if appointment_type == 1:
                    availabilities.append('{}:00'.format(start_hour))
                elif appointment_type == 2:
                    availabilities.append('{}:30'.format(start_hour))
                else:
                    availabilities.append('{}:00'.format(start_hour))
                    availabilities.append('{}:30'.format(start_hour))
            start_hour += 1

    if day_of_week == 2 or day_of_week == 4:
        availabilities.append('10:00')
        availabilities.append('16:00')
        availabilities.append('16:30')

    return availabilities


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def is_available(appointment_time, duration, availabilities):
    """
    Helper function to check if the given time and duration fits within a known set of availability windows.
    Duration is assumed to be one of 30, 60 (meaning minutes).  Availabilities is expected to contain entries of the format HH:MM.
    """
    if duration == 30:
        return interpreted_value(appointment_time) in availabilities
    elif duration == 60:
        second_half_hour_time = increment_time_by_thirty_mins(interpreted_value(appointment_time))
        return interpreted_value(appointment_time) in availabilities and second_half_hour_time in availabilities

    # Invalid duration ; throw error.  We should not have reached this branch due to earlier validation.
    raise Exception('Was not able to understand duration {}'.format(duration))


def get_duration(appointment_type):
    appointment_duration_map = {'cleaning': 30, 'root canal': 60, 'whitening': 30}
    return try_ex(lambda: appointment_duration_map[interpreted_value(appointment_type).lower()])


def get_availabilities_for_duration(duration, availabilities):
    """
    Helper function to return the windows of availability of the given duration, when provided a set of 30 minute windows.
    """
    duration_availabilities = []
    start_time = '10:00'
    while start_time != '17:00':
        if start_time in availabilities:
            if duration == 30:
                duration_availabilities.append(start_time)
            elif increment_time_by_thirty_mins(start_time) in availabilities:
                duration_availabilities.append(start_time)

        start_time = increment_time_by_thirty_mins(start_time)

    return duration_availabilities


def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_book_appointment(appointment_type, date, appointment_time):
    if appointment_type and not get_duration(appointment_type):
        return build_validation_result(False, 'AppointmentType', 'I did not recognize that, can I book you a root canal, cleaning, or whitening?')

    if appointment_time:
        if len(appointment_time["value"]["resolvedValues"]) != 1:
            return build_validation_result(False, 'Time', 'I did not understand that, what time would you like to book your appointment? Please specify AM or PM')
        if len(interpreted_value(appointment_time)) != 5:
            return build_validation_result(False, 'Time', 'I did not recognize that, what time would you like to book your appointment?')

        hour, minute = interpreted_value(appointment_time).split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            return build_validation_result(False, 'Time', 'I did not recognize that, what time would you like to book your appointment?')

        if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(False, 'Time', 'Our business hours are ten a.m. to five p.m.  What time works best for you?')

        if minute not in [30, 0]:
            # Must be booked on the hour or half hour
            return build_validation_result(False, 'Time', 'We schedule appointments every half hour, what time works best for you?')

    if date:
        interpreted_date = interpreted_value(date)
        if not isvalid_date(interpreted_date):
            return build_validation_result(False, 'Date', 'I did not understand that, what date works best for you?')
        elif datetime.datetime.strptime(interpreted_date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'Date', 'Appointments must be scheduled a day in advance.  Can you try a different date?')
        elif dateutil.parser.parse(interpreted_date).weekday() == 5 or dateutil.parser.parse(interpreted_date).weekday() == 6:
            return build_validation_result(False, 'Date', 'Our office is not open on the weekends, can you provide a work day?')

    return build_validation_result(True, None, None)


def build_time_output_string(appointment_time):
    hour, minute = appointment_time.split(':')  # no conversion to int in order to have original string form. for eg) 10:00 instead of 10:0
    if int(hour) > 12:
        return '{}:{} p.m.'.format((int(hour) - 12), minute)
    elif int(hour) == 12:
        return '12:{} p.m.'.format(minute)
    elif int(hour) == 0:
        return '12:{} a.m.'.format(minute)

    return '{}:{} a.m.'.format(hour, minute)


def build_available_time_string(availabilities):
    """
    Build a string eliciting for a possible time slot among at least two availabilities.
    """
    prefix = 'We have availabilities at '
    if len(availabilities) > 3:
        prefix = 'We have plenty of availability, including '

    prefix += build_time_output_string(availabilities[0])
    if len(availabilities) == 2:
        return '{} and {}'.format(prefix, build_time_output_string(availabilities[1]))

    return '{}, {} and {}'.format(prefix, build_time_output_string(availabilities[1]), build_time_output_string(availabilities[2]))


def build_options(slot, appointment_type, date, booking_map):
    """
    Build a list of potential options for a given slot, to be used in responseCard generation.
    """
    day_strings = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if slot == 'AppointmentType':
        return [
            {'text': 'cleaning (30 min)', 'value': 'cleaning'},
            {'text': 'root canal (60 min)', 'value': 'root canal'},
            {'text': 'whitening (30 min)', 'value': 'whitening'}
        ]
    elif slot == 'Date':
        # Return the next five weekdays.
        options = []
        potential_date = datetime.date.today()
        while len(options) < 5:
            potential_date = potential_date + datetime.timedelta(days=1)
            if potential_date.weekday() < 5:
                options.append({'text': '{}-{} ({})'.format((potential_date.month), potential_date.day, day_strings[potential_date.weekday()]),
                                'value': potential_date.strftime('%A, %B %d, %Y')})
        return options
    elif slot == 'Time':
        # Return the availabilities on the given date.
        if not appointment_type or not date:
            return None

        interpreted_date = interpreted_value(date)    
        availabilities = try_ex(lambda: booking_map[interpreted_date])
        if not availabilities:
            return None

        availabilities = get_availabilities_for_duration(get_duration(appointment_type), availabilities)
        if len(availabilities) == 0:
            return None

        options = []
        for i in range(min(len(availabilities), 5)):
            options.append({'text': build_time_output_string(availabilities[i]), 'value': build_time_output_string(availabilities[i])})

        return options


""" --- Functions that control the bot's behavior --- """


def make_appointment(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    appointment_type = intent_request['sessionState']['intent']['slots']['AppointmentType']
    date = intent_request['sessionState']['intent']['slots']['Date']
    appointment_time = intent_request['sessionState']['intent']['slots']['Time']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionState']['sessionAttributes'] if "sessionAttributes" in intent_request['sessionState'] else {}
    booking_map = json.loads(try_ex(lambda: output_session_attributes['bookingMap']) or '{}')

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['sessionState']['intent']['slots']
        validation_result = validate_book_appointment(appointment_type, date, appointment_time)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                output_session_attributes,
                intent_request['sessionState']['intent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                build_response_card(
                    'Specify {}'.format(validation_result['violatedSlot']),
                    validation_result['message']['content'],
                    build_options(validation_result['violatedSlot'], appointment_type, date, booking_map)
                )
            )

        if not appointment_type:
            return elicit_slot(
                output_session_attributes,
                intent_request['sessionState']['intent']['name'],
                intent_request['sessionState']['intent']['slots'],
                'AppointmentType',
                {'contentType': 'PlainText', 'content': 'What type of appointment would you like to schedule?'},
                build_response_card(
                    'Specify Appointment Type', 'What type of appointment would you like to schedule?',
                    build_options('AppointmentType', appointment_type, date, None)
                )
            )

        if appointment_type and not date:
            return elicit_slot(
                output_session_attributes,
                intent_request['sessionState']['intent']['name'],
                intent_request['sessionState']['intent']['slots'],
                'Date',
                {'contentType': 'PlainText', 'content': 'When would you like to schedule your {}?'.format(interpreted_value(appointment_type))},
                build_response_card(
                    'Specify Date',
                    'When would you like to schedule your {}?'.format(interpreted_value(appointment_type)),
                    build_options('Date', appointment_type, date, None)
                )
            )

        if appointment_type and date:
            # Fetch or generate the availabilities for the given date.
            interpreted_date = interpreted_value(date)
            booking_availabilities = try_ex(lambda: booking_map[interpreted_date])
            if booking_availabilities is None:
                booking_availabilities = get_availabilities(interpreted_date)
                booking_map[interpreted_date] = booking_availabilities
                output_session_attributes['bookingMap'] = json.dumps(booking_map)

            appointment_type_availabilities = get_availabilities_for_duration(get_duration(appointment_type), booking_availabilities)
            if len(appointment_type_availabilities) == 0:
                # No availability on this day at all; ask for a new date and time.
                slots['Date'] = None
                slots['Time'] = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['sessionState']['intent']['name'],
                    slots,
                    'Date',
                    {'contentType': 'PlainText', 'content': 'We do not have any availability on that date, is there another day which works for you?'},
                    build_response_card(
                        'Specify Date',
                        'What day works best for you?',
                        build_options('Date', appointment_type, date, booking_map)
                    )
                )

            message_content = 'What time on {} works for you? '.format(interpreted_value(date))
            if appointment_time:
                output_session_attributes['formattedTime'] = build_time_output_string(interpreted_value(appointment_time))
                # Validate that proposed time for the appointment can be booked by first fetching the availabilities for the given day.  To
                # give consistent behavior in the sample, this is stored in sessionAttributes after the first lookup.
                if is_available(appointment_time, get_duration(appointment_type), booking_availabilities):
                    return delegate(output_session_attributes, intent_request['sessionState']['intent']['name'], slots)
                message_content = 'The time you requested is not available. '

            if len(appointment_type_availabilities) == 1:
                # If there is only one availability on the given date, try to confirm it.
                slots['Time'] = build_slot_value(appointment_type_availabilities[0])
                return confirm_intent(
                    output_session_attributes,
                    intent_request['sessionState']['intent']['name'],
                    slots,
                    {
                        'contentType': 'PlainText',
                        'content': '{}{} is our only availability, does that work for you?'.format
                                   (message_content, build_time_output_string(appointment_type_availabilities[0]))
                    },
                    build_response_card(
                        'Confirm Appointment',
                        'Is {} on {} okay?'.format(build_time_output_string(appointment_type_availabilities[0]), interpreted_value(date)),
                        [{'text': 'yes', 'value': 'yes'}, {'text': 'no', 'value': 'no'}]
                    )
                )

            available_time_string = build_available_time_string(appointment_type_availabilities)
            return elicit_slot(
                output_session_attributes,
                intent_request['sessionState']['intent']['name'],
                slots,
                'Time',
                {'contentType': 'PlainText', 'content': '{}{}'.format(message_content, available_time_string)},
                build_response_card(
                    'Specify Time',
                    'What time works best for you?',
                    build_options('Time', appointment_type, date, booking_map)
                )
            )

        return delegate(output_session_attributes, intent_request['sessionState']['intent']['name'], slots)

    # Book the appointment.  In a real bot, this would likely involve a call to a backend service.
    duration = get_duration(appointment_type)
    interpreted_date = interpreted_value(date)
    booking_availabilities = booking_map[interpreted_date]
    if booking_availabilities:
        # Remove the availability slot for the given date as it has now been booked.
        booking_availabilities.remove(interpreted_value(appointment_time))
        if duration == 60:
            second_half_hour_time = increment_time_by_thirty_mins(interpreted_value(appointment_time))
            booking_availabilities.remove(second_half_hour_time)

        booking_map[interpreted_date] = booking_availabilities
        output_session_attributes['bookingMap'] = json.dumps(booking_map)
    else:
        # This is not treated as an error as this code sample supports functionality either as fulfillment or dialog code hook.
        logger.debug('Availabilities for {} were null at fulfillment time.  '
                     'This should have been initialized if this function was configured as the dialog code hook'.format(date))

    return close(
        output_session_attributes,
        intent_request['sessionState']['intent']['name'],
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Okay, I have booked your appointment.  We will see you at {} on {}'.format(build_time_output_string(interpreted_value(appointment_time)), interpreted_date)
        }
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch sessionId={}, intentName={}'.format(intent_request['sessionId'], intent_request['sessionState']['intent']['name']))

    intent_name =  intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'MakeAppointment':
        return make_appointment(intent_request)
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
