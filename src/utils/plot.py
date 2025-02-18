import os
import pickle
from datetime import datetime, timezone

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.dates import date2num

from utils.data import AkashStatsProcessor
from utils.logger import logger

if os.path.exists('data/data.pickle'):
    with open('data/data.pickle', 'rb') as handle:
        data = pickle.load(handle)


def create_gpu_plot(df, name='gpus.png', granularity='day', amount=1, save=True):
    granularities = {'day': 1, 'week': 7, 'month': 30, 'year': 365}
    assert granularity in granularities
    samples = granularities[granularity] * amount
    data = df.tail(samples).copy()
    data['date_numeric'] = date2num(data['date'])

    # Set Seaborn theme for better visualization
    sns.set_theme(style="whitegrid")

    # Create figure and first Y-axis
    fig, ax1 = plt.subplots(figsize=(10, 5))
    sns.lineplot(x=data["date"], y=data["activeGPU"], marker="o", label='Active GPUs', ax=ax1, color='blue')
    if samples > 20:
        sns.regplot(x=data["date_numeric"], y=data["activeGPU"], ax=ax1, scatter=False,
                    line_kws={"color": "blue", "linewidth": 1}, order=2)
    sns.lineplot(x=data["date"], y=data["totalGPU"], marker="D", label='Total GPUs', ax=ax1, color='green')
    if samples > 20:
        sns.regplot(x=data["date_numeric"], y=data["totalGPU"], ax=ax1, scatter=False,
                    line_kws={"color": "green", "linewidth": 1}, order=2)
    # sns.lineplot(x=active_gpu["date"], y=active_gpu["value"]/total_gpu["value"], marker="*", label='GPU utilization')

    # Formatting the x-axis to show Month and Year (e.g., "Apr 2024")
    if granularity == 'day':
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    elif granularity == 'week':
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    elif granularity == 'month':
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    elif granularity == 'year':
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax1.xaxis.set_major_locator(mdates.YearLocator())

    ax1.set_xlabel("Date", weight='bold')
    ax1.set_ylabel("GPUs", weight='bold')
    ax1.tick_params(axis="y")
    ax1.tick_params(axis="x", rotation=25)

    # Create secondary Y-axis (right side)
    ax2 = ax1.twinx()
    # Plot temperature (right axis)
    sns.lineplot(x=data["date"], y=data["utilization"], marker="s", ax=ax2, label="Utilization Rate", color="r",
                 legend=False)
    if samples > 20:
        sns.regplot(x=data["date_numeric"], y=data["utilization"], ax=ax2, scatter=False, color="r",
                    line_kws={"color": "red", "linewidth": 1}, order=2)

    ax2.set_ylabel("Utilization Rate (%)", color="r")
    ax2.tick_params(axis="y", labelcolor="r")
    ax2.set_ylim(0.0, 1.0)
    ax2.grid(False)

    # Combine the handles and labels from both axes
    handles, labels = ax1.get_legend_handles_labels()  # Get handles and labels from left axis
    handles2, labels2 = ax2.get_legend_handles_labels()  # Get handles and labels from right axis

    # Combine the legends
    handles.extend(handles2)
    labels.extend(labels2)

    # Display a single legend
    ax1.legend(handles=handles, labels=labels, loc="upper left")
    plt.title(f"Akash GPUs in the last {amount}-{granularity} period", fontweight='bold')
    if save:
        plt.savefig(name, dpi=300, bbox_inches="tight")
    #plt.show()


def create_usd_plot(df, name='usd_spent.png', granularity='day', amount=7, save=True):
    granularities = {'day': 1, 'week': 7, 'month': 30, 'year': 365}
    assert granularity in granularities
    samples = granularities[granularity] * amount
    df = df.tail(samples).copy()
    df['date_numeric'] = date2num(df['date'])

    # Set Seaborn theme for better visualization
    sns.set_theme(style="whitegrid")

    # Bar for leases, color coded based on GPU activity
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for active leases
    bar_width = 0.35
    index = range(len(df))
    bar1 = ax1.bar(index, df['activeLeaseCount'], bar_width, color='b', label='Active Leases')
    bar2 = ax1.bar([i + bar_width for i in index], df['activeGPU'], bar_width, color='g',
                   label='Active GPUs')

    # Customize x-axis labels
    ax1.set_xlabel('Date', weight='bold')
    ax1.set_xticks([i + bar_width / 2 for i in range(0,len(df),2)])
    dates = df['date'].dt.date.tolist()
    ax1.set_xticklabels([dates[i] for i in range(0,len(df),2)], rotation=35)
    ax1.set_ylabel('Active Leases and GPUs', weight='bold')

    # Create another y-axis for USD spent
    ax2 = ax1.twinx()
    ax2.plot(index, df['dailyUsdSpent'], color='r', marker='o', label='Daily USD Spent', linewidth=3)
    ax2.set_ylabel('Daily USD Spent', weight='bold')

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title(f'Active Leases, GPUs and Daily USD Spent in the last {amount}-{granularity} period', fontweight='bold')
    plt.tight_layout()
    if save:
        plt.savefig(name, dpi=300, bbox_inches="tight")
    #plt.show()


def create_gpu_availability_and_price_plot(gpu_data, name='gpu_details.png', save=True):
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime("%Y-%m-%d")
    gpu_data = gpu_data.to_dict('list')
    labels = gpu_data['model']
    totals = gpu_data['total']
    availables = gpu_data['available']
    prices = gpu_data['price']

    # Bar chart
    x = np.arange(len(labels))
    width = 0.6

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_total = ax.bar(x, totals, width, label="Total GPUs", color="gray")
    bars_available = ax.bar(x, availables, width, label="Available GPUs", color="green")

    # Annotating values
    for bar_total, bar_avail, price in zip(bars_total, bars_available, prices):
        ax.text(bar_total.get_x() + bar_total.get_width() / 2, bar_total.get_height() + 5,
                str(int(bar_total.get_height())), ha='center', fontsize=11, fontweight='bold')
        ax.text(bar_avail.get_x() + bar_avail.get_width() / 2, bar_avail.get_height() - 14,
                str(int(bar_avail.get_height())), ha='center', color='white', fontsize=11, fontweight='bold')
        if price:
            ax.text(bar_total.get_x() + bar_total.get_width() / 2, bar_total.get_height() + 25,
                    f"${price}", ha='center', color='blue', fontsize=15, fontweight='bold')

    # Formatting
    ax.set_xlabel("GPU Models", weight='bold')
    ax.set_ylabel("Number of GPUs", weight='bold')
    ax.set_title(f"GPU Availability and Average Pricing in Akash Network ({formatted_time})", fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", weight='bold')
    ax.legend()

    plt.tight_layout()
    if save:
        plt.savefig(name, dpi=300, bbox_inches="tight")
    #plt.show()


if __name__ == '__main__':
    processor = AkashStatsProcessor()
    df, gpu_details, market_details, dashboard = processor(data)
    create_gpu_plot(df, name='gpus.png', granularity='day', amount=7)
    create_gpu_availability_and_price_plot(gpu_details, name='gpu_details.png')
    create_usd_plot(df, granularity='day', amount=7)
