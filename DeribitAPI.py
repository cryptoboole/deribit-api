import time
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import hmac
from ciso8601 import parse_datetime

class DeribitClient:
    _ENDPOINT = 'https://www.deribit.com/api/v2/'

    def __init__(self, api_key=None, api_secret=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
    
    def _authenticate(self) -> None:
        print('not implemented')
    
    # RESPONSE WRAPPER
    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not 'result' in data:
                print('ERROR', data['error'])
                raise Exception(data['error']['message'])
            return data['result']
        
    # REQUEST WRAPPER
    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        response = self._session.send(request.prepare())
        return self._process_response(response)
    
    
    #################
    # API ENDPOINTS #
    #################
    
    # GET: public/get_instruments
    def get_instruments(self, currency: str, kind: str = 'option', expired: bool = False) -> Any:
        params = { 'currency': currency, 'kind': kind, 'expired': str(expired).lower() }
        return self._request(method='GET', path='public/get_instruments', params=params)
    
    # GET: /public/get_last_trades_by_instrument
    def get_last_trades_by_instrument(self, instrument: str, start_seq: int = None) -> Any:
        params = {
            'instrument_name': instrument,
            'include_old': 'true'
        }
        if (start_seq): params['start_seq'] = int(start_seq)
        return self._request(method='GET', path='/public/get_last_trades_by_instrument', params=params)
    
    # GET: /public/get_last_trades_by_instrument_and_time
    def get_last_trades_by_instrument_and_time(self, instrument: str, start: int, end: int) -> Any:
        params = { 'instrument_name': instrument, 'start_timestamp': int(start), 'end_timestamp': int(end) }
        return self._request(method='GET', path='/public/get_last_trades_by_instrument_and_time', params=params)
    
    
    ##########
    # CUSTOM #
    ##########
    
    # CUSTOM: GETS ALL TRADES FOR INSTRUMENT WITHIN SPECIFIED TIMEFRAME
    def get_all_trades_by_instrument(self, instrument: str, start: int, end: int) -> Any:
        ids = set()
        results = []
        
        # helper functions
        parseTimestamp = lambda x: datetime.datetime.fromtimestamp(x/1000.0)
        dedupeTrades = lambda trades, ids: [trade for trade in trades if trade['trade_seq'] not in ids]
        parseIds = lambda trades: {trade['trade_seq'] for trade in trades}

        # initial time bounded request to get initial sequence (exit if 0 results)
        initial_response = self.get_last_trades_by_instrument_and_time(instrument, start, end)
        if (len(initial_response['trades']) == 0): return []
    
        # populate initial result set
        results.extend(initial_response['trades'])
        ids |= parseIds(initial_response['trades'])

        # iterate to meet criteria
        while True:
            
            # get last trades by instrement starting at specific trade sequence number
            response = self.get_last_trades_by_instrument(instrument, start_seq=max(ids)+1)
            
            # extend result set & merge new ids
            deduped_trades = dedupeTrades(response['trades'], ids)
            results.extend(deduped_trades)
            ids |= parseIds(deduped_trades)
            
            # uncomment below to debug
            # print(f'{len(ids)} TRADES RETRIEVED', response['has_more'], len(response['trades']))
            
            # stop if we have reached the end of data or the end timestamp
            trade_timestamps = [int(x['timestamp']) for x in response['trades']]
            
            if not response['has_more'] or len(trade_timestamps) == 0 or max(trade_timestamps) > end:
                break
                
        # return trades within specified timeframe
        return [trade for trade in results if int(trade['timestamp']) < end]
