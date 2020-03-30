SELECT (Row_ID - 1) AS Bucket_Number,
       SUBSTRING_INDEX(Bucket_Value1, ':', -1) AS Bucket_Lower_Value,
       SUBSTRING_INDEX(Bucket_Value2, ':', -1) AS Bucket_Upper_Value,
       ROUND(Cumulative_Frequency * 100, 2) AS Cumulative_Frequency, 
       ROUND((Cumulative_Frequency - LAG(Cumulative_Frequency, 1, 0) OVER()) * 100, 2) AS Frequency,
       Number_of_Values
  FROM information_schema.COLUMN_STATISTICS
       INNER JOIN JSON_TABLE(
          histogram->'$.buckets', 
          '$[*]' COLUMNS(
               Row_ID FOR ORDINALITY,
               Bucket_Value1 varchar(42) PATH '$[0]',
               Bucket_Value2 varchar(42) PATH '$[1]',
               Cumulative_Frequency double PATH '$[2]',
               Number_of_Values int unsigned PATH '$[3]'
          )
       ) buckets
 WHERE SCHEMA_NAME  = 'world'
       AND TABLE_NAME = 'city_histogram'
       AND COLUMN_NAME = 'CountryCode'
 ORDER BY Row_ID;
