#!/usr/bin/python

# EXAMPLE RUN
# > python export.py BTC 30APR 20210426 20210428

# dependencies
import sys, json, os
import datetime, time
import pandas as pd

# quick and dirty check
if not len(sys.argv) == 5:
    print('INCORRECT ARGUMENTS [CURENCY] [FILTER] [YYYYMMDD] [YYYYMMDD]')
    sys.exit(0)
print('ARGUMENTS:', str(sys.argv))

# make exports folder if it doesn't exist
if not os.path.exists('exports'): os.makedirs('exports')
    
# instantiate deribit API
from DeribitAPI import DeribitClient
deribit = DeribitClient()

# conditions (parameters)
start_dt = datetime.datetime.strptime(sys.argv[3], '%Y%m%d')
end_dt = datetime.datetime.strptime(sys.argv[4], '%Y%m%d')
currency_symbol = sys.argv[1]
instrument_filter = sys.argv[2]

# retrieve filtered instruments
active_options = pd.DataFrame(deribit.get_instruments(currency_symbol, 'option', False))
filtered_active_options = active_options[active_options['instrument_name'].str.contains(instrument_filter)]

# fetch and save trades within timeframe to respective csv
instrument_data = []
print('FETCHING TRADES FOR', len(filtered_active_options), 'INSTRUMENTS FOR', start_dt.strftime("%Y%m%d"), end_dt.strftime("%Y%m%d"))
for index, row in filtered_active_options.iterrows():
    
    # request all trades for instrument within timeframe
    instrument_trades = deribit.get_all_trades_by_instrument(
        instrument=row['instrument_name'],
        start=int(start_dt.timestamp()*1e3),
        end=int(end_dt.timestamp()*1e3))
    
    # parse to dataframe and save to csv
    trades_df = pd.DataFrame(instrument_trades)
    print(start_dt.strftime("%Y%m%d"), row['instrument_name'], 'TRADES:', len(trades_df))
    instrument_data.append(trades_df)
    
merged_df = pd.concat(instrument_data, ignore_index=True)
merged_df['parsed_timestamp'] = pd.to_datetime(merged_df['timestamp'], unit='ms')
merged_df[['currency', 'expiry', 'strike', 'pc']] = merged_df['instrument_name'].str.split('-', 3, expand=True)
merged_df = merged_df.sort_values("timestamp")
filename_components = [
    'exports/TRADES',
    currency_symbol,
    instrument_filter,
    start_dt.strftime("%Y%m%d"),
    end_dt.strftime("%Y%m%d")
]
merged_df.to_csv('_'.join(filename_components)+'.csv', index=False)
print('SAVED', len(merged_df), 'RECORDS TO', '_'.join(filename_components)+'.csv')