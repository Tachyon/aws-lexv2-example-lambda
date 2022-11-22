This example demonstrates use of the built-in [AMAZON.RepeatIntent](https://docs.aws.amazon.com/lex/latest/dg/built-in-intent-repeat.html). This intent can be used to configure bot responses in the case user responds with a word or phrase to requesting bot to repeat the previous message. 

If AMAZON.RepeatIntent is present in a locale, the intent will be triggered when user requests to repeat the previous message. To actually repeat the bot response the application needs to use a Lambda function to save the previous intent information in session variables, or use the GetSession operation to get the previous intent information. This example showcases the first approach.

Follow the steps below to test the lambda using Lex

1. Download the sample bot: [OrderFlower-repeat-DRAFT-LexJson.zip](https://github.com/Tachyon/aws-lexv2-example-lambda/raw/main/python/blueprints/feature-demo/repeat-intent-demo/OrderFlower-repeat-DRAFT-LexJson.zip)
2. Import the sample bot in Amazon Lex. Refer [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/import.html) to get more details on how to Import a bot to Amazon Lex.
3. Use AWS Lambda to create a python function using the code shared in [lexv2-spelling.py](https://github.com/Tachyon/aws-lexv2-example-lambda/blob/main/blueprints/python/spelling-example-bot/lexv2-spelling.py)
4. Attach Lambda function to Lex Alias. More details on how to attach Lambda function to a Lex bot can be found in [Lex documentation](https://docs.aws.amazon.com/lexv2/latest/dg/lambda.html#lambda-attach).
5. Test the experience!

### Sample conversation to try
#### Test # 1
```
User: order flower
Bot: What type of flowers would you like to order?
User: can you please repeat
Bot: What type of flowers would you like to order?
```
#### Test # 2
```
User: order flower
Bot: What type of flowers would you like to order?
User: roses
Bot: What day do you want the roses to be picked up?
User: say that again
Bot: What day do you want the roses to be picked up?
```