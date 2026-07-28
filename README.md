
# 🗄️ CS432 Database Systems Project

OLYMPIA_TRACK_MANAGEMENT

A comprehensive Database Management System (DBMS) project developed as part of the **CS432 - Database Systems** course. This project was implemented incrementally over four assignments, gradually evolving from database schema design into a simplified distributed database system supporting indexing, transactions, crash recovery, and sharding.

---

## 📚 Project Overview

The objective of this project is to understand the internal working of modern Database Management Systems by implementing core DBMS concepts from scratch rather than relying on existing database engines.

The project progresses through four assignments:

| Assignment   | Topic                                           |
| ------------ | ----------------------------------------------- |
| Assignment 1 | Database Design & SQL Implementation            |
| Assignment 2 | Storage Engine (B+ Tree) & REST API             |
| Assignment 3 | Transactions, Locking, WAL & Crash Recovery     |
| Assignment 4 | Database Sharding & Distributed Data Management |

---

# 📁 Repository Structure

```text
CS432_DATABASES_PROJECT/
│
├── Assignment_1/
├── Assignment_2/
├── Assignment_3/
├── Assignment_4/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Assignment 1 – Database Design

### Features

* Entity Relationship (ER) Design
* Relational Schema
* SQL Table Creation Scripts
* Constraints
* Sample Data Population
* Database Dump

### Concepts Covered

* Normalization
* Primary Keys
* Foreign Keys
* Constraints
* SQL DDL & DML

---

# Assignment 2 – Storage Engine & Flask API

This assignment extends Assignment 1 by implementing the database storage layer and exposing database operations through REST APIs.

### Features

* Custom Database Manager
* Table Management
* CRUD Operations
* B+ Tree Indexing
* Flask REST APIs
* Modular Project Structure using Flask Blueprints

### Technologies

* Python
* Flask
* B+ Tree

### Concepts Covered

* Indexing
* Search Keys
* REST APIs
* HTTP Requests
* Flask Blueprints

---

# Assignment 3 – Transactions & Recovery

This assignment extends Assignment 2 by adding transaction management and crash recovery mechanisms.

### Features

* ACID Transactions
* Write-Ahead Logging (WAL)
* Undo Logging
* Commit & Rollback
* Crash Recovery
* Database Checkpointing
* Table-Level Locking
* Transaction Manager

### Concepts Covered

* Atomicity
* Consistency
* Isolation
* Durability
* Two-Phase Locking (Simplified)
* Checkpoint Recovery
* Crash Recovery

---

# Assignment 4 – Database Sharding

This assignment extends Assignment 3 by introducing horizontal partitioning (sharding) to simulate distributed database systems.

### Features

* Multiple Database Shards
* Data Partitioning
* Routing Layer
* Shard Key Based Distribution
* Distributed Query Routing
* Simulated Horizontal Scaling

### Concepts Covered

* Horizontal Scaling
* Sharding
* Data Partitioning
* Distributed Databases
* Query Routing

---

# Technologies Used

* Python
* Flask
* SQLite (Assignment 1)
* B+ Tree Indexing
* JSON
* REST APIs

---

# Core DBMS Concepts Implemented

* Database Design
* Relational Schema
* SQL
* CRUD Operations
* B+ Tree Index
* Transactions
* Write-Ahead Logging (WAL)
* Undo Logging
* Commit & Rollback
* Checkpointing
* Crash Recovery
* Locking
* Concurrency Control
* Database Sharding

---

# Design Philosophy

Each assignment builds upon the previous one without redesigning the architecture.

```text
Assignment 1
Database Schema
        │
        ▼
Assignment 2
Storage Engine + REST API
        │
        ▼
Assignment 3
Transactions + WAL + Recovery
        │
        ▼
Assignment 4
Sharding + Distributed Database Simulation
```

This incremental design closely follows the evolution of real-world database systems, where new capabilities are layered over existing infrastructure instead of replacing it.

---

# Learning Outcomes

Through this project, the following database concepts were implemented and studied:

* Relational Database Design
* Index Structures
* Storage Management
* Transaction Processing
* Concurrency Control
* Crash Recovery
* Write-Ahead Logging
* Checkpointing
* Distributed Database Concepts
* Database Sharding

---

# How to Run

## Clone the Repository

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

## Create a Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

Navigate to the desired assignment directory and execute the corresponding application.

Example:

```bash
cd Assignment_4
python app.py
```

---

# Future Improvements

* Deadlock Detection using Wait-For Graphs
* Row-Level Locking
* Query Optimization

---


Database Systems Project – CS432
