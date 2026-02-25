import re
import json
from typing import Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from tools import execute_tool, ToolResult
from rag import DocumentProcessor

class Agent:
    """Agent agentic com RAG e tools"""

    def __init__(
        self,
        model_name: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        docs_path: str = "./docs"
    ):
        self.model_name = model_name
        self.llm = ChatOllama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=0.7
        )
        self.doc_processor = DocumentProcessor(docs_path=docs_path)
        self.conversation_history = []
        self.max_iterations = 10  # Limite de iterações para evitar loops infinitos

    def _format_tools_description(self) -> str:
        """Retorna descrição formatada das tools disponíveis"""
        return """
## Tools Disponíveis:

### API Calls
- **api.call_api(url, method, headers, data, params)**: Chamar endpoints HTTP
  Exemplo: {"tool": "api", "action": "call_api", "url": "https://...", "method": "GET"}

### File Operations
- **file.read_file(filepath)**: Ler arquivo
- **file.write_file(filepath, content)**: Escrever arquivo

### JSON Processing
- **json.parse_json(content)**: Parse JSON
- **json.validate_json(content)**: Validar JSON

### Debug & Analysis
- **debug.analyze_error(error_message)**: Analisar erro e sugerir solução

### System Info
- **system.get_timestamp()**: Timestamp atual
- **system.get_env_var(var_name)**: Ler variável de ambiente

Use este formato para chamar tools: <tool>{"tool": "name", "action": "method", ...params}</tool>
"""

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse de chamadas de tool no formato <tool>{...}</tool>"""
        pattern = r'<tool>(.*?)</tool>'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def _execute_tool_from_call(self, tool_call: Dict[str, Any]) -> ToolResult:
        """Executa uma tool a partir de um dicionário"""
        tool_name = tool_call.get("tool")
        action = tool_call.get("action")

        # Remove 'tool' e 'action' dos kwargs
        kwargs = {k: v for k, v in tool_call.items() if k not in ["tool", "action"]}

        return execute_tool(tool_name, action, **kwargs)

    def _build_prompt(self, user_query: str) -> str:
        """Constrói prompt com contexto RAG e tools"""
        # Buscar contexto dos documentos
        rag_context = self.doc_processor.build_context(user_query, k=3)

        tools_desc = self._format_tools_description()

        prompt = f"""Você é um assistente inteligente e útil com capacidade de:
1. Responder perguntas usando documentos fornecidos
2. Chamar APIs e endpoints
3. Manipular arquivos
4. Analisar e debugar erros
5. Executar ações para resolver problemas

{tools_desc}

---

{rag_context}

---

Histórico da conversa:
{self._format_conversation_history()}

---

Pergunta do usuário: {user_query}

Instruções:
- Se precisar chamar uma tool, use o formato <tool>{{...}}</tool>
- Forneça respostas claras e acionáveis
- Se encontrar um erro, use debug.analyze_error para sugerir soluções
- Sempre explique o que você está fazendo
- Máximo de 2 chamadas de tool por resposta

Sua resposta:
"""
        return prompt

    def _format_conversation_history(self) -> str:
        """Formata histórico da conversa"""
        if not self.conversation_history:
            return "(Sem histórico)"

        formatted = []
        for item in self.conversation_history[-4:]:  # Últimas 4 mensagens
            formatted.append(f"{item['role'].upper()}: {item['content'][:200]}...")

        return "\n".join(formatted)

    def chat(self, user_query: str) -> str:
        """Chat com iteração automática de tools"""
        print(f"\n🤖 Agent processando: {user_query}\n")

        iteration = 0
        current_query = user_query

        while iteration < self.max_iterations:
            iteration += 1

            # Construir e invocar LLM
            prompt = self._build_prompt(current_query)
            response = self.llm.invoke(prompt)
            response_text = response.content

            print(f"[Iteração {iteration}] Resposta do agent:\n{response_text}\n")

            # Verificar se há chamada de tool
            tool_call = self._parse_tool_call(response_text)

            if not tool_call:
                # Sem tool call, retornar resposta final
                self.conversation_history.append({
                    "role": "user",
                    "content": user_query
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
                return response_text

            # Executar tool
            print(f"🔧 Executando tool: {tool_call.get('tool')}.{tool_call.get('action')}")
            result = self._execute_tool_from_call(tool_call)

            print(f"📊 Resultado: {result}\n")

            # Construir nova query com resultado
            if result.success:
                current_query = f"""Resultado da execução anterior:
Tool: {tool_call.get('tool')}.{tool_call.get('action')}
Sucesso: Sim
Dados: {json.dumps(result.data, ensure_ascii=False)[:500]}

Pergunta original: {user_query}
Por favor, use esse resultado para responder a pergunta original ou execute a próxima ação necessária."""
            else:
                current_query = f"""Erro na execução anterior:
Tool: {tool_call.get('tool')}.{tool_call.get('action')}
Erro: {result.error}

Pergunta original: {user_query}
Por favor, suira outro approach ou analise o erro."""

        return f"⚠️  Máximo de iterações ({self.max_iterations}) atingido"

    def initialize_docs(self) -> bool:
        """Inicializa documentos e vector store"""
        print("📚 Carregando documentos...")
        docs = self.doc_processor.load_documents()

        if not docs:
            print("⚠️  Nenhum documento carregado. Crie arquivos em ./docs/")
            return False

        print("🔄 Criando índice...")
        chunks = self.doc_processor.chunk_documents()
        self.doc_processor.create_vector_store(chunks)
        self.doc_processor.save_vector_store()

        print("✓ Documentos preparados!")
        return True

