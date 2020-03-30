'''Define utility functions for the plugin.'''

def get_columns(table):
    '''Create query against information_schema.COLUMNS to obtain
    meta data for the columns.'''
    session = table.get_session()
    i_s = session.get_schema("information_schema")
    i_s_columns = i_s.get_table("COLUMNS")

    query = i_s_columns.select(
        "COLUMN_NAME AS Field",
        "COLUMN_TYPE AS Type",
        "IS_NULLABLE AS `Null`",
        "COLUMN_KEY AS Key",
        "COLUMN_DEFAULT AS Default",
        "EXTRA AS Extra"
    )
    query = query.where("TABLE_SCHEMA = :schema AND TABLE_NAME = :table")
    query = query.order_by("ORDINAL_POSITION")

    query = query.bind("schema", table.schema.name)
    query = query.bind("table", table.name)

    result = query.execute()
    return result
