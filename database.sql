-- Create the Testing database and switch to it
CREATE DATABASE IF NOT EXISTS PizzaInfo;
USE PizzaInfo;

-- Create the Login table
CREATE TABLE IF NOT EXISTS UserInfo (
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL, 
    LoginID INT AUTO_INCREMENT,
    Points INT(10) default 0,
    isAdmin boolean not null default false,
    Address varchar(255),
    profile_pic VARCHAR(255),
    PRIMARY KEY (LoginID)
);

-- Create the reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    LoginID int not null,
    username VARCHAR(100) NOT NULL,
    rating INT NOT NULL,
    review_text TEXT NOT NULL,
    header VARCHAR(255) NOT NULL,
    photo LONGBLOB,
    date_made DATE NOT NULL,
    FOREIGN KEY (LoginID) references UserInfo(LoginID)
);

-- Create the Menu table
CREATE TABLE IF NOT EXISTS Menu (
    itemID INT AUTO_INCREMENT PRIMARY KEY,
    itemName VARCHAR(50) NOT NULL UNIQUE,
    itemCategory VARCHAR(50) NOT NULL,
    itemPrice DECIMAL(5, 2) NOT NULL
);

-- Create the PizzaSizes table
CREATE TABLE IF NOT EXISTS PizzaSizes (
    sizeID INT AUTO_INCREMENT PRIMARY KEY,
    itemID INT NOT NULL,
    size VARCHAR(10) NOT NULL,
    price DECIMAL(5, 2) NOT NULL,
    FOREIGN KEY (itemID) REFERENCES Menu(itemID) ON DELETE CASCADE,
    UNIQUE (itemID, size)
);
-- Create the MenuSizes table to associate sizes with menu items (specific to Pizza)
CREATE TABLE IF NOT EXISTS MenuSizes (
    menuSizeID INT AUTO_INCREMENT PRIMARY KEY,
    itemID INT NOT NULL, -- Links to Menu
    sizeID INT NOT NULL, -- Links to PizzaSizes
    FOREIGN KEY (itemID) REFERENCES Menu(itemID) ON DELETE CASCADE,
    FOREIGN KEY (sizeID) REFERENCES PizzaSizes(sizeID) ON DELETE CASCADE
);

-- Create the Toppings table (independent of pizzas)
CREATE TABLE IF NOT EXISTS Toppings (
    toppingID INT AUTO_INCREMENT PRIMARY KEY,
    toppingName VARCHAR(50) NOT NULL UNIQUE,
    price DECIMAL(5, 2) NOT NULL 
);

-- Create the OrderHistory table to track orders
CREATE TABLE IF NOT EXISTS OrderHistory (
    orderID INT AUTO_INCREMENT PRIMARY KEY,
    LoginID INT NOT NULL,
    itemID INT NOT NULL,
    sizeID INT,
    date_ordered DATE NOT NULL,
    quantity INT DEFAULT 1,
    price  DECIMAL(10, 2),
    FOREIGN KEY (LoginID) REFERENCES UserInfo(LoginID) ON DELETE CASCADE,
    FOREIGN KEY (itemID) REFERENCES Menu(itemID) ON DELETE CASCADE,
    FOREIGN KEY (sizeID) REFERENCES PizzaSizes(sizeID)
);

