SELECT JSON_PRETTY(HISTOGRAM) AS Histogram
  FROM information_schema.COLUMN_STATISTICS
 WHERE SCHEMA_NAME = 'world'
       AND TABLE_NAME = 'city_histogram'
       AND COLUMN_NAME = 'CountryCode'\G
