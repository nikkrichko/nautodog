import click
from nautodog import log_command # Added import

@click.group()
def report():
    """Commands for reporting"""
    pass

@report.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def ndreport_devices(name):
    click.echo(f"Command: ndreport_devices, Name: {name}")

@report.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def sldreport_devices(name):
    click.echo(f"Command: sldreport_devices, Name: {name}")

@report.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command # Added decorator
def ddreportmonitorcoverage(name):
    click.echo(f"Command: ddreportmonitorcoverage, Name: {name}")
