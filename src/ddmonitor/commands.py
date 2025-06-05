import click
from nautodog import log_command # Added import

@click.group()
def ddmonitor():
    """Commands for monitoring"""
    pass

@ddmonitor.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def addreachablemonitor(name):
    click.echo(f"Command: addreachablemonitor, Name: {name}")

@ddmonitor.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def addinterfacemonitor(name):
    click.echo(f"Command: addinterfacemonitor, Name: {name}")

@ddmonitor.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def addmonitorsbyrules(name):
    click.echo(f"Command: addmonitorsbyrules, Name: {name}")
