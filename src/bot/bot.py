import os
import traceback
from datetime import datetime, timezone

import pytz
import schedule
import tweepy
from openai import OpenAI
from utils.logger import logger
from llm.openai import llm_data_report_request
from utils.plot import create_gpu_plot, create_gpu_availability_and_price_plot, create_usd_plot
from utils.data import AkashStatsRetriever, AkashStatsProcessor
from utils.report import Reporter
import time


class AkashBot:
    granularities = {'day': 1, 'week': 7, 'month': 30, 'year': 365}

    def __init__(self, x_settings, openai_settings, akash_apis):
        super().__init__()
        self.logger = logger.bind(classname=self.__class__.__name__)
        self.x_v1 = tweepy.API(tweepy.OAuth1UserHandler(x_settings.consumer_key,
                                                        x_settings.consumer_secret,
                                                        x_settings.access_token,
                                                        x_settings.access_token_secret))

        self.x_client = tweepy.Client(
            consumer_key=x_settings.consumer_key,
            consumer_secret=x_settings.consumer_secret,
            access_token=x_settings.access_token,
            access_token_secret=x_settings.access_token_secret
        )

        self.openai_client = OpenAI(base_url=openai_settings.base_url, api_key=openai_settings.api_key)
        self.model = openai_settings.model
        self.retriever = AkashStatsRetriever(**akash_apis)
        self.processor = AkashStatsProcessor()
        self.reporter = Reporter()

    def upload_media(self, filepath):
        media = self.x_v1.media_upload(filepath)
        media_id = media.media_id_string
        self.logger.debug(f"Uploaded media {filepath} ID: {media_id}")
        return media_id

    def post_tweet(self, report, tweets, images):
        # Post the first tweet and get its tweet ID
        response = self.x_client.create_tweet(text=report)
        first_tweet_id = response.data['id']
        self.logger.info(f"First tweet posted with ID: {first_tweet_id}")

        # Use the first tweet's ID as the reply reference for the next tweets
        reply_to_tweet_id = first_tweet_id

        # Post each subsequent tweet as a reply to the previous tweet
        for i, (tweet, image) in enumerate(zip(tweets, images)):
            time.sleep(1)
            media_id = self.upload_media(image)
            time.sleep(1)
            response = self.x_client.create_tweet(text=tweet, media_ids=[media_id],
                                                  in_reply_to_tweet_id=reply_to_tweet_id)
            reply_to_tweet_id = response.data['id']
            self.logger.info(f"Tweet posted as reply with ID: {reply_to_tweet_id}")
        time.sleep(1)
        final_tweet = 'Check the official Akash Stats page for more details https://stats.akash.network/'
        self.x_client.create_tweet(text=final_tweet, in_reply_to_tweet_id=reply_to_tweet_id)
        self.logger.info(f"Posted final tweet: {reply_to_tweet_id}")

    def tweet_every_day(self, time_str, tz='UTC', sleep=300):

        schedule.every().day.at(time_str, tz=pytz.timezone(tz)).do(self.generate, granularity='week', amount=4)

        self.logger.info('Starting Akash bot scheduler')
        while True:
            schedule.run_pending()
            time.sleep(sleep)

    def generate(self, granularity='week', amount=4, plot_dir='plots/'):
        try:
            os.makedirs(plot_dir, exist_ok=True)
            current_time = datetime.now(timezone.utc)
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            self.logger.info(f"Current time: {formatted_time}")

            data = self.retriever.retrieve('all')
            df, gpu_details, market_details, dashboard = self.processor(data)
            report = self.reporter.generate_report(market_details, dashboard)
            self.logger.info(report)
            tweets = []
            plot_paths = []
            # gpu stats
            samples = self.granularities[granularity] * amount
            gpu_stats_filepath = os.path.join(plot_dir, f'/gpu_{formatted_time}.png')
            create_gpu_plot(df, granularity=granularity, amount=amount, name=gpu_stats_filepath)
            gpu_data = df.tail(samples)
            gpu_data = gpu_data.loc[:, ['date', 'totalGPU', 'activeGPU', 'utilization']]
            gpu_data['date'] = gpu_data['date'].astype(str)
            tweet = llm_data_report_request(self.openai_client, gpu_data.to_dict('records'), model=self.model)
            tweets.append(tweet)
            plot_paths.append(gpu_stats_filepath)
            self.logger.info(tweet)

            # GPU model pricing
            gpu_plot_filepath = os.path.join(plot_dir, f'gpu_details_{formatted_time}.png')
            create_gpu_availability_and_price_plot(gpu_details, name=gpu_plot_filepath)
            tweet = llm_data_report_request(self.openai_client, gpu_details.to_dict('records'), model=self.model)
            tweets.append(tweet)
            plot_paths.append(gpu_plot_filepath)
            self.logger.info(tweet)

            # USD
            usd_plot_filepath = os.path.join(plot_dir, f'usd_{formatted_time}.png')
            create_usd_plot(df, granularity=granularity, amount=amount, name=usd_plot_filepath)
            usd_data = df.tail(samples)
            usd_data = usd_data.loc[:, ['date', 'activeLeaseCount', 'activeGPU', 'dailyUsdSpent']]
            usd_data['date'] = usd_data['date'].astype(str)
            tweet = llm_data_report_request(self.openai_client, usd_data.to_dict('records'), model=self.model)
            tweets.append(tweet)
            plot_paths.append(usd_plot_filepath)
            self.logger.info(tweet)

            self.post_tweet(report, tweets, plot_paths)
        except Exception as e:
            logger.error(traceback.format_exc())
