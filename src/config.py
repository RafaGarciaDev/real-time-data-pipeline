"""
Configurações centralizadas do projeto
"""

import os
from typing import Dict


class Config:
    """Classe base de configuração"""
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ecommerce-events')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'ecommerce-consumer-group')
    
    # PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'pipeline_db')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin123')
    
    @classmethod
    def get_postgres_config(cls) -> Dict[str, str]:
        """Retorna configuração do PostgreSQL como dicionário"""
        return {
            'host': cls.POSTGRES_HOST,
            'port': cls.POSTGRES_PORT,
            'database': cls.POSTGRES_DB,
            'user': cls.POSTGRES_USER,
            'password': cls.POSTGRES_PASSWORD
        }
    
    @classmethod
    def get_postgres_uri(cls) -> str:
        """Retorna URI de conexão do PostgreSQL"""
        return (
            f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    """Configuração para testes"""
    DEBUG = True
    TESTING = True
    POSTGRES_DB = 'pipeline_test_db'


# Mapeamento de ambientes
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}


def get_config(env: str = None) -> Config:
    """
    Retorna a configuração apropriada baseada no ambiente
    
    Args:
        env: Nome do ambiente (development, production, test)
        
    Returns:
        Classe de configuração apropriada
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'production')
    
    return config_by_name.get(env, ProductionConfig)
