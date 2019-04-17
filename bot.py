#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import telegramcalendar
import pub_api

from datetime import datetime
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, CallbackQueryHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger=logging.getLogger(__name__)

TOKEN=os.environ.get('TELEGRAM_API_TOKEN')
PORT=int(os.environ.get('PORT', '8443'))

TIME_REGEX_STR='^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$'
TIMES_LINE_BUTTONS_COUNT = 6

# states
HALL, TABLE, TIME_FROM, TIME_TO, NUMBER_OF_PEOPLE, NAME, PHONE_NUMBER=range(7)

chunks=lambda l, n: [l[x: x+n] for x in range(0, len(l), n)]

def start(update, context):
  update.message.reply_text(
      'Бот з бронювання столів у Махнопабі вітає вас!\n\n'
      'Натисніть /cancel, щоб завершити розмову та /start, щоб почати спочатку.\n\n'
      'Оберіть дату, на коли ви бажаєте замовити стіл.',
      reply_markup=telegramcalendar.create_calendar())

  return CallbackQueryHandler


def date_selected(update, context):
  selected, date=telegramcalendar.process_calendar_selection(context.bot, update)

  if selected:
    user=update.callback_query.from_user
    date_formatted=date.strftime("%d.%m.%Y")
    logger.info("User %s %s selected date: %s", user.first_name, user.last_name, date_formatted)

    chat_id=update.callback_query.message.chat_id
    item=pub_api.post_table_reservation(chat_id, date_formatted)
    logger.info("item=%s", item)

    context.bot.send_message(
      chat_id=update.callback_query.message.chat_id, 
      text=date_formatted, 
      reply_markup=ReplyKeyboardRemove()
    )

    reply_keyboard=[['Паб', 'Підпілля (концертний)']]

    context.bot.send_message(
      chat_id=update.callback_query.message.chat_id,
      text='Чудово. Ви хочете замовити стіл у першому або другому залі?',
      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

  return HALL


def hall(update, context):
  user=update.message.from_user
  hall=(1 if update.message.text == 'Паб' else 2)
  logger.info("Hall of %s %s: %s", user.first_name, user.last_name, hall)

  chat_id=update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'hall', hall)

  times=pub_api.get_available_from_times()

  reply_keyboard=chunks(times, TIMES_LINE_BUTTONS_COUNT)

  update.message.reply_text('Добре! О котрій годині вас очікувати?',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

  return TIME_FROM


def time_from(update, context):
  user=update.message.from_user
  time_from=update.message.text
  logger.info("%s %s plans be from: %s", user.first_name, user.last_name, time_from)

  chat_id = update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'time_from', time_from)

  times=pub_api.get_available_to_times(chat_id)

  reply_keyboard=chunks(times, TIMES_LINE_BUTTONS_COUNT)

  context.bot.send_message(
    chat_id=update.message.chat_id,
    text='Вкажіть, будь ласка, до котрої години плануєте відпочинок у нас або натисніть /skip, щоб пропустити цей крок.',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

  return TIME_TO


def time_to(update, context):
  user=update.message.from_user
  time_to=update.message.text
  logger.info("%s %s plans be until: %s", user.first_name, user.last_name, time_to)

  return table_query(update, context, time_to)


def skip_time_to(update, context):
  user = update.message.from_user
  logger.info("User %s %s did not send time to.", user.first_name, user.last_name)

  return table_query(update, context, '24:00')


def table_query(update, context, time_to):
  chat_id=update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'time_to', time_to)

  tables=pub_api.get_available_tables(chat_id)

  reply_keyboard=chunks(tables, 5)

  item=pub_api.get_latest_table_reservation(chat_id)
  picture=('pub_hall1.jpg' if item["hall"] == "1" else 'pub_hall2.jpg')

  context.bot.send_photo(update.message.chat_id, photo=open(picture, 'rb'))

  context.bot.send_message(
    chat_id=chat_id,
    text='Гаразд. Який з доступних столів ви бажаєте зайняти?',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

  return TABLE


def table(update, context):
  user=update.message.from_user
  table=update.message.text
  logger.info("Table of %s %s: %s", user.first_name, user.last_name, table)

  chat_id=update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'table', table)

  update.message.reply_text('Дякую! Тепер вкажіть, будь ласка, скільки людей планують прийти до нас?')

  return NUMBER_OF_PEOPLE


