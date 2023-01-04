import os
import json
import boto3

# reuse client connection as global
client = boto3.client('lambda')

def router(event):
    intent_name = event['currentIntent']['name']

    # Read Environment variable for intent to Lambda function mapping
    # This can be used for bots in Lex V1 which use different lambda functions
    fn_name = os.environ.get(intent_name)
    print(f"Intent: {intent_name} -> Lambda: {fn_name}")

    if (fn_name):
        # invoke lambda and return result
        invoke_response = client.invoke(FunctionName=fn_name, Payload = json.dumps(event))
        print(json.dumps(invoke_response))
        payload = json.load(invoke_response['Payload'])
        return payload

    raise Exception('No environment variable for intent: ' + intent_name)

def lambda_handler(event, context):
    # Transform V2 input to V1 Format
    trasformed_event = transform_v2_input_to_v1(event)
    print("Transformed Input to V1 Lambda" + json.dumps(trasformed_event))

    # Route the request to V1 lambda
    response = router(trasformed_event)

    # Transform V1 output to V2 Format and return
    transformed_response = transform_v1_response_to_v2(response, event)
    print("Transformed Output from V2 Lambda" + json.dumps(transformed_response))
    return transformed_response

def transform_v2_input_to_v1(event):
    print(json.dumps(event))
    trasformed_event = {}

    # Active contexts
    trasformed_event['activeContexts'] = []
    for activeContext in event['sessionState']['activeContexts'] if 'activeContexts' in event['sessionState'] else []:
        transformed_context = {}
        transformed_context['timeToLive'] = activeContext['timeToLive']
        transformed_context['name'] = activeContext['name']
        transformed_context['parameters'] = activeContext['contextAttributes']
        trasformed_event['activeContexts'].append(transformed_context)

    # Alternative intents
    trasformed_event['alternativeIntents'] = event['interpretations'][1:]
    # To see the details from the recentIntentSummaryView, use the GetSession operation.

    # Bot
    trasformed_event['bot'] = {}
    trasformed_event['bot']['name'] = event['bot']['name']
    trasformed_event['bot']['alias'] = event['bot']['aliasName'] # Convert to $LATEST
    trasformed_event['bot']['version'] = event['bot']['version'] # Convert to $LATEST

    # Current intent
    trasformed_event['currentIntent'] = {}
    trasformed_event['currentIntent']['name'] = event['sessionState']['intent']['name']
    trasformed_event['currentIntent']['nluConfidenceScore'] = event['interpretations'][0]['nluConfidence']
    trasformed_event['currentIntent']['confirmationStatus'] = event['sessionState']['intent']['confirmationState']

    # Slots
    trasformed_event['currentIntent']['slots'] = {}
    trasformed_event['currentIntent']['slotDetails'] = {}
    for slotname, slot in event['sessionState']['intent']['slots'].items():
        if slot is None:
            trasformed_event['currentIntent']['slots'][slotname] = None
            trasformed_event['currentIntent']['slotDetails'][slotname] = None
        else:
            transformed_slot = {}
            trasformed_event['currentIntent']['slots'][slotname] = slot['value']['interpretedValue']

            transformed_slotDetail = {}
            transformed_slotDetail['resolutions'] = slot['value']['resolvedValues']
            transformed_slotDetail['originalValue'] = slot['value']['originalValue']
            trasformed_event['currentIntent']['slotDetails'][slotname] = transformed_slotDetail


    trasformed_event['currentIntent']['confirmationStatus'] = event['sessionState']['intent']['confirmationState']
    trasformed_event['currentIntent']['confirmationStatus'] = event['sessionState']['intent']['confirmationState']
    trasformed_event['currentIntent']['confirmationStatus'] = event['sessionState']['intent']['confirmationState']

    # Dialog action

    # Amazon Kendra
    trasformed_event['kendraResponse'] = event['sessionState']['intent']['kendraResponse'] if 'kendraResponse' in event['sessionState']['intent'] else None

    # Sentiment
    if 'sentimentResponse' in ['interpretations'][0]:
        trasformed_event['sentimentResponse'] = {}
        trasformed_event['sentimentResponse']['sentimentLabel'] = event['interpretations'][0]['sentimentResponse']['sentiment']
        trasformed_event['sentimentResponse']['sentimentScore'] = event['interpretations'][0]['sentimentResponse']['sentimentScore']
    else:
        trasformed_event['sentimentResponse'] = None

    # Others
    trasformed_event['userId'] = event['sessionId']
    trasformed_event['inputTranscript'] = event['inputTranscript']
    trasformed_event['invocationSource'] = event['invocationSource']
    trasformed_event['outputDialogMode'] = event['responseContentType']
    trasformed_event['messageVersion'] = "1.0",
    trasformed_event['sessionAttributes'] = event['sessionState']['sessionAttributes']
    trasformed_event['requestAttributes'] = event['requestAttributes'] if 'requestAttributes' in event else None

    return trasformed_event

