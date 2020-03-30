'''Defines the report "sessions" that queries the sys.x$session view
for active queries. There is support for specifying what to order by
and in which direction, and the maximum number of rows to include in
the result.'''

SORT_ALLOWED = {
    'thread': 'thd_id',
    'connection': 'conn_id',
    'user': 'user',
    'db': 'db',
    'latency': 'statement_latency',
    'memory': 'current_memory',
}


def sessions(session, args, options):
    '''Defines the report itself. The session argument is the MySQL
    Shell session object, args are unnamed arguments, and options
    are the named options.'''
    sys = session.get_schema('sys')
    session_view = sys.get_table('x$session')
    query = session_view.select(
        'thd_id', 'conn_id', 'user', 'db',
        'sys.format_statement(current_statement) AS statement',
        'sys.format_time(statement_latency) AS latency',
        'format_bytes(current_memory) AS memory')

    # Set what to sort the rows by (--sort)
    try:
        order_by = options['sort']
    except KeyError:
        order_by = 'latency'

    if order_by in ('latency', 'memory'):
        direction = 'DESC'
    else:
        direction = 'ASC'
    query.order_by('{0} {1}'.format(SORT_ALLOWED[order_by], direction))

    # If ordering by latency, ignore those statements with a NULL latency
    # (they are not active)
    if order_by == 'latency':
        query.where('statement_latency IS NOT NULL')

    # Set the maximum number of rows to retrieve is --limit is set.
    try:
        limit = options['limit']
    except KeyError:
        limit = 0
    if limit > 0:
        query.limit(limit)

    result = query.execute()
    report = [result.get_column_names()]
    for row in result.fetch_all():
        report.append(list(row))

    return {'report': report}
