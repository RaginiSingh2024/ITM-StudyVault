# 🛡 Insurance Policy Management System

A backend mini project built using **FastAPI, Strawberry GraphQL, and MongoDB Atlas**.

This system allows users to:
- Create Customers
- Add Insurance Policies
- Fetch Customers with their Policies

---

## 📌 Problem Statement

The goal of this project is to build a backend API using GraphQL that manages customers and their insurance policies. The system should support creating customers, assigning policies to them, and retrieving customer details dynamically.

---

## 🚀 Tech Stack

- **FastAPI** – Backend framework
- **Strawberry GraphQL** – GraphQL implementation
- **MongoDB Atlas** – Cloud NoSQL Database
- **Pymongo** – MongoDB driver for Python
- **Python 3.11**

---

## 📂 Project Structure
insurance_system/
│
├── main.py # FastAPI app & GraphQL router
├── schema.py # GraphQL types, queries & mutations
├── database.py # MongoDB connection setup
├── .env # MongoDB connection string
├── README.md


---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
git clone <your-repo-link>
cd insurance_system


### 2️⃣ Create Virtual Environment
python3.11 -m venv venv
source venv/bin/activate


### 3️⃣ Install Dependencies


pip install fastapi uvicorn pymongo python-dotenv "strawberry-graphql[fastapi]"


---

## 🔐 Configure MongoDB

Create a `.env` file and add your MongoDB Atlas connection string:
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority


---

## ▶️ Run the Project
source venv/bin/activate
python -m uvicorn main:app --reload


Server will run at:


http://127.0.0.1:8000


GraphQL endpoint:


http://127.0.0.1:8000/graphql


---

## 🧪 Sample GraphQL Operations

### 🔹 Create Customer (Mutation)
mutation {
createCustomer(name: "Ragini", email: "ragini@email.com
")
}


### 🔹 Add Policy (Mutation)


mutation {
addPolicy(
customerId: "PASTE_CUSTOMER_ID_HERE"
policyName: "Health Insurance"
premium: 5000
)
}


---

### 🔹 Fetch Customers (Query)


{
customers {
id
name
email
policies {
policyName
premium
}
}
}


---

## 🗄 Database Design

### Customers Collection


{
"_id": ObjectId,
"name": String,
"email": String
}


### Policies Collection


{
"_id": ObjectId,
"customer_id": String,
"policy_name": String,
"premium": Float
}


Policies are linked to customers using `customer_id`.

---

## 🔄 How It Works

1. FastAPI runs the backend server.
2. Strawberry GraphQL defines schema and API structure.
3. MongoDB Atlas stores customer and policy data.
4. Mutations insert data into MongoDB.
5. Queries fetch and return structured GraphQL responses.

---

## 📌 Key Concepts Used

- GraphQL Query vs Mutation
- NoSQL Document Database
- Cloud Database (MongoDB Atlas)
- REST vs GraphQL comparison
- Backend API development

---

## 🎯 Learning Outcomes

- Implemented GraphQL using Strawberry
- Connected FastAPI with MongoDB Atlas
- Designed relational-like structure in NoSQL
- Built and tested live backend API

---

# Insurance Policy Management System

## Tech Stack
- FastAPI
- Strawberry GraphQL
- MongoDB Atlas

## Run Project
source venv/bin/activate
python -m uvicorn main:app --reload

## GraphQL Endpoint
http://127.0.0.1:8000/graphql

## Sample Mutation
mutation {
  createCustomer(name: "Test", email: "test@email.com")
}

## Sample Query
{
  customers {
    name
    email
    policies {
      policyName
      premium
    }
  }
}


## 👩‍💻 Author

Ragini Singh  
Mini Project – GraphQL & Graph Database  