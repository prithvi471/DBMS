# Smart Inventory & Supply Chain Management System

A full-stack web application built using Python Flask, vanilla HTML/CSS/JavaScript, and MySQL.

## Features

- **Dashboard**: Real-time statistics, low-stock alerts, and recent orders.
- **Suppliers, Products, Warehouses, Customers**: Full CRUD pages.
- **Inventory Management**: View stock counts and quickly update quantity. Low-stock products are highlighted automatically.
- **Order Management**: Transactionally place orders connecting Customer, Inventory, and Order_Details tables.
- **Shipment Tracking**: Create shipments and mark them as delivered.

## Tech Stack
- Frontend: HTML5, CSS3, JavaScript (Fetch API) 
- Backend: Python 3.x, Flask, `mysql-connector-python`
- Database: MySQL

## Setup Instructions

1. **Database Requirements**:
   Make sure you have MySQL running locally on port `3306`.
   Ensure `SmartInventoryDB` database has been seeded with the schemas & tables. If not, run your schema/seed file:
   ```bash
   source Unit4_Unit5_MySQL_Commands.sql
   ```

2. **Install Python Dependencies**:
   Navigate to this directory and install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Connectivity**:
   Check `db.py` to ensure credentials match your MySQL setup:
   - `host`: 'localhost'
   - `user`: 'root'
   - `password`: 'root'

4. **Run the Server**:
   ```bash
   python app.py
   ```
   The Flask application will start up, generally at `http://localhost:5000/`.

5. **Access the App**:
   Open a web browser and navigate to `http://localhost:5000`.
