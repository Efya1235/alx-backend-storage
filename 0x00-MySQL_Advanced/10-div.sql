-- Using a SQL script, a function called SafeDiv is created
-- that divides the first number by the second number or 
-- returns 0 if the second number is also 0.
DELIMITER $$ ;
CREATE FUNCTION SafeDiv(
	a INT,
	b INT
)
RETURNS FLOAT
DETERMINISTIC
BEGIN
	DECLARE container FLOAT;
	IF b = 0 THEN
		RETURN 0;
        END IF;
        SET container = (a * 1.0) / b;
        RETURN container;
END;$$
DELIMITER ;
