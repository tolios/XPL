#!/Users/apostolos/Desktop/xpl/.venv/bin/python3

import click
import lib.processor
import lib.config
from lib.db import delete_collection, is_processed, db_exists, list_dbs
from lib.query import answer_question
from tabulate import tabulate
import toml

@click.group()
def cli():
    pass

@cli.command()
@click.option('-d', '--delete', is_flag=True, default=False, help='Deletes the embedded file chunks from the database.')
@click.argument('filename', required=False)
def process(filename, delete):
    """xpl - Explain documents using AI."""
    if filename:
        if delete:  
            try:
                delete_collection(filename)
                click.echo(f"Deleted embeddings for {filename}.")
            except Exception as e:
                raise e
        else:
            lib.processor.process_document(filename)
            click.echo(f"Processed {filename} and stored embeddings.")

@cli.command()
@click.argument("filepath")
@click.argument("question")
def ask(filepath, question):
    """Asks a question about the document."""
    if not db_exists(filepath):
        lib.processor.process_document(filepath)
    if not is_processed(filepath):
        lib.processor.process_document(filepath) 

    response = answer_question(filepath, question)
    click.echo(response)

@cli.command()
def config():
    """Prints config of xpl"""
    click.echo(toml.dumps(lib.config.config))

@cli.command()
def dbs():
    """Prints list of databases """
    databases = list_dbs()
    if not databases:
        click.echo("No databases found.")
        return

    headers = ["ID", "Name", "Tenant"]
    table_data = [[str(db["id"]), db["name"], db["tenant"]] for db in databases]

    click.echo(tabulate(table_data, headers=headers, tablefmt="plain"))


if __name__ == "__main__":
    cli()
