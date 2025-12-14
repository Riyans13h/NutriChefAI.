-- =========================================================
-- NutriChef AI
-- Seed Data for Initial Development & Testing
-- =========================================================

USE nutrichef;

-- =========================================================
-- 1. INGREDIENTS
-- =========================================================

INSERT INTO ingredients (name) VALUES
('rice'),
('onion'),
('tomato'),
('paneer'),
('potato'),
('garlic'),
('ginger'),
('oil'),
('salt'),
('pepper'),
('curd'),
('green chilli'),
('cumin');

-- =========================================================
-- 2. RECIPES
-- =========================================================

INSERT INTO recipes (name, meal_type, cuisine, diet_type, time_to_cook, base_steps) VALUES
(
    'Paneer Tomato Curry',
    'Lunch',
    'Indian',
    'Veg',
    30,
    'Heat oil. Add cumin, ginger, garlic. Add onions and sauté. Add tomatoes and cook till soft. Add paneer and simmer.'
),
(
    'Jeera Rice',
    'Lunch',
    'Indian',
    'Veg',
    20,
    'Cook rice separately. Heat oil, add cumin seeds, then mix rice and salt.'
),
(
    'Curd Rice',
    'Breakfast',
    'Indian',
    'Veg',
    15,
    'Cook rice. Cool slightly. Mix curd, salt, and pepper.'
),
(
    'Potato Stir Fry',
    'Dinner',
    'Indian',
    'Veg',
    25,
    'Heat oil. Add cumin, onions, potatoes, salt, and cook until crispy.'
);

-- =========================================================
-- 3. RECIPE INGREDIENT MAPPING
-- =========================================================

-- Paneer Tomato Curry
INSERT INTO recipe_ingredients VALUES
(1, 2, NULL, NULL),  -- onion
(1, 3, NULL, NULL),  -- tomato
(1, 4, NULL, NULL),  -- paneer
(1, 6, NULL, NULL),  -- garlic
(1, 7, NULL, NULL),  -- ginger
(1, 8, NULL, NULL),  -- oil
(1, 9, NULL, NULL),  -- salt
(1, 13, NULL, NULL); -- cumin

-- Jeera Rice
INSERT INTO recipe_ingredients VALUES
(2, 1, NULL, NULL),  -- rice
(2, 8, NULL, NULL),  -- oil
(2, 9, NULL, NULL),  -- salt
(2, 13, NULL, NULL); -- cumin

-- Curd Rice
INSERT INTO recipe_ingredients VALUES
(3, 1, NULL, NULL),  -- rice
(3, 11, NULL, NULL), -- curd
(3, 9, NULL, NULL),  -- salt
(3, 10, NULL, NULL); -- pepper

-- Potato Stir Fry
INSERT INTO recipe_ingredients VALUES
(4, 5, NULL, NULL),  -- potato
(4, 2, NULL, NULL),  -- onion
(4, 8, NULL, NULL),  -- oil
(4, 9, NULL, NULL),  -- salt
(4, 13, NULL, NULL); -- cumin

-- =========================================================
-- 4. NUTRITION DATA
-- =========================================================

INSERT INTO nutrition (recipe_id, calories, protein, carbs, fat) VALUES
(1, 320, 14, 18, 22),   -- Paneer Tomato Curry
(2, 280, 6, 52, 6),    -- Jeera Rice
(3, 260, 8, 45, 5),    -- Curd Rice
(4, 300, 5, 40, 10);   -- Potato Stir Fry
