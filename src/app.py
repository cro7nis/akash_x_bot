import warnings

warnings.filterwarnings("ignore")

from bot import AkashBot
from configs import settings

generator = AkashBot(x_settings=settings.x, openai_settings=settings.openai, akash_apis=settings.akash_api)
generator.tweet_every_day(settings.bot.time, sleep=60*5)
