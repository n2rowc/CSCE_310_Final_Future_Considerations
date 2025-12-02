USE online_bookstore;

-- ========================================
-- USERS
-- ========================================
INSERT INTO users (username, email, password_hash, role)
VALUES
  ('manager1',  'manager1@example.com',  'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'manager'),
  ('customer1', 'customer1@example.com', 'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'customer'),
  ('customer2', 'customer2@example.com', 'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'customer'),
  ('customer3', 'customer3@example.com', 'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'customer');



-- ========================================
-- BOOKS (Top 50) WITH GENRE + YEAR
-- NOTE: If genre/year were added with ALTER TABLE,
-- this matches the updated structure.
-- ========================================
INSERT INTO books (title, author, price_buy, price_rent, genre, publication_year)
VALUES
  ('A Tale of Two Cities', 'Charles Dickens', 14.99, 5.99, 'Historical Fiction', 1859),
  ('The Little Prince', 'Antoine de Saint-Exupéry', 12.99, 4.99, 'Children', 1943),
  ('The Alchemist', 'Paulo Coelho', 13.99, 4.99, 'Fiction', 1988),
  ('Harry Potter and the Philosopher''s Stone', 'J. K. Rowling', 19.99, 6.99, 'Fantasy', 1997),
  ('And Then There Were None', 'Agatha Christie', 11.99, 4.49, 'Mystery', 1939),
  ('Dream of the Red Chamber', 'Cao Xueqin', 18.99, 6.49, 'Classic', 1791),
  ('The Hobbit', 'J. R. R. Tolkien', 16.99, 5.99, 'Fantasy', 1937),
  ('The Lord of the Rings', 'J. R. R. Tolkien', 24.99, 7.99, 'Fantasy', 1954),
  ('She: A History of Adventure', 'H. Rider Haggard', 10.99, 3.99, 'Adventure', 1887),
  ('The Da Vinci Code', 'Dan Brown', 15.99, 5.99, 'Thriller', 2003),
  ('Harry Potter and the Chamber of Secrets', 'J. K. Rowling', 19.99, 6.99, 'Fantasy', 1998),
  ('Harry Potter and the Prisoner of Azkaban', 'J. K. Rowling', 19.99, 6.99, 'Fantasy', 1999),
  ('Harry Potter and the Goblet of Fire', 'J. K. Rowling', 21.99, 7.49, 'Fantasy', 2000),
  ('Harry Potter and the Order of the Phoenix', 'J. K. Rowling', 21.99, 7.49, 'Fantasy', 2003),
  ('The Catcher in the Rye', 'J. D. Salinger', 12.99, 4.49, 'Classic', 1951),
  ('To Kill a Mockingbird', 'Harper Lee', 14.99, 5.49, 'Classic', 1960),
  ('Pride and Prejudice', 'Jane Austen', 11.99, 3.99, 'Romance', 1813),
  ('The Hunger Games', 'Suzanne Collins', 14.99, 5.49, 'Dystopian', 2008),
  ('Catching Fire', 'Suzanne Collins', 14.99, 5.49, 'Dystopian', 2009),
  ('Mockingjay', 'Suzanne Collins', 14.99, 5.49, 'Dystopian', 2010),
  ('The Tale of Peter Rabbit', 'Beatrix Potter', 9.99, 3.49, 'Children', 1902),
  ('The Very Hungry Caterpillar', 'Eric Carle', 8.99, 2.99, 'Children', 1969),
  ('The Lion, the Witch and the Wardrobe', 'C. S. Lewis', 11.99, 3.99, 'Fantasy', 1950),
  ('The Godfather', 'Mario Puzo', 15.99, 5.99, 'Crime', 1969),
  ('The Fault in Our Stars', 'John Green', 13.99, 4.99, 'Young Adult', 2012),
  ('Gone Girl', 'Gillian Flynn', 14.99, 5.49, 'Thriller', 2012),
  ('The Book Thief', 'Markus Zusak', 13.99, 4.99, 'Historical Fiction', 2005),
  ('All the Light We Cannot See', 'Anthony Doerr', 16.99, 5.99, 'Historical Fiction', 2014),
  ('1984', 'George Orwell', 12.99, 4.49, 'Dystopian', 1949),
  ('Animal Farm', 'George Orwell', 9.99, 3.49, 'Political Satire', 1945),
  ('The Great Gatsby', 'F. Scott Fitzgerald', 12.99, 4.49, 'Classic', 1925),
  ('The Lord of the Flies', 'William Golding', 11.99, 3.99, 'Classic', 1954),
  ('Brave New World', 'Aldous Huxley', 12.99, 4.49, 'Dystopian', 1932),
  ('Crime and Punishment', 'Fyodor Dostoevsky', 15.99, 5.99, 'Classic', 1866),
  ('War and Peace', 'Leo Tolstoy', 19.99, 7.49, 'Classic', 1869),
  ('Les Misérables', 'Victor Hugo', 18.99, 6.99, 'Classic', 1862),
  ('The Divine Comedy', 'Dante Alighieri', 17.99, 6.49, 'Classic', 1320),
  ('Don Quixote', 'Miguel de Cervantes', 17.99, 6.49, 'Classic', 1605),
  ('One Hundred Years of Solitude', 'Gabriel García Márquez', 15.99, 5.99, 'Magical Realism', 1967),
  ('The Grapes of Wrath', 'John Steinbeck', 14.99, 5.49, 'Historical Fiction', 1939),
  ('Dune', 'Frank Herbert', 16.99, 5.99, 'Sci-Fi', 1965),
  ('The Chronicles of Narnia', 'C. S. Lewis', 24.99, 7.99, 'Fantasy', 1956),
  ('The Kite Runner', 'Khaled Hosseini', 13.99, 4.99, 'Historical Fiction', 2003),
  ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 14.99, 5.49, 'Thriller', 2005),
  ('Fifty Shades of Grey', 'E. L. James', 13.99, 4.99, 'Romance', 2011),
  ('The Outsiders', 'S. E. Hinton', 11.99, 3.99, 'Young Adult', 1967),
  ('The Hobbit and The Lord of the Rings Box Set', 'J. R. R. Tolkien', 34.99, 9.99, 'Fantasy', 2001),
  ('The Plague', 'Albert Camus', 13.99, 4.99, 'Classic', 1947),
  ('Man''s Search for Meaning', 'Viktor E. Frankl', 12.99, 4.49, 'Psychology', 1946),
  ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 14.99, 5.49, 'Self-Help', 2016);



-- ========================================
-- INVENTORY (1 row per book)
-- (Default 10 copies each)
-- ========================================
INSERT INTO inventory (book_id, total_copies, available_copies)
SELECT id, 10, 10 FROM books;



-- ========================================
-- ORDERS (same as before)
-- ========================================

-- Customer1: user_id = 2
INSERT INTO orders (user_id, total_price, payment_status)
VALUES
  (2, 29.98, 'Paid'),
  (2, 16.99, 'Pending'),
  (2, 45.98, 'Paid');

-- Customer2: user_id = 3
INSERT INTO orders (user_id, total_price, payment_status)
VALUES
  (3, 19.99, 'Pending'),
  (3, 36.98, 'Paid'),
  (3, 28.98, 'Paid');

-- Customer3: user_id = 4
INSERT INTO orders (user_id, total_price, payment_status)
VALUES
  (4, 12.99, 'Paid'),
  (4, 31.98, 'Pending'),
  (4, 17.99, 'Paid');



-- ========================================
-- ORDER ITEMS (same as before)
-- ========================================

-- Orders for customer1
INSERT INTO order_items (order_id, book_id, type, price)
VALUES
  (1, 1, 'buy', 14.99),
  (1, 2, 'buy', 14.99),

  (2, 3, 'rent', 6.99),

  (3, 4, 'buy', 19.99),
  (3, 5, 'buy', 25.99);

-- Orders for customer2
INSERT INTO order_items (order_id, book_id, type, price)
VALUES
  (4, 7, 'buy', 19.99),

  (5, 10, 'buy', 15.99),
  (5, 11, 'buy', 20.99),

  (6, 12, 'rent', 12.99),
  (6, 13, 'rent', 15.99);

-- Orders for customer3
INSERT INTO order_items (order_id, book_id, type, price)
VALUES
  (7, 15, 'buy', 12.99),

  (8, 16, 'buy', 14.99),
  (8, 17, 'buy', 16.99),

  (9, 20, 'buy', 17.99);



-- ========================================
-- RENTALS (only for order_items where type='rent')
-- ========================================
-- order_item_id values correspond exactly to AUTOINCREMENT order

-- Customer1 rental (order 2 → order_item_id = 3)
INSERT INTO rentals (order_item_id, user_id, book_id, rented_at, due_date)
VALUES
  (3, 2, 3, NOW(), DATE_ADD(NOW(), INTERVAL 14 DAY));

-- Customer2 rentals (order 6 → order_item_id = 8 and 9)
INSERT INTO rentals (order_item_id, user_id, book_id, rented_at, due_date)
VALUES
  (8, 3, 12, NOW(), DATE_ADD(NOW(), INTERVAL 14 DAY)),
  (9, 3, 13, NOW(), DATE_ADD(NOW(), INTERVAL 14 DAY));


-- ========================================
-- REVIEWS & RATINGS (Future Consideration)
-- ========================================

INSERT INTO reviews (user_id, book_id, rating, review_text)
VALUES
  -- Customer 1 reviews
  (2, 1, 5, 'A timeless classic. Really enjoyed it.'),
  (2, 4, 5, 'Loved the world-building and magic.'),
  (2, 15, 4, 'Interesting themes and well-written.'),

  -- Customer 2 reviews
  (3, 7, 5, 'One of my favorite fantasy books ever.'),
  (3, 10, 4, 'Good pacing and suspense throughout.'),
  (3, 28, 5, 'Beautiful storytelling; highly recommend.'),

  -- Customer 3 reviews
  (4, 20, 4, 'Great dystopian energy and strong characters.'),
  (4, 31, 3, 'Well-written but a bit slow in the middle.'),
  (4, 47, 5, 'A powerful book that really made me think.');
