# Amazon Lex V2 - Lambda Blueprints to work with Example bots 

The Amazon Lex V2 console provides example bots (called bot blueprints) that are preconfigured so you can quickly create and test a bot in the console. Unlike Lex V1, Lex V2 does not provide corresponding Lambda function blueprints. I have taken the Lex V1 Lambda blueprints and modified them to work with Lex v2 Lambda interface. These python scripts can help Lex v2 users play with Lex V2 and Lambda integration. 

These blueprints provide sample code that works with their corresponding bots. You can use these blueprints to quickly create a bot that is configured with a Lambda function as a code hook, and test the end-to-end setup without having to write code.

## Using Lambda in Lex V2 bot
1. Create the example bot as mentioned in Lex v2 documentation https://docs.aws.amazon.com/lexv2/latest/dg/exercise-1.html
2. Create a Lambda function from Lambda console
   - Select 'Author from Scratch' 
   - Choose 'Python 2.7' as the runtime
   - Pick appropriate name for the function
   - Click on 'Create Function'
3. Update the 'Code Source' of lambda function with code from the package. Make sure to use code corresponding to the bot blueprint you used to create the example bot
   - Amazon Lex blueprint — OrderFlowers
     - AWS Lambda blueprint — lexv2-book-trip.py
   - Amazon Lex blueprint — ScheduleAppointment
     - AWS Lambda blueprint — lexv2-make-appointment.py
   - Amazon Lex blueprint — BookTrip
     - AWS Lambda blueprint — lexv2-book-trip.py
5. Build the locale
6. Go to Alias settings for the bot and select the alias where you wish to add lambda function
7. Under the lamguage section click on the language you want to update. **Currently we only have implementation of English (US) **
8. Select the lambda function which you just created and save
9. To test the lambda integration. 
   - Go to Alias setting page 
   - Under language setting select the radio button infront of the language which you added lambda settings
   - Click on 'Test'. This will open a test window with the alias settings of current alias.
   - Test!

## Backlog / TODO

1. Add suport for other languages supported by Lex V2
2. Add blueprint in other languages supported by AWS Lambda
