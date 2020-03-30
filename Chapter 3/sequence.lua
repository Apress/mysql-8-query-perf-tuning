-- Validate that a command was provided
if sysbench.cmdline.command == nil then
    error("Command is required. Supported commands: " ..
          "prepare, run, cleanup, help")
end

-- Specify the supported options for this test
sysbench.cmdline.options = {
    skip_trx = {"Don't start explicit transactions and " ..
                "execute all queries in the AUTOCOMMIT mode",
                false},
    table_size = {"The number of rows per table. Supported " ..
                  "values: 1-99999", 1},
    tables = {"The number of tables", 1}
}

-- Initialize the script
-- Initialize the global variables used in the rest of the script
function thread_init()
    -- Initialize the database driver and connections
    db = sysbench.sql.driver()
    cnx = db:connect()
end

-- Clean up after the test
function thread_done()
    -- Close the connection to the database
    cnx:disconnect()
end

-- Called for each iteration
function event()
    -- Check the --skip_trx option which determines
    -- whether explicit transactions are required.
    if not sysbench.opt.skip_trx then
        cnx:query("BEGIN")
    end

    -- Execute the customer test
    do_increment()

    -- If necessary, commit the transaction
    if not sysbench.opt.skip_trx then
        cnx:query("COMMIT")
    end
end

-- Generate the table name from the table number
function gen_table_name(table_num)
    return string.format("sbtest%d", table_num)
end

-- Generate the key from an id
function gen_key(id)
    return string.format("sbkey%d", id)
end

-- Increment the counter and fetch the new value
function do_increment()
    -- Choose a random table and id
    -- among the tables and rows available
    table_num = math.random(sysbench.opt.tables)
    table_name = gen_table_name(table_num)
    id = math.random(sysbench.opt.table_size)
    key = gen_key(id)
    query = string.format([[
UPDATE %s
   SET val = LAST_INSERT_ID(val+1)
 WHERE id = '%s']], table_name, key)
    cnx:query(query)
    cnx:query("SELECT LAST_INSERT_ID()")
end

-- Prepare the table
-- Can be parallelized up to the number of tables
function do_prepare()
    -- The script only supports up to 99999 rows
    -- as the id column is a varchar(10) and five
    -- characters is used by 'sbkey'
    assert(sysbench.opt.table_size > 0 and
           sysbench.opt.table_size < 100000,
           "Only 1-99999 rows per table is supported.")

    -- Initialize the database driver and connection
    local db = sysbench.sql.driver()
    local cnx = db:connect()

    -- Create table based on thread id
    for i = sysbench.tid % sysbench.opt.threads + 1,
            sysbench.opt.tables,
            sysbench.opt.threads do
        create_table(cnx, i)
    end

    -- Disconnect
    cnx:disconnect()
end

-- Create the Nth table
function create_table(cnx, table_num)
    table_name = gen_table_name(table_num)
    print(string.format(
          "Creating table '%s'...", table_name))

    -- Drop the table if it exists
    query = string.format(
        "DROP TABLE IF EXISTS %s", table_name)
    cnx:query(query)

    -- Create the new table
    query = string.format([[
CREATE TABLE %s (
  id varchar(10) NOT NULL,
  val bigint unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
)]], table_name)
    cnx:query(query)

    -- Insert the rows inside a transaction
    cnx:query("BEGIN")
    for i = 1, sysbench.opt.table_size, 1 do
        query = string.format([[
INSERT INTO %s (id)
VALUES ('%s')]], table_name, gen_key(i))
        cnx:query(query)
    end
    cnx:query("COMMIT")
end

-- Cleanup after the test
function cleanup()
    -- Initialize the database driver and connection
    local db = sysbench.sql.driver()
    local cnx = db:connect()

    -- Drop each table
    for i = 1, sysbench.opt.tables, 1 do
        table_name = gen_table_name(i)
        print(string.format(
              "Dropping table '%s' ...", table_name))
        query = string.format(
            "DROP TABLE IF EXISTS %s", table_name)
        cnx:query(query)
    end

    -- Disconnect
    cnx:disconnect()
end

-- Specify the actions other than run that support
-- execution in parallel.
-- (Other supported actions are found based on the
-- function name except 'help' that is built-in.)
sysbench.cmdline.commands = {
    prepare = {do_prepare, sysbench.cmdline.PARALLEL_COMMAND}
}
