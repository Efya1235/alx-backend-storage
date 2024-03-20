-- Script that generates a trigger to reduce an item's amount after adding a new order.
-- amount after adding a new order.
CREATE TRIGGER decrease_q AFTER INSERT ON orders FOR EACH ROW
UPDATE items SET quantity = quantity - NEW.number WHERE name=NEW.item_name;
