from pyrogram import Client, filters
import asyncio
from pyrogram import Client
from pyrogram.raw.functions import auth,account
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid,PhoneCodeExpired , AuthKeyUnregistered
from BackendInterface import BackendInterface

api_id = 26261816
api_hash = "a507aa6622033ed9015594c949795ce9"

backendInterface = BackendInterface()


async def send_code(phone):
    account = backendInterface.get_account(phone)
    if not account:
        return None,None

    client = Client(account.phone, account.cli_info.api_key, account.cli_info.api_hash)
    await client.connect()
    try:
        sent_code = await client.send_code(phone)
        # client.disconnect()
        return sent_code,client
    except:
        return None,None


async def signin(client,phone,code,sent_code):
    account = backendInterface.get_account(phone)
    if not account:
        return "invalid"
    try:
        await client.sign_in(phone_number= account.phone,phone_code_hash=sent_code.phone_code_hash,phone_code=code)
        hash = await client.export_session_string()
        await client.disconnect()
        return hash
    except SessionPasswordNeeded:
        await client.disconnect()
        return "password"

    except PhoneCodeInvalid:
        await client.disconnect()
        return "invalid"

    except PhoneCodeExpired:
        await client.disconnect()
        return "invalid"


async def client_set_password(client,password):
    try:
        client.check_password(password)
        hash = await client.export_session_string()
        await client.disconnect()
        return hash

    except PasswordHashInvalid:
        return "invalid"


async def check_session(phone):
    account = backendInterface.get_account(phone)
    if not account:
        return False

    client = Client(phone.replace("+",""),api_id=account.cli_info.api_key, api_hash=account.cli_info.api_hash,workdir="media/sessions")
    await client.connect()
    any_account_is_logged_in = False
    try:
        result = await client.invoke(account.GetAuthorizations())
        for authoriz in result.authorizations:
            if authoriz.current != True:
                any_account_is_logged_in = True
        if not any_account_is_logged_in:
            return True
        else:
            return False


    except AuthKeyUnregistered:
        pass
    return False







async def change_bio_image(phone,hash,bio_text,profile_image):
    account = backendInterface.get_account(phone)
    if not account:
        return False

    client = Client(phone, api_id=account.cli_info.api_key, api_hash=account.cli_info.api_hash,session_string=hash)
    await client.connect()
    try:
        await client.update_profile(bio=bio_text)
        await client.set_profile_photo(profile_image)
        await client.disconnect()
        return True
        
    except:
        await client.disconnect()
        return False



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