USE online_bookstore;

-- -------------------------------------------------------
-- USERS
-- -------------------------------------------------------
INSERT INTO users (username, email, password_hash, role)
VALUES
  ('manager1',  'manager1@example.com',  'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'manager'),
  ('customer1', 'customer1@example.com', 'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'customer'),
  ('customer2', 'customer2@example.com', 'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'customer'),
  ('customer3', 'customer3@example.com', 'pbkdf2:sha256:260000$wSGPLW0varIymCee$da228c3be22d5a86ae5b41fb2d4367dfa3055483878d13c0a545847971fc8f3a', 'customer');

-- -------------------------------------------------------
-- BOOKS (TOP 50)  — SAME AS BEFORE
-- -------------------------------------------------------
INSERT INTO books (title, author, price_buy, price_rent) VALUES
  -- (same exact 50 books from previous seed — KEEP THEM HERE)
  ('A Tale of Two Cities', 'Charles Dickens', 14.99, 5.99),
  ('The Little Prince', 'Antoine de Saint-Exupéry', 12.99, 4.99),
  ('The Alchemist', 'Paulo Coelho', 13.99, 4.99),
  ('Harry Potter and the Philosopher''s Stone', 'J. K. Rowling', 19.99, 6.99),
  ('And Then There Were None', 'Agatha Christie', 11.99, 4.49),
  ('Dream of the Red Chamber', 'Cao Xueqin', 18.99, 6.49),
  ('The Hobbit', 'J. R. R. Tolkien', 16.99, 5.99),
  ('The Lord of the Rings', 'J. R. R. Tolkien', 24.99, 7.99),
  ('She: A History of Adventure', 'H. Rider Haggard', 10.99, 3.99),
  ('The Da Vinci Code', 'Dan Brown', 15.99, 5.99),
  ('Harry Potter and the Chamber of Secrets', 'J. K. Rowling', 19.99, 6.99),
  ('Harry Potter and the Prisoner of Azkaban', 'J. K. Rowling', 19.99, 6.99),
  ('Harry Potter and the Goblet of Fire', 'J. K. Rowling', 21.99, 7.49),
  ('Harry Potter and the Order of the Phoenix', 'J. K. Rowling', 21.99, 7.49),
  ('The Catcher in the Rye', 'J. D. Salinger', 12.99, 4.49),
  ('To Kill a Mockingbird', 'Harper Lee', 14.99, 5.49),
  ('Pride and Prejudice', 'Jane Austen', 11.99, 3.99),
  ('The Hunger Games', 'Suzanne Collins', 14.99, 5.49),
  ('Catching Fire', 'Suzanne Collins', 14.99, 5.49),
  ('Mockingjay', 'Suzanne Collins', 14.99, 5.49),
  ('The Tale of Peter Rabbit', 'Beatrix Potter', 9.99, 3.49),
  ('The Very Hungry Caterpillar', 'Eric Carle', 8.99, 2.99),
  ('The Lion, the Witch and the Wardrobe', 'C. S. Lewis', 11.99, 3.99),
  ('The Godfather', 'Mario Puzo', 15.99, 5.99),
  ('The Fault in Our Stars', 'John Green', 13.99, 4.99),
  ('Gone Girl', 'Gillian Flynn', 14.99, 5.49),
  ('The Book Thief', 'Markus Zusak', 13.99, 4.99),
  ('All the Light We Cannot See', 'Anthony Doerr', 16.99, 5.99),
  ('1984', 'George Orwell', 12.99, 4.49),
  ('Animal Farm', 'George Orwell', 9.99, 3.49),
  ('The Great Gatsby', 'F. Scott Fitzgerald', 12.99, 4.49),
  ('The Lord of the Flies', 'William Golding', 11.99, 3.99),
  ('Brave New World', 'Aldous Huxley', 12.99, 4.49),
  ('Crime and Punishment', 'Fyodor Dostoevsky', 15.99, 5.99),
  ('War and Peace', 'Leo Tolstoy', 19.99, 7.49),
  ('Les Misérables', 'Victor Hugo', 18.99, 6.99),
  ('The Divine Comedy', 'Dante Alighieri', 17.99, 6.49),
  ('Don Quixote', 'Miguel de Cervantes', 17.99, 6.49),
  ('One Hundred Years of Solitude', 'Gabriel García Márquez', 15.99, 5.99),
  ('The Grapes of Wrath', 'John Steinbeck', 14.99, 5.49),
  ('Dune', 'Frank Herbert', 16.99, 5.99),
  ('The Chronicles of Narnia', 'C. S. Lewis', 24.99, 7.99),
  ('The Kite Runner', 'Khaled Hosseini', 13.99, 4.99),
  ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 14.99, 5.49),
  ('Fifty Shades of Grey', 'E. L. James', 13.99, 4.99),
  ('The Outsiders', 'S. E. Hinton', 11.99, 3.99),
  ('The Hobbit and The Lord of the Rings Box Set', 'J. R. R. Tolkien', 34.99, 9.99),
  ('The Plague', 'Albert Camus', 13.99, 4.99),
  ('Man''s Search for Meaning', 'Viktor E. Frankl', 12.99, 4.49),
  ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 14.99, 5.49);

-- -------------------------------------------------------
-- ORDERS (Each customer: 2–3 orders; at least 1 Pending)
-- -------------------------------------------------------

-- Customer1: user_id = 2
INSERT INTO orders (user_id, total_price, payment_status)
VALUES
  (2, 29.98, 'Paid'),     -- Order #1
  (2, 16.99, 'Pending'),  -- Order #2
  (2, 45.98, 'Paid');     -- Order #3

-- Customer2: user_id = 3
INSERT INTO orders (user_id, total_price, payment_status)
VALUES
  (3, 19.99, 'Pending'),  -- Order #4
  (3, 36.98, 'Paid'),     -- Order #5
  (3, 28.98, 'Paid');     -- Order #6

-- Customer3: user_id = 4
INSERT INTO orders (user_id, total_price, payment_status)
VALUES
  (4, 12.99, 'Paid'),     -- Order #7
  (4, 31.98, 'Pending'),  -- Order #8
  (4, 17.99, 'Paid');     -- Order #9


-- -------------------------------------------------------
-- ORDER ITEMS
-- Using sample book IDs from your seeded 50 books.
-- You can update the book numbers, but these will work.
-- -------------------------------------------------------

-- Orders for customer1
INSERT INTO order_items (order_id, book_id, type, price)
VALUES
  (1, 1, 'buy', 14.99),
  (1, 2, 'buy', 14.99),

  (2, 3, 'rent', 6.99),

  (3, 4, 'buy', 19.99),
  (3, 5, 'buy', 25.99);  -- sum = 45.98

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
