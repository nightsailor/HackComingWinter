SET sql_safe_updates = FALSE;
USE defaultdb;
DROP DATABASE IF EXISTS test CASCADE;


CREATE DATABASE test;
USE test;

CREATE TABLE users (
    user_id INT8 NOT NULL DEFAULT unique_rowid(),
    username VARCHAR(60) NULL,
    email VARCHAR NULL,
    password VARCHAR NULL,
    create_date TIMESTAMP NULL,
    CONSTRAINT "primary" PRIMARY KEY (user_id ASC),
    FAMILY "primary" (user_id, username, email, password, create_date)
  );