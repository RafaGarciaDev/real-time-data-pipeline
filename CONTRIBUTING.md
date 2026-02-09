# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o Pipeline de Dados em Tempo Real! Este documento fornece diretrizes para contribuições.

## Código de Conduta

Este projeto adere a padrões de conduta profissional. Ao participar, espera-se que você:

- Use linguagem acolhedora e inclusiva
- Seja respeitoso com diferentes pontos de vista
- Aceite críticas construtivas graciosamente
- Foque no que é melhor para a comunidade

## Como Contribuir

### Reportando Bugs

Antes de criar um bug report:
1. Verifique se o bug já foi reportado
2. Colete informações sobre o problema
3. Tente reproduzir com configuração limpa

**Template de Bug Report**:
```markdown
**Descrição do Bug**
Descrição clara e concisa do que ocorreu.

**Passos para Reproduzir**
1. Execute '...'
2. Faça '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots/Logs**
Se aplicável, adicione screenshots ou logs.

**Ambiente**
- OS: [ex: Ubuntu 22.04]
- Docker: [ex: 24.0.7]
- Python: [ex: 3.9]
```

### Sugerindo Melhorias

**Template de Feature Request**:
```markdown
**Problema que Resolve**
Descrição clara do problema.

**Solução Proposta**
Como você imagina que isso funcione.

**Alternativas Consideradas**
Outras soluções que você considerou.

**Contexto Adicional**
Qualquer outra informação relevante.
```

### Pull Requests

1. **Fork o Repositório**
```bash
git clone https://github.com/seu-usuario/real-time-data-pipeline.git
cd real-time-data-pipeline
```

2. **Crie uma Branch**
```bash
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bug-fix
```

3. **Faça suas Mudanças**
- Siga os padrões de código
- Adicione testes se aplicável
- Atualize documentação

4. **Commit suas Mudanças**
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
```

**Padrão de Commits** (Conventional Commits):
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças em documentação
- `style:` - Formatação, ponto-e-vírgula faltando, etc
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Atualização de tarefas de build, configs, etc

5. **Push para sua Branch**
```bash
git push origin feature/minha-feature
```

6. **Abra um Pull Request**
- Descreva claramente as mudanças
- Referencie issues relacionadas
- Adicione screenshots se aplicável

## Padrões de Desenvolvimento

### Estilo de Código Python

Seguimos PEP 8 com algumas exceções:

```python
# Bom
def process_event(event: dict) -> bool:
    """
    Processa um evento individual.
    
    Args:
        event: Dicionário com dados do evento
        
    Returns:
        True se processado com sucesso
    """
    if not validate_event(event):
        return False
    
    # Processamento
    return True

# Ruim
def process_event(event):
    if not validate_event(event): return False
    return True
```

**Ferramentas Recomendadas**:
- Black para formatação
- Flake8 para linting
- mypy para type checking

```bash
# Instalar ferramentas
pip install black flake8 mypy

# Executar
black src/
flake8 src/
mypy src/
```

### Testes

Todo código novo deve incluir testes:

```python
# tests/test_nova_feature.py
import pytest
from src.module import nova_funcao


def test_nova_funcao_caso_basico():
    """Testa caso básico"""
    resultado = nova_funcao(input_valido)
    assert resultado == esperado


def test_nova_funcao_edge_case():
    """Testa edge case"""
    with pytest.raises(ValueError):
        nova_funcao(input_invalido)
```

Execute testes:
```bash
make test
```

### Documentação

- Docstrings para todas as funções públicas
- README atualizado para novas features
- Comentários para lógica complexa

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Descrição breve da função.
    
    Descrição mais detalhada se necessário,
    explicando casos de uso e comportamentos.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
        
    Returns:
        Dicionário com resultados processados
        
    Raises:
        ValueError: Se param2 for negativo
        
    Example:
        >>> complex_function("test", 42)
        {'status': 'success', 'value': 42}
    """
    pass
```

## Estrutura de Diretórios

Ao adicionar novos arquivos:

```
real-time-data-pipeline/
├── src/              # Código fonte
│   ├── producer.py
│   ├── consumer.py
│   └── novo_modulo.py
├── tests/            # Testes
│   └── test_novo_modulo.py
├── docker/           # Dockerfiles
├── docs/             # Documentação extra
└── scripts/          # Scripts utilitários
```

## Checklist do Pull Request

Antes de submeter, verifique:

- [ ] Código segue padrões do projeto
- [ ] Testes passam (`make test`)
- [ ] Testes adicionados para novo código
- [ ] Documentação atualizada
- [ ] Commit messages seguem padrão
- [ ] Branch atualizada com main
- [ ] Sem conflitos de merge
- [ ] Build Docker funciona
- [ ] README atualizado se necessário

## Processo de Review

1. Mantenedores revisam PR
2. Feedback é dado via comentários
3. Faça mudanças solicitadas
4. Push para mesma branch
5. Aprovação e merge

## Desenvolvimento Local

### Setup Inicial

```bash
# Clone
git clone https://github.com/seu-usuario/real-time-data-pipeline.git
cd real-time-data-pipeline

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências
make install

# Iniciar apenas infra
make dev
```

### Workflow de Desenvolvimento

```bash
# 1. Criar branch
git checkout -b feature/minha-feature

# 2. Desenvolver
# ... editar código ...

# 3. Testar localmente
python src/producer.py  # Terminal 1
python src/consumer.py  # Terminal 2
python src/dashboard.py # Terminal 3

# 4. Executar testes
make test

# 5. Commit e push
git add .
git commit -m "feat: minha feature"
git push origin feature/minha-feature

# 6. Abrir PR no GitHub
```

## Recursos Úteis

- [Documentação Python](https://docs.python.org/3/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## Dúvidas?

- Abra uma issue
- Entre em contato via email
- Participe das discussões

## Agradecimentos

Obrigado por contribuir! Cada contribuição, por menor que seja, é valiosa para o projeto.
