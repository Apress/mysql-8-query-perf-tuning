SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME,
       HISTOGRAM->>'$."histogram-type"' AS Histogram_Type,
       CAST(HISTOGRAM->>'$."last-updated"' AS DATETIME(6)) AS Last_Updated,
       CAST(HISTOGRAM->>'$."sampling-rate"' AS DECIMAL(4,2)) AS Sampling_Rate,
       JSON_LENGTH(HISTOGRAM->'$.buckets') AS Number_of_Buckets,
       CAST(HISTOGRAM->'$."number-of-buckets-specified"'AS UNSIGNED) AS Number_of_Buckets_Specified
  FROM information_schema.COLUMN_STATISTICS;
