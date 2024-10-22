-- Create the Testing database and switch to it
CREATE DATABASE IF NOT EXISTS PizzaInfo;
USE PizzaInfo;

-- Create the Login table
CREATE TABLE IF NOT EXISTS UserInfo (
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL, 
    LoginID INT AUTO_INCREMENT,
    PRIMARY KEY (LoginID)
);

-- TRUNCATE TABLE Login;

Select * from UserInfo;
