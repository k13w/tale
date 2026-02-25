#!/usr/bin/env python3
"""
CLI simples para o Agent agentic local
Uso: python main.py "sua pergunta aqui"
"""

import sys
import os
from pathlib import Path
from agent import Agent
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def print_header():
    """Exibe header da aplicação"""
    console.print(Panel(
        "[bold cyan]🤖 AGENT LOCAL COM RAG[/bold cyan]\n"
        "[dim]Processamento de documentos + Execução de actions[/dim]",
        expand=False,
        border_style="cyan"
    ))

def initialize_agent() -> Agent:
    """Inicializa o agent"""
    agent = Agent(
        model_name="mistral",
        ollama_base_url="http://localhost:11434",
        docs_path="./docs"
    )
    return agent

def create_sample_docs():
    """Cria documentos de exemplo"""
    docs_dir = Path("./docs")
    docs_dir.mkdir(exist_ok=True)

    # Exemplo 1: API Documentation
    api_doc = """
# Documentação da API

## Endpoints disponíveis

### GET /users
Retorna lista de usuários
- Status: 200
- Response: {"users": [...]}

### GET /users/{id}
Retorna um usuário específico
- Parâmetros: id (obrigatório)
- Status: 200, 404

### POST /users
Cria novo usuário
- Body: {"name": string, "email": string}
- Status: 201

## Erros comuns

- 401: Autenticação necessária
- 404: Recurso não encontrado
- 500: Erro no servidor
"""

    # Exemplo 2: Troubleshooting
    troubleshooting_doc = """
# Guia de Troubleshooting

## Problema: Timeout em requisições

### Causas possíveis
1. Servidor lento
2. Problema de rede
3. Timeout muito curto

### Soluções
1. Aumentar timeout para 30s
2. Verificar conectividade
3. Tentar novamente

## Problema: Erro 401

### Causas
- Credenciais inválidas
- Token expirado

### Soluções
1. Verificar API key
2. Renovar token
3. Verificar permissões
"""

    # Salvar documentos
    (docs_dir / "api.md").write_text(api_doc)
    (docs_dir / "troubleshooting.md").write_text(troubleshooting_doc)

    console.print("[green]✓ Documentos de exemplo criados em ./docs/[/green]")

def main():
    """Função principal"""
    print_header()

    # Criar docs de exemplo se não existirem
    if not Path("./docs").exists():
        console.print("[yellow]Criando documentos de exemplo...[/yellow]")
        create_sample_docs()

    # Inicializar agent
    console.print("[cyan]Inicializando agent...[/cyan]")
    agent = initialize_agent()

    # Preparar documentos
    if not agent.initialize_docs():
        console.print("[red]Erro ao carregar documentos[/red]")
        sys.exit(1)

    # Processar queries
    if len(sys.argv) > 1:
        # Query passada como argumento
        query = " ".join(sys.argv[1:])
        response = agent.chat(query)
        console.print(Panel(response, border_style="green", title="Resposta do Agent"))
    else:
        # Modo interativo
        console.print("\n[cyan]Entrando em modo interativo...[/cyan]")
        console.print("[dim]Digite 'sair' para encerrar[/dim]\n")

        while True:
            try:
                query = console.input("[bold cyan]Você:[/bold cyan] ")

                if query.lower() in ["sair", "exit", "quit"]:
                    console.print("[yellow]Encerrando...[/yellow]")
                    break

                if not query.strip():
                    continue

                response = agent.chat(query)
                console.print(Panel(response, border_style="green", title="Agent"))

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrompido pelo usuário[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Erro: {e}[/red]")

if __name__ == "__main__":
    main()

