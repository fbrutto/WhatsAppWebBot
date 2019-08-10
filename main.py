# Imports everything
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.chat import GroupChat
from telegram.ext import Updater, CommandHandler
from time import sleep

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
        self.driver = WhatsAPIDriver(client="chrome", username="bot", chrome_options=[])
        self.logged = False
        self.time = 0
        self.map = {}

    def send_message(self, text):
        """
        Send a message to the default user chat
        :param text: The text to send
        :type text: str
        """
        self.bot.send_message(self.id, text)


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
        bot.send_message(update.message.chat_id, 'Invalid arguments')
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
    # Assign the selected name to the chat
    name = arguments[2].replace('_', ' ')
    current_user.map[name] = update.message.chat_id
    bot.send_message(update.message.chat_id, 'Done')


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
        if user.driver.is_logged_in():
            # If the user has logged in updates its status
            user.logged = True
            updater.bot.send_message(user.id, 'logged in, your user id is: {}'.format(user.id))
        else:
            # After some time send the new qr code to the user
            user.time += 1
            if user.time >= 10:
                user.time = 0
                send_qr(updater.bot, user)
    else:
        # Check if there are any unread messages
        for unread_chat in user.driver.get_unread():
            for unread in unread_chat.messages:
                # Check if the message is from a group or from a person
                # Check if the sender is know, if so send it to the right chat
                if isinstance(unread_chat.chat, GroupChat):
                    if unread_chat.chat.name in user.map:
                        chat = user.map[unread_chat.chat.name]
                        message = '{}: {}'.format(unread.sender.name, unread.content)
                    else:
                        chat = user.id
                        message = '{}: {}: {}'.format(unread_chat.chat.name, unread.sender.name, unread.content)
                else:
                    if unread.sender.name in user.map:
                        chat = user.map[unread.sender.name]
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
