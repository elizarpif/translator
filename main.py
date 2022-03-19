# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator
from gtts import gTTS

import config
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
help_msg = f'/multi - установить мультрежим русский-турецкий \n' \
           f'(P.S. иногда перевод языка A->A может приводить к неожиданным результатам)\n' \
           f'/tr - установить переводчик с турецкого на русский\n' \
           f'/ru - установить переводчик с русского на турецкий\n' \
           f'/help - справка\n'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    update.message.reply_text(help_msg)


def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(help_msg)


translator = Translator()

# 0 = ru-tr, 1 = tr-ru
Current_mode = 0
Multi = False


def switch_dest():
    if Current_mode == 0:
        return 'tr'

    return 'ru'


def switch_src():
    if Current_mode == 0:
        return 'ru'

    return 'tr'


filename = 'voice2.ogg'


def voice(text):
    tts = gTTS(text, lang=switch_dest())
    tts.save(filename)


def voice_lang(text, lang='tr'):
    tts = gTTS(text, lang=lang)
    tts.save(filename)


ru_lang = 'ru'
en_lang = 'en'


def multi_translate(update: Update):
    """
    переводит в обе стороны
    :param update:
    """
    text = update.message.text

    rutu = translator.translate(text, dest='tr').text
    turu = translator.translate(text, dest='ru').text

    # делаем озвучку и отправляем ее
    voice_lang(rutu, 'tr')
    with open(filename, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=rutu)

    # делаем озвучку и отправляем ее
    voice_lang(turu, 'ru')
    with open(filename, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=turu)


# Define a few command handlers. These usually take the two arguments update and
# context.

def translate(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /turkish"""
    if Multi:
        multi_translate(update)
        return

    res = translator.translate(update.message.text, switch_dest(), switch_src()).text

    # делаем озвучку и отправляем ее
    voice(res)

    with open(filename, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=res)


def set_base_turk(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    global Current_mode
    Current_mode = 1
    global Multi
    Multi = False
    update.message.reply_text('Set base lang: Turkish')


def set_base_ru(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    global Current_mode
    Current_mode = 0
    global Multi
    Multi = False
    update.message.reply_text('Set base lang: Russian')


def set_base_multi(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    global Multi
    Multi = True
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
