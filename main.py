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


def main():
    """Função principal"""
    print_header()

    # Criar docs de exemplo se não existirem
    if not Path("./docs").exists():
        console.print("[yellow]Criando documentos de exemplo...[/yellow]")

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
