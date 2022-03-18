# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from translate import Translator
import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
help_msg = f'/multi - установить мультрежим русский-турецкий ' \
           f'(P.S. иногда перевод языка A->A может приводить к неожиданным результатам)\n' \
           f'/tr - установить переводчик с турецкого на русский ' \
           f'(работает 2-ная схема: с турецкого на русский и результат - на турецкий снова\n' \
           f'/ru - установить переводчик с русского на турецкий\n' \
           f'(работает 2-ная схема: с русского на турецкий и результат - на русский снова\n' \
           f'/help - справка'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    update.message.reply_text(help_msg)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(help_msg)


from_tu_to_ru_translator = Translator(to_lang='ru', from_lang='tr')
from_ru_to_tu_translator = Translator(to_lang='tr', from_lang='ru')

# 0 - tr-ru, 1 - ru-tr, 2 - multi
Current_mode = 1


# Define a few command handlers. These usually take the two arguments update and
# context.
def translate(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /turkish"""
    # update.message.reply_text('set language: turkish')
    t = update.message.text

    rutu = from_ru_to_tu_translator.translate(t)
    turu = from_tu_to_ru_translator.translate(t)

    switcher = {
        0: f'{turu}\n\n{from_tu_to_ru_translator.translate(turu)} (tr)',
        1: f'{rutu}\n\n{from_tu_to_ru_translator.translate(rutu)} (ru)',
        2: f'{rutu} (ru-tr)\n\n{turu} (tr-ru)'
    }
    update.message.reply_text(switcher.get(Current_mode))


def set_base_turk(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    global Current_mode
    Current_mode = 0
    update.message.reply_text('Set base lang: Turkish')


def set_base_ru(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    global Current_mode
    Current_mode = 1
    update.message.reply_text('Set base lang: Russian')


def set_base_multi(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    global Current_mode
    Current_mode = 2
    update.message.reply_text('Set multi mode')


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("tr", set_base_turk))
    dispatcher.add_handler(CommandHandler("ru", set_base_ru))
    dispatcher.add_handler(CommandHandler("multi", set_base_multi))
    dispatcher.add_handler(CommandHandler("help", help))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, translate))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
