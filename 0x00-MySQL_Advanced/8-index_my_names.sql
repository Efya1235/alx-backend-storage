-- script that builds the table names and the first
-- letter of the names into an index called idx_name_first.
CREATE INDEX idx_name_first ON names(name(1))
