This directory contains the bot export zip and its Lambda function used in the "Example Code" section of https://docs.aws.amazon.com/lexv2/latest/dg/using-transcript-confidence-scores.html. 

This example demonstrate a conversation flow to order a birth stone and take in name and month of birth. It used Lambda to validate that month is from an expected list and uses alternative transcripts to override if not. It also uses alternative names from transcripts to re prompt in cases where the top resolution does not have a high enough confidence score. 

Follow the steps below to test the lambda using Lex

1. Download the sample bot: [OrderBirthStone-DRAFT-EGMYCAGN5I-LexJson.zip](https://github.com/Tachyon/aws-lexv2-example-lambda/raw/main/blueprints/python/nbest-transcriptions-example-bot/OrderBirthStone-DRAFT-EGMYCAGN5I-LexJson.zip)
2. Import the sample bot in Amazon Lex. Refer [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/import.html) to get more details on how to Import a bot to Amazon Lex.
3. Use AWS Lambda to create a python function using the code shared in [lexv2-nbest-transcriptions.py](https://github.com/Tachyon/aws-lexv2-example-lambda/blob/main/blueprints/python/nbest-transcriptions-example-bot/lexv2-nbest-transcriptions.py)
4. Attach Lambda function to Lex Alias. More details on how to attach Lambda function to a Lex bot can be found in [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/lambda.html#lambda-attach).
5. Test the experience!
