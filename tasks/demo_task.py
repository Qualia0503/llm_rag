from celery import shared_task

@shared_task(queue='dataset')
def task(msg):
    print(msg)

