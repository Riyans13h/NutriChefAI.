-- =========================================================
-- NutriChef AI
-- MySQL Database Schema
-- =========================================================

-- Drop database if exists (optional for development)
-- DROP DATABASE IF EXISTS nutrichef;

-- Create database
CREATE DATABASE IF NOT EXISTS nutrichef;
USE nutrichef;

-- =========================================================
-- 1. USERS TABLE
-- Stores authentication and identity data
-- =========================================================

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 2. RECIPES TABLE
-- Stores high-level recipe metadata
-- =========================================================

CREATE TABLE recipes (
    recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    meal_type ENUM('Breakfast', 'Lunch', 'Dinner', 'Snack') NOT NULL,
    cuisine VARCHAR(100),
    diet_type ENUM('Veg', 'Non-Veg', 'Vegan') NOT NULL,
    time_to_cook INT NOT NULL,
    base_steps TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 3. INGREDIENTS TABLE
-- Stores normalized ingredient names
-- =========================================================

CREATE TABLE ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- =========================================================
-- 4. RECIPE_INGREDIENTS TABLE
-- Many-to-many relationship between recipes and ingredients
-- This table enables set-theoretic matching
-- =========================================================

CREATE TABLE recipe_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity FLOAT,
    unit VARCHAR(50),
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
        ON DELETE CASCADE
);

-- =========================================================
-- 5. NUTRITION TABLE
-- Stores verified nutrition values per recipe
-- =========================================================

CREATE TABLE nutrition (
    recipe_id INT PRIMARY KEY,
    calories FLOAT NOT NULL,
    protein FLOAT NOT NULL,
    carbs FLOAT NOT NULL,
    fat FLOAT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        ON DELETE CASCADE
);

-- =========================================================
-- 6. USER_FEEDBACK TABLE
-- Stores implicit feedback for reinforcement learning
-- =========================================================

CREATE TABLE user_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    reward INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        ON DELETE CASCADE
);

-- =========================================================
-- Indexes for performance optimization
-- =========================================================

CREATE INDEX idx_recipes_meal_type ON recipes(meal_type);
CREATE INDEX idx_recipes_diet_type ON recipes(diet_type);
CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_feedback_user ON user_feedback(user_id);
