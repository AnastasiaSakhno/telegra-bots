#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json

BASE_PUB_URL = os.environ.get('PUB_BASE_URL')
BASE_API_URL = f'{BASE_PUB_URL}/api'
LOGIN_URL = f'{BASE_API_URL}/login'
TABLE_RESERVATIONS_URL = f'{BASE_API_URL}/table_reservations'
BLACKOUT_DATES_URL = f'{BASE_API_URL}/table_reservation_blackout_dates'
LATEST_TABLE_RESERVATION_URL = f'{BASE_API_URL}/table_reservations/latest'
AVAILABLE_TABLES_URL = f'{BASE_API_URL}/table_reservations/available_tables'
AVAILABLE_FROM_TIMES_URL = f'{BASE_API_URL}/table_reservations/available_from_times'
AVAILABLE_TO_TIMES_URL = f'{BASE_API_URL}/table_reservations/available_to_times'
BLACK_LIST_URL = f'{BASE_API_URL}/table_reservations/black_lists'

def auth_token():
  try:
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
  except:
    return None


def post_table_reservation(chat_id, date):
  try:
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
  except:
    return None


def get_blackout_dates(date, hall):
  try:
    headers = {
      'Authorization': auth_token()
    } 

    response = requests.get(f'{BLACKOUT_DATES_URL}?date={date}&hall={hall}', headers = headers)

    return response.json()
  except:
    return None


def get_black_list(user_phone):
  try:
    headers = {
      'Authorization': auth_token()
    } 

    response = requests.get(f'{BLACK_LIST_URL}?user_phone={user_phone}', headers = headers)

    return response.json()
  except:
    return None


def get_latest_table_reservation(chat_id):
  try:
    headers = {
      'Authorization': auth_token()
    } 

    response = requests.get(f'{LATEST_TABLE_RESERVATION_URL}?chat_id={chat_id}', headers = headers)

    return response.json()
  except:
    return None


def put_table_reservation(chat_id, attr, value):
  try:
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
  except:
    return None


def delete_table_reservation(chat_id):
  try:
    item = get_latest_table_reservation(chat_id)

    headers = {
      'Content-type': 'application/json',
      'Authorization': auth_token()
    } 

    response = requests.delete(f'{TABLE_RESERVATIONS_URL}/{item["id"]}', headers = headers)
  except:
    return None


def get_available_tables(chat_id):
  try:
    headers = {
      'Authorization': auth_token()
    } 

    response = requests.get(f'{AVAILABLE_TABLES_URL}?chat_id={chat_id}', headers = headers)

    return response.json()
  except:
    return None


def get_available_from_times():
  try:
    headers = {
      'Authorization': auth_token()
    } 

    response = requests.get(AVAILABLE_FROM_TIMES_URL, headers = headers)

    return response.json()
  except:
    return None


def get_available_to_times(chat_id):
  try:
    headers = {
      'Authorization': auth_token()
    } 

    response = requests.get(f'{AVAILABLE_TO_TIMES_URL}?chat_id={chat_id}', headers = headers)

    return response.json()
  except:
    return None