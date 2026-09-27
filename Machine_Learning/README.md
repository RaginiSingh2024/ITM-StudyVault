# E-Commerce Customer Purchase Prediction

A Machine Learning mini project that predicts whether an e-commerce customer is likely to make a purchase based on customer and website-behaviour features.

## Team Members

| Name | Roll No. |
|---|---|
| **Ragini Singh** | 1500967240232 |
| **Sakshi Shinghole** | 150096724056 |

---

## Project Overview

Customer purchase prediction is a practical Machine Learning problem in the E-Commerce domain. Online businesses can use customer information and website interaction data to understand purchase behaviour and identify customers who are more likely to complete a purchase.

In this project, we build and compare three classification models to predict the `PurchaseStatus` of a customer:

1. Logistic Regression
2. Decision Tree Classifier
3. Random Forest Classifier

The project follows the complete Machine Learning workflow, including data understanding, data cleaning, preprocessing, exploratory data analysis, model training, evaluation, model comparison, best-model selection, and final prediction.

---

## Problem Statement

The objective of this project is to predict whether a customer will make a purchase using available customer and website-behaviour features. The prediction can help an e-commerce business better understand customer behaviour and support data-driven marketing and engagement strategies.

---

## Objectives

- Understand the given customer purchase dataset.
- Clean and preprocess the data.
- Explore relationships between customer features and purchase behaviour.
- Perform meaningful Exploratory Data Analysis (EDA).
- Train multiple classification models.
- Evaluate the models using Accuracy, Precision, Recall, and F1-score.
- Compare model performance and select the best model.
- Demonstrate purchase prediction for a new customer.
- Discuss limitations and possible future improvements.

---

## Dataset

### Dataset File

`customer_purchase_data.csv`

### Dataset Details

- **Initial records:** 1,500
- **Columns:** 9
- **Features:** 8
- **Target variable:** `PurchaseStatus`
- **Missing values:** None
- **Duplicate records:** 112 duplicates were identified and removed during preprocessing
- **Records after duplicate removal:** 1,388

### Features

| Feature | Description |
|---|---|
| `Age` | Customer age |
| `Gender` | Encoded gender value |
| `AnnualIncome` | Customer annual income |
| `NumberOfPurchases` | Number of previous purchases |
| `ProductCategory` | Encoded product category |
| `TimeSpentOnWebsite` | Time spent by the customer on the website |
| `LoyaltyProgram` | Whether the customer is part of the loyalty program |
| `DiscountsAvailed` | Number of discounts availed |
| `PurchaseStatus` | Target: 0 = No Purchase, 1 = Purchase |

### Dataset Source

The notebook uses the supplied project dataset file `customer_purchase_data.csv`. The original external/public source of this exact dataset is not specified in the project notebook, so no external source is claimed here.

---

## Machine Learning Problem

This is a **binary classification** problem because the target variable has two possible outcomes:

- `0` → No Purchase
- `1` → Purchase

---

## Data Preprocessing

The following preprocessing steps were performed:

1. Checked the dataset structure and data types.
2. Checked for missing values.
3. Identified duplicate records.
4. Removed 112 duplicate records.
5. Verified that `PurchaseStatus` contains only binary values (`0` and `1`).
6. Separated input features (`X`) and target (`y`).
7. Split the data into training and testing sets using an 80:20 ratio.
8. Used stratification so that the target class distribution is maintained between training and testing data.
9. Applied feature scaling for Logistic Regression using `StandardScaler`.

The supplied dataset already represents categorical/binary variables numerically, so additional one-hot encoding was not required.

---

## Exploratory Data Analysis

The project includes more than the required five visualizations.

### EDA Visualizations

1. Purchase Status Distribution
2. Age Distribution by Purchase Status
3. Annual Income by Purchase Status
4. Time Spent on Website by Purchase Status
5. Loyalty Program vs Purchase Status
6. Correlation Heatmap
7. Number of Previous Purchases by Purchase Status

### Important EDA Findings

- The cleaned dataset contains **740 non-purchasing customers** and **648 purchasing customers**.
- `LoyaltyProgram` has a positive correlation with `PurchaseStatus` in the dataset.
- `DiscountsAvailed` and `TimeSpentOnWebsite` also show positive relationships with purchase status.
- `Age` has a negative correlation with purchase status in the correlation analysis.
- `TimeSpentOnWebsite` is the most important feature in both the Decision Tree and Random Forest feature-importance results.

---

## Models Used

### 1. Logistic Regression

Logistic Regression is a supervised classification algorithm used to predict the probability of a binary outcome. It provides a useful baseline for the purchase prediction problem.

### 2. Decision Tree Classifier

Decision Tree classifies customers by making a sequence of feature-based decisions. It is easy to interpret and can capture non-linear relationships.

### 3. Random Forest Classifier

