"""
Dashboard Web - Visualização em tempo real das métricas do pipeline
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configurações PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'pipeline_db'),
    'user': os.getenv('POSTGRES_USER', 'admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'admin123')
}


def get_db_connection():
    """Cria conexão com banco de dados"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    return jsonify({'status': 'unhealthy'}), 500


@app.route('/api/metrics/summary')
def get_summary_metrics():
    """Retorna métricas resumidas"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Total de eventos
        cursor.execute("SELECT COUNT(*) as total FROM events")
        total_events = cursor.fetchone()['total']
        
        # Eventos nas últimas 24h
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM events 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        events_24h = cursor.fetchone()['total']
        
        # Total de transações
        cursor.execute("SELECT COUNT(*) as total FROM transactions")
        total_transactions = cursor.fetchone()['total']
        
        # Receita total
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM transactions")
        total_revenue = float(cursor.fetchone()['total'])
        
        # Receita últimas 24h
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as total 
            FROM transactions 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        revenue_24h = float(cursor.fetchone()['total'])
        
        # Usuários únicos
        cursor.execute("SELECT COUNT(DISTINCT user_id) as total FROM events")
        unique_users = cursor.fetchone()['total']
        
        # Produtos únicos vendidos
        cursor.execute("SELECT COUNT(DISTINCT product_id) as total FROM transactions")
        unique_products = cursor.fetchone()['total']
        
        # Taxa de conversão (compras / total de eventos)
        conversion_rate = (total_transactions / total_events * 100) if total_events > 0 else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_events': total_events,
            'events_24h': events_24h,
            'total_transactions': total_transactions,
            'total_revenue': round(total_revenue, 2),
            'revenue_24h': round(revenue_24h, 2),
            'unique_users': unique_users,
            'unique_products': unique_products,
            'conversion_rate': round(conversion_rate, 2)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas resumidas: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/timeline')
def get_timeline_metrics():
    """Retorna métricas ao longo do tempo"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Eventos por hora nas últimas 24h
        cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as event_count,
                COUNT(DISTINCT user_id) as user_count,
                SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchase_count
            FROM events
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour
        """)
        
        timeline_data = []
        for row in cursor.fetchall():
            timeline_data.append({
                'hour': row['hour'].isoformat(),
                'events': row['event_count'],
                'users': row['user_count'],
                'purchases': row['purchase_count']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(timeline_data)
        
    except Exception as e:
        logger.error(f"Erro ao obter timeline: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/top-products')
def get_top_products():
    """Retorna produtos mais vendidos"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.product_name,
                p.category,
                COUNT(t.id) as total_sales,
                SUM(t.quantity) as total_quantity,
                SUM(t.total_amount) as total_revenue
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            GROUP BY p.product_id, p.product_name, p.category
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'name': row['product_name'],
                'category': row['category'],
                'sales': row['total_sales'],
                'quantity': row['total_quantity'],
                'revenue': float(row['total_revenue'])
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(products)
        
    except Exception as e:
        logger.error(f"Erro ao obter top produtos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/by-category')
def get_category_metrics():
    """Retorna métricas por categoria"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.category,
                COUNT(t.id) as total_transactions,
                SUM(t.quantity) as total_quantity,
                SUM(t.total_amount) as total_revenue
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            GROUP BY p.category
            ORDER BY total_revenue DESC
        """)
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'category': row['category'],
                'transactions': row['total_transactions'],
                'quantity': row['total_quantity'],
                'revenue': float(row['total_revenue'])
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(categories)
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas por categoria: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/event-types')
def get_event_type_distribution():
    """Retorna distribuição de tipos de eventos"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                event_type,
                COUNT(*) as count
            FROM events
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY event_type
            ORDER BY count DESC
        """)
        
        event_types = []
        for row in cursor.fetchall():
            event_types.append({
                'type': row['event_type'],
                'count': row['count']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(event_types)
        
    except Exception as e:
        logger.error(f"Erro ao obter distribuição de eventos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/realtime')
def get_realtime_metrics():
    """Retorna métricas em tempo real (último minuto)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Eventos no último minuto
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM events
            WHERE timestamp > NOW() - INTERVAL '1 minute'
        """)
        events_per_minute = cursor.fetchone()['count']
        
        # Compras no último minuto
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM transactions
            WHERE timestamp > NOW() - INTERVAL '1 minute'
        """)
        result = cursor.fetchone()
        purchases_per_minute = result['count']
        revenue_per_minute = float(result['revenue'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'events_per_minute': events_per_minute,
            'purchases_per_minute': purchases_per_minute,
            'revenue_per_minute': round(revenue_per_minute, 2),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas em tempo real: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
