# 🚀 QUICK START - Agent Local

## 1️⃣ Instalar & Configurar (5 min)

```bash
# Instalar Ollama (macOS)
brew install ollama

# Ou baixe em: https://ollama.ai
```

## 2️⃣ Terminal 1 - Inicie o Ollama

```bash
ollama serve
# Aguarde a mensagem: "Listening on localhost:11434"
```

## 3️⃣ Terminal 2 - Download de Modelos

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

## 4️⃣ Terminal 3 - Setup do Project

```bash
cd /Users/gilmar.filho/GolandProjects/tale

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 5️⃣ Terminal 3 - Execute!

```bash
# Modo interativo
python main.py

# Ou com query direta
python main.py "Qual é a documentação da API?"
```

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────────────┐
│               TERMINAL (CLI)                        │
│            python main.py "pergunta"                │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   AGENT (agent.py)    │
         │  - LLM (Ollama)       │
         │  - RAG (FAISS)        │
         │  - Tool Executor      │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼─┐    ┌────▼────┐   ┌──▼──┐
    │ RAG │    │  TOOLS   │   │ LLM  │
    └─────┘    └──────────┘   └──────┘
      │            │             │
  ┌───▼────┐   ┌───▼────────┐  │
  │FAISS   │   │API,Files,  │  │
  │Vector  │   │JSON,Debug  │  │
  │Store   │   │System      │  │
  └────────┘   └────────────┘  │
                                │
                    ┌───────────▼─────┐
                    │ Ollama Server   │
                    │ :11434          │
                    └─────────────────┘
```

---

## 🎯 O que você pode fazer

### ✅ Consultar documentos
```
Agent: "Como uso a API de autenticação?"
```

### ✅ Chamar APIs
```
Agent: "Busque dados em https://api.example.com/users"
```

### ✅ Processar dados
```
Agent: "Valide este JSON e salve em output.json"
```

### ✅ Debugar problemas
```
Agent: "Recebi erro 404, o que fazer?"
```

### ✅ Executar ações em cadeia
```
Agent: "Chame a API, processe a resposta e crie um arquivo"
```

---

## 📁 Adicionar seus documentos

```bash
# Crie a pasta
mkdir -p docs

# Adicione seus arquivos (PDF, TXT, MD, DOCX)
cp seu-documento.pdf docs/
cp seu-guia.md docs/

# Execute - agent carrega automaticamente
python main.py "pergunta sobre seu documento"
```

---

## 🔧 Editar Tools

Abra `tools.py` e adicione novas actions:

```python
class MyTool:
    @staticmethod
    def my_action(param: str) -> ToolResult:
        # Sua lógica aqui
        return ToolResult(success=True, data=resultado)
```

Registre em `TOOLS` e use:
```
<tool>{"tool": "mytool", "action": "my_action", "param": "valor"}</tool>
```

---

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| "Connection refused" | Execute `ollama serve` no Terminal 1 |
| "Model not found" | Execute `ollama pull mistral` |
| Documentos não carregam | Crie pasta `docs/` e adicione arquivos |
| Muito lento | Use modelo mais leve: `ollama pull phi` |

---

## 📚 Estrutura

```
tale/
├── main.py              ← Executar isto!
├── agent.py             ← Lógica principal
├── rag.py               ← Processamento de docs
├── tools.py             ← Actions/Tools
├── requirements.txt     ← Dependências
├── docs/                ← Seus documentos
└── vector_store/        ← Cache (criado auto)
```

---

## 🎓 Aprenda mais

Veja exemplos em `EXAMPLES.txt` e documentation em `README.md`

**Pronto! Seu agent local está funcionando! 🎉**

