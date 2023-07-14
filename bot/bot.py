import logging
import sys

from pyrogram import Client
from pyrogram.enums import ChatType

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(funcName)s, %(message)s',
)
logger = logging.getLogger(__name__)


class Bot:

    def __init__(self, env):
        self.client = Client(
            'my_account',
            env.get('API_ID'),
            env.get('API_HASH')
        )
        self.CHATS = dict()
        self.DIALOGS = dict()

    def get_dialog_list(self):
        list_type = [ChatType.SUPERGROUP, ChatType.GROUP]
        with self.client:
            for dialog in self.client.get_dialogs():
                if dialog.chat.type in list_type:
                    self.DIALOGS[dialog.chat.title] = dialog.chat.id

    def get_config(self):
        with open('config.txt') as file:
            lines = file.readlines()
        for line in lines:
            line = line.split(': ')
            if len(line) != 2:
                logger.critical('Config is invalid!')
                raise Exception(f'Строка {line} не соответствует формату формат: '
                                'Название темы: название_чата1, название_чата2 ...')
            term = line[0]
            chats_name_list = line[1].split(', ')
            chats_id = list()
            for chat_name in chats_name_list:
                if chat_name in self.DIALOGS.keys():
                    chats_id.append(self.DIALOGS[chat_name])
            self.CHATS[term] = chats_id

        logger.debug('Config valid')

    def get_message(self):
        with self.client as client:
            for message in client.get_chat_history('me', limit=1):
                return message

    @staticmethod
    def pars_terms(caption):
        text = caption.split('\n')
        terms = text[0].split(': ')
        if len(terms) < 2:
            logger.critical('First line message is invalid!')
            raise Exception(
                'В сообщении первая строка должна быть в виде: Темы: [темы через запятую и пробел]')
        terms = terms[1].split(', ')
        return terms

    def get_chats(self, terms):
        chats = list()
        for term in terms:
            chats_list = self.CHATS.get(term.lower())
            if chats_list is None:
                print(f'Тема {term} не содержит чатов')
                continue
            chats.extend(chats_list)
        return chats

    def send_message(self, message, chats):
        text = message.caption
        text = text.split('\n')
        text = '\n'.join(text[1:])
        for chat in chats:
            try:
                with self.client:
                    message.copy(chat, caption=text)
            except Exception as error:
                logger.error(f'Can`t send message to chat {chat}, because {error}')
                print(f'Не удалось переслать сообщение в чат "{chat}"')

    def start(self):
        self.get_dialog_list()
        self.get_config()
        message = self.get_message()

        if message is None:
            logger.debug('No message to resend')
            print('Нет сообщения для пересылки.')
            sys.exit(0)

        terms = self.pars_terms(caption=message.caption)
        chats = self.get_chats(terms)
        if not chats:
            logger.critical('Send list of chats is empty')
            raise Exception('В файле config.txt нет выбранных Вами тем или они пусты. '
                            'Отредактируйте файл!')
        self.send_message(message, chats)
