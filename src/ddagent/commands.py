import click
from nautodog import log_command # Added import

@click.group()
def ddagent():
    """Commands for ddagent"""
    pass

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def ddastatus(name):
    click.echo(f"Command: ddastatus, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def ddaerrors(name):
    click.echo(f"Command: ddaerrors, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def ddalogs(name):
    click.echo(f"Command: ddalogs, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def dduploadconfigs(name):
    click.echo(f"Command: dduploadconfigs, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def dddownloadconfigs(name):
    click.echo(f"Command: dddownloadconfigs, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def configconsistency(name):
    click.echo(f"Command: configconsistency, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def downloadconfigs(name): # Note: This might be a duplicate or a more generic version of dddownloadconfigs
    click.echo(f"Command: downloadconfigs, Name: {name}")

@ddagent.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def uploadconfigs(name): # Note: This might be a duplicate or a more generic version of dduploadconfigs
    click.echo(f"Command: uploadconfigs, Name: {name}")
