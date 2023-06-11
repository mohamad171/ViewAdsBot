import datetime
import json
import random
from unicodedata import name
from .celery import app as celery_app
import time
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import os
from website.models import *
from django.utils import timezone
import asyncio
from asgiref.sync import async_to_sync


@celery_app.task(bind=True)
def get_orders(self):
    return "ok"




@celery_app.task(bind=True)
def run_orders(self):


        loop = asyncio.get_event_loop()
        # loop.run_until_complete(do_action_task(accounts))

        # for o in (join_orders + view_orders):
        #     o.status = Order.OrderStatusChoices.FINISHED
        #     o.save()


@celery_app.task(bind=True)
def check_accounts(self):
    from ClientApiInterface import check_is_ban

    accounts = Account.objects.filter(is_active=True, is_logged_in=True)
    for account in accounts:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(check_is_ban(account))
