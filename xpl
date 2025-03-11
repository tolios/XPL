#!/Users/apostolos/Desktop/xpl/.venv/bin/python3

import click
import lib.processor
import lib.config
from lib.db import delete_collection, is_processed, db_exists_for_file, db_exists, list_dbs, list_collections
from lib.bm25 import delete_bm25_collection
from lib.query import answer_question
from tabulate import tabulate
import toml
import shutil

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
                delete_bm25_collection(filename)
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
    if not db_exists_for_file(filepath):
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

@cli.command()
@click.argument("folderpath")
def ls(folderpath):
    """Prints list of docs processed in a given folder (if it exists)"""
    if not db_exists(folderpath):
        click.echo("No database found...")
    else:
        # iterating to generate all docs
        collections = list_collections(folderpath)

        term_width = shutil.get_terminal_size().columns
        max_len = max(len(f) for f in collections) if collections else 0
        col_width = max_len + 2  # Padding
        cols = max(1, term_width // col_width)  # Number of columns that fit
    
        for i, file in enumerate(collections):
            print(file.ljust(col_width), end="")
            if (i + 1) % cols == 0:  # Move to a new line
                print()
    
        if len(collections) % cols != 0:  # Ensure the last line ends properly
            print()

if __name__ == "__main__":
    cli()
