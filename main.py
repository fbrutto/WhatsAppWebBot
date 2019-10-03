#!/usr/bin/env python3
"""This is a telegram bot that redirects all whatsapp messages to telegram"""
# Imports everything
from webwhatsapi.objects.chat import GroupChat
from telegram.ext import CommandHandler, MessageHandler, Updater
from telegram.ext.filters import Filters
from time import sleep
from selenium.common.exceptions import NoSuchElementException

# Import libraries
from classes import User, Chat

# Log every error of the bot
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main():
    """
    Entry point of the program
    """
    # Starts the bot and add all handlers
    updater = Updater(open("token.txt").readline().replace('\n',''), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('start_group', start_group))
    dp.add_handler(MessageHandler(Filters.all, send_message))
    # dp.add_error_handler(error)
    updater.start_polling()
    # Loop through the users
    while True:
        for user in users:
            loop(updater, user)
        sleep(1)


def start(update, context):
    """
    Handle the start command by creating a new user and making him scan the WhatsApp qr code
    :param context: The context of the message
    :param update: The event the has happened
    :type context: telegram.ext.CallbackContext
    :type update: telegram.Update
    """
    update.message.reply_text('started')
    # Find if the user already exist
    current_user = None
    for user in users:
        if user.id == update.message.from_user.id:
            current_user = user
            break
    # If the user doesn't exist create it
    if current_user is None:
        current_user = User(context.bot, update.message.from_user)
        users.append(current_user)
    # Make the user scan the qr code
    current_user.send_message('Scan the qr code')
    send_qr(context.bot, current_user)


def loop(updater, user):
    """
    Execute actions for the selected user
    :param updater: The representation of the bot
    :param user: The user to update
    :type updater: telegram.ext.Updater
    :type user: User
    """
    # Check is the user is already logged in
    if not user.logged:
        if user.driver.is_logged_in():
            # If the user has logged in updates its status
            user.logged = True
            updater.bot.send_message(user.user.id, 'logged in, your user id is: {}'.format(user.user.id))
        else:
            # After some time send the new qr code to the user
            user.time += 1
            if user.time >= 10:
                user.time = 0
                try:
                    send_qr(updater.bot, user)
                except NoSuchElementException:
                    # If the user has logged in updates its status
                    user.logged = True
                    updater.bot.send_message(user.user.id, 'logged in, your user id is: {}'.format(user.user.id))
    else:
        # Check if there are any unread messages
        for unread_chat in user.driver.get_unread():
            for unread in unread_chat.messages:
                # Check if the message is from a group or from a person
                # Check if the sender is know, if so send it to the right chat
                if isinstance(unread_chat.chat, GroupChat):
                    if user.contains_whatsapp(unread_chat.chat.name):
                        chat = user.get_whatsapp(unread_chat.chat.name).telegram_chat_id
                        message = '{}: {}'.format(unread.sender.name, unread.content)
                    else:
                        chat = user.user.id
                        message = '{}: {}: {}'.format(unread_chat.chat.name, unread.sender.name, unread.content)
                else:
                    if user.contains_whatsapp(unread.sender.name):
                        chat = user.get_whatsapp(unread.sender.name).telegram_chat_id
                        message = unread.content
                    else:
                        chat = user.user.id
                        message = '{}: {}'.format(unread.sender.name, unread.content)
                updater.bot.send_message(chat, message)


def send_qr(bot, user):
    """
    Send the qr code to the selected user
    :param bot: The representation of the bot
    :param user: The user to send the qr code
    :type bot: telegram.Bot
    :type user: User
    """
    # Send the qr code as an image
    user.driver.get_qr('qr.png')
    bot.send_photo(user.user.id, open('qr.png', 'rb'))


def start_group(update, context):
    """
    Associate this group with a contact
    :param context: The context of the message
    :param update: The event the has happened
    :type context: telegram.ext.CallbackContext
    :type update: telegram.Update
    """
    # Tokenize the command
    arguments = update.message.text.split(' ')
    if len(arguments) != 2:
        context.bot.send_message(update.message.chat_id,
                                 'Invalid arguments, use "/start_group USER_ID WHATSAPP_CHAT_NAME"')
        return
    current_user = None
    # Check if the user exist
    chat_id = update.message.from_user.id
    for user in users:
        if user.user.id == chat_id:
            current_user = user
            break
    if current_user is None:
        context.bot.send_message(update.message.chat_id, 'User id not found')
        return
    # Find the selected whatsapp chat
    name = arguments[1].replace('_', ' ')
    chats = current_user.driver.get_all_chats()
    current_chat = None
    for chat in chats:
        if chat.name == name:
            current_chat = chat
            break
    if current_chat is None:
        context.bot.send_message(update.message.chat_id, 'Whatsapp chat not found')
        return
    # Associate the telegram chat with the whatsapp chat
    current_user.chats.append(Chat(current_user, current_chat, update.message.chat_id))
    context.bot.send_message(update.message.chat_id, 'Done')


def send_message(update, context):
    """
    Callback for a new telegram message to the bot
    :param context: The context of the message
    :param update: The event the has happened
    :type context: telegram..ext.CallbackContext
    :type update: telegram.Update
    """
    current_user = None
    chat = None
    for user in users:
        if user.contains_telegram(update.message.chat_id):
            current_user = user
            chat = user.get_telegram(update.message.chat_id)
    chat.send_whatsapp(update.message.text)


def send_message_command(update, context):
    """
    Callback for a new telegram message to the bot
    :param context: The context of the message
    :param update: The event the has happened
    :type context: telegram..ext.CallbackContext
    :type update: telegram.Update
    """

    current_user = None
    chat = None
    for user in users:
        if user.contains_telegram(update.message.chat_id):
            current_user = user
            chat = user.get_telegram(update.message.chat_id)
    chat.send_whatsapp(update.message.text)


def error(update, context):
    """
    Print bot related error
    :param context: The context of the error
    :param update: The event the has happened
    :type context: telegram.ext.CallbackContext
    :type update: telegram.Update
    """
    # Print the exception to the default output
    raise context.error


# Start the program
if __name__ == '__main__':
    users = []
    main()
