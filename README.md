# Akash X bot
<img src="assets/bot.png" alt="drawing" width="500"/>

Akash X bot is dedicated to provide daily summaries of  Akash Network's on-chain statistics, keeping you up-to-date on the latest network activity.
This bot was created for on of the the Akash network [zealy tasks](https://zealy.io/cw/akashnetwork/).

Follow the bot's X (Twitter) account [here](https://x.com/AkashBot48145)

## Flow
* Collect data 
  * The bot queries the Akash console and Cloudmos APIs to retrieve network and chain statistics, market data and hardware capacity.
* Preprocess data
  * The bot preprocess the data for easier handling
* Report generation
  * The bot create a simple report with the available information
* Plot generaton
  * The bot create insightful plots 
* AI-generated descriptions
  * The bot uses [AkashChat API](https://chatapi.akash.network/) to generate automatic descriptions using the plot data
* Tweet generation
  * The bot uses the generated report, the plots and the corresponding AI-generated descriptions to create a daily thread on X

## Environment variables
To use this bot you need to provide the all the nesessarry credentials from the [X Developer Portal](https://developer.x.com/)
```
_X__CONSUMER_KEY=<consumer_key>
_X__CONSUMER_SECRET=<consumer_key>
_X__ACCESS_TOKEN=<consumer_key>
_X__ACCESS_TOKEN_SECRET=<consumer_key>
```
Then you need to provide the OpenAI compatible base url and api key. You can get these from [AkashChat API](https://chatapi.akash.network/) 
```
_OPENAI__BASE_URL=<base_url>
_OPENAI__API_KEY=<api_key>
```

## Generated thread example
### Report

<img src="assets/1.png" alt="drawing" width="500"/>

### Plots and descriptions

<img src="assets/2.png" alt="drawing" width="500"/>
<hr>
<img src="assets/3.png" alt="drawing" width="500"/>
<hr>
<img src="assets/4.png" alt="drawing" width="500"/>

