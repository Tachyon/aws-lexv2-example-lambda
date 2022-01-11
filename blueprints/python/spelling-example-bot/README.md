This directory contains the bot export zip and its Lambda function used in the "Example Code" section of https://docs.aws.amazon.com/lexv2/latest/dg/using-spelling.html. 

This example demonstrate a conversation flow to first trigger intent, then re-fill in PostalCode slot using SpellByWord style. Please search 'SpellByWord' in the Lambda function to see where to set this slot elicitation style.

Follow the steps below to test the lambda using Lex

1. Download the sample bot: [SST_Doc_Bot-DRAFT-WPCKL6OHLO-LexJson.zip](https://github.com/Tachyon/aws-lexv2-example-lambda/raw/main/blueprints/python/spelling-example-bot/SST_Doc_Bot-DRAFT-WPCKL6OHLO-LexJson.zip)
2. Import the sample bot in Amazon Lex. Refer [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/import.html) to get more details on how to Import a bot to Amazon Lex.
3. Use AWS Lambda to create a python function using the code shared in [lexv2-spelling.py](https://github.com/Tachyon/aws-lexv2-example-lambda/blob/main/blueprints/python/spelling-example-bot/lexv2-spelling.py)
4. Attach Lambda function to Lex Alias. More details on how to attach Lambda function to a Lex bot can be found in [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/lambda.html#lambda-attach).
5. Test the experience!
