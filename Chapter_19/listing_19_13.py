queries = [
    ("SELECT * FROM `city` WHERE `ID` = ?", [130, 3805]),
    ("SELECT * FROM `city` WHERE `CountryCode` = ?", ['AUS', 'CHN', 'IND']),
    ("SELECT * FROM `country` WHERE CODE = ?", ['DEU', 'GBR', 'BRA', 'USA']),
]

for query in queries:
    sql = query[0]
    parameters = query[1]
    for param in parameters:
        result = session.run_sql(sql, (param,))


