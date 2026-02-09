#!/usr/bin/env python
"""
Script de exemplo para análise de dados do pipeline

Demonstra como conectar ao banco e fazer análises customizadas.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta
import os


def get_connection():
    """Cria conexão com o banco de dados"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'pipeline_db'),
        user=os.getenv('POSTGRES_USER', 'admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'admin123'),
        cursor_factory=RealDictCursor
    )


def analyze_user_behavior():
    """Analisa comportamento de usuários"""
    conn = get_connection()
    
    query = """
    SELECT 
        user_id,
        COUNT(DISTINCT session_id) as total_sessions,
        COUNT(*) as total_events,
        COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as total_purchases,
        MIN(timestamp) as first_seen,
        MAX(timestamp) as last_seen
    FROM events
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY user_id
    ORDER BY total_events DESC
    LIMIT 20
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("\n=== TOP 20 USUÁRIOS MAIS ATIVOS (24h) ===\n")
    print(df.to_string(index=False))
    print(f"\nTotal de usuários únicos: {len(df)}")
    
    return df


def analyze_conversion_funnel():
    """Analisa funil de conversão"""
    conn = get_connection()
    
    query = """
    SELECT 
        event_type,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users
    FROM events
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY event_type
    ORDER BY event_count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("\n=== FUNIL DE CONVERSÃO (24h) ===\n")
    print(df.to_string(index=False))
    
    # Calcular taxa de conversão
    if 'page_view' in df['event_type'].values and 'purchase' in df['event_type'].values:
        views = df[df['event_type'] == 'page_view']['event_count'].values[0]
        purchases = df[df['event_type'] == 'purchase']['event_count'].values[0]
        conversion_rate = (purchases / views) * 100
        print(f"\nTaxa de Conversão: {conversion_rate:.2f}%")
    
    return df


def analyze_revenue_by_hour():
    """Analisa receita por hora do dia"""
    conn = get_connection()
    
    query = """
    SELECT 
        EXTRACT(HOUR FROM timestamp) as hour,
        COUNT(*) as transactions,
        SUM(total_amount) as revenue,
        AVG(total_amount) as avg_ticket
    FROM transactions
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY EXTRACT(HOUR FROM timestamp)
    ORDER BY hour
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("\n=== RECEITA POR HORA DO DIA (24h) ===\n")
    print(df.to_string(index=False))
    print(f"\nReceita Total: R$ {df['revenue'].sum():.2f}")
    print(f"Ticket Médio: R$ {df['avg_ticket'].mean():.2f}")
    
    return df


def analyze_product_categories():
    """Analisa performance por categoria de produto"""
    conn = get_connection()
    
    query = """
    SELECT 
        p.category,
        COUNT(t.id) as total_sales,
        SUM(t.quantity) as units_sold,
        SUM(t.total_amount) as revenue,
        AVG(t.total_amount) as avg_sale,
        COUNT(DISTINCT t.event_id) as unique_transactions
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY p.category
    ORDER BY revenue DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("\n=== PERFORMANCE POR CATEGORIA ===\n")
    print(df.to_string(index=False))
    
    return df


def analyze_cohort_retention():
    """Analisa retenção de usuários por coorte"""
    conn = get_connection()
    
    query = """
    WITH user_first_event AS (
        SELECT 
            user_id,
            DATE(MIN(timestamp)) as cohort_date
        FROM events
        GROUP BY user_id
    ),
    user_activities AS (
        SELECT 
            e.user_id,
            uf.cohort_date,
            DATE(e.timestamp) as activity_date
        FROM events e
        JOIN user_first_event uf ON e.user_id = uf.user_id
        WHERE e.timestamp > NOW() - INTERVAL '7 days'
    )
    SELECT 
        cohort_date,
        COUNT(DISTINCT user_id) as cohort_size,
        COUNT(DISTINCT CASE 
            WHEN activity_date > cohort_date THEN user_id 
        END) as retained_users
    FROM user_activities
    GROUP BY cohort_date
    ORDER BY cohort_date DESC
    LIMIT 7
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['retention_rate'] = (df['retained_users'] / df['cohort_size'] * 100).round(2)
        
        print("\n=== ANÁLISE DE RETENÇÃO (7 dias) ===\n")
        print(df.to_string(index=False))
    
    return df


def main():
    """Executa todas as análises"""
    print("=" * 60)
    print("ANÁLISE DE DADOS DO PIPELINE")
    print("=" * 60)
    
    try:
        analyze_user_behavior()
        analyze_conversion_funnel()
        analyze_revenue_by_hour()
        analyze_product_categories()
        analyze_cohort_retention()
        
        print("\n" + "=" * 60)
        print("ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nErro durante análise: {e}")
        print("Certifique-se de que o pipeline está rodando.")


if __name__ == '__main__':
    main()
