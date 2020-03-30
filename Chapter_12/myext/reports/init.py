'''Import the report in sessions.py into the module.'''
import mysqlsh
from myext.reports import sessions

shell = mysqlsh.globals.shell
shell.register_report(
    'sessions_myext',
    'list',
    sessions.sessions,
    {
        'brief': 'Shows which sessions exist.',
        'details': ['You need the SELECT privilege on sys.session view and ' +
                    'the underlying tables and functions used by it.'],
        'options': [
            {
                'name': 'limit',
                'brief': 'The maximum number of rows to return.',
                'shortcut': 'l',
                'type': 'integer'
            },
            {
                'name': 'sort',
                'brief': 'The field to sort by.',
                'shortcut': 's',
                'type': 'string',
                'values': list(sessions.SORT_ALLOWED.keys())
            }
        ],
        'argc': '0'
    }
)
