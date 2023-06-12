from django.shortcuts import render
from .. import BackendInterface
import asyncio
from django.http import HttpResponse

backend_interface = BackendInterface.BackendInterface()


async def do_action_task(accounts):
    from ClientApiInterface import do_action
    for account in accounts:
        await do_action(account)

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
    accounts = backend_interface.get_orders()
    task = asyncio.create_task(do_action_task(accounts))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return HttpResponse("Ok")