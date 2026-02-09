"""
Data Consumer - Processa eventos do Kafka e armazena no PostgreSQL
"""

import json
import logging
import time
import os
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import pool

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ecommerce-events')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'ecommerce-consumer-group')

# Configurações PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'pipeline_db'),
    'user': os.getenv('POSTGRES_USER', 'admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'admin123')
}


class EventConsumer:
    """Consumidor de eventos Kafka com persistência em PostgreSQL"""
    
    def __init__(self, bootstrap_servers, topic, group_id, postgres_config):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.db_pool = None
        self.postgres_config = postgres_config
        self.batch_size = 100
        self.batch_timeout = 5
        
        self.connect_kafka()
        self.connect_database()
        
    def connect_kafka(self):
        """Conecta ao Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                max_poll_records=500,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(f"Conectado ao Kafka: {self.bootstrap_servers}")
            logger.info(f"Inscrito no tópico: {self.topic}")
        except KafkaError as e:
            logger.error(f"Erro ao conectar ao Kafka: {e}")
            raise
    
    def connect_database(self):
        """Conecta ao PostgreSQL usando connection pool"""
        try:
            self.db_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **self.postgres_config
            )
            logger.info(f"Conectado ao PostgreSQL: {self.postgres_config['host']}")
            
            # Testa conexão
            conn = self.db_pool.getconn()
            conn.close()
            self.db_pool.putconn(conn)
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
            raise
    
    def get_connection(self):
        """Obtém conexão do pool"""
        return self.db_pool.getconn()
    
    def return_connection(self, conn):
        """Retorna conexão ao pool"""
        self.db_pool.putconn(conn)
    
    def process_event(self, event, conn):
        """
        Processa um evento individual
        
        Args:
            event: Dicionário com dados do evento
            conn: Conexão com banco de dados
        """
        cursor = conn.cursor()
        
        try:
            # Insere evento
            cursor.execute("""
                INSERT INTO events (event_id, event_type, timestamp, user_id, session_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
            """, (
                event['event_id'],
                event['event_type'],
                event['timestamp'],
                event['user_id'],
                event['session_id']
            ))
            
            # Insere produto se não existir
            product = event.get('product', {})
            if product:
                cursor.execute("""
                    INSERT INTO products (product_id, product_name, category, price)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (product_id) DO NOTHING
                """, (
                    product['id'],
                    product['name'],
                    product['category'],
                    product['price']
                ))
            
            # Se for uma compra, insere na tabela de transações
            if event['event_type'] == 'purchase' and product:
                cursor.execute("""
                    INSERT INTO transactions (
                        transaction_id, event_id, product_id, quantity,
                        total_amount, payment_method, timestamp
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (transaction_id) DO NOTHING
                """, (
                    f"TXN_{event['event_id']}",
                    event['event_id'],
                    product['id'],
                    event.get('quantity', 1),
                    event.get('total_amount', 0),
                    event.get('payment_method'),
                    event['timestamp']
                ))
            
            conn.commit()
            logger.debug(f"Evento processado: {event['event_id']} - {event['event_type']}")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao processar evento {event.get('event_id')}: {e}")
            return False
        
        finally:
            cursor.close()
    
    def process_batch(self, events):
        """
        Processa um lote de eventos
        
        Args:
            events: Lista de eventos para processar
        """
        if not events:
            return
        
        conn = self.get_connection()
        
        try:
            success_count = 0
            for event in events:
                if self.process_event(event, conn):
                    success_count += 1
            
            logger.info(
                f"Lote processado: {success_count}/{len(events)} eventos | "
                f"Taxa de sucesso: {(success_count/len(events)*100):.1f}%"
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar lote: {e}")
        
        finally:
            self.return_connection(conn)
    
    def run(self):
        """Executa o consumer"""
        logger.info("Iniciando consumer...")
        
        batch = []
        last_batch_time = time.time()
        total_processed = 0
        start_time = time.time()
        
        try:
            for message in self.consumer:
                event = message.value
                batch.append(event)
                
                # Processa lote quando atingir tamanho ou timeout
                current_time = time.time()
                should_process = (
                    len(batch) >= self.batch_size or
                    (current_time - last_batch_time) >= self.batch_timeout
                )
                
                if should_process and batch:
                    self.process_batch(batch)
                    total_processed += len(batch)
                    batch = []
                    last_batch_time = current_time
                    
                    # Log de progresso a cada 1000 eventos
                    if total_processed % 1000 == 0:
                        elapsed = time.time() - start_time
                        rate = total_processed / elapsed
                        logger.info(
                            f"Progresso: {total_processed} eventos processados | "
                            f"Taxa: {rate:.2f} eventos/s"
                        )
        
        except KeyboardInterrupt:
            logger.info("Consumer interrompido pelo usuário")
            if batch:
                self.process_batch(batch)
        
        finally:
            elapsed = time.time() - start_time
            logger.info(
                f"Consumer finalizado: {total_processed} eventos em {elapsed:.2f}s | "
                f"Taxa média: {total_processed/elapsed:.2f} eventos/s"
            )
            self.close()
    
    def close(self):
        """Fecha conexões"""
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer Kafka fechado")
        
        if self.db_pool:
            self.db_pool.closeall()
            logger.info("Pool de conexões PostgreSQL fechado")


def main():
    """Função principal"""
    # Aguarda serviços estarem prontos
    time.sleep(10)
    
    consumer = EventConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        topic=KAFKA_TOPIC,
        group_id=KAFKA_GROUP_ID,
        postgres_config=POSTGRES_CONFIG
    )
    
    consumer.run()


if __name__ == '__main__':
    main()
