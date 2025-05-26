import click

@click.group()
def cli():
    """A simple CLI application."""
    pass

@cli.command()
@click.argument('name')
def hello(name):
    """Greets a person by their name."""
    click.echo(f"Hello, {name}!")

if __name__ == '__main__':
    cli()
