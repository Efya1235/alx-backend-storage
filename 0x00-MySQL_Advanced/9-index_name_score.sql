-- script that builds the first letter of each name, the score
-- and the table names into an index called idx_name_first_score.
CREATE INDEX idx_name_first_score on names(name(1), score)
