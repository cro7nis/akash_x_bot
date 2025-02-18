import json
import pickle
from abc import ABC, abstractmethod
import os
from datetime import datetime, timezone

import pandas as pd
import requests

from utils.data import AkashStatsRetriever, AkashStatsProcessor
from utils.logger import logger
from configs import settings


class Reporter:

    def generate_report(self, market_data, dashboard):
        current_time = datetime.now(timezone.utc)
        formatted_time = current_time.strftime("%Y-%m-%d")
        price_emoji = '🚀' if market_data['priceChangePercentage24'] >= 0.0 else '📉'

        total_gpus = dashboard['networkCapacity']['totalGPU']
        active_gpus_now = dashboard['now']['activeGPU']
        active_gpus_yesterday = dashboard['compare']['activeGPU']
        utilization = active_gpus_now/total_gpus
        gpu_change_prc = ((active_gpus_now - active_gpus_yesterday) / active_gpus_yesterday) *100
        gpu_emoji = '📈' if gpu_change_prc >= 0.0 else '📉'

        usd_spend_now = dashboard['now']['dailyUUsdSpent'] / 1000000000
        usd_spend_now_yesterday = dashboard['compare']['dailyUUsdSpent'] / 1000000000
        usd_spend_change_prc = ((usd_spend_now - usd_spend_now_yesterday) / usd_spend_now_yesterday) *100
        usd_spent_emoji = '📈' if gpu_change_prc >= 0.0 else '📉'


        report = (f"Akash Network Daily Report - {formatted_time}\n\n"
                  f"{price_emoji} $AKT: {market_data['price']:.2f}$ ({market_data['priceChangePercentage24']:+.2f}% in 24h), staking APR: {dashboard['chainStats']['stakingAPR']*100:.2f}, bonded: {(dashboard['chainStats']['bondedTokens']/dashboard['chainStats']['totalSupply'])*100:.2f}%\n"
                  f"{gpu_emoji} Active GPUs: {active_gpus_now} ({gpu_change_prc:+.2f}% in 24h) (out of {total_gpus} GPUs, {utilization:.2}% util)\n"
                  f"{usd_spent_emoji} Daily USD spent: ${usd_spend_now:.2f}K ({usd_spend_change_prc:+.2f}% in 24h)\n"
                  f"@akashnet_ #DeCloud #DePIN #AI")

        return report

if __name__ == '__main__':
    retriever = AkashStatsRetriever(**settings.akash_api)
    if os.path.exists('data/data.pickle'):
        with open('data/data.pickle', 'rb') as handle:
            data = pickle.load(handle)
    else:
        data = retriever.retrieve('all', save_to_json=True)
        with open('data/data.pickle', 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    processor = AkashStatsProcessor()
    df, gpu_details, market_details, dashboard= processor(data)

    reporter = Reporter()
    report = reporter.generate_report(market_details, dashboard)

    logger.info(report)
    logger.info(len(report))