# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [1.0.0] - 2026-02-09

### Adicionado
- Pipeline de dados em tempo real completo
- Gerador de eventos (Producer) com Apache Kafka
- Processador de eventos (Consumer) com persistência em PostgreSQL
- Dashboard web interativo com métricas em tempo real
- Containerização completa com Docker e Docker Compose
- Testes unitários com pytest
- Documentação completa (README, QUICKSTART, ARCHITECTURE)
- CI/CD com GitHub Actions
- Makefile com comandos úteis
- Scripts de análise de dados
- Sistema de logging estruturado
- Health checks para todos os serviços
- Views materializadas no PostgreSQL
- Índices otimizados para queries
- Connection pooling no consumer
- Batch processing para melhor performance
- Retry logic com backoff exponencial
- Validação de eventos
- Métricas coletadas em tempo real

### Tipos de Eventos Suportados
- `page_view` - Visualização de página de produto
- `add_to_cart` - Adição de produto ao carrinho
- `remove_from_cart` - Remoção de produto do carrinho
- `purchase` - Compra realizada
- `search` - Busca de produtos

### Métricas do Dashboard
- Total de eventos processados
- Transações realizadas
- Receita total e por período
- Usuários únicos
- Timeline de eventos
- Top 10 produtos mais vendidos
- Distribuição por categoria
- Tipos de eventos
- Taxa de conversão

### Infraestrutura
- Apache Kafka 3.5.0
- Zookeeper para coordenação
- PostgreSQL 15
- Python 3.9+
- Flask para API REST
- Plotly.js para visualizações

### DevOps
- Docker Compose para orquestração
- Healthchecks automáticos
- Volumes persistentes
- Network isolation
- Auto-restart de containers

### Documentação
- README completo com badges
- Guia de início rápido (5 minutos)
- Documentação de arquitetura detalhada
- Guia de contribuição
- Licença MIT
- Changelog

### Qualidade de Código
- Testes unitários
- Code coverage
- Linting com flake8
- Type hints
- Docstrings
- Conventional commits

## [0.1.0] - 2026-02-08

### Adicionado
- Projeto inicial
- Estrutura básica de diretórios
- Configuração inicial

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correção de bugs
- `Segurança` para vulnerabilidades corrigidas

## Links

[Unreleased]: https://github.com/seu-usuario/real-time-data-pipeline/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/seu-usuario/real-time-data-pipeline/releases/tag/v1.0.0
[0.1.0]: https://github.com/seu-usuario/real-time-data-pipeline/releases/tag/v0.1.0
