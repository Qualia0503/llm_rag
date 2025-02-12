import click

@click.command("hello")
def run():
    click.echo("hello world.")

