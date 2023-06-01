from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('افزودن اکانت', callback_data='add_account')], ]
    return InlineKeyboardMarkup(keyboard)