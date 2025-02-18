import json
import pickle
from abc import ABC, abstractmethod
import os

import pandas as pd
import requests
from utils.logger import logger
from configs import settings


class Retriever(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def retrieve(self, query):
        pass


class AkashStatsRetriever(Retriever):

    def __init__(self, console_server, cloudmos_server):
        super().__init__()
        self.console_server = console_server
        self.cloudmos_server = cloudmos_server
        self.attr2url = {'dashboard': os.path.join(self.console_server, 'dashboard-data'),
                         'market': os.path.join(self.console_server, 'market-data'),
                         }
        self.attr2url.update({attr: os.path.join(self.console_server, 'provider-graph-data', attr) for attr in
                              ['cpu', 'gpu', 'memory', 'storage', 'count']})
        self.attr2url.update({'gpu_details': os.path.join(self.console_server, 'gpu')})
        self.attr2url.update({'gpu_prices': os.path.join(self.cloudmos_server, 'gpu-prices')})
        self.attr2url.update({attr: os.path.join(self.console_server, 'graph-data', attr) for attr in
                              ['activeLeaseCount', 'totalLeaseCount', 'dailyLeaseCount', 'totalUAktSpent',
                               'dailyUAktSpent',
                               'totalUUsdcSpent', 'dailyUUsdcSpent', 'totalUUsdSpent', 'dailyUUsdSpent', 'activeCPU',
                               'activeGPU',
                               'activeMemory', 'activeStorage']})

    def retrieve(self, query, save_to_json=False):
        data = {}
        try:
            if query == 'all':
                for attr, url in self.attr2url.items():
                    data[attr] = requests.get(url).json()
                    if save_to_json:
                        with open(f'data/{attr}.json', 'w', encoding='utf-8') as f:
                            json.dump(data[attr], f, ensure_ascii=False, indent=4)
                return data
            elif query in self.attr2url:
                data[query] = requests.get(self.attr2url[query]).json()
                return data
            else:
                raise ValueError(f'Unknown query {query}')
        except Exception as e:
            logger.error(f"Something went wrong retrieving {query}: {e}")


class AkashStatsProcessor:
    attrs = ['activeLeaseCount', 'totalLeaseCount', 'dailyLeaseCount', 'totalUAktSpent',
             'dailyUAktSpent',
             'totalUUsdcSpent', 'dailyUUsdcSpent', 'totalUUsdSpent', 'dailyUUsdSpent', 'activeCPU',
             'activeGPU',
             'activeMemory', 'activeStorage', 'cpu', 'gpu', 'memory', 'storage', 'count']

    def __init__(self):
        super().__init__()

    def __call__(self, data):
        dfs = []
        for attr in self.attrs:
            df = pd.DataFrame(data[attr]["snapshots"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            df.columns = [attr]
            dfs.append(df)

        df = pd.concat(dfs, join="inner", axis=1)
        df = df.reset_index()

        df.rename(columns={'totalUUsdSpent': 'totalUsdSpent',
                           'totalUAktSpent': 'totalAktSpent',
                           'dailyUAktSpent': 'dailyAktSpent',
                           'dailyUUsdSpent': 'dailyUsdSpent',
                           'gpu': 'totalGPU',
                           'cpu': 'totalCPU',
                           'memory': 'totalMemory',
                           'storage': 'totalStorage'}, inplace=True)
        df['utilization'] = df['activeGPU'] / df['totalGPU']
        df['totalUsdSpent'] = df['totalUsdSpent'] / 1000000
        df['totalAktSpent'] = df['totalAktSpent'] / 1000000
        df['dailyAktSpent'] = df['dailyAktSpent'] / 1000000
        df['dailyUsdSpent'] = df['dailyUsdSpent'] / 1000000

        gpu_data = []
        other_total = 0
        other_available = 0
        other_prices = []

        for model in data['gpu_prices']["models"]:
            model_name = f"{model['model']} {model['ram']} {model['interface']}"
            total = model["availability"]["total"]
            available = model["availability"]["available"]
            price = model["price"]["avg"] if model["price"] else None

            if total > 10:
                gpu_data.append((model_name, total, available, price))
            else:
                other_total += total
                other_available += available
                if price:
                    other_prices.append(price)

        if other_total > 0:
            other_price_avg = round(sum(other_prices) / len(other_prices), 2) if other_prices else None
            gpu_data.append(("Other", other_total, other_available, other_price_avg))

        # Sorting by total GPUs
        gpu_data.sort(key=lambda x: x[1], reverse=True)
        gpu_details = pd.DataFrame(gpu_data, columns=['model', 'total', 'available', 'price'])

        return df, gpu_details, data['market'], data['dashboard']


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

    logger.info(dashboard['now'])
