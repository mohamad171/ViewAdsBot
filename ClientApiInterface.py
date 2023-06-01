from pyrogram import Client, filters
import asyncio

from pyrogram import Client

async def run() :
    api_id = 26261816
    api_hash = "a507aa6622033ed9015594c949795ce9"
    async with Client("17845265572", api_id, api_hash) as app:
        print(await app.export_session_string())
        # print(await app.send_code())

asyncio.run(run())

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