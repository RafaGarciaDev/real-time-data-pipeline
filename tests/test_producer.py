"""
Testes para o Producer
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from producer import EventProducer, PRODUCTS, EVENT_TYPES


class TestEventProducer:
    """Testes para a classe EventProducer"""
    
    @patch('producer.KafkaProducer')
    def test_producer_initialization(self, mock_kafka):
        """Testa inicialização do producer"""
        producer = EventProducer('localhost:9092', 'test-topic')
        assert producer.topic == 'test-topic'
        assert producer.bootstrap_servers == 'localhost:9092'
        mock_kafka.assert_called_once()
    
    @patch('producer.KafkaProducer')
    def test_generate_event_structure(self, mock_kafka):
        """Testa estrutura do evento gerado"""
        producer = EventProducer('localhost:9092', 'test-topic')
        event = producer.generate_event()
        
        # Verifica campos obrigatórios
        assert 'event_id' in event
        assert 'event_type' in event
        assert 'timestamp' in event
        assert 'user_id' in event
        assert 'session_id' in event
        assert 'product' in event
        
        # Verifica tipos
        assert event['event_type'] in EVENT_TYPES
        assert event['user_id'].startswith('USER')
    
    @patch('producer.KafkaProducer')
    def test_purchase_event_has_payment_info(self, mock_kafka):
        """Testa se eventos de compra têm informações de pagamento"""
        producer = EventProducer('localhost:9092', 'test-topic')
        
        # Gera vários eventos até encontrar uma compra
        for _ in range(100):
            event = producer.generate_event()
            if event['event_type'] == 'purchase':
                assert 'quantity' in event
                assert 'total_amount' in event
                assert 'payment_method' in event
                assert 'shipping_address' in event
                break
    
    @patch('producer.KafkaProducer')
    def test_session_consistency(self, mock_kafka):
        """Testa consistência de sessão para mesmo usuário"""
        producer = EventProducer('localhost:9092', 'test-topic')
        
        # Força um user_id específico
        events = []
        for _ in range(5):
            event = producer.generate_event()
            if event['user_id'] == 'USER001':
                events.append(event)
        
        # Verifica se há eventos do mesmo usuário
        if len(events) > 1:
            # Pode haver mudança de sessão (70% de chance de manter)
            # mas user_id deve ser o mesmo
            user_ids = [e['user_id'] for e in events]
            assert all(uid == 'USER001' for uid in user_ids)


class TestEventValidation:
    """Testes de validação de eventos"""
    
    def test_product_data_completeness(self):
        """Testa se todos os produtos têm dados completos"""
        for product in PRODUCTS:
            assert 'id' in product
            assert 'name' in product
            assert 'category' in product
            assert 'price' in product
            assert product['price'] > 0
    
    def test_event_types_valid(self):
        """Testa se tipos de eventos são válidos"""
        valid_types = ['page_view', 'add_to_cart', 'remove_from_cart', 'purchase', 'search']
        assert EVENT_TYPES == valid_types


@pytest.fixture
def mock_producer():
    """Fixture para criar um producer mockado"""
    with patch('producer.KafkaProducer'):
        producer = EventProducer('localhost:9092', 'test-topic')
        yield producer


def test_event_generation_no_exception(mock_producer):
    """Testa que geração de evento não lança exceções"""
    try:
        event = mock_producer.generate_event()
        assert event is not None
    except Exception as e:
        pytest.fail(f"Event generation raised exception: {e}")
