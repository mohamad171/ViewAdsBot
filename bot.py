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
from utils.regexes import *
from ClientApiInterface import send_code , signin, client_set_password
import re
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

add_phone_data = {}

logger = logging.getLogger(__name__)
backend_interface = BackendInterface.BackendInterface()


SET_PHONE_NUMBER, SET_CODE,SET_PASSWORD = range(3)

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
        await query.message.reply_text("شماره موبایل را وارد کنید نمونه: +17845333959",reply_markup=add_account_keyboard())
        return SET_PHONE_NUMBER

    await query.message.reply_text("کاربر یافت نشد",reply_markup=main_menu_keyboard())
    return ConversationHandler.END


async def set_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone = update.message.text
    if re.match(phone_regex,phone):
        add_phone_data[update.message.chat_id]["phone"] = phone
        r,client = await send_code(phone)
        if r:
            add_phone_data[update.message.chat_id]["sent_code"] = r
            add_phone_data[update.message.chat_id]["client"] = client
            await update.message.reply_text(f"کد تایید برای شماره {phone} ارسال شد",reply_markup=add_account_keyboard())
            await update.message.reply_text("کد تایید را وارد کنید",reply_markup=add_account_keyboard())
            return SET_CODE
        
    await update.message.reply_text("شماره موبایل را صحیح وارد کنید نمونه: +17845333959",reply_markup=add_account_keyboard())
    return SET_PHONE_NUMBER


async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    password = update.message.text
    client = add_phone_data[update.message.chat_id]["client"]
    r = await client_set_password(client,password)
    if r == "invalid":
        await update.message.reply_text("رمز عبور صحیح نیست لطفا مجددا تلاش کنید",reply_markup=add_account_keyboard())
        return SET_PASSWORD

    user = backend_interface.get_user(update.message.chat_id)
    if user:
        status, result = backend_interface.add_account(user, add_phone_data[update.message.chat_id]["phone"], r)
        if status:
            add_phone_data[update.message.chat_id] = {}

        await update.message.reply_text(f"{result}")

    else:
        await update.message.reply_text("کاربر یافت نشد",reply_markup=main_menu_keyboard())


async def set_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code = update.message.text
    sent_code = add_phone_data[update.message.chat_id]["sent_code"]
    phone = add_phone_data[update.message.chat_id]["phone"]
    client = add_phone_data[update.message.chat_id]["client"]
    r = await signin(client,phone,code,sent_code)
    if r == "password":
        await update.message.reply_text("ورود دو مرحله ای نیاز است\nلطفا رمز عبور را وارد کنید",reply_markup=add_account_keyboard())
        return SET_PASSWORD
    elif r == "invalid":
        await update.message.reply_text("کد وارد شده صحیح نیست دوباره کد را وارد کنید",reply_markup=add_account_keyboard())
        return SET_CODE
    

    user = backend_interface.get_user(update.message.chat_id)
    if user:
        status,result = backend_interface.add_account(user,add_phone_data[update.message.chat_id]["phone"],r)
        if status:
            add_phone_data[update.message.chat_id] = {}

        await update.message.reply_text(f"{result}")
        return ConversationHandler.END

    else:
        await update.message.reply_text("کاربر یافت نشد",reply_markup=add_account_keyboard())




async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("عملیات با موفقیت لغو شد.")
    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید",
                                        reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def main() -> None:

    application = Application.builder().token("411779048:AAHaRZg1pphD9DkIt0IYpZdemKGaFK0Rbak").build()

    add_account_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("افزودن اکانت"), set_phone_number)],
        states={
            SET_PHONE_NUMBER: [
                MessageHandler(filters.Regex("^(?!\لغو).*$"), set_phone_number),
            ],
            SET_CODE: [
                MessageHandler(filters.Regex("^(?!\لغو).*$"), set_code),
            ],

            SET_PASSWORD: [
                MessageHandler(filters.Regex("^(?!\لغو).*$"), set_password),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("لغو"), cancel)],
    )
    # application.add_handler(MessageHandler(filters.Regex("\/start [a-z0-9]{8}"), join_to_room))
    application.add_handler(MessageHandler(filters.Regex("\/start"), start))
    application.add_handler(add_account_conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()