-- Create the OrderToppings table to associate toppings with orders
CREATE TABLE IF NOT EXISTS OrderToppings (
    orderToppingID INT AUTO_INCREMENT PRIMARY KEY,
    orderID INT NOT NULL,
    toppingID INT NOT NULL,
    FOREIGN KEY (orderID) REFERENCES OrderHistory(orderID) ON DELETE CASCADE,
    FOREIGN KEY (toppingID) REFERENCES Toppings(toppingID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Categories (
    categoryID INT AUTO_INCREMENT PRIMARY KEY,
    itemCategory VARCHAR(50) NOT NULL UNIQUE,
    categoryOrder INT DEFAULT 0
);

-- Create the inventory table
-- Optional table which will subtract inventory quantity - order quantity
-- Stock/quantity will be 99 and will reset each day
create table if not exists inventory (
    inventoryID int primary key AUTO_INCREMENT,
    itemID int,
    quantity int,
    FOREIGN KEY (itemID) references menu(itemID)
);

-- Insert menu list
insert into menu(itemName, itemPrice, itemCategory) VALUES
('Plain Cheese Pizza', 8.99, 'Pizza'), 
('White Pizza', 9.25,'Pizza'),
('Extra Cheese Pizza', 10.95, 'Pizza'),
('Onions & Green Pepper Pizza', 10.95, 'Pizza'),
('Salami Pizza',10.95,'Pizza'),     
('Mushroom Pizza', 10.95,'Pizza'),
('Olive Pizza', 10.95,'Pizza'),
('Anchovies Pizza', 10.95,'Pizza'),
('Sausage Pizza', 10.95,'Pizza'), 
('Bacon Pizza', 10.95,'Pizza'),
('Spinach Pizza', 11.95,'Pizza'),
('Broccoli Pizza', 11.95,'Pizza'),
('Veggie Pizza', 11.95,'Pizza'),
('Hawaiian Pizza', 11.95,'Pizza'),
('Greek Pizza', 11.95,'Pizza'), 
('Steak Pizza', 11.95,'Pizza'),
('Shrimp Pizza', 11.95,'Pizza'), 
('Philly Cheesesteak Pizza', 11.95,'Pizza'),
('Chicken Pizza', 11.95,'Pizza'), 
('Buffalo Chicken Pizza', 11.95,'Pizza'),
('Meat Lovers Pizza', 12.25,'Pizza'), 
('Fiesta Special Pizza', 12.25,'Pizza'),
('Pepperoni Pizza', 10.95, 'Pizza'),
('Beef Pepperoni Pizza', 10.75,'Pizza'), 
('Beef Sausage Pizza', 10.95,'Pizza'),
('BBQ Chicken Pizza', 10.95,'Pizza'), 
('Pineapple Pizza', 10.95,'Pizza'),
('Ham Pizza', 10.95,'Pizza'), 
('Onion Pizza', 10.95,'Pizza'),
('Green Pepper Pizza', 10.95,'Pizza'), 
('Jalapeno Pizza', 14.50,'Pizza'),
('Mini Cheese Pizza', 5.25,'Pizza'), 
('Mini Pizza with One Topping', 5.95,'Pizza'),
('Chicken Mini Pizza', 6.50,'Pizza'), 
('Steak Mini Pizza', 6.50,'Pizza'),
('Veggie Mini Pizza', 6.50,'Pizza'), 
('Fiesta Special Breakfast', 8.95, 'Breakfast'),
('Eggs & Hot Cakes', 8.95,'Breakfast'),
('Eggs & French Toast', 8.95,'Breakfast'),
('Eggs, Potatoes, Toast & Coffee', 7.95,'Breakfast'),
('Eggs, Potatoes, Toast', 7.95,'Breakfast'),
('2 Eggs, Potatoes, Toast & Any Meat', 8.95,'Breakfast'),
('3 Eggs, Potatoes, Toast & Any Meat', 9.25,'Breakfast'),
('Eggs, Hot Cakes, Bacon & Sausage', 9.25,'Breakfast'),
('Eggs, French Toast, Bacon & Sausage', 8.25,'Breakfast'),
('Eggs, Waffles, Bacon & Sausage', 8.25,'Breakfast'),
('French Toast', 7.95,'Breakfast'),
('Hot Cakes', 7.95,'Breakfast'),
('Waffles', 7.95,'Breakfast'),
('French Toast & Any Meat', 9.25,'Breakfast'),
('Hot Cakes & Any Meat', 9.25,'Breakfast'),
('Waffles & Any Meat', 9.25,'Breakfast'),
('Omelette', 8.95,'Breakfast'),
('Mushroom Omelette', 9.50,'Breakfast'),
('Cheese Omelette', 9.50,'Breakfast'),
('Ham Omelette', 9.50,'Breakfast'),
('Western Omelette', 9.50,'Breakfast'),
('Steak Omelette', 9.50,'Breakfast'),
('Broccoli Omelette', 9.50,'Breakfast'),
('Spinach Omelette', 9.50,'Breakfast'),
('Greek Omelette', 9.50,'Breakfast'),
('Florentine Omelette', 9.50,'Breakfast'),
('Bacon Omelette', 9.50,'Breakfast'),
('Veggie Omelette', 9.50,'Breakfast'),
('Side of Scrapple', 4.50,'Breakfast'),
('Side of Beef Scrapple', 4.50,'Breakfast'),
('Side of Beef Sausage', 4.50,'Breakfast'),
('Side of Turkey Sausage', 4.50,'Breakfast'),
('Side of Breakfast Sausage', 4.50,'Breakfast'),
('Side of Italian Sausage', 4.95,'Breakfast'),
('Side of Beef Bacon', 5.50,'Breakfast'),
('Side of Turkey Bacon', 4.50,'Breakfast'),
('French Fries', 4.50,'Sides'),
('Curly Fries', 5.50,'Sides'),
('Cheese Fries', 8.25,'Sides'),
('Pizza Fries', 7.25,'Sides'),
('Cheddar Cheese Fries', 6.50,'Sides'),
('Home Fries', 4.95,'Sides'),
('Mozzarella Fries', 8.95,'Sides'),
('Buffalo Mozzarella Fries', 7.95,'Sides'),
('Buffalo Chicken Mozzarella Fries', 7.50,'Sides'),
('Mega Fries', 8.25,'Sides'),
('Chili Cheese Fries', 8.95,'Sides'),
('Chili', 8.95,'Sides'),
('Potato Skins', 8.25,'Sides'),
('Lettuce & Tomato', 1.95,'Sides'),
('Sweet Peppers', 0.50,'Sides'),
('Hot Peppers', 0.50,'Sides'),
('Jalapeno Poppers', 7.25,'Sides'),
('Onion Rings', 4.75,'Sides'),
('Mozzarella Sticks', 7.50,'Sides'),
('Coleslaw', 4.95,'Sides'),
('Garlic Bread', 2.25,'Sides'),
('Garlic Pizza Bread', 3.75,'Sides'),
('Potato Salad', 4.95,'Sides'),
('Macaroni Salad', 4.95,'Sides'),
('Apple Sauce', 4.95,'Sides'),
('Green Vegetable', 4.95,'Sides'),
('Kaiser Roll', 1.50,'Sides'),
('Grilled Cheese', 5.95,'Sides'),
('Salad', 5.95, 'Salads'),
('Egg Salad', 8.95, 'Salads'),
('Caesar Salad', 8.95, 'Salads'),
('Turkey & Cheese Salad', 12.95, 'Salads'),
('Antipasto Salad', 12.95, 'Salads'),
('King Salad', 12.95, 'Salads'),
('Queen Salad', 12.95, 'Salads'),
('Fiesta Salad', 12.95, 'Salads'),
('Greek Salad', 12.95, 'Salads'),
('Cheese Salad', 12.95, 'Salads'),
('Grilled Chicken Salad', 12.95, 'Salads'),
('Grilled Chicken Caesar Salad', 12.95, 'Salads'),
('Grilled Buffalo Chicken Salad', 12.95, 'Salads'),
('Chicken Finger Salad', 12.95, 'Salads'),
('Buffalo Chicken Finger Salad', 12.95, 'Salads'),
('House Special Salad', 14.95, 'Salads'),
('Shrimp Caesar Salad', 14.95, 'Salads'),
('Flounder Caesar Salad', 12.95, 'Salads'),
('Salmon Garden Salad', 14.95, 'Salads'),
('Salmon Caesar Salad', 14.95, 'Salads'),
('Chicken Wings', 10.95, 'Wings'),
('Chicken Wings Platter', 14.95, 'Wings'),
('Wing Dings', 11.75, 'Wings'),
('Wing Dings Platter', 13.95, 'Wings'),
('Boneless Wings', 10.95, 'Wings'),
('Boneless Wings Platter', 14.95, 'Wings'),
('Plain Stromboli', 6.50,'Strombolis'),
('Veal Stromboli', 7.95,'Strombolis'),
('Vegetarian Stromboli', 7.95,'Strombolis'),
('Meatball Stromboli', 7.95,'Strombolis'),
('Italian Stromboli', 7.95,'Strombolis'),
('Olive Stromboli', 7.95,'Strombolis'),
('Sausage Stromboli', 7.95,'Strombolis'),
('Steak Stromboli', 8.30,'Strombolis'),
('Pepperoni Stromboli', 7.95,'Strombolis'),
('Tuna Stromboli', 8.30,'Strombolis'),
('Chicken Stromboli', 7.95,'Strombolis'),
('Gyro Stromboli', 7.95,'Strombolis'),
('Beef Pepperoni Stromboli', 7.95,'Strombolis'),
('Beef Sausage Stromboli', 7.95,'Strombolis'),
('Buffalo Chicken Stromboli', 7.95,'Strombolis'),
('House Special Stromboli', 13.50,'Strombolis'),
('Chicken Salad Sandwich', 7.25,'Sandwiches'),
('Tuna Salad Sandwich', 7.95,'Sandwiches'),
('Sliced Turkey Sandwich', 7.95,'Sandwiches'),
('B.L.T Sandwich', 7.25,'Sandwiches'),
('Mixed Cheese Sandwich', 7.25,'Sandwiches'),
('Broiled Ham & Cheese Sandwich', 7.25,'Sandwiches'),
('Roast Beef & Cheese Sandwich', 7.25,'Sandwiches'),
('Corned Beef & Cheese Sandwich', 7.25,'Sandwiches'),
('Grilled Cheese Sandwich', 6.25,'Sandwiches'),
('Grilled Cheese & Tomato Sandwich', 7.25,'Sandwiches'),
('Grilled Cheese & Ham Sandwich', 7.25,'Sandwiches'),
('Grilled Cheese & Bacon Sandwich', 7.25,'Sandwiches'),
('Cheeseburger Melt Sandwich', 7.95,'Sandwiches'),
('Egg & Cheese Sandwich', 5.95,'Sandwiches'),
('Bacon, Egg & Cheese Sandwich', 6.95,'Sandwiches'),
('Steak, Egg & Cheese Sandwich', 6.95,'Sandwiches'),
('Ham, Egg & Cheese Sandwich', 7.25,'Sandwiches'),
('Turkey Bacon, Egg & Cheese Sandwich', 6.95,'Sandwiches'),
('Beef Bacon, Egg & Cheese Sandwich', 6.95,'Sandwiches'),
('Italian Sausage Sandwich', 7.95,'Sandwiches'),
('Tuna Melt with Tomato Sandwich', 7.95,'Sandwiches'),
('Marinated Chicken Breast Sandwich', 7.95,'Sandwiches'),
('Hot Corned Beef Sandwich', 6.95,'Sandwiches'),
('Hot Roast Beef Sandwich', 12.25,'Sandwiches'),
('Hot Roast Turkey Sandwich', 12.25,'Sandwiches'),
('Turkey Double Decker Sandwich', 9.50,'Sandwiches'),
('Tuna Salad Double Decker Sandwich', 9.50,'Sandwiches'),
('Chicken Salad Double Decker Sandwich', 9.50,'Sandwiches'),
('Ham & Cheese Double Decker Sandwich', 9.50,'Sandwiches'),
('Roast Beef & Cheese Double Decker Sandwich', 9.50,'Sandwiches'),
('Corned Beef & Cheese Double Decker Sandwich', 9.50,'Sandwiches'),
('B.L.T Double Decker Sandwich', 9.50,'Sandwiches'),
('Cheeseburger Club Double Decker Sandwich', 9.50,'Sandwiches'),
('Turkey Cheeseburger Club Double Decker Sandwich', 9.50,'Sandwiches'),
('Veggie Cheeseburger Club Double Decker Sandwich', 9.50,'Sandwiches'),
('Grilled Chicken Club Double Decker Sandwich', 9.50,'Sandwiches'),
('Hamburger', 5.95,'Burgers'),
('Hamburger Platter', 9.95,'Burgers'),
('Cheeseburger', 6.50,'Burgers'),
('Cheeseburger Platter', 10.50,'Burgers'),
('Pizza Burger', 6.95,'Burgers'),
('Pizza Burger Platter', 11.95,'Burgers'),
('Turkey Cheeseburger', 6.95,'Burgers'),
('Turkey Cheeseburger Platter', 10.25,'Burgers'),
('Veggie Cheeseburger', 7.25,'Burgers'),
('Veggie Cheeseburger Platter', 10.50,'Burgers'),
('Bacon Hamburger', 6.95,'Burgers'),
('Bacon Hamburger Platter', 10.95,'Burgers'),
('Bacon Cheeseburger', 7.95,'Burgers'),
('Bacon Cheeseburger Platter', 11.50,'Burgers'),
('Grilled Chicken Breast Burger', 7.25,'Burgers'),
('Grilled Chicken Breast Burger Platter', 11.25,'Burgers'),
('Honey Chicken Sandwich', 7.50,'Burgers'),
('Honey Chicken Sandwich Platter', 11.25,'Burgers'),
('Teriyaki Chicken Sandwich', 7.95,'Burgers'),
('Teriyaki Chicken Sandwich Platter', 10.95,'Burgers'),
('Buffalo Chicken Sandwich', 7.50,'Burgers'),
('Buffalo Chicken Sandwich Platter', 11.25,'Burgers'),
('Double Cheeseburger', 9.50,'Burgers'),
('Double Cheeseburger Platter', 12.50,'Burgers'),
('Grilled Cajun Chicken Burger', 7.50,'Burgers'),
('Grilled Cajun Chicken Burger Platter', 12.50,'Burgers'),
('Salmon Cheeseburger', 7.95,'Burgers'),
('Salmon Cheeseburger Platter', 11.95,'Burgers'),
('Italian Hoagie', 9.25, 'Hoagies'),
('American Cheese Hoagie', 9.25, 'Hoagies'),
('Ham & Cheese Hoagie', 9.25, 'Hoagies'),
('Turkey & Cheese Hoagie', 9.25, 'Hoagies'),
('Tuna Salad Hoagie', 9.25, 'Hoagies'),
('Chicken Salad Hoagie', 9.25, 'Hoagies'),
('Provolone Cheese Hoagie', 9.25, 'Hoagies'),
('Cooked Salami Hoagie', 9.25, 'Hoagies'),
('Veggie Hoagie', 9.25, 'Hoagies'),
('Turkey Hoagie', 9.25, 'Hoagies'),
('Roast Beef Hoagie', 9.25, 'Hoagies'),
('Corned Beef Hoagie', 9.25, 'Hoagies'),
('Grilled Chicken Hoagie', 9.25, 'Hoagies'),
('Meatball Hoagie', 9.25, 'Hoagies'),
('Fish Fillet Hoagie', 9.25, 'Hoagies'),
('Chicken Finger Hoagie', 9.25, 'Hoagies'),
('Chicken Breast Hoagie', 9.25, 'Hoagies'),
('Veal Hoagie', 9.25, 'Hoagies'),
('B.L.T Hoagie', 9.25, 'Hoagies'),
('Italian Grinder',9.25,'Grinders'),
('American Cheese Grinder',9.25,'Grinders'),
('Ham & Cheese Grinder',9.25,'Grinders'),
('Turkey & Cheese Grinder',9.25,'Grinders'),
('Tuna Salad Grinder',9.25,'Grinders'),
('Chicken Salad Grinder',9.25,'Grinders'),
('Provolone Cheese Grinder',9.25,'Grinders'),
('Cooked Salami Grinder',9.25,'Grinders'),
('Veggie Grinder',9.25,'Grinders'),
('Turkey Grinder',9.25,'Grinders'),
('Roast Beef Grinder',9.25,'Grinders'),
('Corned Beef Grinder',9.25,'Grinders'),
('Grilled Chicken Grinder',9.25,'Grinders'),
('Eggplant Grinder',9.25,'Grinders'),
('Meatball Grinder',9.25,'Grinders'),
('Fish Fillet Grinder',9.25,'Grinders'),
('Chicken Finger Grinder',9.25,'Grinders'),
('Chicken Breast Grinder',9.25,'Grinders'),
('Italian Sausage Grinder',9.25,'Grinders'),
('Veal Grinder',9.25,'Grinders'),
('Chicken Parmigiana Grinder',9.25,'Grinders'),
('B.L.T Grinder',9.25,'Grinders'),
('Cheeseburger Grinder',9.25,'Grinders'),
('Turkey Cheese Wrap',9.99,'Wraps'),
('Tuna Salad Wrap',9.99,'Wraps'),
('Chicken Salad Wrap',9.99,'Wraps'),
('Chicken Finger Wrap',9.99,'Wraps'),
('Steak Wrap',10.25,'Wraps'),
('Veggie Wrap',9.99,'Wraps'),
('Buffalo Chicken Wrap',10.25,'Wraps'),
('Chicken Caesar Wrap',9.99,'Wraps'),
('Cajun Breast Wrap',9.99,'Wraps'),
('Chicken Florentine Wrap',9.99,'Wraps'),
('Salmon Wrap',11.95,'Wraps'),
('Chicken Quesadilla',10.25,'Quesadillas'),
('Steak Quesadilla',10.25,'Quesadillas'),
('Veggie Quesadilla',10.25,'Quesadillas'),
('Cajun Chicken Quesadilla',10.25,'Quesadillas'),
('Salmon Quesadilla',11.95,'Quesadillas'),
('Bacon Quesadilla',10.25,'Quesadillas'),
('Buffalo Chicken Quesadilla',10.25,'Quesadillas'),
('Shrimp Quesadilla',11.95,'Quesadillas'),
('Steak Sandwich',9.75,'Steaks'),
('Cheesesteak Sandwich',10.75,'Steaks'),
('Mushroom Cheesesteak Sandwich',11.95,'Steaks'),
('Pizza Steak Sandwich',11.95,'Steaks'),
('Pepperoni Cheesesteak Sandwich',11.95,'Steaks'),
('Cheesesteak Hoagie',11.95,'Steaks'),
('Bacon Cheesesteak Sandwich',12.25,'Steaks'),
('Fiesta Special Cheesesteak Sandwich',13.95,'Steaks'),
('Cheesesteak Platter',13.25,'Steaks'),
('Double Cheesesteak Sandwich',14.50,'Steaks'),
('Double Pizza Steak Sandwich',14.95,'Steaks'),
('Double Cheesesteak Hoagie',14.95,'Steaks'),
('Chicken Steak Sandwich',9.95,'Chicken Steaks'),
('Chicken Cheesesteak Sandwich',10.75,'Chicken Steaks'),
('Buffalo Chicken Cheesesteak Sandwich',10.95,'Chicken Steaks'),
('Buffalo Chicken Cheesesteak Platter',12.95,'Chicken Steaks'),
('Chicken Cheesesteak Hoagie',11.95,'Chicken Steaks'),
('Chicken Cheesesteak Deluxe Sandwich',13.25,'Chicken Steaks'),
('Double Chicken Cheesesteak Sandwich',14.50,'Chicken Steaks'),
('Cajun Chicken Cheesesteak Sandwich',12.95,'Chicken Steaks'),
('Mushroom Chicken Cheesesteak Sandwich',11.95,'Chicken Steaks'),
('Fiesta Chicken Cheesesteak Sandwich',13.95,'Chicken Steaks'),
('Fiesta Burrito',10.50,'Fiesta Specials'),
('Fiesta Beef Bowl',10.50,'Fiesta Specials'),
('Fiesta Chicken Bowl',10.50,'Fiesta Specials'),
('Spaghetti with Sauce',10.95,'Pasta'),
('Spaghetti with Meatballs',12.95,'Pasta'),
('Spaghetti with Sausage',12.95,'Pasta'),
('Manicotti',11.95,'Pasta'),
('Ravioli',12.95,'Pasta'),
('Stuffed Shells',11.95,'Pasta'),
('Lasagna',12.50,'Pasta'),
('Chicken Parmigiana Pasta',12.95,'Pasta'),
('Veal Parmigiana Pasta',12.50,'Pasta'),
('Eggplant Parmigiana Pasta',12.50,'Pasta'),
('Porkchops Center Cut Platter',13.95,'Dinner Platters'),
('Chopped Steak Platter',13.95,'Dinner Platters'),
('Baked Meatloaf Platter',13.95,'Dinner Platters'),
('Tuna Salad Platter',12.50,'Cold Platters'),
('Chicken Salad Platter',12.50,'Cold Platters'),
('Broiled Ham & Cheese Platter',12.50,'Cold Platters'),
('Sliced Turkey & Cheese Platter',12.50,'Cold Platters'),
('Corned Beef Special Platter',7.95,'Cold Platters'),
('Roast Beef Special Platter',7.95,'Cold Platters'),
('Turkey Special Platter',7.95,'Cold Platters'),
('Reuben Deluxe Platter',11.50,'Cold Platters'),
('Chicken Cacciatore', 13.95,'Special Platters'),
('Chicken Marsala', 13.95,'Special Platters'),
('Chicken Piccanti', 13.95,'Special Platters'),
('Chicken Scampi', 13.95,'Special Platters'),
('Chicken Curry', 13.95,'Special Platters'),
('Shrimp Oriental', 13.95,'Special Platters'),
('Chicken Stir Fry', 13.95,'Special Platters'),
('Chicken Oriental', 13.95,'Special Platters'),
('Chicken Teriyaki', 13.95,'Special Platters'),
('Shrimp Scampi', 13.95,'Special Platters'),
('Shrimp Stir Fry', 13.95,'Special Platters'),
('Cajun Chicken', 13.95,'Special Platters'),
('Fish & Chips', 13.95,'Seafood'),
('Deviled Crab', 13.95,'Seafood'),
('Shrimp in a Basket', 13.95,'Seafood'),
('Fried Flounder', 14.95,'Seafood'),
('Fried Shrimp', 14.95,'Seafood'),
('Fried Scallops', 14.95,'Seafood'),
('Seafood Combination', 15.95,'Seafood'),
('Fillet Salmon Platter', 15.95,'Seafood'),
('Lamb Gyro Sandwich', 8.25,'Greek'),
('Lamb Gyro Platter', 12.50,'Greek'),
('Chicken Gyro Sandwich', 8.25,'Greek'),
('Chicken Gyro Platter', 12.50,'Greek'),
('Chicken Souvlaki Sandwich',7.95,'Greek'),
('Chicken Souvlaki Platter', 12.95,'Greek'),
('Lamb Souvlaki Sandwich', 8.50,'Greek'),
('Lamb Souvlaki Platter', 12.95,'Greek'),
('Spinach Pie Platter', 10.95,'Greek'),
('Chicken Nuggets', 6.95,'Chicken'),
('Chicken Nuggets Platter', 11.50,'Chicken'),
('Half Broiled Chicken', 9.95,'Chicken'),
('Half Broiled Chicken Platter', 13.95,'Chicken'),
('Half Broiled BBQ Chicken', 9.95,'Chicken'),
('Half Broiled BBQ Chicken Platter', 13.95,'Chicken'),
('Chicken Fingers', 8.95,'Chicken'),
('Chicken Fingers Platter', 13.95,'Chicken'),
('Half BBQ Chicken', 9.95,'Chicken'),
('Half BBQ Chicken Platter', 11.95,'Chicken'),
('Fried Chicken Wings', 10.50,'Chicken'),
('Fried Chicken Wings Platter', 13.50,'Chicken'),
('Fried Chicken', 10.99,'Chicken'),
('Fried Chicken Platter', 13.95,'Chicken'),
('Whole BBQ Chicken Platter', 17.95,'Chicken'),
('Whole Broiled Chicken Platter', 17.95,'Chicken'),
('Kids Chicken Nuggets & Fries', 7.50,'Kids'),
('Kids Chicken Fingers & Fries', 7.50,'Kids'),
('Kids Chicken Wings & Fries', 7.50,'Kids'),
('Kids Spaghetti', 7.50,'Kids'),
('Kids Flouder & Fries', 7.50,'Kids'),
('Kids Cheeseburger & Fries', 7.50,'Kids'),
('Kids Pizza with One Topping', 5.25,'Kids'),
('Cheesecake', 4.25,'Dessert'),
('Cake', 4.25,'Dessert'),
('Assorted Pies', 3.50,'Dessert'),
('Corn Muffins', 3.25,'Dessert'),
('Cinnamon Buns', 3.25,'Dessert'),
('Bagels', 2.50,'Dessert'),
('Rice Pudding', 4.50,'Dessert'),
('Banana Pudding', 4.50,'Dessert'),
('Ice Cream', 1.95,'Dessert'),
('Mistic', 2.75,'Drinks'),
('Snapple', 2.75,'Drinks'),
('Water', 1.00,'Drinks'),
('Red Bull', 2.99,'Drinks'),
('Arizona', 2.50,'Drinks'),
('Minutemaid', 2.75,'Drinks'),
('Calypso', 2.95,'Drinks'),
('Nesquick', 2.75,'Drinks'),
('Coffee', 1.55,'Drinks'),
('Milkshake', 6.25,'Drinks'),
('Nantucket', 2.95,'Drinks'),
('Soda', 1.75,'Drinks'),
('Gatorade', 2.99,'Drinks'),
('Vitamin Water', 2.99,'Drinks'),
('Gold Peak', 2.99,'Drinks'),
('Aloe', 2.99,'Drinks');

INSERT INTO PizzaSizes (itemID, size, price) VALUES
(1, 'Small', 8.99), (1, 'Large', 12.95), (1, 'Giant', 18.95),
(2, 'Small', 9.25), (2, 'Large', 12.97), (2, 'Giant', 18.95),
(3, 'Small', 10.95), (3, 'Large', 15.50), (3, 'Giant', 24.50),
(4, 'Small', 10.95), (4, 'Large', 15.50), (4, 'Giant', 23.95),
(5, 'Small', 10.95), (5, 'Large', 15.50), (5, 'Giant', 24.50),
(6, 'Small', 10.95), (6, 'Large', 15.50), (6, 'Giant', 24.50),
(7, 'Small', 10.95), (7, 'Large', 15.50), (7, 'Giant', 23.85),
(8, 'Small', 10.95), (8, 'Large', 15.50), (8, 'Giant', 23.95),
(9, 'Small', 10.95), (9, 'Large', 15.50), (9, 'Giant', 24.50),
(10, 'Small', 10.95), (10, 'Large', 15.50), (10, 'Giant', 26.00),
(11, 'Small', 11.95), (11, 'Large', 15.50), (11, 'Giant', 26.00),
(12, 'Small', 11.95), (12, 'Large', 15.50), (12, 'Giant', 26.00),
(13, 'Small', 11.95), (13, 'Large', 15.50), (13, 'Giant', 26.00),
(14, 'Small', 11.95), (14, 'Large', 15.50), (14, 'Giant', 26.00),
(15, 'Small', 11.95), (15, 'Large', 16.95), (15, 'Giant', 26.00),
(16, 'Small', 11.95), (16, 'Large', 16.95), (16, 'Giant', 26.00),
(17, 'Small', 11.95), (17, 'Large', 16.95), (17, 'Giant', 26.00),
(18, 'Small', 11.95), (18, 'Large', 16.95), (18, 'Giant', 26.00),
(19, 'Small', 11.95), (19, 'Large', 16.95), (19, 'Giant', 26.00),
(20, 'Small', 11.95), (20, 'Large', 16.95), (20, 'Giant', 27.00),
(21, 'Small', 12.25), (21, 'Large', 16.95), (21, 'Giant', 26.20),
(22, 'Small', 12.25), (22, 'Large', 16.95), (22, 'Giant', 26.20),
(23, 'Small', 10.95), (23, 'Large', 15.50), (23, 'Giant', 24.50),
(24, 'Small', 10.75), (24, 'Large', 15.50), (24, 'Giant', 24.90),
(25, 'Small', 10.95), (25, 'Large', 14.25), (25, 'Giant', 23.95),
(26, 'Small', 10.95), (26, 'Large', 15.95), (26, 'Giant', 26.00),
(27, 'Small', 10.95), (27, 'Large', 15.95), (27, 'Giant', 24.50),
(28, 'Small', 10.95), (28, 'Large', 14.50), (28, 'Giant', 23.90),
(29, 'Small', 10.95), (29, 'Large', 14.50), (29, 'Giant', 23.90),
(30, 'Small', 10.95), (30, 'Large', 13.95), (30, 'Giant', 23.90),
(31, 'Large', 14.50), (31, 'Giant', 25.00);

-- Insert into Toppings
INSERT INTO Toppings (toppingName, price) VALUES
('Extra Cheese', 1.50),
('Pepperoni', 2.00),
('Mushrooms', 1.75),
('Onions', 1.25),
('Green Peppers', 1.25),
('Olives', 1.50),
('Bacon', 2.50);

-- Sort categories
INSERT INTO Categories (itemCategory, categoryOrder) VALUES
('Pizza', 1),
('Strombolis', 2),
('Sandwiches', 3),
('Burgers', 4),
('Wraps', 5),
('Quesadillas', 6),
('Wings', 7),
('Seafood', 8),
('Sides', 9),
('Salads', 10),
('Pasta', 11),
('Fiesta Specials', 12),
('Special Platters', 13),
('Dinner Platters', 14),
('Cold Platters', 15),
('Greek', 16),
('Breakfast', 17),
('Drinks', 18),
('Steaks', 19),
('Chicken Steaks', 20),
('Chicken', 21),
('Hoagies', 22), 
('Grinders', 23),
('Kids', 24),
('Dessert', 25);