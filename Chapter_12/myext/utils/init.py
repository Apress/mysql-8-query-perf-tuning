'''Import the utilities into the plugin.'''
import mysqlsh
from myext.utils import util

shell = mysqlsh.globals.shell
# Get the global object (the myext plugin)
try:
    # See if myext has already been registered
    global_obj = mysqlsh.globals.myext
except AttributeError:
    # Register myext
    global_obj = shell.create_extension_object()
    description = {
        'brief': 'Various MySQL Shell extensions.',
        'details': [
            'More detailed help. To be added later.'
        ]
    }
    shell.register_global('myext', global_obj, description)

# Get the utils extension
try:
    plugin_obj = global_obj.utils
except IndexError:
    # The utils extension does not exist yet, so register it
    plugin_obj = shell.create_extension_object()
    description = {
        'brief': 'Utilities.',
        'details': ['Various utilities.']
    }
    shell.add_extension_object_member(global_obj, "util", plugin_obj,
                                      description)

definition = {
    'brief': 'Describe a table.',
    'details': ['Show information about the columns of a table.'],
    'parameters': [
        {
            'name': 'table',
            'type': 'object',
            'class': 'Table',
            'required': True,
            'brief': 'The table to get the columns for.',
            'details': ['A table object for the table.']
        }
    ]
}

try:
    shell.add_extension_object_member(plugin_obj, 'get_columns',
                                      util.get_columns, definition)
except SystemError as e:
    shell.log("ERROR", "Failed to register myext util.get_columns ({0})."
              .format(str(e).rstrip()))
