'''Various example tools.'''
import random
import mysqlsh
from myext.utils import util


def dice():
    '''Roll a dice with six sides.'''
    return random.randint(1, 6)


def describe(schema_name, table_name):
    '''Simulate the DESC statement for a table and dump the rows
    to the console. Uses util.get_columns() to get the column
    information.'''
    shell = mysqlsh.globals.shell
    session = shell.get_session()
    schema = session.get_schema(schema_name)
    table = schema.get_table(table_name)
    columns = util.get_columns(table)
    shell.dump_rows(columns)
