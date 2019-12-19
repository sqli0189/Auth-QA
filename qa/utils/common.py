import requests
import logging
from json import dumps

import qa.utils.payload as payload
from qa.settings import *

# Create a request headers
def headers(vungle_src=None, vungle_version='1.0', auth_token=None):
    
    headers = { 'Accept': "application/json",
            'Content-Type': "application/json",
            'cache-control': "no-cache"
            }

    if vungle_src is not None:
        headers['vungle-source'] = vungle_src
    
    # For Auth service, the field vungle-version is a mandatory key
    headers['vungle-version'] = vungle_version
    if vungle_version is None:
        headers.pop('vungle-version', 0)
    
    if auth_token is not None:
        headers['Authorization'] = 'Bearer %s' % auth_token

    return headers

# Create a GET request and return the resposne instance
def get(url, params=None, headers=headers()):
    try:
        logging.info('Send get request with below parameters:')
        logging.info('Request headers =\n%s' % dumps(headers, indent = 4))
        r = requests.get(url=url, params=params, headers=headers)
        logging.info('Request Url = %s' % r.url)
        if r.text!='':
            logging.info('Response payload =\n%s' % dumps(r.json(), indent = 4))
        return r
    except Exception as ex:
        logging.exception('An exception happens while sending get request')
        raise ex

# Create a DELETE reqeust and return the response instance
def delete(url, params=None, headers=()):
    try:
        logging.info('Send delete request with below parameters:')
        logging.info('Request headers =\n%s' % dumps(headers, indent = 4))
        r = requests.delete(url=url, params=params, headers=headers)
        if r.text!='':
            logging.info('Response payload =\n%s' % dumps(r.json(), indent = 4))
        return r
    except Exception as ex:
        logging.exception('An excepiton happens while sending delete request')
        raise ex

# Create a POST request and return the response instance
def post(url, json, headers=headers()):
    logging.info('Send post request with below parameters:')
    logging.info('Request Url = %s' % url)
    logging.info('Request payload =\n%s' % dumps(json, indent = 4))
    logging.info('Request headers =\n%s' % dumps(headers, indent = 4))
    try:
        r = requests.post(url, json=json, headers=headers)
        if r.text !='':
            logging.info('Response payload =\n%s' % dumps(r.json(), indent = 4))
        return r
    except Exception as ex:
        logging.exception('An exception happens while sending get request')
        raise ex

def patch(url, json, params=None, headers=headers()):
    logging.info('Send patch request with below parameters:')
    logging.info('Request Url = %s' % url)
    logging.info('Request payload =\n%s' % dumps(json, indent = 4))
    logging.info('Request headers =\n%s' % dumps(headers, indent = 4))
    try:
        r = requests.patch(url, params=params, json=json, headers=headers)
        if r.text !='':
            logging.info('Response payload =\n%s' % dumps(r.json(), indent = 4))
        return r
    except Exception as ex:
        logging.exception('An exception happens while sending pact request')
        raise ex

def put(url, json, params=None, headers=headers()):
    logging.info('Send patch request with below parameters:')
    logging.info('Request Url = %s' % url)
    logging.info('Request payload =\n%s' % dumps(json, indent = 4))
    logging.info('Request headers =\n%s' % dumps(headers, indent = 4))
    try:
        r = requests.put(url, params=params, json=json, headers=headers)
        if r.text !='':
            logging.info('Response payload =\n%s' % dumps(r.json(), indent = 4))
        return r
    except Exception as ex:
        logging.exception('An exception happens while sending put request')
        raise ex