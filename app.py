from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px

import numpy as np

from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
app = Flask(__name__)


um_futures_client = UMFutures()

def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)   
    for i in arr:
        temp = (((i - min(arr))*diff)/diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr

all_symbols = [d['symbol'] for d in um_futures_client.ticker_24hr_price_change() if d['symbol'].endswith("USDT")]

all_symbol_long_short_ratio_data_normalized = []
symbol_tags = []
for symbol in all_symbols:
  data = um_futures_client.long_short_account_ratio(symbol, "5m", limit=150)
  data = [float(d['longAccount']) for d in data]
  if len(data) == 150:
    norm_data = normalize(data, 0, 1)
    all_symbol_long_short_ratio_data_normalized.append(norm_data)
    symbol_tags.append(symbol)


@app.route('/')
def graph():
    fig = px.imshow(all_symbol_long_short_ratio_data_normalized, y = symbol_tags, color_continuous_scale='rdylgn')
    fig.layout.height = 1300
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('notdash.html', graphJSON=graphJSON)

@app.route('/a')
def notdash():
   df = pd.DataFrame({
      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 
      'Bananas'],
      'Amount': [4, 1, 2, 2, 4, 5],
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
   })
   fig = px.bar(df, x='Fruit', y='Amount', color='City', 
      barmode='group')
   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template('notdash.html', graphJSON=graphJSON)
