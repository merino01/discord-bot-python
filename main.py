from settings import app_name
from modules.core import logger
from bot import Bot


def main():
    logger.start()
    logger.info("Arrancando aplicación %s", app_name)

    bot = Bot()
    bot.init()


if __name__ == "__main__":
    main()
