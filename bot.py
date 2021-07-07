from telegram import ChatAction,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,CallbackQueryHandler,PicklePersistence
import logging
import os
from functools import wraps
import requests

api_key = os.environ.get("api_key","") # bot token
token = os.environ.get("bot_token","") # api key from https://ocr.space/ocrapi

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and context
#Your bot will repond when you type / and then respective commands e.g /start , /help
@run_async     
@send_typing_action
def start(update,context):
    """send /start"""
    global first
    first=update.message.chat.first_name
    update.message.reply_text('سلام این ربات میتونه تکست رو از عکس استخراج کنه متاسفانه زبان فارسی ساپورت نمیشه 📥')

@run_async
@send_typing_action
def convert_image(update,context):
        file_id = update.message.photo[-1].file_id
        newFile=context.bot.get_file(file_id)
        file= newFile.file_path
        context.user_data['filepath']=file
        keyboard = [[InlineKeyboardButton("🏴󠁧󠁢󠁥󠁮󠁧󠁿 انگلیسی", callback_data='eng'), InlineKeyboardButton("🇷🇺 روسی", callback_data='rus'),InlineKeyboardButton("🇨🇿 چکی", callback_data='cze')],
                    [InlineKeyboardButton("🇨🇳 چینی ساده شده", callback_data='chs'), InlineKeyboardButton("🇨🇳 چینی سنتی", callback_data='cht')],[InlineKeyboardButton("🇯🇵 ژاپنی", callback_data='jpn')] ,
                    [InlineKeyboardButton("🇸🇦 عربی", callback_data='ara'),InlineKeyboardButton("🇿🇦 آفریقایی", callback_data='AFR'), InlineKeyboardButton("🇩🇪 آلمانی", callback_data='gre')],
                    [InlineKeyboardButton("🇮🇹 ایتالیایی", callback_data='ita'),InlineKeyboardButton("🇮🇩 اندونزی", callback_data='eng'),InlineKeyboardButton("🇫🇷 فرانسوی", callback_data='fre')],
                    [InlineKeyboardButton ("🇪🇸 اسپانیایی", callback_data='spa'),InlineKeyboardButton("🇵🇹 پرتغالی", callback_data='por'),InlineKeyboardButton("🇰🇷 کره ای", callback_data='kor')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('لطفا زبان خود را انتخاب کنید : ', reply_markup=reply_markup)

@run_async
def button(update,context):
    filepath=context.user_data['filepath']
    query = update.callback_query
    query.answer()
    query.edit_message_text("wait ...")
    data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={api_key}&url={filepath}&language={query.data}&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
    data=data.json()
    if data['IsErroredOnProcessing']==False:
        message=data['ParsedResults'][0]['ParsedText']
        query.edit_message_text(f"{message}")
    else:
        query.edit_message_text(text="error")

persistence=PicklePersistence('userdata')
def main(): 
    bot_token=token
    updater = Updater(bot_token,use_context=True,persistence=persistence)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(MessageHandler(Filters.photo, convert_image))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling(clean=True)
    updater.idle()
 
	
if __name__=="__main__":
	main()