def number_of_people(update, context):
  user=update.message.from_user
  number_of_people=update.message.text
  logger.info("Number of people for %s %s: %s", user.first_name, user.last_name, number_of_people)

  chat_id=update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'people_number', number_of_people)

  reply_keyboard = [[KeyboardButton(text='Залишити свій номер телефону', request_contact=True)]]

  update.message.reply_text(
      'Будь ласка, натисніть кнопку "Залишити свій номер телефону", щоб ми могли з вами зв\'язатися.',
      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

  return PHONE_NUMBER


def phone_number(update, context):
  user=update.message.from_user
  phone_number=update.message.contact.phone_number
  logger.info("Phone number of %s %s: %s", user.first_name, user.last_name, phone_number)

  pub_api.put_table_reservation(update.message.chat_id, 'user_phone', phone_number)

  update.message.reply_text('Дякую. Як до вас можно звертатися?')

  return NAME


def name(update, context):
  user=update.message.from_user
  name=update.message.text
  logger.info("Name of %s %s: %s", user.first_name, user.last_name, name)

  chat_id=update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'user_name', f'{name} ({user.first_name} {user.last_name})')

  item=pub_api.get_latest_table_reservation(chat_id)
  pub_api.put_table_reservation(chat_id, 'status', 'filled')

  time_lasts_up=datetime.strptime(item["time_lasts_up"], '%Y-%m-%dT%H:%M:%S+02:00').strftime('%H:%M')

  update.message.reply_text(
    'Дуже дякую.\n\n'
    f'Якщо ви не зможете прийти, будь ласка, попередьте нас. Бронь триматиметься до {time_lasts_up}\n\n'
    'Наш менеджер зателефонує вам.\n\n'
    'Якщо ви хочете зарезервувати ще один стіл, натисніть /start.\n\n'
    'Навседобре!')

  return ConversationHandler.END


def cancel(update, context):
  user=update.message.from_user
  logger.info("User %s canceled the conversation.", user.first_name)

  chat_id=update.message.chat_id
  pub_api.put_table_reservation(chat_id, 'status', 'cancelled')

  update.message.reply_text('Навседобре! Якщо ви хочете почати спочатку, натисніть /start.',
                              reply_markup=ReplyKeyboardRemove())

  return ConversationHandler.END


def error(update, context):
  """Log Errors caused by Updates."""
  logger.warning('Update "%s" caused error "%s"', update, context.error)



def main():
  # Create the Updater and pass it your bot's token.
  # Make sure to set use_context=True to use the new context based callbacks
  # Post version 12 this will no longer be necessary
  updater=Updater(token=TOKEN, use_context=True)

  # Get the dispatcher to register handlers
  dp=updater.dispatcher

  # Add conversation handler with the states TIME_FROM, HALL, TABLE, NUMBER_OF_PEOPLE and NAME
  conv_handler=ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
      TIME_FROM: [RegexHandler(TIME_REGEX_STR, time_from)],

      TIME_TO: [RegexHandler(TIME_REGEX_STR, time_to),
                CommandHandler('skip', skip_time_to)],

      HALL: [RegexHandler('^(Паб|Підпілля \(концертний\))$', hall)],

      TABLE: [MessageHandler(Filters.text, table)],

      NUMBER_OF_PEOPLE: [MessageHandler(Filters.text, number_of_people)],
      
      PHONE_NUMBER: [MessageHandler(Filters.contact, phone_number)],

      NAME: [MessageHandler(Filters.text, name)]
    },

    fallbacks=[
      CommandHandler('cancel', cancel),
      CallbackQueryHandler(date_selected)
    ]
  )

  dp.add_handler(conv_handler)

  # log all errors
  dp.add_error_handler(error)

  # Start the Bot
  updater.bot.set_webhook()
  if "HEROKU" in list(os.environ.keys()):
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://telegra-bots.herokuapp.com/" + TOKEN)
  else:
    updater.start_polling()

  # Run the bot until you press Ctrl-C or the process receives SIGINT,
  # SIGTERM or SIGABRT. This should be used most of the time, since
  # start_polling() is non-blocking and will stop the bot gracefully.
  updater.idle()


if __name__ == '__main__':
    main()