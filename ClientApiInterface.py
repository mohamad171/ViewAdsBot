from pyrogram import Client, filters
import asyncio
from pyrogram import Client
from pyrogram.raw.functions import auth
api_id = 26261816
api_hash = "a507aa6622033ed9015594c949795ce9"


def send_code(phone):
    with Client(phone, api_id, api_hash) as app:
        sent_code = app.send_code(phone)
        return sent_code


def signin(phone,code,sent_code):
    with Client(phone, api_id, api_hash) as app:
        result = auth.sign_in.SignIn(phone_number=phone,phone_code=code,phone_code_hash=sent_code.phone_code_hash)
        return result

# phone = "+99**********8"
# name = "ali"
# api_id='********'
# api_hash='***************************'
# app = Client(name, api_id,api_hash,test_mode=True,proxy=dict(hostname="127.0.0.1",port=9050))

# def mainapp() -> User:
#     try:
#         app.connect()

#         sent_code = app.send_code(phone)
#         code = input("Code? ")

#         signed_in = app.sign_in(phone, sent_code.phone_code_hash, code)

#         if isinstance(signed_in, User):
#             return signed_in
#     except RPCError as e:
#         raise e
#     finally:
#         app.disconnect()

# print(mainapp())