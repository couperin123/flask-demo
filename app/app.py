from flask import Flask, render_template, request, redirect, flash
# from app import app
from forms import TickerForm
from config import Config
from math import pi

import os
import requests
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)
app.config.from_object(Config)

app.vars = {}

# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = TickerForm()
    if form.validate_on_submit(): # If user submit a valid ticker value
        # flash('Checking Price of {}'.format(form.ticker.data))
        app.vars['ticker'] = request.form['ticker']
        # print(app.vars['ticker'])
        payload = {'function': 'TIME_SERIES_DAILY', 'symbol': app.vars['ticker'], 'outputsize': 'compact', 'apikey':os.environ.get('ALPHAVANTAGE_KEY')}
        r = requests.get('https://www.alphavantage.co/query', params=payload)
        # print(r.status_code)
        if (r.status_code == 200) and ('Error Message' not in r.json().keys()):
            # Iniitialization
            dt = []
            close_price = []

            for x,y in r.json()['Time Series (Daily)'].items():
                dt.append(x)
                close_price.append(y['4. close'])
            df = pd.DataFrame({'Date':dt, 'Closing Price':close_price})
            df['Date'] = df['Date'].astype('datetime64')
            df = df.set_index('Date')
            df['Closing Price'] = df['Closing Price'].astype('float32')

            month = df.loc[df.index.max():(df.index.max() - pd.DateOffset(months=1))]

            # make_plot
            p = figure(title=r.json()['Meta Data']['2. Symbol'].upper(), plot_height=350, plot_width=800)
            p.xaxis.ticker = list(range(len(month.index)))
            p.xaxis.major_label_overrides = {
                i: date.strftime('%b %d') for i, date in enumerate(month.index[::-1])
            }
            p.xaxis.major_label_orientation = pi/4
            p.xgrid.grid_line_color=None
            p.ygrid.grid_line_alpha=0.5
            p.xaxis.axis_label = 'Date'
            p.yaxis.axis_label = 'Closing Price'
            p.line(range(len(month.index)), month['Closing Price'][::-1], line_width=4)
            script, div = components(p)

            return render_template('dashboard.html', plots=[(script, div)])
        else: # If the submitted value is invalid
            flash("Invalid ticker symbol...")
            return render_template('index.html', form=form)
    return render_template('index.html', form=form) # If the submitted value is not valid (or not yet assigned)

# @app.route('/dashboard')
# def show_dashboard():
#     plots = []
#     plots.append(make_plot())
#
#     return render_template('dashboard.html', plots=plots)
#
# def make_plot():
#     p = figure(x_axis_type="datetime", title=r.json()['Meta Data']['2. Symbol'], plot_height=350, plot_width=800)
#     p.xgrid.grid_line_color=None
#     p.ygrid.grid_line_alpha=0.5
#     p.xaxis.axis_label = 'Date'
#     p.yaxis.axis_label = 'Closing Price'
#     p.line(month.index, month['Closing Price'], line_width=4)
#
#     script, div = components(p)
#     return script, div

if __name__ == '__main__':
    app.run(port=33507, debug=True)
