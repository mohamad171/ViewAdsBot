
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

    def add_account(self,user,phone,hash):
        if not Account.objects.filter(phone=phone).exists():
            account = Account()
            account.user = user
            account.phone = phone
            account.session_string = hash
            account.is_active = False
            account.is_logged_in = True

            account.save()
            with open(f"{phone}.session","rb") as f:
                account.session_file.save(f"{phone}.session", File(f))
            account.save()
            os.remove(f"{phone}.session")
            return True,"اکانت با موفقیت اضافه شد.\n برای ادامه لطفا از اکانت خارج شوید و سپس روی دکمه تایید کلیک کنید"
        return False,"اکانت قبلا اضافه شده"

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