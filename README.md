# Amazon Lex V2 - Lambda Blueprints to work with Example bots 

The Amazon Lex V2 console provides example bots (called bot blueprints) that are preconfigured so you can quickly create and test a bot in the console. Unlike Lex V1, Lex V2 does not provide corresponding Lambda function blueprints. I have taken the Lex V1 Lambda blueprints and modified them to work with Lex v2 Lambda interface. These python scripts can help Lex v2 users play with Lex V2 and Lambda integration. 

These blueprints provide sample code that works with their corresponding bots. You can use these blueprints to quickly create a bot that is configured with a Lambda function as a code hook, and test the end-to-end setup without having to write code.

## Using Lambda in Lex V2 bot
1. Create the example bot as mentioned in Lex v2 documentation https://docs.aws.amazon.com/lexv2/latest/dg/exercise-1.html
2. Create a Lambda function from Lambda console
  1. Select 'Author from Scratch' 
  2. Choose 'Python 2.7' as the runtime
  3. Pick appropriate name for the function
  4. Click on 'Create Function'
3. Update the 'Code Source' of lambda function with code from the package. Make sure to use code corresponding to the bot blueprint you used to create the example bot
  1. Amazon Lex blueprint — OrderFlowers
    i) AWS Lambda blueprint — lexv2-book-trip.py
  2. Amazon Lex blueprint — ScheduleAppointment
    i). AWS Lambda blueprint — lexv2-make-appointment.py
  3. Amazon Lex blueprint — BookTrip
    i) AWS Lambda blueprint — lexv2-book-trip.py
5. Build the locale
6. Go to Alias settings for the bot and select the alias where you wish to add lambda function
7. Under the lamguage section click on the language you want to update. **Currently we only have implementation of English (US) **
8. Select the lambda function which you just created and save
9. To test the lambda integration. 
  1. Go to Alias setting page 
  2. Under language setting select the radio button infront of the language which you added lambda settings
  3. Click on 'Test'. This will open a test window with the alias settings of current alias.
  4. Test!



