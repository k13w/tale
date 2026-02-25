#!/usr/bin/env bash
# CHECKLIST DE SETUP - Siga passo-a-passo

echo "═══════════════════════════════════════════════════════════════"
echo "  🤖 AGENT LOCAL COM RAG - CHECKLIST DE SETUP"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# CORES
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_mark() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# ============================================================================
echo "PASSO 1: Verificar Prerequisites"
echo "─────────────────────────────────────────────────────────────────────"

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    check_mark "Python 3 instalado (v$PYTHON_VERSION)"
else
    error "Python 3 não encontrado. Instale em: https://www.python.org"
    exit 1
fi

# Verificar Ollama
if command -v ollama &> /dev/null; then
    check_mark "Ollama instalado"
else
    warning "Ollama não encontrado"
    echo "  Instale em: https://ollama.ai"
    echo "  Depois rode: ollama serve"
    read -p "  Deseja continuar mesmo assim? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# ============================================================================
echo "PASSO 2: Setup do Projeto"
echo "─────────────────────────────────────────────────────────────────────"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    check_mark "Ambiente virtual criado"
else
    check_mark "Ambiente virtual já existe"
fi

# Ativar venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
check_mark "Ambiente virtual ativado"

# Instalar dependências
echo ""
echo "Instalando dependências Python..."
pip install -q -r requirements.txt
check_mark "Dependências instaladas"

echo ""

# ============================================================================
echo "PASSO 3: Criar Pastas Necessárias"
echo "─────────────────────────────────────────────────────────────────────"

mkdir -p docs
check_mark "Pasta 'docs/' criada"

mkdir -p vector_store
check_mark "Pasta 'vector_store/' criada"

echo ""

# ============================================================================
echo "PASSO 4: Verificar Ollama"
echo "─────────────────────────────────────────────────────────────────────"

# Tentar conectar ao Ollama
if curl -s http://localhost:11434/api/tags &>/dev/null; then
    check_mark "Ollama server rodando em localhost:11434"

    # Verificar modelos
    echo ""
    echo "Modelos disponíveis:"
    curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | while read model; do
        check_mark "$model"
    done
else
    warning "Ollama server não está rodando"
    echo ""
    echo "⚠️  IMPORTANTE: Execute em outro terminal:"
    echo ""
    echo "  ${YELLOW}ollama serve${NC}"
    echo ""
    echo "E em um terceiro terminal, baixe os modelos:"
    echo ""
    echo "  ${YELLOW}ollama pull mistral${NC}"
    echo "  ${YELLOW}ollama pull nomic-embed-text${NC}"
    echo ""
    read -p "Pressione Enter quando Ollama estiver rodando..."
fi

echo ""

# ============================================================================
echo "PASSO 5: Criar Documentos de Exemplo"
echo "─────────────────────────────────────────────────────────────────────"

if [ ! -f "docs/api.md" ]; then
    python3 << 'EOF'
docs_dir = "docs"

api_doc = """# Documentação da API

## Endpoints

### GET /users
Retorna lista de usuários

### POST /login
Faz login
Body: {"email": "...", "password": "..."}

## Erros

- 401: Autenticação necessária
- 404: Recurso não encontrado
"""

with open(f"{docs_dir}/api.md", "w") as f:
    f.write(api_doc)
EOF
    check_mark "Documentos de exemplo criados"
else
    check_mark "Documentos já existem"
fi

echo ""

# ============================================================================
echo "PASSO 6: Testar Agent"
echo "─────────────────────────────────────────────────────────────────────"

echo ""
echo "Pronto para teste! Execute:"
echo ""
echo "  ${GREEN}python main.py${NC}"
echo ""
echo "Ou com uma pergunta:"
echo ""
echo "  ${GREEN}python main.py \"Qual é a documentação da API?\"${NC}"
echo ""

# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ SETUP COMPLETO!"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "📚 Próximas leituras:"
echo "  1. QUICK_START.md"
echo "  2. DEMO_VISUAL.md"
echo "  3. README.md"
echo ""

echo "🔗 Recursos:"
echo "  - Adicionar documentos em ./docs/"
echo "  - Criar Tools em tools.py"
echo "  - Customizar em agent.py"
echo ""

echo "🆘 Troubleshooting:"
echo "  - Se 'Connection refused': ollama serve"
echo "  - Se 'Model not found': ollama pull mistral"
echo "  - Se ImportError: pip install -r requirements.txt"
echo ""

echo "🚀 Você está pronto para usar seu Agent Local!"
echo ""

