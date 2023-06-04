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
from ClientApiInterface import send_code , signin, client_set_password,check_session
import re
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

add_phone_data = {}
add_checkout_data = {}
logger = logging.getLogger(__name__)
backend_interface = BackendInterface.BackendInterface()


SET_PHONE_NUMBER, SET_CODE,SET_PASSWORD = range(3)
SET_CARD_NUMBER, SET_ACCOUNT_COUNT = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        username = user["username"]
    except:
        username = None
    first_name = user["first_name"]
    backend_interface.register(update.message.chat_id, first_name, username)
    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید",reply_markup=main_menu_keyboard())

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("برای ادامه دکمه تایید را بزنید",reply_markup=check_clear_session_keyboard())


async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user = backend_interface.get_user(query.message.chat_id)
    if user:
        add_phone_data[query.message.chat_id] = {}
        await query.message.reply_text("لطفا اکانت مورد نظر خود را همراه با پیش شماره وارد کنید : مثال : +19901102345",reply_markup=add_account_keyboard())
        return SET_PHONE_NUMBER

    await query.message.reply_text("کاربر یافت نشد",reply_markup=main_menu_keyboard())
    return ConversationHandler.END


async def set_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone = update.message.text
    if re.match(phone_regex,phone):
        add_phone_data[update.message.chat_id] = {}
        add_phone_data[update.message.chat_id]["phone"] = phone
        r,client = await send_code(phone)
        if r:
            add_phone_data[update.message.chat_id]["sent_code"] = r
            add_phone_data[update.message.chat_id]["client"] = client
            await update.message.reply_text(f"کد برای شماره {phone} ارسال شد",reply_markup=add_account_keyboard())
            await update.message.reply_text("کد ارسال شده را وارد کنید",reply_markup=add_account_keyboard())
            return SET_CODE
        
    await update.message.reply_text("شماره موبایل را صحیح وارد کنید نمونه: +19901102345",reply_markup=add_account_keyboard())
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
        status, result = backend_interface.add_account(user, add_phone_data[update.message.chat_id]["phone"],r)
        if status:
            await update.message.reply_text(f"{result}",reply_markup=check_clear_session_keyboard())
        else:
            await update.message.reply_text(f"{result}", reply_markup=main_menu_keyboard())

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
            await update.message.reply_text(f"{result}",reply_markup=check_clear_session_keyboard())
        else:
            await update.message.reply_text(f"{result}", reply_markup=main_menu_keyboard())

        return ConversationHandler.END

    else:
        await update.message.reply_text("کاربر یافت نشد",reply_markup=add_account_keyboard())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("عملیات با موفقیت لغو شد.")

    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید",
                                        reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def accept_logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = backend_interface.get_user(query.message.chat_id)
    # phone = "+989106664920"
    phone = add_phone_data[update.message.chat_id]["phone"]
    account = user.accounts.filter(phone=phone).first()
    result = await check_session(account.phone)
    if result:
        r = backend_interface.activate_account(user,phone)
        if r:
            await query.message.reply_text("اکانت با موفقیت تایید شد و اعتبار به موجودی شما اضافه شد",reply_markup=main_menu_keyboard())
        else:
            await query.message.reply_text("این اکانت قبلا تایید شده است",
                                           reply_markup=main_menu_keyboard())

    else:
        await query.message.reply_text("عملیات انجام نشد. لطفا بعد از پاک کردن تمامی نشست های فعال خود روی دکمه تایید کلیک کنید(نشست فعال ربات را حذف نکنید)",reply_markup=check_clear_session_keyboard())


async def user_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = backend_interface.get_user(update.message.chat_id)
    user_id , account_count = backend_interface.get_account_details(user)
    
    await update.message.reply_text(f"شناسه کاربری شما : {user_id}\nتعداد اکانت های تایید شده ارسالی شما : {account_count}")


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("شماره کارت خود را ارسال کنید ✅")
    add_checkout_data[update.message.chat_id] = {}
    return SET_CARD_NUMBER

async def set_card_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_checkout_data[update.message.chat_id]["card_number"] = update.message.text
    user = backend_interface.get_user(update.message.chat_id)
    checkout_account_count = backend_interface.get_checkout_account_count(user)
    await update.message.reply_text(f"تعداد اکانت برای تسویه را وارد کنید ✅ \n تعداد اکانت قابل تسویه: {checkout_account_count}")
    return SET_ACCOUNT_COUNT 

async def set_account_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = backend_interface.get_user(update.message.chat_id)
    checkout_account_count = backend_interface.get_checkout_account_count(user)
    try:
        if int(update.message.text) <= checkout_account_count and int(update.message.text) > 0:
            add_checkout_data[update.message.chat_id]["account_count"] = update.message.text
            count = add_checkout_data[update.message.chat_id]["account_count"]
            card_number = add_checkout_data[update.message.chat_id]["card_number"]
            result = backend_interface.add_checkout_request(user,card_number,count)
            if result:
                await update.message.reply_text("درخواست شما با موفقیت ثبت شد ✅")
            else:
                await update.message.reply_text("خطایی رخ داده با پشتیبانی تماس بگیرید")

            return ConversationHandler.END

            
        else:
            await update.message.reply_text("عدد وارد شده بیشتر از تعداد اکانت قابل تسویه است")
            return SET_ACCOUNT_COUNT
    except:
        pass
    await update.message.reply_text("عدد وارد شده صحیح نمیباشد")
    return SET_ACCOUNT_COUNT
    

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("ئشتیبانی")


def main() -> None:

    application = Application.builder().token("411779048:AAHaRZg1pphD9DkIt0IYpZdemKGaFK0Rbak").build()

    add_account_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("➕ ارسال اکانت ➕"), set_phone_number)],
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

    checkout_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("تسویه حساب ♻️"), checkout)],
        states={
            SET_CARD_NUMBER: [
                MessageHandler(filters.Regex("^(?!\لغو).*$"), set_card_number),
            ],
            SET_ACCOUNT_COUNT: [
                MessageHandler(filters.Regex("^(?!\لغو).*$"), set_account_count),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("لغو"), cancel)],
    )
    # application.add_handler(MessageHandler(filters.Regex("\/start [a-z0-9]{8}"), join_to_room))
    application.add_handler(MessageHandler(filters.Regex("\/start"), start))
    application.add_handler(MessageHandler(filters.Regex("\/debug"), debug))
    application.add_handler(CallbackQueryHandler(accept_logout,"accept_logout"))
    application.add_handler(add_account_conv_handler)
    application.add_handler(checkout_conv_handler)
    
    application.add_handler(MessageHandler(filters.Regex("حساب کاربری 🔒"), user_account))
    application.add_handler(MessageHandler(filters.Regex("پشتیبانی 📮"), support))

    application.run_polling()


if __name__ == "__main__":
    main()