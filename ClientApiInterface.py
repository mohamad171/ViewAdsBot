
from pyrogram import Client
from pyrogram.raw.functions import auth,account as rawaccount,messages
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid,PhoneCodeExpired \
    , AuthKeyUnregistered,UserDeactivatedBan,SessionRevoked
from BackendInterface import BackendInterface
import time
# api_id = 26261816
# api_hash = "a507aa6622033ed9015594c949795ce9"

backendInterface = BackendInterface()





async def send_code(phone):
    account = backendInterface.get_account(phone)
    if not account:
        return None,None
    
    proxy = {
     "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
     "hostname": account.proxy_info.ip,
     "port": account.proxy_info.port,
     "username": account.proxy_info.username,
     "password": account.proxy_info.password
    }

    client = Client(account.phone, account.cli_info.api_key, account.cli_info.api_hash,
                    device_model=account.device_model,system_version=account.system_version,
                    app_version=account.app_version, proxy=proxy)
    await client.connect()
    try:
        sent_code = await client.send_code(phone)
        # client.disconnect()
        return sent_code,client
    except Exception as ex:
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
    proxy = {
     "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
     "hostname": account.proxy_info.ip,
     "port": account.proxy_info.port,
     "username": account.proxy_info.username,
     "password": account.proxy_info.password
    }

    client = Client(phone.replace("+",""),api_id=account.cli_info.api_key,
                     api_hash=account.cli_info.api_hash,workdir="media/sessions",
                    device_model=account.device_model,system_version=account.system_version,
                    app_version=account.app_version,proxy=proxy)
    await client.connect()
    any_account_is_logged_in = False
    try:
        result = await client.invoke(rawaccount.GetAuthorizations())
        for authoriz in result.authorizations:
            if authoriz.current != True:
                any_account_is_logged_in = True
        if not any_account_is_logged_in:
            await client.disconnect()
            return True,False
        else:
            await client.disconnect()
            return False,False


    except AuthKeyUnregistered:
        pass
    except UserDeactivatedBan:
        await client.disconnect()
        return False,True
    await client.disconnect()
    return False,False



async def check_is_ban(account):

    proxy = {
     "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
     "hostname": account.proxy_info.ip,
     "port": account.proxy_info.port,
     "username": account.proxy_info.username,
     "password": account.proxy_info.password
    }

    client = Client(account.phone.replace("+",""),api_id=account.cli_info.api_key,
                     api_hash=account.cli_info.api_hash,workdir="media/sessions",
                    device_model=account.device_model,system_version=account.system_version,
                    app_version=account.app_version,proxy=proxy)
    await client.connect()
    any_account_is_logged_in = False
    try:
        result = await client.invoke(rawaccount.GetAuthorizations())
        for authoriz in result.authorizations:
            if authoriz.current != True:
                any_account_is_logged_in = True
        if not any_account_is_logged_in:
            account.is_active = True
            account.is_logged_in = True
            account.is_ban = False

        else:
            account.is_active = False
            account.is_logged_in = True
            account.is_ban = False



    except AuthKeyUnregistered:
        account.is_active = False
        account.is_logged_in = False
        account.is_ban = False

    except UserDeactivatedBan:
        account.is_active = False
        account.is_logged_in = False
        account.is_ban = False

    account.save()

    await client.disconnect()





async def change_bio_details(phone, bio_text, profile_image):
    account = backendInterface.get_account(phone)
    if not account:
        return False

    proxy = {
     "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
     "hostname": account.proxy_info.ip,
     "port": account.proxy_info.port,
     "username": account.proxy_info.username,
     "password": account.proxy_info.password
    }

    client = Client(phone.replace("+",""),api_id=account.cli_info.api_key,
                     api_hash=account.cli_info.api_hash,workdir="media/sessions",
                    device_model=account.device_model,system_version=account.system_version,
                    app_version=account.app_version,proxy=proxy)
    await client.connect()
    try:
        await client.update_profile(bio=bio_text)
        await client.set_profile_photo(photo=profile_image)
        await client.disconnect()
        return True
        
    except:
        await client.disconnect()
        return False

def do_action(account_data):
    account = account_data["account"]
    print(account.phone)
    proxy = {
     "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
     "hostname": account.proxy_info.ip,
     "port": account.proxy_info.port,
     "username": account.proxy_info.username,
     "password": account.proxy_info.password
    }

    client = Client(account.phone.replace("+",""),api_id=account.cli_info.api_key,
                     api_hash=account.cli_info.api_hash,workdir="media/sessions",
                    device_model=account.device_model,system_version=account.system_version,
                    app_version=account.app_version,proxy=proxy)
    client.connect()

    action_results = []
    for action in account_data["actions"]:
        action_result = {}
        try:
            if action["order_type"] == 1:
                print(str(action["link"]))
                client.join_chat(str(action["link"]).strip())
            else:
                client.invoke(messages.get_messages_views.GetMessagesViews(
                    id=action["link"],
                    increment=True
                ))

            action_result["order_id"] = action["order_id"]
            action_result["result"] = True
        except SessionRevoked:
            action_result["order_id"] = action["order_id"]
            action_result["result"] = False

            account.is_logged_in = False
            account.is_active = False
            account.save()
        except Exception as ex:
            print(ex)
            action_result["order_id"] = action["order_id"]
            action_result["result"] = False



        
        action_results.append(action_result)

    
    client.disconnect()

    time.sleep(2)
    return action_results
