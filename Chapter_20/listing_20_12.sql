CREATE SCHEMA IF NOT EXISTS chapter_20;

DELIMITER $$

CREATE PROCEDURE chapter_20.testproc()
    SQL SECURITY INVOKER
    NOT DETERMINISTIC
    MODIFIES SQL DATA
BEGIN
    DECLARE v_iter, v_id int unsigned DEFAULT 0;
    DECLARE v_name char(35) CHARSET latin1;

    SET v_id = CEIL(RAND()*4079);
    SELECT Name
      INTO v_name
      FROM world.city
     WHERE ID = v_id;

    SELECT *
      FROM world.city
     WHERE Name = v_name;
END$$

DELIMITER ;
