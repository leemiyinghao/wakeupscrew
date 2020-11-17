import yfinance, pprint
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib import dates, ticker
import random
import time
import numpy as np
from MediaWarehouse import MediaWarehouse
import io
import datetime
import json

async def getFinance(basePath):
    companys = [
        ("TWD=X", "USD/TWD"),
        ("TWDJPY=X", "TWD/JPY"),
        ("BTC-USD", "Bitcoin USD"),
        ("ETH-USD", "Ethereum USD"),
        ("AAPL", "Apple Inc."),
        ("GOOG", "Alphabet Inc."),
        ("FB", "Facebook, Inc."),
        ("AMZN", "Amazon.com, Inc."),
        ("TSLA", "Tesla, Inc."),
        ("UBER", "Uber Technologies, Inc."),
        ("ADBE", "Adobe Inc."),
        ("NVDA", "NVIDIA Corporation"),
        ("AMD", "Advanced Micro Devices, Inc."),
        ("INTC", "Intel Corporation"),
        ("QCOM", "QUALCOMM Incorporated"),
        ("TXN", "Texas Instruments Incorporated"),
        ("CSCO", "Cisco Systems, Inc."),
        ("ORCL", "Oracle Corporation"),
        ("IBM", "International Business Machines Corporation"),
        ("HPQ", "HP Inc."),
        ("NOK", "Nokia Corporation"),
        ("EA", "Electronic Arts Inc."),
        ("ATVI", "Activision Blizzard, Inc."),
        ("F", "Ford Motor Company"),
        ("GM", "General Motors Company"),
        ("MSFT", "Microsoft Corporation"),
        ("2330.TW", "Taiwan Semiconductor Manufacturing Company Limited "),
        ("2303.TW", "United Microelectronics Corporation"),
        ("2357.TW", "ASUSTeK Computer Inc."),
        ("2388.TW", "VIA Technologies, Inc."),
        ("2382.TW", "Quanta Computer Inc."),
        ("2409.TW", "AU Optronics Corp."),
        ("2454.TW", "MediaTek Inc."),
        ("3481.TW", "Innolux Corporation"),
        ("2317.TW", "Hon Hai Precision Industry Co., Ltd."),
        ("2412.TW", "Chunghwa Telecom Co., Ltd."),
        ("2002.TW", "China Steel Corporation"),
        ("1301.TW", "Formosa Plastics Corporation"),
        ("7974.T", "Nintendo Co., Ltd."),
        ("7203.T", "Toyota Motor Corporation"),
        ("7267.T", "Honda Motor Co., Ltd."),
        ("7951.T", "Yamaha Corporation"),
        ("7269.T", "Suzuki Motor Corporation"),
        ("7270.T", "Subaru Corporation"),
        ("2502.T", "Asahi Group Holdings, Ltd."),
        ("2501.T", "Sapporo Holdings Limited"),
        ("2587.T", "Suntory Beverage & Food Limited"),
        ("6758.T", "Sony Corporation"),
        ("BMW.DE", "Bayerische Motoren Werke Aktiengesellschaft"),
        ("DAI.DE", "Daimler AG")
    ]

    company, companyName = random.choice(companys)
    #mpl.style.use('default')
    _ticker = yfinance.Ticker(company)
    history = _ticker.history('1mo')
    currency = ""
    try:
        currency = _ticker.info['currency']
    except:
        pass
    lastOpen = history.Open[-1]
    lastClose = history.Close[-1]
    ohlc_data = []
    for line in history.iterrows():
        ohlc_data.append((dates.date2num(line[0]), np.float64(line[1].Open), np.float64(line[1].High), np.float64(line[1].Low), np.float64(line[1].Close)))
    fig, ax1 = plt.subplots()
    candlestick_ohlc(ax1, ohlc_data, width = 0.5, colorup = 'g', colordown = 'r', alpha = 0.8)
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%Y/%m/%d'))
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(4))
    plt.xticks(rotation = 30)
    plt.grid()
    plt.tight_layout()
    filename = "{}_{}.png".format(company, time.strftime("%Y_%m_%d"))
    data = io.BytesIO()
    plt.savefig(data, format='png')
    data = data.getvalue()
    url = MediaWarehouse.convertURL(MediaWarehouse.create(
        extension='png',
        data=data,
        thumbnail=data,
        sourceType="FINANCE",
        source="https://finance.yahoo.com/quote/{}".format(company),
        mainDescription="{} - {}".format(companyName, datetime.datetime.now()),
        additionalData=json.dumps({'company': company, 'companyName': companyName, 'lastOpen': lastOpen, "lastClose": lastClose, "currency": currency}, ensure_ascii=False)
        )['id'])
    plt.close()
    return url, company, companyName, lastOpen, lastClose, currency

if __name__ == '__main__':
    print(getFinance('.'))
