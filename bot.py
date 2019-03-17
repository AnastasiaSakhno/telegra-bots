#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import telegramcalendar

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, CallbackQueryHandler,
													ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
										level=logging.INFO)

logger = logging.getLogger(__name__)

# states
HALL, TABLE, NUMBER_OF_PEOPLE, NAME = range(4)


def start(update, context):
		update.message.reply_text(
				'Вітаю!\n\n'
				'Натисніть /cancel щоб завершити розмову.\n'
				'Натисніть /start щоб почати спочатку.\n\n'
				'Будь ласка, оберіть дату.',
				reply_markup=telegramcalendar.create_calendar())

		return CallbackQueryHandler


def date_selected(update, context):
		selected, date = telegramcalendar.process_calendar_selection(context.bot, update)

		if selected:
			user = update.callback_query.from_user
			date_formatted = date.strftime("%d.%m.%Y")
			logger.info("User %s %s selected date: %s", user.first_name, user.last_name, date_formatted)

			context.bot.send_message(
				chat_id=update.callback_query.from_user.id,
				text=date_formatted,
				reply_markup=ReplyKeyboardRemove())

		reply_keyboard = [['Перший', 'Другий']]

		context.bot.send_message(
			chat_id=update.callback_query.from_user.id,
			text='Чудово. Ви хочете замовити стіл у першому або другому залі?',
			reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

		return HALL


def hall(update, context):
		user = update.message.from_user
		logger.info("Hall of %s %s: %s", user.first_name, user.last_name, update.message.text)

		picture = ('pub_hall1.jpg' if update.message.text == 'Перший' else 'pub_hall2.jpg')

		if update.message.text == 'Перший':
			reply_keyboard = [['1', '2', '3', '4', '5', '6', '7'], 
								['8', '9', '10', '11', '12', '13']]
		else:
			reply_keyboard = [['1', '2', '3', '4', '5', '6', '7', '8'], 
								['9', '10', '11', '12', '13', '14', '15', '16'], 
								['17', '18', '19', '20', '21', '22', '23']]

		context.bot.send_photo(update.message.chat_id, photo=open(picture, 'rb'))

		update.message.reply_text('Добре! Який стіл?',
															reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

		return TABLE


def table(update, context):
		user = update.message.from_user
		logger.info("Table of %s %s: %s", user.first_name, user.last_name, update.message.text)
		update.message.reply_text('Дякую! Тепер вкажіть, будь ласка, скільки людей планують прийти до нас?')

		return NUMBER_OF_PEOPLE


def number_of_people(update, context):
		user = update.message.from_user
		logger.info("Number of people for %s %s: %s", user.first_name, user.last_name, update.message.text)
		update.message.reply_text('Зрозуміло. '
															'Як до вас можно звертатися?')

		return NAME


def name(update, context):
		user = update.message.from_user
		logger.info("Name of %s %s: %s", user.first_name, user.last_name, update.message.text)
		update.message.reply_text('Дуже дякую! Наш менеджер зателефонує вам. ')

		return ConversationHandler.END


def cancel(update, context):
		user = update.message.from_user
		logger.info("User %s canceled the conversation.", user.first_name)
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
		updater = Updater(token = os.environ.get('TELEGRAM_API_TOKEN'), use_context=True)

		# Get the dispatcher to register handlers
		dp = updater.dispatcher

		# Add conversation handler with the states HALL, TABLE, NUMBER_OF_PEOPLE and NAME
		conv_handler = ConversationHandler(
				entry_points=[CommandHandler('start', start)],

				states={
						HALL: [RegexHandler('^(Перший|Другий)$', hall)],

						TABLE: [MessageHandler(Filters.text, table)],

						NUMBER_OF_PEOPLE: [MessageHandler(Filters.text, number_of_people)],

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
		updater.start_polling()

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		updater.idle()


if __name__ == '__main__':
		main()