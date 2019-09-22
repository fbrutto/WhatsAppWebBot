from webwhatsapi import WhatsAPIDriver


# Utility classes
class User(object):
    """Represent a single user using the bot"""

    def __init__(self, bot, user):
        """
        :param bot: The representation of this bot
        :param user: The command sender id
        :type bot: telegram.Bot
        :type user: telegram.User
        """
        # Initialize all values
        self.bot = bot
        self.user = user
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
        self.bot.send_message(self.user.id, text)

    def contains_whatsapp(self, name):
        """
        Check if this user has the given chat
        :param name: The name of the chat to find
        :type name: str
        :return: If the chat instance is this user
        :rtype: bool
        """
        # Find the chat by checking every chat
        for chat in self.chats:
            if chat.whatsapp_chat.name == name:
                return True
        return False

    def get_whatsapp(self, name):
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
            if chat.whatsapp_chat.name == name:
                return chat
        raise Exception('Chat not found')

    def contains_telegram(self, telegram_chat_id):
        """
        Check if this user has the given chat
        :param telegram_chat_id: The name of the chat to find
        :type telegram_chat_id: int
        :return: If the chat instance is this user
        :rtype: bool
        """
        # Find the chat by checking every chat
        for chat in self.chats:
            if chat.telegram_chat_id == telegram_chat_id:
                return True
        return False

    def get_telegram(self, telegram_chat_id):
        """
        Get the chat instance from the name
        :param telegram_chat_id: The name of the chat to find
        :type telegram_chat_id: int
        :return: The chat instance
        :rtype: Chat
        :raise: If the chat doesn't exist
        """
        # Find the chat by checking every chat
        for chat in self.chats:
            if chat.telegram_chat_id == telegram_chat_id:
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
