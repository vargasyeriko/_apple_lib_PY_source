--SELECT

SELECT * FROM film;
--challenge #_1 ; "*" will give you all table
SELECT first_name, last_name, email FROM customer;

--UNIQUE VALUES

--Disticnt What are the unique manes that are in the column 
SELECT DISTINCT 
-- how many different release dates we have
SELECT DISTINCT(release_year) FROM film;
--SELECT DISTINCTrelease_year FROM film; same was yo write it but differently
--Disticnt rental dates?
SELECT DISTINCT rental_rate FROM film;
--Challenge #_2 -- showing different ratings from the films shown in table film
SELECT DISTINCT rating FROM film;

--MAY13
--COUNT

--SELECT COUNT(name) FROM table 
-- count of unique rating in table
SELECT COUNT(DISTINCT rating) FROM film;
--column amount in table "payment"
SELECT amount FROM payment;
--How many unique amounts? A: use two functions
SELECT COUNT(DISTINCT amount) FROM payment;

--SELECT WHERE
--select rows where something desired  from table where something desired
--SELECT name,choice FROM table WHERE name = '' and choice = ''
SELECT * FROM customer
WHERE first_name = 'Jared';
--Combine with lofical operators --can change the * for a specific column and apply count
SELECT * FROM film
WHERE rental_rate > 4
--choose the one that are expensive to replace
AND replacement_cost >= 19.99
--Now I just want the rating having the R label
AND rating = 'R';

--count 
SELECT COUNT(*) FROM film
WHERE rental_rate > 4
--choose the one that are expensive to replace
AND replacement_cost >= 19.99
--Now I just want the rating having the R label
AND rating = 'R';

--OR
--count # of movies that have ratings R & PG-13
SELECT COUNT(*) FROM film
WHERE rating = 'R' OR rating = 'PG-13';

--Movies that have everything but ratings of R
SELECT title,rating  FROM film
WHERE rating != 'R';

--CHALLENGE #_3
--  someone forgot their wallet with name NANCY Thomas, find her email!
SELECT email FROM customer
WHERE first_name = 'Nancy' AND last_name = 'Thomas';

--CHALLENGE #_3.1
-- guy wants to know what the movie "Outlaw Hanky" is about, give the description of movie
SELECT description FROM film
WHERE title = 'Outlaw Hanky';

--CHALLENGE #_3.2
-- guy is late on the movie return, sent a letter to '259 Ipoh Drive'; its needed to call him as well
SELECT phone FROM address
WHERE address = '259 Ipoh Drive';

--May 14

-- order
SELECT * FROM customer

--acending order specifically 
--Order by firt_name ASC
--decending order specifically 
Order by first_name DESC;

-- order by id first and then by firts name
SELECT store_id, first_name, last_name FROM customer
Order by store_id, first_name;

--you can do this way too
SELECT store_id, first_name, last_name FROM customer
Order by store_id DESC, first_name ASC;

--LIMIT

SELECT * FROM payment
WHERE amount != 0.00
ORDER BY payment_date DESC
--what were the most recent payments
LIMIT 5;

--to get an idea of what we can have in tables
SELECT * FROM payment
LIMIT 1;





