"""This is a telegram bot that redirects all whatsapp messages to telegram"""
# Imports everything
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.chat import GroupChat
from telegram.ext import Updater, CommandHandler, MessageHandler
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import traceback

# Log every error of the bot
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Utility class
class User(object):
    """Represent a single user using the bot"""

    def __init__(self, bot, chat_id):
        """
        :param bot: The representation of this bot
        :param chat_id: The command sender id
        :type bot: telegram.Bot
        :type chat_id: int
        """
        # Initialize all values
        self.bot = bot
        self.id = chat_id
        self.driver = WhatsAPIDriver(client="firefox", username="bot", chrome_options=[], loadstyles=True)
        self.logged = False
        self.time = 0
        self.chats = []

    def send_message(self, text):
        """
        Send a message to the default user chat
        :param text: The text to send
        :type text: str
        """
        # Send a message using the user id
        self.bot.send_message(self.id, text)

    def contains(self, name):
        """
        Check if this user has the given chat
        :param name: The name of the chat to find
        :type name: str
        :return: If the chat instance is this user
        :rtype: bool
        """
        # Find the chat by checking every chat
        for chat in self.chats:
            if chat.name == name:
                return True
        return False

    def get(self, name):
        """
        Get the chat instance from the name
        :param name: The name of the chat to find
        :type name: str
        :return: The chat instance
        :rtype: Chat
        :raise: If the chat doesn't exist
        """
        # Find the chat by checking every chat
        for chat in self.chats:
            if chat.name == name:
                return chat
        raise Exception('Chat not found')


class Chat(object):
    """Represent a single chat"""
    def __init__(self, user, whatsapp_chat, telegram_chat_id):
        """
        Initialize this chat
        :param user: The user containing this chat
        :param whatsapp_chat: The whatsapp chat
        :param telegram_chat_id: The chat id
        :type user: User
        :type whatsapp_chat: webwhatsapi.objects.chat.Chat
        :type telegram_chat_id: int
        """
        self.user = user
        self.whatsapp_chat = whatsapp_chat
        self.telegram_chat_id = telegram_chat_id

    def send_whatsapp(self, message):
        """
        Send a message to the corresponding whatsapp chat
        :param message: The message to send
        :type message: str
        """
        self.whatsapp_chat.send_message(message)

    def send_telegram(self, message):
        """
        Send a message to the corresponding telegram chat
        :param message: The message to send
        :type message: str
        """
        self.user.bot.send_message(self.telegram_chat_id, message)


def start(bot, update):
    """
    Handle the start command by creating a new user and making him scan the WhatsApp qr code
    :param bot: The representation of the bot
    :param update: The event the has happened
    :type bot: telegram.Bot
    :type update: telegram.Update
    """
    update.message.reply_text('started')
    # Find if the user already exist
    current_user = None
    for user in users:
        if user.id == update.message.chat_id:
            current_user = user
            break
    # If the user doesn't exist create it
    if current_user is None:
        current_user = User(bot, update.message.chat_id)
        users.append(current_user)
    # Make the user scan the qr code
    current_user.send_message('Scan the qr code')
    send_qr(bot, current_user)


def start_group(bot, update):
    """
    Associate this group with a contact
    :param bot: The representation of the bot
    :param update: The event the has happened
    :type bot: telegram.Bot
    :type update: telegram.Update
    """
    # Tokenize the command
    arguments = update.message.text.split(' ')
    if len(arguments) != 3:
        bot.send_message(update.message.chat_id, 'Invalid arguments, use "/start_group USER_ID WHATSAPP_CHAT_NAME"')
        return
    current_user = None
    # Check if the user exist
    chat_id = arguments[1]
    for user in users:
        if str(user.id) == chat_id:
            current_user = user
            break
    if current_user is None:
        bot.send_message(update.message.chat_id, 'User id not found')
        return
    # Find the selected whatsapp chat
    name = arguments[2].replace('_', ' ')
    chats = current_user.driver.get_all_chats()
    current_chat = None
    for chat in chats:
        if chat.name == name:
            current_chat = chat
            break
    if current_chat is None:
        bot.send_message(update.message.chat_id, 'Whatsapp chat not found')
    # Associate the telegram chat with the whatsapp chat
    current_user.map.append(Chat(current_user, current_chat, update.message.chat_id))
    bot.send_message(update.message.chat_id, 'Done')


def send_message(bot, update):
    """
    Callback for a new telegram message to the bot
    :param bot: The representation of the bot
    :param update: The event the has happened
    :type bot: telegram.Bot
    :type update: telegram.Update
    """
    current_user = None
    chat = None
    for user in users:
        if user.containsTelegram(update.message.chat_id):
            current_user = user
            chat = user.getTelegram(update.message.chat_id)
    chat.send_whatsapp(update.message.content)


def error(bot, update, exception):
    """
    Print bot related error
    :param bot: The representation of the bot
    :param update: The event the has happened
    :exception: The exception
    :type bot: telegram.Bot
    :type update: telegram.Update
    :type exception: Exception
    """
    # Print the exception to the default output
    print('{} {}: {}'.format(bot, update, exception))


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
    bot.send_photo(user.id, open('qr.png', 'rb'))


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
        try:
            if user.driver.is_logged_in():
                # If the user has logged in updates its status
                user.logged = True
                updater.bot.send_message(user.id, 'logged in, your user id is: {}'.format(user.id))
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
                        updater.bot.send_message(user.id, 'logged in, your user id is: {}'.format(user.id))
        except Exception as e:
            traceback.print_exc()
    else:
        # Check if there are any unread messages
        for unread_chat in user.driver.get_unread():
            for unread in unread_chat.messages:
                # Check if the message is from a group or from a person
                # Check if the sender is know, if so send it to the right chat
                if isinstance(unread_chat.chat, GroupChat):
                    if user.contains(unread_chat.chat.name):
                        chat = user.get(unread_chat.chat.name).telegram_chat_id
                        message = '{}: {}'.format(unread.sender.name, unread.content)
                    else:
                        chat = user.id
                        message = '{}: {}: {}'.format(unread_chat.chat.name, unread.sender.name, unread.content)
                else:
                    if unread.sender.name in user.chats:
                        chat = user.chats[unread.sender.name]
                        message = unread.content
                    else:
                        chat = user.id
                        message = '{}: {}'.format(unread.sender.name, unread.content)
                updater.bot.send_message(chat, message)


def main():
    """
    Entry point of the program
    """
    # Starts the bot and add all handlers
    updater = Updater(open("telegram_bot_token.txt").readline())
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('start_group', start_group))
    dp.add_handler(MessageHandler(callback=send_message, filters=None))
    dp.add_error_handler(error)
    updater.start_polling()
    # Loop through the users
    while True:
        for user in users:
            loop(updater, user)
        sleep(1)


# Start the program
if __name__ == '__main__':
    users = []
    main()
