# Agent Local com RAG - Guia Completo

Um **agent inteligente local** que:
- 📚 Consulta seus documentos (RAG)
- 🔗 Chama APIs e endpoints
- 📝 Manipula arquivos
- 🐛 Debugga e resolve problemas
- 🔄 Itera automaticamente para ações complexas

## Setup Rápido

### 1. Instalar Ollama
```bash
# macOS
brew install ollama

# Ou faça download em: https://ollama.ai
```

### 2. Baixar modelo Mistral (ou outro)
```bash
ollama pull mistral
ollama pull nomic-embed-text  # Para embeddings
```

### 3. Iniciar servidor Ollama
```bash
ollama serve
# Roda em http://localhost:11434
```

### 4. Em outro terminal, instalar dependências
```bash
pip install -r requirements.txt
```

### 5. Executar agent

**Modo com query direta:**
```bash
python main.py "Qual é o status da API de usuários?"
```

**Modo interativo:**
```bash
python main.py
```

## Exemplos de Uso

### Exemplo 1: Consultar documentação
```
Você: Como autenticar na API?
Agent: [consulta docs] → Responde com informações dos documentos
```

### Exemplo 2: Chamar API e processar resposta
```
Você: Busque os dados do usuário ID 123 em https://api.example.com/users/123
Agent: [chama endpoint] → [processa JSON] → Exibe resultado
```

### Exemplo 3: Resolver problema
```
Você: Recebi erro 401 ao chamar a API, o que fazer?
Agent: [busca docs] → [analisa erro] → Sugere soluções
```

### Exemplo 4: Criar arquivo baseado em API
```
Você: Faça uma requisição GET para https://api.example.com/data e salve o resultado em output.json
Agent: [chama API] → [valida JSON] → [salva arquivo] → Confirma
```

## Estrutura do Projeto

```
tale/
├── requirements.txt      # Dependências Python
├── main.py              # CLI principal
├── agent.py             # Lógica do agent
├── rag.py               # Processamento de documentos
├── tools.py             # Tools/Actions disponíveis
├── docs/                # Seus documentos (criar esta pasta)
│   ├── api.md           # Documentação de API
│   ├── guide.pdf        # Guias
│   └── ...
└── vector_store/        # Índice FAISS (criado automaticamente)
```

## Adicionar Documentos

1. Crie uma pasta `./docs/`
2. Adicione seus arquivos (PDF, TXT, MD, DOCX)
3. Execute o agent - ele carregará automaticamente

```bash
mkdir -p docs
cp seu-documento.pdf docs/
python main.py "pergunta sobre seu documento"
```

## Adicionar Novas Tools

Abra `tools.py` e crie uma nova classe:

```python
class MyTool:
    @staticmethod
    def my_action(param1: str) -> ToolResult:
        """Descrição da ação"""
        try:
            # Sua lógica aqui
            return ToolResult(success=True, data=resultado)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

Depois registre em `TOOLS`:
```python
TOOLS = {
    ...
    "mytool": MyTool,
}
```

Use no agent:
```
<tool>{"tool": "mytool", "action": "my_action", "param1": "valor"}</tool>
```

## Configurações

### Trocar modelo de LLM
```python
agent = Agent(model_name="neural-chat")  # ou "llama2", "orca", etc
```

### Ajustar RAG
```python
# Em rag.py, método chunk_documents()
agent.doc_processor.chunk_documents(
    chunk_size=2000,      # Tamanho dos chunks
    chunk_overlap=400     # Sobreposição
)
```

### Aumentar iterações
```python
agent.max_iterations = 20  # Padrão: 10
```

## Troubleshooting

### Erro: "Connection refused"
```bash
# Ollama não está rodando, execute:
ollama serve
```

### Erro: "Model not found"
```bash
# Baixe o modelo:
ollama pull mistral
ollama pull nomic-embed-text
```

### Documentos não carregam
```bash
# Verificar pasta docs/
ls -la docs/

# Se vazia, criar exemplos:
python main.py  # Cria exemplos automaticamente
```

### Agent muito lento
- Reduza `chunk_size` em `rag.py`
- Use modelo mais leve: `ollama pull phi` (2GB)
- Reduza `k` em `search()`: `k=2` em vez de `k=3`

## Segurança & Privacidade

- ✅ Tudo roda **localmente**
- ✅ Nenhum dado é enviado para cloud
- ✅ Controle total sobre documentos
- ⚠️ Proteja sua pasta `docs/` e `.env` (se usar)

## Próximas Melhorias

- [ ] Integração com mais modelos locais
- [ ] Cache de embeddings
- [ ] Web UI com Streamlit
- [ ] Logging e auditoria
- [ ] Suporte a banco de dados (SQLite)
- [ ] Agentes especializados (finance, devops, etc)

## Referências

- [Ollama](https://ollama.ai)
- [LangChain](https://langchain.com)
- [FAISS](https://github.com/facebookresearch/faiss)
- [RAG Pattern](https://python.langchain.com/docs/use_cases/question_answering/)

---

**Desenvolvido com ❤️ para automação local**

