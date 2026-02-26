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

### 🌐 API Calls - Use quando precisar:
- Buscar dados de uma URL
- Fazer requisições HTTP/HTTPS
- Chamar APIs REST
- Obter informações de serviços externos

**api.call_api(url, method, headers, data, params)**
Exemplos de uso:
```
<tool>{"tool": "api", "action": "call_api", "url": "https://api.github.com/users/octocat", "method": "GET"}</tool>
<tool>{"tool": "api", "action": "call_api", "url": "https://jsonplaceholder.typicode.com/posts", "method": "POST", "data": {"title": "foo", "body": "bar"}}</tool>
```

### 📁 File Operations - Use quando precisar:
- Ler conteúdo de arquivos
- Salvar dados em arquivos
- Criar novos arquivos

**file.read_file(filepath)** - Ler arquivo
**file.write_file(filepath, content)** - Escrever arquivo
Exemplos:
```
<tool>{"tool": "file", "action": "read_file", "filepath": "./config.json"}</tool>
<tool>{"tool": "file", "action": "write_file", "filepath": "./output.txt", "content": "Hello World"}</tool>
```

### 📊 JSON Processing - Use quando precisar:
- Validar JSON
- Fazer parse de strings JSON

**json.parse_json(content)** - Parse JSON
**json.validate_json(content)** - Validar JSON

### 🐛 Debug & Analysis - Use quando:
- Houver erros para analisar
- Precisar sugerir soluções

**debug.analyze_error(error_message)** - Analisar erro

### ⚙️ System Info
**system.get_timestamp()** - Timestamp atual
**system.get_env_var(var_name)** - Ler variável de ambiente

---

## IMPORTANTE: Como decidir qual tool usar

**Perguntas que DEVEM usar api.call_api:**
- "Busque dados de [URL]"
- "Chame a API [nome]"
- "Faça uma requisição para..."
- "Obtenha informações de [endpoint]"
- "Consulte [serviço web]"

**Formato obrigatório:** <tool>{"tool": "...", "action": "...", "parametros": "..."}</tool>
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
        # Detectar intenção
        intent = self._detect_tool_intent(user_query)
        enhanced_query = self._enhance_query_with_intent(user_query, intent)

        # Buscar contexto dos documentos
        rag_context = self.doc_processor.build_context(user_query, k=3)

        tools_desc = self._format_tools_description()

        prompt = f"""Você é um assistente inteligente e útil com capacidade de:
1. Responder perguntas usando documentos fornecidos
2. Chamar APIs e endpoints HTTP
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

Pergunta do usuário: {enhanced_query}

Instruções:
- SEMPRE use uma tool quando a pergunta pedir para:
  * Buscar/obter/consultar dados de URL, API ou serviço web
  * Ler ou escrever arquivos
  * Executar operações de sistema
- Se precisar chamar uma tool, use EXATAMENTE o formato: <tool>{{...}}</tool>
- Forneça respostas claras e acionáveis
- Se encontrar um erro, use debug.analyze_error
- Sempre explique o que você está fazendo ANTES de chamar a tool
- Máximo de 2 chamadas de tool por resposta

EXEMPLO: Se o usuário pedir "busque dados de https://api.exemplo.com/users", você DEVE responder:
"Vou fazer uma chamada HTTP para obter os dados:
<tool>{{"tool": "api", "action": "call_api", "url": "https://api.exemplo.com/users", "method": "GET"}}</tool>"

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

    def _detect_tool_intent(self, user_query: str) -> Optional[str]:
        """Detecta automaticamente se a query requer uma tool específica"""
        query_lower = user_query.lower()

        # Padrões para chamadas HTTP/API
        http_patterns = [
            'http://', 'https://', 'api', 'endpoint', 'url',
            'busque dados de', 'obtenha dados de', 'consulte',
            'faça uma requisição', 'chame', 'acesse o endpoint'
        ]

        # Padrões para arquivos
        file_patterns = [
            'leia o arquivo', 'ler arquivo', 'salve no arquivo',
            'escreva no arquivo', 'arquivo', '.txt', '.json', '.csv'
        ]

        # Detectar intenção
        if any(pattern in query_lower for pattern in http_patterns):
            return "api_call"
        elif any(pattern in query_lower for pattern in file_patterns):
            return "file_operation"

        return None

    def _enhance_query_with_intent(self, user_query: str, intent: Optional[str]) -> str:
        """Adiciona dica de intenção à query se detectada"""
        if intent == "api_call":
            return f"""{user_query}

[DICA AUTOMÁTICA: Esta pergunta parece requerer uma chamada HTTP/API. Use a tool api.call_api]"""
        elif intent == "file_operation":
            return f"""{user_query}

[DICA AUTOMÁTICA: Esta pergunta parece requerer operação de arquivo. Use file.read_file ou file.write_file]"""

        return user_query

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

