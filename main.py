# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from telegram import Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import config
import logging
import translator
import html
import json
import traceback

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.

def translate(update: Update, context: CallbackContext) -> None:
    """Action on message"""
    if Multi:
        translator.multi_translate(update)
        return
    translator.translate(update)


def set_base_turk(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /try is issued."""
    global Current_mode
    Current_mode = 1
    global Multi
    Multi = False
    update.message.reply_text('Set base lang: Turkish')


def set_base_ru(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /ru is issued."""
    global Current_mode
    Current_mode = 0
    global Multi
    Multi = False
    update.message.reply_text('Set base lang: Russian')


def set_base_multi(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /multi is issued."""
    global Multi
    Multi = True
    update.message.reply_text('Set multi mode')


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


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=config.DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


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

    # add error handler
    dispatcher.add_error_handler(error_handler)

    # Message handler
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
