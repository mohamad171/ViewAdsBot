import json
import atexit
import os.path
import pickle
from concurrent.futures import ThreadPoolExecutor

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
from ClientApiInterface import send_code, signin, client_set_password, check_session, change_bio_details
import re
from telegram.ext.filters import ChatType
from multiprocessing import Process, Pool
from multiprocessing.pool import ThreadPool

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# add_phone_data = {}
# add_checkout_data = {}


def save_data():
    print("saveing data...")
    with open('add_phone_data.pickle', 'wb') as handle:
        pickle.dump(add_phone_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('add_checkout_data.pickle', 'wb') as handle:
        pickle.dump(add_checkout_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_phone_data():
    add_phone_data = {}
    if os.path.exists("add_phone_data.pickle"):
        f = open('add_phone_data.pickle', 'rb')

        try:
            add_phone_data = pickle.load(f)
        except:
            add_phone_data = {}

    return add_phone_data


def load_checkout_data():
    add_checkout_data = {}
    if os.path.exists("add_checkout_data.pickle"):

        f = open('add_checkout_data.pickle', 'rb')
        try:
            add_checkout_data = pickle.load(f)
        except:
            add_checkout_data = {}



    return add_checkout_data


add_phone_data = load_phone_data()
add_checkout_data = load_checkout_data()

atexit.register(save_data)

logger = logging.getLogger(__name__)
backend_interface = BackendInterface.BackendInterface()

SET_PHONE_NUMBER, SET_CODE, SET_PASSWORD = range(3)
SET_CARD_NUMBER, SET_ACCOUNT_COUNT = range(2)
import time
import asyncio

def callback(value):
    print("Call back called")

def do_action_task(accounts):
    from ClientApiInterface import do_action
    for account in accounts:
        executor = ThreadPoolExecutor(1)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor,do_action, account)

    # loop = asyncio.get_event_loop()
    # tasks = []
    # for account in accounts:
    #     loop.create_task(do_action(account_data=account))
    #
    # loop.run_until_complete(asyncio.wait(tasks))
    # loop.close()
    # pool = ThreadPool(processes=10)
    # pool.map_async(do_action,accounts)



        # for result in results:
        #     print("Setting result...")
        #     order = Order.objects.filter(id=result["order_id"]).first()
        #     if order:
        #         if result["result"]:
        #             order.success_count += 1
        #         else:
        #             order.faild_count += 1
        #         order.save()



async def send_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text("دستور اجرا صادر شد")
    accounts = backend_interface.get_orders()
    do_action_task(accounts)

async def send_payment_message(message, context: ContextTypes.DEFAULT_TYPE):
    try:
        setting = backend_interface.get_setting()
        print(setting.payment_log_channel_id)
        await context.bot.send_message(chat_id=setting.payment_log_channel_id, text=message)
    except:
        pass


async def send_log_message(message, context: ContextTypes.DEFAULT_TYPE):
    try:
        setting = backend_interface.get_setting()
        print(setting.account_log_channel_id)
        await context.bot.send_message(chat_id=setting.account_log_channel_id, text=message)
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        username = user["username"]
    except:
        username = None
    first_name = user["first_name"]
    backend_interface.register(update.message.chat_id, first_name, username)
    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید", reply_markup=main_menu_keyboard())


async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.channel_post.text == "chatinfo":
        await update.channel_post.reply_text(update.channel_post.chat_id)


async def chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.channel_post.reply_text(update.channel_post.chat_id)


async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user = backend_interface.get_user(query.message.chat_id)
    if user:
        add_phone_data[query.message.chat_id] = {}
        await query.message.reply_text("لطفا اکانت مورد نظر خود را همراه با پیش شماره وارد کنید : مثال : +19901102345",
                                       reply_markup=cancele_keyboard())
        return SET_PHONE_NUMBER

    await query.message.reply_text("کاربر یافت نشد", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


async def set_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone = update.message.text
    if re.match(phone_regex, phone):
        add_phone_data[update.message.chat_id] = {}
        add_phone_data[update.message.chat_id]["phone"] = phone
        user = backend_interface.get_user(update.message.chat_id)
        await update.message.reply_text("درحال بررسی و ارسال کد (ممکن است کمی زمان ببرد)",
                                        reply_markup=cancele_keyboard())
        result, msg = backend_interface.add_account(user, phone)
        if result:
            r, client = await send_code(phone)
            if r:
                add_phone_data[update.message.chat_id]["sent_code"] = r
                add_phone_data[update.message.chat_id]["client"] = client
                await update.message.reply_text(f"کد برای شماره {phone} ارسال شد", reply_markup=cancele_keyboard())
                await update.message.reply_text("کد ارسال شده را وارد کنید", reply_markup=cancele_keyboard())
                return SET_CODE
        else:
            await update.message.reply_text(msg, reply_markup=main_menu_keyboard())
            return ConversationHandler.END

    await update.message.reply_text("شماره موبایل را صحیح وارد کنید نمونه: +19901102345",
                                    reply_markup=cancele_keyboard())
    return SET_PHONE_NUMBER


async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    password = update.message.text
    client = add_phone_data[update.message.chat_id]["client"]
    phone = add_phone_data[update.message.chat_id]["phone"]
    r = await client_set_password(client, password)
    if r == "invalid":
        await update.message.reply_text("رمز عبور صحیح نیست لطفا مجددا تلاش کنید", reply_markup=cancele_keyboard())
        return SET_PASSWORD

    user = backend_interface.get_user(update.message.chat_id)
    if user:
        status, result = backend_interface.set_account_loggedin(phone)
        if status:
            account = backend_interface.get_account(phone)
            if account:
                await change_bio_details(phone=account.phone, bio_text=account.bio,
                                         profile_image=account.image_profile.path)
            await send_log_message(f"اکانت جدید با شماره{phone} توسط {user.chat_id} در سیستم ثبت شد", context=context)
            await update.message.reply_text(f"{result}", reply_markup=check_clear_session_keyboard())
        else:
            await update.message.reply_text(f"{result}", reply_markup=main_menu_keyboard())

    else:
        await update.message.reply_text("کاربر یافت نشد", reply_markup=main_menu_keyboard())


async def set_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code = update.message.text
    sent_code = add_phone_data[update.message.chat_id]["sent_code"]
    phone = add_phone_data[update.message.chat_id]["phone"]
    client = add_phone_data[update.message.chat_id]["client"]
    r = await signin(client, phone, code, sent_code)
    if r == "password":
        await update.message.reply_text("ورود دو مرحله ای نیاز است\nلطفا رمز عبور را وارد کنید",
                                        reply_markup=cancele_keyboard())
        return SET_PASSWORD
    elif r == "invalid":
        await update.message.reply_text("کد وارد شده صحیح نیست دوباره کد را وارد کنید", reply_markup=cancele_keyboard())
        return SET_CODE

    user = backend_interface.get_user(update.message.chat_id)
    if user:
        # status,result = backend_interface.add_account(user,add_phone_data[update.message.chat_id]["phone"],r)
        status, result = backend_interface.set_account_loggedin(add_phone_data[update.message.chat_id]["phone"])
        if status:
            account = backend_interface.get_account(phone)
            if account:
                await change_bio_details(phone=account.phone, bio_text=account.bio,
                                         profile_image=account.image_profile.path)

            await send_log_message(f"اکانت جدید با شماره{phone} توسط {user.chat_id} در سیستم ثبت شد", context=context)
            await update.message.reply_text(f"{result}", reply_markup=check_clear_session_keyboard())
        else:
            await update.message.reply_text(f"{result}", reply_markup=main_menu_keyboard())

        return ConversationHandler.END

    else:
        await update.message.reply_text("کاربر یافت نشد", reply_markup=cancele_keyboard())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("عملیات با موفقیت لغو شد.")

    await update.message.reply_text("برای ادامه یکی از گزینه های زیر را انتخاب کنید",
                                    reply_markup=main_menu_keyboard())
    return ConversationHandler.END


async def accept_logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    
    user = backend_interface.get_user(query.message.chat_id)
    # phone = "+989106664920"
    phone = add_phone_data[query.message.chat_id]["phone"]
    account = user.accounts.filter(phone=phone).first()
    result,is_ban = await check_session(account.phone)
    if result:
        r = backend_interface.activate_account(user, phone)
        if r:
            await query.edit_message_reply_markup(reply_markup=None)
            await send_log_message(f"شماره {phone} با موفقیت فعال شد", context=context)
            await query.message.reply_text("اکانت با موفقیت تایید شد و اعتبار به موجودی شما اضافه شد",
                                           reply_markup=main_menu_keyboard())
        else:
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("این اکانت قبلا تایید شده است",
                                           reply_markup=main_menu_keyboard())

    else:
        if is_ban:
            await query.message.reply_text(
                "اکانت توسط تلگرام دیلیت یا بن شده است",
                reply_markup=check_clear_session_keyboard())
            account.delete()
        else:
            await query.message.reply_text(
                "عملیات انجام نشد. لطفا بعد از پاک کردن تمامی نشست های فعال خود روی دکمه تایید کلیک کنید(نشست فعال ربات را حذف نکنید)",
                reply_markup=check_clear_session_keyboard())


async def user_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = backend_interface.get_user(update.message.chat_id)
    user_id, account_count = backend_interface.get_account_details(user)

    await update.message.reply_text(
        f"شناسه کاربری شما : {user_id}\nتعداد اکانت های تایید شده ارسالی شما : {account_count}")


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("شماره کارت خود را ارسال کنید ✅", reply_markup=cancele_keyboard())
    add_checkout_data[update.message.chat_id] = {}
    return SET_CARD_NUMBER


async def set_card_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_checkout_data[update.message.chat_id]["card_number"] = update.message.text
    user = backend_interface.get_user(update.message.chat_id)
    checkout_account_count = backend_interface.get_checkout_account_count(user)
    await update.message.reply_text(
        f"تعداد اکانت برای تسویه را وارد کنید ✅ \n تعداد اکانت قابل تسویه: {checkout_account_count}",
        reply_markup=cancele_keyboard())
    return SET_ACCOUNT_COUNT


async def set_account_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = backend_interface.get_user(update.message.chat_id)
    checkout_account_count = backend_interface.get_checkout_account_count(user)
    try:
        if int(update.message.text) <= int(checkout_account_count) and int(update.message.text) > 0:
            add_checkout_data[update.message.chat_id]["account_count"] = update.message.text
            count = add_checkout_data[update.message.chat_id]["account_count"]
            card_number = add_checkout_data[update.message.chat_id]["card_number"]
            result = backend_interface.add_checkout_request(user, card_number, count, set_checkouted=True)
            if result:
                await send_payment_message(
                    f"درخواست جدید برای تسویه حساب {count} اکانت توسط {user.chat_id} با شماره کارت {card_number} ثبت شد",
                    context=context)
                await update.message.reply_text("درخواست شما با موفقیت ثبت شد ✅", reply_markup=main_menu_keyboard())
            else:
                await update.message.reply_text("خطایی رخ داده با پشتیبانی تماس بگیرید",
                                                reply_markup=cancele_keyboard())

            return ConversationHandler.END


        else:
            await update.message.reply_text("عدد وارد شده بیشتر از تعداد اکانت قابل تسویه است",
                                            reply_markup=cancele_keyboard())
            return SET_ACCOUNT_COUNT
    except Exception as ex:
        print(ex)

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
    application.add_handler(MessageHandler(filters.Regex("\/send_orders"), send_orders))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, debug))
    application.add_handler(CallbackQueryHandler(accept_logout, "accept_logout"))
    application.add_handler(add_account_conv_handler)
    application.add_handler(checkout_conv_handler)

    application.add_handler(MessageHandler(filters.Regex("حساب کاربری 🔒"), user_account))
    application.add_handler(MessageHandler(filters.Regex("پشتیبانی 📮"), support))
    # application.add_handler(MessageHandler("chatinfo",chat_info))
    application.run_polling()


if __name__ == "__main__":
    main()
