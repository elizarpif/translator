from googletrans import Translator
from gtts import gTTS
from telegram import Update
import config

translator = Translator()


class Language:
    def __init__(self, current_foreign='tr', current_base='ru'):
        self.current_foreign_lang = current_foreign
        self.current_base_lang = current_base
        self.multi = False
        self.switcher_long_short = {
            'Turkish': 'tr',
            'English': 'en',
            'Serbian': 'sr',
        }
        self.switcher_short_long = {
            'tr': 'Turkish',
            'en': 'English',
            'sr': 'Serbian',
        }

    def set_foreign(self, lang='tr'):
        self.current_foreign_lang = lang

    def set_base(self, lang='ru'):
        self.current_base_lang = lang

    def get_foreign_string(self):
        return self.switcher_short_long.get(self.current_foreign_lang)

    def get_foreign(self):
        return self.current_foreign_lang

    def get_base(self):
        return self.current_base_lang

    def enable_multi_mode(self):
        self.multi = True

    def disable_multi_mode(self):
        self.multi = False


def set_base():
    global Current_mode
    Current_mode = 0
    global Multi
    Multi = False


def set_foreign():
    global Current_mode
    Current_mode = 1
    global Multi
    Multi = False


def set_multi():
    global Multi
    Multi = True


def voice(text, lang: Language):
    tts = gTTS(text, lang=lang.get_foreign())
    tts.save(config.FILENAME)


def voice_lang(text, lang='tr'):
    tts = gTTS(text, lang=lang)
    tts.save(config.FILENAME)


# multi_translate translates in Multi mode, when we dont know what language
def multi_translate(update: Update, lang: Language):
    """
    переводит в обе стороны
    :param update:
    """
    text = update.message.text

    tr = lang.get_foreign()
    ru = lang.get_base()

    rutu = translator.translate(text, dest=tr).text
    turu = translator.translate(text, dest=ru).text

    # делаем озвучку и отправляем ее
    voice_lang(rutu, tr)
    with open(config.FILENAME, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=rutu)

    # делаем озвучку и отправляем ее
    voice_lang(turu, ru)
    with open(config.FILENAME, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=turu)


# translate in usual mode (Ru->Tr or Tr->Ru)
def translate(update: Update, lang: Language):
    res = translator.translate(update.message.text, dest=lang.get_foreign(), src=lang.get_base()).text

    # делаем озвучку и отправляем ее
    voice(res, lang=lang)

    with open(config.FILENAME, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=res)
