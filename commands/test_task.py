# commands/test_task.py
import click
from tasks.demo_task import task as demo_task
from tasks.dataset_segment_embed_task import task as dataset_segment_embed_task

@click.command("test_task")
def run():
    # 调用立即执行
    # demo_task.delay('exec now')
    # # 调用后延迟10秒再执行
    # demo_task.apply_async(
    #     kwargs = {'msg': 'exec async'},
    #     countdown = 10
    # )

    dataset_segment_embed_task.delay(7)

    click.echo("success.")