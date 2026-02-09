"""
Funções utilitárias compartilhadas
"""

import logging
import time
from functools import wraps
from typing import Callable, Any


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura e retorna um logger
    
    Args:
        name: Nome do logger
        level: Nível de logging
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator para retry com backoff exponencial
    
    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay inicial em segundos
        backoff: Multiplicador do delay a cada tentativa
        
    Example:
        @retry(max_attempts=3, delay=1.0)
        def my_function():
            # código que pode falhar
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger = logging.getLogger(func.__module__)
                        logger.warning(
                            f"Tentativa {attempt}/{max_attempts} falhou: {e}. "
                            f"Tentando novamente em {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator


def timing(func: Callable) -> Callable:
    """
    Decorator para medir tempo de execução de uma função
    
    Example:
        @timing
        def my_function():
            # código
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        logger = logging.getLogger(func.__module__)
        logger.debug(f"{func.__name__} executou em {end - start:.4f}s")
        
        return result
    
    return wrapper


def validate_event(event: dict) -> bool:
    """
    Valida se um evento possui os campos obrigatórios
    
    Args:
        event: Dicionário do evento
        
    Returns:
        True se válido, False caso contrário
    """
    required_fields = ['event_id', 'event_type', 'timestamp', 'user_id', 'session_id']
    return all(field in event for field in required_fields)


def sanitize_string(s: str, max_length: int = 255) -> str:
    """
    Sanitiza uma string removendo caracteres especiais e limitando tamanho
    
    Args:
        s: String para sanitizar
        max_length: Tamanho máximo
        
    Returns:
        String sanitizada
    """
    if not s:
        return ""
    
    # Remove caracteres nulos
    s = s.replace('\x00', '')
    
    # Limita tamanho
    if len(s) > max_length:
        s = s[:max_length]
    
    return s.strip()


class HealthChecker:
    """Classe para verificar saúde de componentes"""
    
    @staticmethod
    def check_kafka(bootstrap_servers: str, timeout: int = 5) -> bool:
        """
        Verifica se Kafka está acessível
        
        Args:
            bootstrap_servers: Endereço do Kafka
            timeout: Timeout em segundos
            
        Returns:
            True se acessível, False caso contrário
        """
        try:
            from kafka import KafkaAdminClient
            admin = KafkaAdminClient(
                bootstrap_servers=bootstrap_servers,
                request_timeout_ms=timeout * 1000
            )
            admin.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_postgres(config: dict, timeout: int = 5) -> bool:
        """
        Verifica se PostgreSQL está acessível
        
        Args:
            config: Dicionário de configuração do banco
            timeout: Timeout em segundos
            
        Returns:
            True se acessível, False caso contrário
        """
        try:
            import psycopg2
            conn = psycopg2.connect(
                **config,
                connect_timeout=timeout
            )
            conn.close()
            return True
        except Exception:
            return False


class MetricsCollector:
    """Coletor de métricas simples"""
    
    def __init__(self):
        self.metrics = {}
    
    def increment(self, metric_name: str, value: int = 1):
        """Incrementa uma métrica"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0
        self.metrics[metric_name] += value
    
    def set(self, metric_name: str, value: float):
        """Define valor de uma métrica"""
        self.metrics[metric_name] = value
    
    def get(self, metric_name: str) -> float:
        """Obtém valor de uma métrica"""
        return self.metrics.get(metric_name, 0)
    
    def get_all(self) -> dict:
        """Retorna todas as métricas"""
        return self.metrics.copy()
    
    def reset(self):
        """Reseta todas as métricas"""
        self.metrics = {}