def transform_v1_response_to_v2(response, request):
    print(json.dumps(response))
    trasformed_response = {}
    trasformed_response['sessionState'] = {}

    # Dialog action
    trasformed_response['sessionState']['dialogAction'] = {}
    trasformed_response['sessionState']['dialogAction']['type'] = response['dialogAction']['type']
    trasformed_response['sessionState']['dialogAction']['slotToElicit'] = response['dialogAction']['slotToElicit'] if 'slotToElicit' in response['dialogAction'] else None
    trasformed_response['sessionState']['dialogAction']['kendraQueryRequestPayload'] = response['dialogAction']['kendraQueryRequestPayload'] if 'kendraQueryRequestPayload' in response['dialogAction'] else None
    trasformed_response['sessionState']['dialogAction']['kendraQueryFilterString'] = response['dialogAction']['kendraQueryFilterString'] if 'kendraQueryFilterString' in response['dialogAction'] else None

    # Messages
    trasformed_response['messages'] = []
    if 'message' in response['dialogAction']:
        transformed_message = {}
        transformed_message['contentType'] = response['dialogAction']['message']['contentType']
        transformed_message['content'] = response['dialogAction']['message']['content']
        trasformed_response['messages'].append(transformed_message)

    if 'responseCard' in response['dialogAction']:
        for message in response['dialogAction']['responseCard']['genericAttachments']:
            transformed_message = {}
            transformed_message['contentType'] = response['dialogAction']['responseCard']['contentType']
            transformed_message['imageResponseCard']['title'] = message['title']
            transformed_message['imageResponseCard']['subtitle'] = message['subTitle']
            transformed_message['imageResponseCard']['imageUrl'] = message['imageUrl']
            transformed_message['imageResponseCard']['buttons'] = message['buttons']
            trasformed_response['messages'].append(transformed_message)

    # Intents and slots
    transformed_intent = {}
    if 'intentName' in response['dialogAction']:
        transformed_intent['name'] = response['dialogAction']['intentName']
    elif 'name' in request['sessionState']['intent']:
        transformed_intent['name'] = request['sessionState']['intent']['name']

    if 'fulfillmentState' in response['dialogAction']:
        transformed_intent['state'] = response['dialogAction']['fulfillmentState']
    transformed_intent['slots'] = {}
    for slotname, slotvalue in response['dialogAction']['slots'].items() if 'slots' in response['dialogAction'] else []:
        transformed_slot = {}
        transformed_slot['value'] = {}
        transformed_slot['value']['interpretedValue'] = slotvalue if slotvalue is not None else None
        transformed_slot['value']['originalValue'] = slotvalue if slotvalue is not None else None # Should not be required
        transformed_intent['slots'][slotname] = transformed_slot
    trasformed_response['sessionState']['intent'] = transformed_intent

    # Session Attribute
    trasformed_response['sessionState']['sessionAttributes'] = response['sessionAttributes']
    return trasformed_response
