#!/bin/bash
# setup.sh - Setup rápido do projeto

echo "🚀 Configurando Agent Local..."

# Instalar Ollama se não existir
if ! command -v ollama &> /dev/null; then
    echo "📥 Instalando Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Criar pasta de docs
mkdir -p docs

echo ""
echo "✅ Setup concluído!"
echo ""
echo "⏭️  Próximos passos:"
echo ""
echo "1. Em um terminal, inicie o Ollama:"
echo "   ollama serve"
echo ""
echo "2. Em outro terminal, baixe os modelos:"
echo "   ollama pull mistral"
echo "   ollama pull nomic-embed-text"
echo ""
echo "3. Execute o agent:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""

