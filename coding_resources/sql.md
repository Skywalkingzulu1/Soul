# SQL Quick Reference

## Basic Queries
```sql
-- Select
SELECT * FROM users;
SELECT name, email FROM users WHERE age > 18;

-- Insert
INSERT INTO users (name, email) VALUES ('Alice', 'alice@email.com');

-- Update
UPDATE users SET email = 'new@email.com' WHERE id = 1;

-- Delete
DELETE FROM users WHERE id = 1;
```

## Filtering & Sorting
```sql
-- Where conditions
SELECT * FROM users WHERE age >= 21 AND city = 'NYC';
SELECT * FROM users WHERE name LIKE 'A%';  -- Starts with A
SELECT * FROM users WHERE age IN (18, 21, 25);

-- Order by
SELECT * FROM users ORDER BY name ASC, age DESC;

-- Limit
SELECT * FROM users LIMIT 10 OFFSET 20;
```

## Joins
```sql
-- Inner join
SELECT u.name, o.total 
FROM users u 
INNER JOIN orders o ON u.id = o.user_id;

-- Left join
SELECT u.name, o.total 
FROM users u 
LEFT JOIN orders o ON u.id = o.user_id;

-- Multiple joins
SELECT * 
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON o.product_id = p.id;
```

## Aggregations
```sql
SELECT COUNT(*) FROM users;
SELECT SUM(amount) FROM orders;
SELECT AVG(age) FROM users;
SELECT MIN(price), MAX(price) FROM products;

-- Group by
SELECT city, COUNT(*) as users 
FROM users 
GROUP BY city 
HAVING COUNT(*) > 10;
```

## Subqueries
```sql
SELECT * FROM users 
WHERE age > (SELECT AVG(age) FROM users);

SELECT name FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE total > 100);
```

## Common Table Expressions (CTE)
```sql
WITH total_orders AS (
    SELECT user_id, COUNT(*) as orders 
    FROM orders 
    GROUP BY user_id
)
SELECT u.name, t.orders
FROM users u
JOIN total_orders t ON u.id = t.user_id;
```