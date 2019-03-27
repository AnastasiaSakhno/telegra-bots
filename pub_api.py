#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json

BASE_PUB_URL = os.environ.get('PUB_BASE_URL')
BASE_API_URL = f'{BASE_PUB_URL}/api'
LOGIN_URL = f'{BASE_API_URL}/login'
TABLE_RESERVATIONS_URL = f'{BASE_API_URL}/table_reservations'
LATEST_TABLE_RESERVATION_URL = f'{BASE_API_URL}/table_reservations/latest'
AVAILABLE_TABLES_URL = f'{BASE_API_URL}/table_reservations/available_tables'

def auth_token():
	payload = {
		'user': {
			'email': os.environ.get('ADMIN_EMAIL'),
			'password': os.environ.get('ADMIN_PASSWORD')
		}
  }

	headers = {
		'Content-type': 'application/json'
	} 

	response = requests.post(LOGIN_URL, data = json.dumps(payload), headers = headers)

	return response.json()['token']


def post_table_reservation(chat_id, date):
  payload = {
    'table_reservation': {
      'chat_id': chat_id,
      'date': date
    }
  }

  headers = {
    'Content-type': 'application/json',
    'Authorization': auth_token()
  } 

  response = requests.post(TABLE_RESERVATIONS_URL, data = json.dumps(payload), headers = headers)

  return response.json()


def get_latest_table_reservation(chat_id):
  headers = {
    'Authorization': auth_token()
  } 

  response = requests.get(f'{LATEST_TABLE_RESERVATION_URL}?chat_id={chat_id}', headers = headers)

  return response.json()


def put_table_reservation(chat_id, attr, value):
  item = get_latest_table_reservation(chat_id)

  payload = {
    'table_reservation': {
      f'{attr}': value
    }
  }

  headers = {
    'Content-type': 'application/json',
    'Authorization': auth_token()
  } 

  response = requests.put(f'{TABLE_RESERVATIONS_URL}/{item["id"]}', data = json.dumps(payload), headers = headers)


def get_available_tables(chat_id):
  headers = {
    'Authorization': auth_token()
  } 

  response = requests.get(f'{AVAILABLE_TABLES_URL}?chat_id={chat_id}', headers = headers)

  return response.json()
