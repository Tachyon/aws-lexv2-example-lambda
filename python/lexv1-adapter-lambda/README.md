Lex V2 migration tool (or [StartMigration API](https://docs.aws.amazon.com/lex/latest/dg/API_StartMigration.html)) can be used for migrating the bot definition. The tool does not migrate the associated lambda functions. This is an attempt to ease some of that effort for initial testing. This solution can be used for testing the migrated bot with Lex V2 without making much changes to lambda function. The solution should not be used in production as in this approach the adapter lambda calls original lambda functions.

Key differences between lex V1 and lex V2 lambda integration
1. Amazon Lex V2 allows only one Lambda function for each language in a bot. The Lambda function and its settings are configured for the bot alias that you use at runtime.
2. Amazon Lex V2 Lambda functions have a different input and output message format from Amazon Lex V1. 
   1. These are the differences in the Lambda function input format.
      1. Amazon Lex V2 replaces the currentIntent and alternativeIntents structures with the interpretations structure. Each interpretation contains an intent, the NLU confidence score for the intent, and an optional sentiment analysis.
      2. Amazon Lex V2 moves the activeContexts, sessionAttributes in Amazon Lex V1 to the unified sessionState structure. This structure provides information about the current state of the conversation, including the originating request ID.
      3. Amazon Lex V2 doesn't return the recentIntentSummaryView. Use the information in the sessionState structure instead.
      4. The Amazon Lex V2 input provides the botId and localeId in the bot attribute.
      5. The input structure contains an inputMode attribute that provides information on the type of input: text, speech, or DTMF.  
   2. These are the differences in the Lambda function output format:
      1. The activeContexts and sessionAttributes structures in Amazon Lex V1 are replaced by the sessionState structure in Amazon Lex V2.
      2. The recentIntentSummaryView isn't included in the output.
      3. The Amazon Lex V1 dialogAction structure is split into two structures, dialogAction that is part of the sessionState structure, and messages that is required when the dialogAction.type is ElicitIntent. Amazon Lex chooses messages from this structure to show to the user.

This adapter lambda abstracts both of the differences above
1. Transforms the lambda input to Lex V1 format 
2. Invokes a separate Lex V1 function. Different lambda can be invoked for each intent
3. Transforms the lambda output to Lex V2 format

Follow the steps below to test the lambda using Lex

1. Use AWS Lambda to create a python function using the code shared in [lexv1-adapter-lambda.py](https://github.com/Tachyon/aws-lexv2-example-lambda/blob/main/blueprints/python/lexv1-adapter-lambda/lexv1-adapter-lambda.py)
2. Attach Lambda function to Lex Alias. More details on how to attach Lambda function to a Lex bot can be found in [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/lambda.html#lambda-attach).
3. Update environment variable with intent to lambda function mapping where variable name is the intent name and value is the Lambda function name in the same region. If lambda function is shared by multiple intent, you will have to edit the ```router``` method accordingly.
4. Test the experience!
