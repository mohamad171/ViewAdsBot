
import os
import random
import django
from django.db.models import Q

os.environ["DJANGO_SETTINGS_MODULE"] = "ViewAdsBot.settings"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from website.models import *


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
        if not Account.objects.filter(phone=phone).exists():
            account = Account()
            account.user = user
            account.phone = phone
            account.save()
            return True,"اکانت با موفقیت اضافه شد"
        return False,"اکانت قبلا اضافه شده"

