-- Create 'foodItems' table
CREATE TABLE IF NOT EXISTS `foodItems` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT 'Name of the food item (e.g., Apple, Chicken Breast)',
    `description` TEXT COMMENT 'Detailed description of the food item',
    `brand` VARCHAR(255) COMMENT 'Brand name if applicable (e.g., Quaker, Dole)',
    `serving_size_unit` VARCHAR(50) DEFAULT 'g' COMMENT 'Unit for serving size (e.g., g, ml, piece)',
    `serving_size_value` DECIMAL(10, 2) DEFAULT 100.00 COMMENT 'Value for the standard serving size (e.g., 100 for 100g)',
    `calories_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Total calories per defined serving size',
    `protein_grams_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Protein in grams per defined serving size',
    `carbohydrates_grams_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Carbohydrates in grams per defined serving size',
    `fat_grams_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Fat in grams per defined serving size',
    `fiber_grams_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Fiber in grams per defined serving size',
    `sugar_grams_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Sugar in grams per defined serving size',
    `sodium_mg_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Sodium in milligrams per defined serving size',
    `cholesterol_mg_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Cholesterol in milligrams per defined serving size',
    `saturated_fat_grams_per_serving` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Saturated fat in grams per defined serving size',
    `source` VARCHAR(100) DEFAULT 'user_added' COMMENT 'Source of the food item data (e.g., USDA, user_added, branded_db)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create 'loggedFoods' table
CREATE TABLE IF NOT EXISTS `loggedFoods` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT 'ID of the user who logged the food',
    `food_item_id` INT NOT NULL COMMENT 'ID of the food item logged',
    `logged_quantity_value` DECIMAL(10, 2) NOT NULL COMMENT 'Quantity of the food logged (e.g., 150 for 150g, or 1 for 1 serving)',
    `logged_quantity_unit` VARCHAR(50) NOT NULL DEFAULT 'g' COMMENT 'Unit for the logged quantity (e.g., g, ml, serving, piece)',
    `logged_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp when the food was logged',
    `meal_type` VARCHAR(50) COMMENT 'Type of meal (e.g., breakfast, lunch, dinner, snack)',
    `notes` TEXT COMMENT 'Optional notes about the food log entry',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_logged_foods_user_id` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_logged_foods_food_item_id` FOREIGN KEY (`food_item_id`) REFERENCES `foodItems`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;