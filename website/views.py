from django.shortcuts import render
import asyncio
from django.http import HttpResponse
from .models import *
from django.utils import timezone
from multiprocessing import Process

def get_orders():
    orders = Order.objects.filter(status=Order.OrderStatusChoices.WATING, accept_to_start=True,
                                  start_at__lte=timezone.now())
    accounts = []
    if orders.count() > 0:
        join_orders = orders.filter(order_type=Order.OrderTypeChoices.JOIN).order_by("-count")
        view_orders = orders.filter(order_type=Order.OrderTypeChoices.VIEW).order_by("-count")

        biggest_order = 0
        if join_orders.count() > 0:
            biggest_order = join_orders.first().count
        if view_orders:
            if view_orders.first().count > biggest_order:
                biggest_order = view_orders.first()

        all_accounts = Account.objects.filter(is_active=True, is_logged_in=True, is_ban=False).order_by("last_used")
        if all_accounts.count() >= biggest_order:

            for a in all_accounts:
                accounts.append({
                    "account": a,
                    "actions": []
                })

            for join_order in join_orders:
                for account in accounts[0:join_order.count]:
                    account["actions"].append({
                        "order_id": join_order.id,
                        "order_type": join_order.order_type,
                        "link": join_order.link
                    })
                    join_order.status = Order.OrderStatusChoices.RUNNING
                    join_order.save()

            for view_order in view_orders:
                for account in accounts[0:view_order.count]:
                    account["actions"].append({
                        "order_id": view_order.id,
                        "order_type": view_order.order_type,
                        "link": view_order.link
                    })
                    # view_order.status = Order.OrderStatusChoices.RUNNING
                    # view_order.save()

        else:
            pass

        return accounts

def do_action_task(accounts):
    from ClientApiInterface import do_action
    orders = []
    for account in accounts:
        print(f"Going in {account.phone}")
        results = do_action(account)
        for result in results:
            print("Setting result...")
            order = Order.objects.filter(id=result["order_id"]).first()
            if order:
                if result["result"]:
                    order.success_count += 1
                else:
                    order.faild_count += 1
                order.save()

                if order not in orders:
                    orders.append(order)

    for o in orders:
        o.status = Order.OrderStatusChoices.FINISHED
        o.save()


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


def run_tasks(request):
    background_tasks = set()
    accounts = get_orders()
    print(accounts)
    p = Process(target=do_action_task, args=(accounts,))
    p.start()
    #
    # task = asyncio.create_task(do_action_task(accounts))
    # background_tasks.add(task)
    # task.add_done_callback(background_tasks.discard)

    return HttpResponse("Ok")