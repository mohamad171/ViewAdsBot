from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [
            KeyboardButton('➕ ارسال اکانت ➕'),
            KeyboardButton('حساب کاربری 🔒')

        ],
        [
            KeyboardButton('تسویه حساب ♻️'),
            KeyboardButton('پشتیبانی 📮')
        ]
    ]
    return ReplyKeyboardMarkup(keyboard,resize_keyboard=True)

def add_account_keyboard():
    keyboard = [
        [
            KeyboardButton('لغو'),
        ],

    ]
    return ReplyKeyboardMarkup(keyboard,resize_keyboard=True)

def check_clear_session_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('تایید خروج از اکانت',callback_data='accept_logout'),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)