from googletrans import Translator
from gtts import gTTS
from telegram import Update

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


# multi_translate translates in Multi mode, when we dont know what language
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


# translate in usual mode (Ru->Tr or Tr->Ru)
def translate(update: Update):
    res = translator.translate(update.message.text, switch_dest(), switch_src()).text

    # делаем озвучку и отправляем ее
    voice(res)

    with open(filename, 'rb') as f:
        # отправляем
        update.message.reply_voice(f, caption=res)
