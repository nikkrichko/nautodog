import click
from nautodog import log_command # Added import

@click.group()
def ddmainconfig():
    """Commands for main configuration"""
    pass

@ddmainconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def addtag(name):
    click.echo(f"Command: addtag, Name: {name}")

@ddmainconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def apikey(name):
    click.echo(f"Command: apikey, Name: {name}")
