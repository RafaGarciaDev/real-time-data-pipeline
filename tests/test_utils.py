"""
Testes para funções utilitárias
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import validate_event, sanitize_string, MetricsCollector


class TestValidateEvent:
    """Testes para validação de eventos"""
    
    def test_valid_event(self):
        """Testa evento válido"""
        event = {
            'event_id': '123',
            'event_type': 'purchase',
            'timestamp': '2024-01-01T00:00:00',
            'user_id': 'USER001',
            'session_id': 'SESSION001'
        }
        assert validate_event(event) is True
    
    def test_missing_field(self):
        """Testa evento com campo faltando"""
        event = {
            'event_id': '123',
            'event_type': 'purchase',
            'timestamp': '2024-01-01T00:00:00',
            'user_id': 'USER001'
            # session_id faltando
        }
        assert validate_event(event) is False
    
    def test_empty_event(self):
        """Testa evento vazio"""
        assert validate_event({}) is False
    
    def test_extra_fields_allowed(self):
        """Testa que campos extras são permitidos"""
        event = {
            'event_id': '123',
            'event_type': 'purchase',
            'timestamp': '2024-01-01T00:00:00',
            'user_id': 'USER001',
            'session_id': 'SESSION001',
            'extra_field': 'extra_value'
        }
        assert validate_event(event) is True


class TestSanitizeString:
    """Testes para sanitização de strings"""
    
    def test_normal_string(self):
        """Testa string normal"""
        assert sanitize_string("Hello World") == "Hello World"
    
    def test_string_with_null_chars(self):
        """Testa string com caracteres nulos"""
        assert sanitize_string("Hello\x00World") == "HelloWorld"
    
    def test_long_string(self):
        """Testa string longa"""
        long_string = "a" * 300
        result = sanitize_string(long_string, max_length=255)
        assert len(result) == 255
    
    def test_empty_string(self):
        """Testa string vazia"""
        assert sanitize_string("") == ""
    
    def test_whitespace_trimming(self):
        """Testa remoção de espaços"""
        assert sanitize_string("  Hello World  ") == "Hello World"
    
    def test_none_input(self):
        """Testa entrada None"""
        assert sanitize_string(None) == ""


class TestMetricsCollector:
    """Testes para coletor de métricas"""
    
    def test_increment_new_metric(self):
        """Testa incremento de métrica nova"""
        collector = MetricsCollector()
        collector.increment('events')
        assert collector.get('events') == 1
    
    def test_increment_existing_metric(self):
        """Testa incremento de métrica existente"""
        collector = MetricsCollector()
        collector.increment('events')
        collector.increment('events')
        collector.increment('events')
        assert collector.get('events') == 3
    
    def test_increment_with_value(self):
        """Testa incremento com valor específico"""
        collector = MetricsCollector()
        collector.increment('revenue', 100)
        collector.increment('revenue', 50)
        assert collector.get('revenue') == 150
    
    def test_set_metric(self):
        """Testa definição de métrica"""
        collector = MetricsCollector()
        collector.set('temperature', 25.5)
        assert collector.get('temperature') == 25.5
    
    def test_get_nonexistent_metric(self):
        """Testa obtenção de métrica inexistente"""
        collector = MetricsCollector()
        assert collector.get('nonexistent') == 0
    
    def test_get_all_metrics(self):
        """Testa obtenção de todas as métricas"""
        collector = MetricsCollector()
        collector.increment('events')
        collector.set('temperature', 25.5)
        
        all_metrics = collector.get_all()
        assert all_metrics == {'events': 1, 'temperature': 25.5}
    
    def test_reset_metrics(self):
        """Testa reset de métricas"""
        collector = MetricsCollector()
        collector.increment('events')
        collector.set('temperature', 25.5)
        collector.reset()
        
        assert collector.get('events') == 0
        assert collector.get('temperature') == 0
        assert collector.get_all() == {}


@pytest.fixture
def metrics_collector():
    """Fixture para criar um coletor de métricas"""
    return MetricsCollector()


def test_multiple_metrics(metrics_collector):
    """Testa múltiplas métricas simultaneamente"""
    metrics_collector.increment('events', 10)
    metrics_collector.increment('purchases', 5)
    metrics_collector.set('conversion_rate', 0.5)
    
    assert metrics_collector.get('events') == 10
    assert metrics_collector.get('purchases') == 5
    assert metrics_collector.get('conversion_rate') == 0.5
