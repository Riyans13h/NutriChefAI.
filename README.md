# 🍽 NutriChefAI – Intelligent Ingredient-Based Meal Recommendation System

## Overview
**NutriChefAI** is an intelligent recipe recommendation and generation system that creates **feasible, nutrition-aware recipes strictly based on ingredients available with the user**.

Unlike traditional recipe platforms or pure LLM-based systems, NutriChefAI **prevents hallucination**, **enforces ingredient feasibility**, **grounds all generation in verified data** using a hybrid AI architecture, and **improves over time using reinforcement learning**.

## 🎯 Core Idea
> **Ingredients are decided by data science logic, not by the language model.**

The LLM is used **only to explain and format recipes**, never to invent ingredients or nutritional values.

## 🏗 System Architecture
The system follows a sequential pipeline architecture:

1.  **Input**: User provides available ingredients and nutritional goal.
2.  **Ingredient Processing**:
    *   **Normalizer**: Standardizes ingredient names and quantities.
    *   **Matching Engine**: Finds recipes containing these ingredients from the database.
    *   **Feasibility Filter**: Discards recipes requiring too many unavailable ingredients.
3.  **Scoring & Ranking**:
    *   **Scoring Engine**: Calculates a final score for each recipe based on ingredient coverage, nutritional alignment with the user's goal, and a penalty for missing items.
    *   **Ranking**: Sorts recipes by their final score.
4.  **Intelligent Generation**:
    *   **Retrieval**: Fetches the top-ranked, relevant recipe instructions and details from the vector store.
    *   **Context Building**: Prepares a precise context package for the LLM.
    *   **Constrained LLM Generation**: The LLM formats and explains the retrieved recipe, strictly forbidden from adding new ingredients.
5.  **Output & Learning**:
    *   **Final Output**: User receives a feasible, well-formatted recipe.
    *   **Feedback Loop**: User ratings and engagement metrics are fed to a Reinforcement Learning (RL) agent.
    *   **Continuous Improvement**: The RL agent analyzes feedback to dynamically update the weights in the scoring formula, optimizing future recommendations.

**Data Layer**: The system interacts with a structured MySQL database for recipes and a ChromaDB vector store for efficient semantic search.

## 🧮 Ingredient-Constrained Logic
Ingredient feasibility is enforced using **set theory**:
*   **User Ingredients (U)**: What the user has available.
*   **Recipe Ingredients (R)**: What a recipe requires.

**Calculation**:
*   **Matched Ingredients**: `M = U ∩ R`
*   **Missing Ingredients**: `X = R − U`
*   **Coverage Score**: `|M| / |R|`

Recipes with insufficient coverage are **discarded before reaching the AI layer**.

## 📊 Mathematical Scoring Framework
The final score determines recipe ranking and is calculated as:
```
FinalScore = w₁ × Coverage + w₂ × HealthScore + w₃ × Penalty
```
*(Weights w₁, w₂, w₃ are dynamically adjusted via Reinforcement Learning)*

This ensures **ingredient feasibility is prioritized**, **nutrition goals are respected**, and recommendations remain **practical**.

### Nutrition-Aware Scoring Formulas
*   **Weight Loss**: `Health = 2P - 0.5H - F - 0.01C`
*   **Muscle Gain**: `Health = 3P + 0.5H - 0.2F`
*   **Balanced Diet**: `Health = 2P + H - F`

Where: **P** = Protein, **H** = Fiber, **F** = Fat, **C** = Calories.

## 🤖 Reinforcement Learning Feedback Loop
The system learns from user interactions to improve personalization.

**RL Model**:
*   **State**: User profile + available ingredients + nutritional goal.
*   **Action**: Recommending a specific recipe.
*   **Reward**: User rating (1-5 stars) combined with engagement metrics.
*   **Policy**: The algorithm that maps states to actions (continuously optimized).

**Learning Process**: The system adjusts the scoring weights (`w₁, w₂, w₃`) using feedback. A simplified update rule is:
`Updated_Weight = Current_Weight + α × (Reward - Expected_Reward) × Feature_Value`
Where `α` is the learning rate.

## 🔍 Retrieval-Augmented Generation (RAG)
To ensure accuracy, the LLM does not generate recipes from scratch.

**Process**:
1.  The user query (ingredients + goal) is converted into a numerical vector (embedding).
2.  This vector is used to search for the most relevant existing recipes in the ChromaDB vector store.
3.  The text from these top recipes is packaged as "context."
4.  This context, along with strict instructions, is sent to the LLM.
5.  The LLM reformats and explains the retrieved recipe based solely on the provided context.

**Why RAG?**: Prevents hallucination, ensures factual correctness, and keeps the LLM grounded in real, vetted data.

## ✍️ Prompt Control Strategy
The LLM receives strict instructions that enforce:

**❌ Prohibited**:
*   Inventing new ingredients not in the context.
*   Guessing nutritional values.

**✅ Required**:
*   Explicitly listing any missing ingredients the recipe requires.
*   Outputting in a clean, structured format.

## 🛠 Technology Stack
*   **Backend**: Python, Flask, SQLAlchemy, MySQL
*   **AI & Data Science**: NumPy, Pandas, Scikit-learn, OpenAI Embeddings, ChromaDB, Custom RL/RLlib
*   **Frontend**: HTML, CSS, JavaScript (for feedback collection)

## ✅ Key Advantages
*   **Feasible Recipes**: Strictly based on user's available ingredients.
*   **Hallucination-Free**: Grounded generation via RAG.
*   **Explainable Logic**: Transparent, mathematical scoring.
*   **Personalized**: Adapts to health goals (weight loss, muscle gain, etc.).
*   **Self-Improving**: Continuously optimizes via Reinforcement Learning.
*   **Production-Ready**: Modular and testable architecture.

## ⚠ Limitations
*   Dependent on the quality and breadth of the underlying recipe database.
*   Incurs costs for external embedding APIs.
*   Initial nutrition scoring is rule-based.
*   Requires consistent user feedback for effective RL optimization.

## 🔮 Future Scope
*   Integration with smart refrigerators for automatic inventory tracking.
*   Ingredient ranking based on expiry dates to reduce waste.
*   Automated weekly meal planning.
*   Development of a mobile application.
*   Implementation of advanced multi-agent RL systems.

---

## 🏁 Conclusion
NutriChefAI demonstrates a responsible and effective hybrid approach, combining **classical data science logic** with **modern generative AI**. By enforcing hard constraints on ingredients, grounding outputs in retrieved data, and adapting through user feedback via reinforcement learning, the system delivers **practical, accurate, and continuously improving** recipe recommendations.