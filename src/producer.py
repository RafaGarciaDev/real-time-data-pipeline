"""
Data Producer - Gera eventos simulados de e-commerce
"""

import json
import time
import logging
import random
from datetime import datetime
from uuid import uuid4
from kafka import KafkaProducer
from kafka.errors import KafkaError
from faker import Faker
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

fake = Faker()

# Configurações
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ecommerce-events')

# Produtos e categorias
PRODUCTS = [
    {'id': 'PROD001', 'name': 'Laptop Dell XPS 15', 'category': 'Electronics', 'price': 1299.99},
    {'id': 'PROD002', 'name': 'iPhone 15 Pro', 'category': 'Electronics', 'price': 999.99},
    {'id': 'PROD003', 'name': 'Sony WH-1000XM5', 'category': 'Electronics', 'price': 399.99},
    {'id': 'PROD004', 'name': 'Kindle Paperwhite', 'category': 'Electronics', 'price': 139.99},
    {'id': 'PROD005', 'name': 'Nike Air Max', 'category': 'Fashion', 'price': 129.99},
    {'id': 'PROD006', 'name': "Levi's 501 Jeans", 'category': 'Fashion', 'price': 89.99},
    {'id': 'PROD007', 'name': 'The Great Gatsby Book', 'category': 'Books', 'price': 14.99},
    {'id': 'PROD008', 'name': 'Yoga Mat Premium', 'category': 'Sports', 'price': 49.99},
    {'id': 'PROD009', 'name': 'Coffee Maker Deluxe', 'category': 'Home', 'price': 79.99},
    {'id': 'PROD010', 'name': 'Gaming Chair RGB', 'category': 'Furniture', 'price': 299.99},
]

EVENT_TYPES = ['page_view', 'add_to_cart', 'remove_from_cart', 'purchase', 'search']
PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'crypto', 'bank_transfer']


class EventProducer:
    """Gerador de eventos de e-commerce"""
    
    def __init__(self, bootstrap_servers, topic):
        self.topic = topic
        self.producer = None
        self.bootstrap_servers = bootstrap_servers
        self.active_sessions = {}
        self.connect()
        
    def connect(self):
        """Conecta ao Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retries=5,
                retry_backoff_ms=500,
                max_in_flight_requests_per_connection=5,
                acks='all'
            )
            logger.info(f"Conectado ao Kafka: {self.bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Erro ao conectar ao Kafka: {e}")
            raise
    
    def generate_event(self):
        """Gera um evento aleatório"""
        event_type = random.choice(EVENT_TYPES)
        user_id = f"USER{random.randint(1, 100):03d}"
        
        # Mantém sessão ativa para usuário ou cria nova
        if user_id not in self.active_sessions or random.random() > 0.7:
            self.active_sessions[user_id] = str(uuid4())
        
        session_id = self.active_sessions[user_id]
        product = random.choice(PRODUCTS)
        
        event = {
            'event_id': str(uuid4()),
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'session_id': session_id,
            'product': product,
            'ip_address': fake.ipv4(),
            'user_agent': fake.user_agent(),
        }
        
        # Adicionar campos específicos por tipo de evento
        if event_type == 'search':
            event['search_query'] = fake.word()
            event['results_count'] = random.randint(0, 50)
            
        elif event_type == 'add_to_cart':
            event['quantity'] = random.randint(1, 5)
            
        elif event_type == 'purchase':
            quantity = random.randint(1, 3)
            event['quantity'] = quantity
            event['total_amount'] = round(product['price'] * quantity, 2)
            event['payment_method'] = random.choice(PAYMENT_METHODS)
            event['shipping_address'] = {
                'street': fake.street_address(),
                'city': fake.city(),
                'state': fake.state(),
                'zip_code': fake.zipcode(),
                'country': fake.country()
            }
            
        elif event_type == 'page_view':
            event['page_url'] = f"/products/{product['category'].lower()}/{product['id']}"
            event['referrer'] = random.choice(['google', 'facebook', 'direct', 'email', 'instagram'])
        
        return event
    
    def send_event(self, event):
        """Envia evento para Kafka"""
        try:
            future = self.producer.send(
                self.topic,
                key=event['event_id'],
                value=event
            )
            
            # Callback de sucesso
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Evento enviado: {event['event_type']} | "
                f"Topic: {record_metadata.topic} | "
                f"Partition: {record_metadata.partition} | "
                f"Offset: {record_metadata.offset}"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Erro ao enviar evento: {e}")
            return False
    
    def run(self, events_per_second=2, duration=None):
        """
        Executa o produtor
        
        Args:
            events_per_second: Número de eventos por segundo
            duration: Duração em segundos (None para executar indefinidamente)
        """
        logger.info(f"Iniciando producer: {events_per_second} eventos/segundo")
        
        start_time = time.time()
        event_count = 0
        
        try:
            while True:
                # Verifica duração
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Gera e envia evento
                event = self.generate_event()
                if self.send_event(event):
                    event_count += 1
                
                # Controla taxa de eventos
                time.sleep(1.0 / events_per_second)
                
                # Log de progresso a cada 100 eventos
                if event_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = event_count / elapsed
                    logger.info(
                        f"Progresso: {event_count} eventos enviados | "
                        f"Taxa: {rate:.2f} eventos/s"
                    )
        
        except KeyboardInterrupt:
            logger.info("Produtor interrompido pelo usuário")
        
        finally:
            elapsed = time.time() - start_time
            logger.info(
                f"Producer finalizado: {event_count} eventos em {elapsed:.2f}s | "
                f"Taxa média: {event_count/elapsed:.2f} eventos/s"
            )
            self.close()
    
    def close(self):
        """Fecha conexão com Kafka"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer fechado")


def main():
    """Função principal"""
    producer = EventProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        topic=KAFKA_TOPIC
    )
    
    # Executa indefinidamente gerando 2 eventos por segundo
    producer.run(events_per_second=2)


if __name__ == '__main__':
    main()
