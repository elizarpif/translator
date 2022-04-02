# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from telegram import Update, ForceReply, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

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


class Bot:
    def __init__(self):
        self.lang = translator.Language()
        self.help_msg = f'/multi - установить мультрежим \n' \
                        f'/to_ru - установить переводчик с иностранного на русский\n' \
                        f'/from_ru - установить переводчик с русского на иностранный\n' \
                        f'/settings - настройка текущего инностранного языка\n' \
                        f'/help - справка\n'

    def translate(self, update: Update, context: CallbackContext) -> None:
        """Action on message"""
        if self.lang.multi:
            translator.multi_translate(update, self.lang)
            return
        translator.translate(update, self.lang)

    def set_base_foreign(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /to-ru is issued."""
        self.lang.set_to_ru()
        self.lang.disable_multi_mode()

        update.message.reply_text(f'Set base lang: {self.lang.get_foreign_string()}')

    def set_base_ru(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /from-ru is issued."""
        self.lang.set_from_ru()
        self.lang.disable_multi_mode()

        update.message.reply_text('Set base lang: Russian')

    def set_base_multi(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /multi is issued."""
        self.lang.enable_multi_mode()
        self.lang.set_from_ru()

        update.message.reply_text('Set multi mode')

    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\!',
            reply_markup=ForceReply(selective=True),
        )
        self.lang.set_base()
        self.lang.set_foreign()
        self.lang.disable_multi_mode()

        update.message.reply_text(self.help_msg)

    def help(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        update.message.reply_text(self.help_msg)

    def error_handler(self, update: object, context: CallbackContext) -> None:
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

    def start_selection(self, update: Update, context: CallbackContext) -> None:
        """Sends a message with three inline buttons attached."""
        # TODO move it to Language
        keyboard = [
            [
                InlineKeyboardButton("English", callback_data='English'),
                InlineKeyboardButton("Turkish", callback_data='Turkish'),
            ],
            [InlineKeyboardButton("Serbian", callback_data='Serbian')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose foreign language:', reply_markup=reply_markup)

    def button(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        query.answer()

        # TODO move it to Language
        switcher = {
            'Turkish': 'tr',
            'English': 'en',
            'Serbian': 'sr',
        }
        self.lang.set_foreign(lang=switcher.get(query.data))

        query.edit_message_text(text=f"Selected foreign language: {query.data}")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    bot = Bot()

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", bot.start))
    dispatcher.add_handler(CommandHandler("to_ru", bot.set_base_foreign))
    dispatcher.add_handler(CommandHandler("from_ru", bot.set_base_ru))
    dispatcher.add_handler(CommandHandler("multi", bot.set_base_multi))
    dispatcher.add_handler(CommandHandler("help", bot.help))

    dispatcher.add_handler(CommandHandler("settings", bot.start_selection))
    updater.dispatcher.add_handler(CallbackQueryHandler(bot.button))

    # add error handler
    dispatcher.add_error_handler(bot.error_handler)

    # Message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, bot.translate))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
