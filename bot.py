from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler
import logging
import re
import random
import string
from utils import keyboards
import BackendInterface
from utils.keyboards import *
from ClientApiInterface import *
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

add_phone_data = {}

logger = logging.getLogger(__name__)
backend_interface = BackendInterface.BackendInterface()


SET_PHONE_NUMBER, SET_CODE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        username = user["username"]
    except:
        username = None
    first_name = user["first_name"]
    backend_interface.register(update.message.chat_id, first_name, username)
    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید",reply_markup=main_menu_keyboard())


async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user = backend_interface.get_user(query.message.chat_id)
    if user:
        add_phone_data[query.message.chat_id] = {}
        await query.message.reply_text("شماره موبایل را وارد کنید نمونه: +17845333959")
        return SET_PHONE_NUMBER

    await query.message.reply_text("کاربر یافت نشد")
    return ConversationHandler.END


async def set_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone = update.message.text
    add_phone_data[update.message.chat_id]["phone"] = phone
    r = send_code(phone)
    add_phone_data[update.message.chat_id]["sent_code"] = r
    await update.message.reply_text(f"کد تایید به شماره {phone} پیامک شد")
    await update.message.reply_text("کد تایید را وارد کنید")
    return SET_CODE


async def set_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code = update.message.text
    await update.message.reply_text(f"ok code is {code}")
    sent_code = add_phone_data[update.message.chat_id]["sent_code"]
    phone = add_phone_data[update.message.chat_id]["phone"]
    r = signin(phone,code,sent_code)
    print(r)
    user = backend_interface.get_user(update.message.chat_id)
    if user:
        status,result = backend_interface.add_account(user,add_phone_data[update.message.chat_id]["phone"])
        await update.message.reply_text(f"{result}")

    else:
        await update.message.reply_text("کاربر یافت نشد")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("عملیات با موفقیت لغو شد.")
    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید",
                                        reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def main() -> None:
    bk = BackendInterface.BackendInterface()

    application = Application.builder().token("411779048:AAHaRZg1pphD9DkIt0IYpZdemKGaFK0Rbak").build()

    add_account_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_account_command, "add_account")],
        states={
            SET_PHONE_NUMBER: [
                MessageHandler(filters.Regex("^(?!\/cancel).*$"), set_phone_number),

            ],
            SET_CODE: [
                MessageHandler(filters.Regex("^(?!\/cancel).*$"), set_code),

            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    # application.add_handler(MessageHandler(filters.Regex("\/start [a-z0-9]{8}"), join_to_room))
    application.add_handler(MessageHandler(filters.Regex("\/start"), start))
    application.add_handler(add_account_conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()