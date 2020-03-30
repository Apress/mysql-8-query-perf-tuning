\use world_x
DROP TABLE IF EXISTS mvalue_index;
CREATE TABLE mvalue_index LIKE countryinfo;

INSERT INTO mvalue_index (doc)
SELECT doc
  FROM countryinfo;

UPDATE mvalue_index
   SET doc = JSON_INSERT(doc, '$.cities',
                         (SELECT JSON_ARRAYAGG(
                                    JSON_OBJECT(
                                       'district', district,
                                       'name', name,
                                       'population', Info->'$.Population'
                                    )
                                 )
                            FROM city
                           WHERE CountryCode = mvalue_index._id
                         )
                        );

SELECT JSON_PRETTY(doc->>'$.cities[*].name')
  FROM mvalue_index
 WHERE _id = 'AUS'\G

