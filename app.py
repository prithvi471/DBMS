from flask import Flask, render_template, request, jsonify
from db import get_connection
from datetime import date, datetime
from decimal import Decimal
import json

app = Flask(__name__)

# Serialize Decimals and Dates correctly
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder
app.json.default = CustomJSONEncoder().default

# --- PAGE ROUTES ---
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/suppliers')
def suppliers():
    return render_template('suppliers.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/warehouses')
def warehouses():
    return render_template('warehouses.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/customers')
def customers():
    return render_template('customers.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/order_details')
def order_details():
    return render_template('order_details.html')

@app.route('/shipments')
def shipments():
    return render_template('shipments.html')

# --- API ROUTES ---

TABLE_PK_MAP = {
    'supplier': 'supplier_id',
    'product': 'product_id',
    'warehouse': 'warehouse_id',
    'inventory': 'inventory_id',
    'customer': 'customer_id',
    'orders': 'order_id',
    'order_details': 'order_detail_id',
    'shipment': 'shipment_id'
}

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            data = cursor.fetchall()
            return data
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Special GET route overloads with JOINS where the frontend demands them explicitly:
@app.route('/api/Product', methods=['GET'])
def get_products():
    query = """
    SELECT p.*, s.supplier_name 
    FROM Product p 
    LEFT JOIN Supplier s ON p.supplier_id = s.supplier_id
    """
    try:
        data = execute_query(query, fetch=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/Inventory', methods=['GET'])
def get_inventory():
    query = """
    SELECT i.*, p.product_name, w.warehouse_name 
    FROM Inventory i
    LEFT JOIN Product p ON i.product_id = p.product_id
    LEFT JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
    """
    try:
        data = execute_query(query, fetch=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/Orders', methods=['GET'])
def get_orders():
    query = """
    SELECT o.*, c.customer_name 
    FROM Orders o
    LEFT JOIN Customer c ON o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
    """
    try:
        data = execute_query(query, fetch=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Top 5 Recent Orders for Dashboard
@app.route('/api/dashboard/recent-orders', methods=['GET'])
def recent_orders():
    query = """
    SELECT o.*, c.customer_name 
    FROM Orders o
    LEFT JOIN Customer c ON o.customer_id = c.customer_id
    ORDER BY o.order_id DESC
    LIMIT 5
    """
    try:
        data = execute_query(query, fetch=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Generic CRUD:
@app.route('/api/<table>', methods=['GET'])
def api_get_all(table):
    if table.lower() not in TABLE_PK_MAP:
        return jsonify({'error': 'Invalid table'}), 400
    try:
        data = execute_query(f"SELECT * FROM {table}")
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>', methods=['POST'])
def api_insert(table):
    if table.lower() not in TABLE_PK_MAP:
        return jsonify({'error': 'Invalid table'}), 400
    try:
        body = request.get_json()
        keys = list(body.keys())
        values = list(body.values())
        placeholders = ','.join(['%s'] * len(keys))
        columns = ','.join(keys)
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        lastid = execute_query(query, tuple(values))
        return jsonify({'message': f'{table} added', 'id': lastid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>/<int:id>', methods=['PUT'])
def api_update(table, id):
    if table.lower() not in TABLE_PK_MAP:
        return jsonify({'error': 'Invalid table'}), 400
    pk = TABLE_PK_MAP[table.lower()]
    try:
        body = request.get_json()
        if pk in body:
            del body[pk]
        
        keys = list(body.keys())
        values = list(body.values())
        set_clause = ', '.join([f"{k}=%s" for k in keys])
        values.append(id)
        
        query = f"UPDATE {table} SET {set_clause} WHERE {pk} = %s"
        execute_query(query, tuple(values))
        
        return jsonify({'message': f'{table} updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>/<int:id>', methods=['DELETE'])
def api_delete(table, id):
    if table.lower() not in TABLE_PK_MAP:
        return jsonify({'error': 'Invalid table'}), 400
    pk = TABLE_PK_MAP[table.lower()]
    try:
        query = f"DELETE FROM {table} WHERE {pk} = %s"
        execute_query(query, (id,))
        return jsonify({'message': f'{table} deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Special APIs
@app.route('/api/dashboard', methods=['GET'])
def dashboard_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as c FROM Supplier")
        suppliers = cursor.fetchone()['c']
        
        cursor.execute("SELECT COUNT(*) as c FROM Product")
        products = cursor.fetchone()['c']
        
        cursor.execute("SELECT COUNT(*) as c FROM Orders")
        orders = cursor.fetchone()['c']
        
        cursor.execute("SELECT SUM(total_amount) as s FROM Orders")
        revenue = cursor.fetchone()['s'] or 0
        
        cursor.execute("SELECT COUNT(*) as c FROM Inventory i JOIN Product p ON i.product_id = p.product_id WHERE i.quantity_available < p.reorder_level")
        low_stock_count = cursor.fetchone()['c']
        
        conn.close()
        
        return jsonify({
            'total_suppliers': suppliers,
            'total_products': products,
            'total_orders': orders,
            'total_revenue': float(revenue),
            'low_stock_count': low_stock_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/low-stock', methods=['GET'])
def inventory_low_stock():
    try:
        query = """
            SELECT p.product_name, w.warehouse_name, i.quantity_available, p.reorder_level 
            FROM Inventory i
            JOIN Product p ON i.product_id = p.product_id
            JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
            WHERE i.quantity_available < p.reorder_level
        """
        data = execute_query(query, fetch=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:id>/details', methods=['GET'])
def order_details_special(id):
    try:
        query = """
            SELECT od.order_detail_id, od.order_id, p.product_name, od.quantity, od.price 
            FROM Order_Details od
            JOIN Product p ON od.product_id = p.product_id
            WHERE od.order_id = %s
        """
        data = execute_query(query, (id,), fetch=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/place', methods=['POST'])
def place_order():
    body = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute(
            "INSERT INTO Orders (order_date, total_amount, status, customer_id) VALUES (CURDATE(), %s, 'PENDING', %s)",
            (body['total_amount'], body['customer_id'])
        )
        order_id = cursor.lastrowid
        for item in body.get('items', []):
            cursor.execute(
                "INSERT INTO Order_Details (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
                (order_id, item['product_id'], item['quantity'], item['price'])
            )
            cursor.execute(
                "UPDATE Inventory SET quantity_available = quantity_available - %s WHERE product_id = %s",
                (item['quantity'], item['product_id'])
            )
        conn.commit()
        return jsonify({'message': 'Order placed', 'order_id': order_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/shipments/<int:id>/deliver', methods=['PUT'])
def shipment_deliver(id):
    try:
        query = "UPDATE Shipment SET status = 'DELIVERED', delivery_date = CURDATE() WHERE shipment_id = %s"
        execute_query(query, (id,))
        return jsonify({'message': 'Shipment delivered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
