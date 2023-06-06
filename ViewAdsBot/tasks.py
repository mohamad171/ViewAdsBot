import datetime
import random
from unicodedata import name
from .celery import app as celery_app
import time
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import os
from website.models import *
from django.utils import timezone
from ClientApiInterface import do_action

@celery_app.task(bind=True)
def run_orders(self):
    orders = Order.objects.filter(status=Order.OrderStatusChoices.WATING,accept_to_start=True,start_at__lte=timezone.now())
    join_orders = orders.filter(order_type=Order.OrderTypeChoices.JOIN).order_by("-count")
    view_orders = orders.filter(order_type=Order.OrderTypeChoices.VIEW).order_by("-count")
    accounts = []

    biggest_order = join_orders.first().count

    if view_orders.first().count > biggest_order:
        biggest_order = view_orders.first()
    

    all_accounts = Account.objects.filter(is_active=True,is_logged_in=True).order_by("last_used")
    if all_accounts.count() >= biggest_order:

        for a in all_accounts:
            accounts.append({
                "account":a,
                "actions": []
            })

        for join_order in join_orders:
            for account in accounts[0:join_order.count]:
                account["actions"].append({
                    "order_id":join_order.id,
                    "order_type":join_order.order_type,
                    "link":join_order.link
                })
                join_order.status = Order.OrderStatusChoices.RUNNING
                join_order.save()
        
        for view_order in view_orders:
            for account in accounts[0:view_order.count]:
                account["actions"].append({
                    "order_id":view_order.id,
                    "order_type":view_order.order_type,
                    "link":view_order.link
                })
                view_order.status = Order.OrderStatusChoices.RUNNING
                view_order.save()
        
    else:
        pass

    for account in accounts:
        results = do_action(account_data=account)
        for result in results:
            order = Order.objects.filter(id=result["order_id"]).first()
            if order:
                if result["result"]:
                    order.success_count += 1
                else:
                    order.faild_count += 1
                order.save()

        time.sleep(20)
    
    for o in (join_orders + view_orders):
        o.status = Order.OrderStatusChoices.FINISHED
        o.save()