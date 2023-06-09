
import os
import random
import sys

import django
from django.db.models import Q

os.environ["DJANGO_SETTINGS_MODULE"] = "ViewAdsBot.settings"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from website.models import *
from django.core.files.base import ContentFile, File


class BackendInterface:

    def register(self, chat_id, full_name, username):
        obj, created = StartedUser.objects.get_or_create(chat_id=chat_id, full_name=full_name, username=username)
        return True

    def get_user(self,chat_id):
        s_u = StartedUser.objects.filter(chat_id=chat_id).first()
        if s_u:
            return s_u
        return None

    def add_account(self,user,phone):
        account = Account.objects.filter(phone=phone).first()

        if not account:
            cli_info = CliInfo.objects.filter(can_use=True,is_active=True).first()
            proxy_info = ProxyInfo.objects.filter(can_use=True,is_active=True).first()
            image = SampleProfileImage.objects.filter().order_by("?").first()
            bio = SampleBio.objects.filter().order_by("?").first()

            if not cli_info or not proxy_info:
                return False,"امکان افزودن اکانت درحا حاضر وجود ندارد"

            DEVICE_MODELS = ["PC","Mobile","Web"]
            SYSTEM_VERSION = ["Android","Linux","Windows","Ios","Macos"]
            APP_VERSION = ["4.8.1","4.8","4.7","4.6","4.5"]

            account = Account()
            account.user = user
            account.phone = phone
            account.session_string = None
            account.is_active = False
            account.is_logged_in = False
            account.proxy_info = proxy_info
            account.cli_info = cli_info
            account.image_profile = image.image_profile
            account.system_version = random.choice(SYSTEM_VERSION)
            account.device_model = random.choice(DEVICE_MODELS)
            account.app_version = random.choice(APP_VERSION)
            account.bio = bio
            account.save()
            return True,None

        if account.is_logged_in == False:
            return True,None
        return False,"اکانت قبلا اضافه شده"

    def set_account_loggedin(self,phone):
        account = self.get_account(phone)
        if account:
            account.is_logged_in = True
            with open(f"{phone}.session","rb") as f:
                account.session_file.save(f"{phone}.session", File(f))
            account.save()
            os.remove(f"{phone}.session")
            return True,"اکانت با موفقیت دریافت شد ✅\nلطفا بعد از خارج شدن از اکانت روی دکمه زیر بزنید تا اکانت تایید شود ✅"
        else:
            return False,"اکانت یافت نشد"

    def get_account_details(self,user):
        account_count = Account.objects.filter(user=user,is_active=True).count()
        return user.chat_id,account_count

    def get_account(self,phone):
        account = Account.objects.filter(phone=phone).first()
        return account

    def get_checkout_account_count(self,user):
        account_count = Account.objects.filter(user=user,is_active=True,is_checkout=False).count()
        return account_count

    def add_checkout_request(self,user,card_number,account_count,set_checkouted=False):
        count = Account.objects.filter(user=user,is_active=True,is_checkout=False).count()
        
        if count >= int(account_count):
            ch = Checkout()
            ch.user = user
            ch.account_count = account_count
            ch.card_number = card_number
            ch.save()

            if set_checkouted:
                for a in range(0,count):
                    account = Account.objects.filter(user=user,is_active=True,is_checkout=False).first()
                    account.is_checkout = True
                    account.save()
            return True
        return False

    def get_all_accounts(self):
        accounts = Account.objects.filter(is_active=True,is_logged_in=True)
        return accounts

    def activate_account(self,user,phone):
        account = Account.objects.filter(phone=phone,user=user,is_active=False).first()
        if account:
            account.is_active = True
            account.save()

            u = account.user
            u.credit += 5000
            u.save()
            return True
        return False
    def get_random_bio(self):
        bio = SampleBio.objects.filter().order_by("?")
        return bio.first()
    
    def get_random_image(self):
        profile_photo = SampleProfileImage.objects.filter().order_by("?")
        return profile_photo.first().image_profile.path