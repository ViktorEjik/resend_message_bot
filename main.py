import logging
import os

import dotenv
from bot.bot import Bot


dotenv.load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(funcName)s, %(message)s',
)
logger = logging.getLogger(__name__)

ENV = {
    'API_ID': os.getenv('API_ID'),
    'API_HASH': os.getenv('API_HASH'),
    'PHONE': os.getenv('PHONE'),
}


def check_env():
    err = list()
    for env_elem in ENV:
        if not ENV[env_elem]:
            logger.critical('"{}" is None'.format(env_elem))
            err.append(env_elem)
            return False, err
    logger.debug('Environment filled in successfully!')
    return True, err


def main():
    flag, err = check_env()
    if not flag:
        print(f'ENV не полное, дополнике его полями {err} и запустите программу заново!')
    bot = Bot(ENV)
    bot.start()


if __name__ == '__main__':
    main()
