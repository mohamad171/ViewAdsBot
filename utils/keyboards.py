from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [
            KeyboardButton('افزودن اکانت'),
            KeyboardButton('مشاهده لیست اکانت ها')

        ],
        [
            KeyboardButton('مشاهده موجودی'),
            KeyboardButton('پشتیبانی')
        ]
    ]
    return ReplyKeyboardMarkup(keyboard)

def add_account_keyboard():
    keyboard = [
        [
            KeyboardButton('لغو'),
        ],

    ]
    return ReplyKeyboardMarkup(keyboard)