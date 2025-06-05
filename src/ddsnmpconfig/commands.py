import click
from nautodog import log_command
from src.utils.print_info import PrintInfo # Added import

@click.group()
def ddsnmpconfig():
    """Commands for SNMP configuration"""
    pass

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def addsnmpv3(name):
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: addsnmpv3, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def addsnmpv2(name):
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: addsnmpv2, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def uploadcustopprofile(name): # Corrected typo: uploadcustopProfile -> uploadcustopprofile
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: uploadcustopprofile, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def createlocalconfig(name):
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: createlocalconfig, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def verifydevices(name):
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: verifydevices, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def autodiscoveryv2(name): # Corrected typo: autodicsoveryv2 -> autodiscoveryv2
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: autodiscoveryv2, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def autodiscoveryv3(name):
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: autodiscoveryv3, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def rollbackconfig(name):
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: rollbackconfig, Name: {name}")

@ddsnmpconfig.command()
@click.option('-n', '--name', required=True, help='Name to use.')
@log_command
def revokedevice(name): # Corrected typo: revokedivice -> revokedevice
    PrintInfo().print_caller_name() # Added call
    click.echo(f"Command: revokedevice, Name: {name}")
