'''Import the plugin tools.'''
import mysqlsh
from myext.tools import example

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
    shell.register_global("myext", global_obj, description)

# Get the tools extension
try:
    plugin_obj = global_obj.tools
except IndexError:
    # The tools extension does not exist yet, so register it
    plugin_obj = shell.create_extension_object()
    description = {
        'brief': 'Tools.',
        'details': ['Various tools including describe() and dice().']
    }
    shell.add_extension_object_member(global_obj, "tools", plugin_obj,
                                      description)

definition_describe = {
    'brief': 'Describe a table.',
    'details': ['Show information about the columns of a table.'],
    'parameters': [
        {
            'name': 'schema_name',
            'type': 'string',
            'required': True,
            'brief': 'The name of the schema the table is in.',
            'details': ['A string with the schema name.']
        },
        {
            'name': 'table_name',
            'type': 'string',
            'required': True,
            'brief': 'The name of the table to describe.',
            'details': ['A string with the table name.']
        }
    ]
}

try:
    shell.add_extension_object_member(plugin_obj, 'describe', example.describe,
                                      definition_describe)
except SystemError as e:
    shell.log("ERROR", "Failed to register myext example.describe ({0})."
              .format(str(e).rstrip()))

definition_dice = {
    'brief': 'Roll a dice'
}

try:
    shell.add_extension_object_member(plugin_obj, 'dice', example.dice,
                                      definition_dice)
except SystemError as e:
    shell.log("ERROR", "Failed to register myext exmaple.dice ({0})."
              .format(str(e).rstrip()))