Random Forest combines multiple decision trees and uses their combined predictions to improve robustness and predictive performance.

---

## Model Evaluation

Since this is a classification problem, the following evaluation metrics were used:

- **Accuracy** – overall proportion of correct predictions.
- **Precision** – proportion of predicted purchases that were actually purchases.
- **Recall** – proportion of actual purchases correctly identified by the model.
- **F1-score** – harmonic mean of Precision and Recall.
- **Confusion Matrix** – shows correct and incorrect predictions for both classes.

---

## Model Performance

The models produced the following results on the test set:

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.8309 | 0.8168 | 0.8231 | 0.8199 |
| Decision Tree | 0.8525 | 0.8201 | 0.8769 | 0.8476 |
| **Random Forest** | **0.9281** | **0.9297** | **0.9154** | **0.9225** |

---

## Best Model

### Random Forest Classifier

Random Forest achieved the highest F1-score among the three models:

- **Accuracy:** 92.81%
- **Precision:** 92.97%
- **Recall:** 91.54%
- **F1-score:** 92.25%

Therefore, **Random Forest was selected as the best-performing model** for this project based on the highest F1-score.

---

## Feature Importance

The Random Forest model identified the following features as the most influential in prediction:

1. `TimeSpentOnWebsite`
2. `Age`
3. `AnnualIncome`
4. `DiscountsAvailed`
5. `NumberOfPurchases`
6. `LoyaltyProgram`
7. `ProductCategory`
8. `Gender`

The feature-importance results suggest that website engagement and customer characteristics contribute to purchase prediction in the supplied dataset.

---

## Final Prediction Example

A sample customer was passed to the selected best model with the following values:

```text
Age: 30
Gender: 1
Annual Income: 80,000
Number of Purchases: 10
Product Category: 2
Time Spent on Website: 35
Loyalty Program: 1
Discounts Availed: 3
```
## Project Workflow

Problem Identification
        ↓
Dataset Collection / Loading
        ↓
Data Understanding
        ↓
Data Cleaning
        ↓
Data Preprocessing
        ↓
Exploratory Data Analysis
        ↓
Train-Test Split
        ↓
Model Training
        ↓
Model Evaluation
        ↓
Model Comparison
        ↓
Best Model Selection
        ↓
Final Prediction
        ↓
Conclusion & Future Scope

## Technology Stack
Python
Google Colab / Jupyter Notebook
NumPy
Pandas
Matplotlib
Seaborn
Scikit-learn

## **Project Structure**

```text
ECommerce-Customer-Purchase-Prediction/
│
├── Customer_Purchase_Prediction.ipynb
├── customer_purchase_data.csv
├── README.md
│
├── presentation/
│   └── ECommerce_Customer_Purchase_Prediction.pptx
│
└── report/
    └── ECommerce_Customer_Purchase_Prediction_Report.docx

```

## How to Run the Project
Option 1: Google Colab
Open Customer_Purchase_Prediction.ipynb in Google Colab.
Upload customer_purchase_data.csv to the Colab environment.
Run the notebook cells from top to bottom.
Review the EDA visualizations, model performance, comparison table, and final prediction.
Option 2: Local Jupyter Notebook

Install the required libraries:

pip install numpy pandas matplotlib seaborn scikit-learn jupyter

## Project Deliverables

This repository contains the working files for the Machine Learning mini project:

Jupyter / Google Colab Notebook – complete ML implementation
Dataset – customer_purchase_data.csv
Presentation – project PPT
Report – project documentation
README – project overview and results


## Limitations
The dataset contains a limited set of customer and website-behaviour features.
The supplied dataset may not represent all types of e-commerce customers.
The model is based on the patterns present in the available dataset and may not generalize to every real-world e-commerce platform.
Historical customer behaviour may change over time.
No hyperparameter tuning or cross-validation is included in the current notebook.

## Future Scope

The project can be improved by:

Using a larger and more diverse dataset.
Adding additional behavioural and transaction-level features.
Applying hyperparameter tuning.
Using cross-validation for more robust evaluation.
Testing additional classification algorithms such as KNN, SVM, or Gradient Boosting.
Deploying the trained model as a web application or API.
Connecting the model to real-time e-commerce customer activity.

# Team

**Ragini Singh**
Roll No.: 1500967240232

**Sakshi Shinghole**
Roll No.: 150096724056

## Conclusion

This project demonstrates the use of Machine Learning for predicting customer purchase behaviour in an E-Commerce environment. Three classification algorithms were trained and compared using Accuracy, Precision, Recall, and F1-score.

Among the evaluated models, Random Forest achieved the strongest overall performance with an F1-score of 0.9225 and was selected as the best-performing model.

The project demonstrates a complete Machine Learning workflow from data preparation and visualization to model evaluation and final prediction.


