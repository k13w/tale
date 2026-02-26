import re
import json
import uuid
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

        # Rastreamento de estado para detectar loops e conclusões
        self.execution_history = []  # Histórico de execuções (tool + resultado)
        self.last_tool_call = None  # Última tool chamada
        self.consecutive_successes = 0  # Contador de sucessos consecutivos

    def _format_tools_description(self) -> str:
        """Retorna descrição formatada das tools disponíveis"""
        return """
## Tools Disponíveis (FORMATO: <tool>{...}</tool>):

### 🌐 API Calls
Use quando precisar: buscar dados, chamar APIs, fazer requisições HTTP/HTTPS

FORMATO:
<tool>{"tool": "api", "action": "call_api", "url": "https://...", "method": "GET", "headers": {...}, "data": {...}}</tool>

EXEMPLOS:
GET: <tool>{"tool": "api", "action": "call_api", "url": "https://api.github.com/users/octocat", "method": "GET"}</tool>
POST: <tool>{"tool": "api", "action": "call_api", "url": "https://api.exemplo.com/users", "method": "POST", "data": {"nome": "João", "email": "joao@example.com"}}</tool>
Headers: <tool>{"tool": "api", "action": "call_api", "url": "http://...", "method": "POST", "headers": {"Authorization": "Bearer token", "X-Custom": "value"}, "data": {...}}</tool>

---

### 📁 File Operations
Use quando precisar: ler, escrever ou criar arquivos

FORMATO:
Ler: <tool>{"tool": "file", "action": "read_file", "filepath": "./arquivo.txt"}</tool>
Escrever: <tool>{"tool": "file", "action": "write_file", "filepath": "./output.txt", "content": "conteúdo aqui"}</tool>

---

### 📊 JSON Processing
Use quando precisar: validar ou fazer parse de JSON

FORMATO:
<tool>{"tool": "json", "action": "parse_json", "content": "{\\"key\\": \\"value\\"}"}</tool>
<tool>{"tool": "json", "action": "validate_json", "content": "{\\"key\\": \\"value\\"}"}</tool>

---

### 🐛 Debug & Analysis
Use quando houver erros para analisar

FORMATO:
<tool>{"tool": "debug", "action": "analyze_error", "error_message": "descrição do erro"}</tool>

---

### ⚙️ System Info
Use quando precisar de timestamp ou variáveis de ambiente

FORMATO:
<tool>{"tool": "system", "action": "get_timestamp"}</tool>
<tool>{"tool": "system", "action": "get_env_var", "var_name": "HOME"}</tool>

"""

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse de chamadas de tool no formato <tool>{...}</tool>"""
        # Tenta primeiro o padrão padrão
        pattern = r'<tool>(.*?)</tool>'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            json_str = match.group(1).strip()

            # Tenta fazer parse do JSON
            result = self._try_parse_json(json_str)
            if result:
                return result

        # Se não encontrou, tenta extrair JSON entre chaves
        # Padrão alternativo: procura por { ... } mesmo sem <tool> tags
        json_pattern = r'\{.*?"tool".*?"action".*?\}'
        json_match = re.search(json_pattern, text, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            result = self._try_parse_json(json_str)
            if result:
                return result

        return None

    def _try_parse_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """Tenta fazer parse de JSON com várias estratégias"""
        # Estratégia 1: Tentar parse direto
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Estratégia 2: Converter single quotes para double quotes
        try:
            # Replace single quotes que envolvem valores
            fixed_json = re.sub(r"'([^']*)'", r'"\1"', json_str)
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            pass

        # Estratégia 3: Remover comentários e espaços problemáticos
        try:
            # Remove trailing commas
            fixed_json = re.sub(r',(\s*[}\]])', r'\1', json_str)
            # Replace single quotes
            fixed_json = re.sub(r"'([^']*)'", r'"\1"', fixed_json)
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            pass

        print(f"⚠️  Falha ao fazer parse de JSON após 3 tentativas")
        print(f"   JSON string: {json_str[:100]}...")
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

═══════════════════════════════════════════════════════════════════════════════

🔴 INSTRUÇÕES CRÍTICAS - LEIA COM ATENÇÃO:

## Transaction ID:
Se você vir "[SISTEMA: Transaction ID gerado automaticamente: ...]" na pergunta:
- USE esse ID nas chamadas de API
- É um UUID único gerado para esta ação
- Se o usuário não informou um ID, use o gerado automaticamente

## Quando chamar uma TOOL:
1. Você PRECISA chamar uma tool se a pergunta pede para chamar API, ler/escrever arquivo, etc
2. A tool DEVE ser chamada em PRIMEIRO, no formato EXATO: <tool>{{"tool": "...", "action": "...", ...}}</tool>
3. DEPOIS da tool, você pode explicar o que fez ou pedir próximos passos

❌ ERRADO (Explicação ANTES da tool):
"Vou fazer uma chamada HTTP para..."
<tool>{{...}}</tool>

✅ CORRETO (Tool PRIMEIRO, depois explicação):
<tool>{{"tool": "api", "action": "call_api", "url": "...", "method": "GET"}}</tool>
"Acabo de executar a chamada HTTP. Os dados foram..."

═══════════════════════════════════════════════════════════════════════════════

## CRITÉRIOS DE PARADA (QUANDO PARAR):
⛔ VOCÊ DEVE PARAR (NÃO chamar mais tools) SE:
1. A ação foi executada com sucesso (success=True) E resolveu o problema original
2. Você receber um erro recuperável e já tentou uma solução alternativa
3. A resposta final responde completamente à pergunta do usuário
4. Você não consegue executar a ação mesmo após várias tentativas

✅ SINAIS DE CONCLUSÃO (termine com resposta clara):
- "Ação concluída com sucesso"
- "Problema resolvido"
- "Pronto! [descrição do que foi feito]"
- "A solicitação foi processada"
- "Feito! [confirmação do resultado]"

═══════════════════════════════════════════════════════════════════════════════

EXEMPLO CORRETO COMPLETO:

Usuário: "busque dados de https://api.github.com/users/octocat"

Sua resposta:
<tool>{{"tool": "api", "action": "call_api", "url": "https://api.github.com/users/octocat", "method": "GET"}}</tool>

Encontrei os dados do usuário octocat. A requisição foi bem-sucedida e retornou as informações do perfil.

═══════════════════════════════════════════════════════════════════════════════

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

    def _is_conclusive_response(self, response_text: str) -> bool:
        """Detecta se a resposta indica conclusão da tarefa"""
        conclusive_patterns = [
            'ação concluída',
            'problema resolvido',
            'pronto',
            'feito',
            'solicitação foi processada',
            'sucesso',
            'concluído com êxito',
            'tarefa finalizada',
            'operação completa'
        ]

        response_lower = response_text.lower()
        return any(pattern in response_lower for pattern in conclusive_patterns)

    def _detect_repeated_tool_call(self, tool_call: Dict[str, Any]) -> bool:
        """Detecta se a mesma tool foi chamada repetidas vezes (indicativo de loop)"""
        if not self.execution_history:
            return False

        # Extrair identificador da tool
        current_tool_id = f"{tool_call.get('tool')}.{tool_call.get('action')}"

        # Contar quantas vezes essa tool foi executada recentemente
        recent_calls = [
            exec_history for exec_history in self.execution_history[-3:]
            if exec_history['tool_id'] == current_tool_id
        ]

        # Se a mesma tool foi chamada 2+ vezes nos últimos 3, é um loop
        return len(recent_calls) >= 2

    def _detect_infinite_loop(self, current_query: str) -> bool:
        """Detecta se estamos em um loop infinito (mesma query reconstruída)"""
        if not self.execution_history:
            return False

        # Se as últimas 2 execuções tiveram tools idênticas, é suspeito de loop
        if len(self.execution_history) >= 2:
            last_two = self.execution_history[-2:]
            if (last_two[0]['tool_id'] == last_two[1]['tool_id'] and
                last_two[0]['success'] == last_two[1]['success']):
                return True

        return False

    def _reset_execution_state(self):
        """Reseta o estado de execução para nova conversa"""
        self.execution_history = []
        self.last_tool_call = None
        self.consecutive_successes = 0

    def _extract_transaction_id(self, text: str) -> Optional[str]:
        """Extrai transaction ID da query do usuário"""
        # Padrões comuns para transaction ID
        patterns = [
            r'transaction\s+id:?\s*([a-f0-9\-]{36})',  # UUID format
            r'transaction\s+id:?\s*([a-f0-9\-]+)',      # Qualquer hexadecimal
            r'txn[:\s]+([a-f0-9\-]{36})',               # txn id
            r'id:?\s*([a-f0-9\-]{36})',                 # Genérico: id
        ]

        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _generate_transaction_id(self) -> str:
        """Gera um transaction ID único (UUID v4)"""
        return str(uuid.uuid4())

    def _enrich_query_with_transaction_id(self, user_query: str) -> str:
        """
        Se a query não contém transaction ID, gera um automaticamente
        e adiciona à query para o agent usar
        """
        transaction_id = self._extract_transaction_id(user_query)

        if not transaction_id:
            # Gerar novo transaction ID
            transaction_id = self._generate_transaction_id()

            # Adicionar à query para o agent saber que há um ID disponível
            enriched = f"""{user_query}

[SISTEMA: Transaction ID gerado automaticamente: {transaction_id}]"""

            print(f"📝 Transaction ID gerado: {transaction_id}")
            return enriched
        else:
            print(f"📝 Transaction ID encontrado: {transaction_id}")
            return user_query

    def chat(self, user_query: str) -> str:
        """Chat com iteração automática de tools com critérios de parada melhorados"""
        print(f"\n🤖 Agent processando: {user_query}\n")

        # Enriquecer query com transaction ID se necessário
        enriched_query = self._enrich_query_with_transaction_id(user_query)

        iteration = 0
        current_query = enriched_query
        self._reset_execution_state()  # Limpar estado anterior

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

            # Detectar padrões problemáticos
            if self._detect_repeated_tool_call(tool_call):
                print("⚠️  [PARADA] Mesma tool sendo executada repetidamente (loop detectado)")
                print(f"Resposta final do agent:\n{response_text}\n")
                return response_text + "\n\n[Sistema: Loop detectado, interrompendo iterações]"

            if self._detect_infinite_loop(current_query):
                print("⚠️  [PARADA] Loop infinito detectado (mesmas execuções)")
                return response_text + "\n\n[Sistema: Loop infinito detectado, interrompendo]"

            # Executar tool
            print(f"🔧 Executando tool: {tool_call.get('tool')}.{tool_call.get('action')}")
            result = self._execute_tool_from_call(tool_call)
            print(f"📊 Resultado: {result}\n")

            # Registrar execução no histórico
            tool_id = f"{tool_call.get('tool')}.{tool_call.get('action')}"
            self.execution_history.append({
                'iteration': iteration,
                'tool_id': tool_id,
                'success': result.success,
                'error': result.error
            })

            # Lógica de parada após sucesso
            if result.success:
                self.consecutive_successes += 1

                # Se houve sucesso, adicionar sinal explícito ao LLM
                current_query = f"""[✅ AÇÃO EXECUTADA COM SUCESSO]

Resultado da execução anterior:
Tool: {tool_id}
Sucesso: Sim
Dados: {json.dumps(result.data, ensure_ascii=False)[:500]}

Pergunta original: {user_query}

IMPORTANTE: A ação anterior foi executada com SUCESSO. Se isso resolve o problema original, 
RESPONDA APENAS CONFIRMANDO QUE FOI RESOLVIDO e NÃO CHAME MAIS TOOLS.
Caso contrário, indique qual é o próximo passo necessário."""

                # Se conseguimos sucesso na primeira tentativa e resposta é conclusiva, parar
                if self.consecutive_successes >= 1 and self._is_conclusive_response(response_text):
                    print("✅ [PARADA] Ação bem-sucedida e conclusão detectada")
                    return response_text
            else:
                # Reset counter em caso de erro
                self.consecutive_successes = 0

                current_query = f"""[❌ ERRO NA EXECUÇÃO]

Erro na execução anterior:
Tool: {tool_id}
Erro: {result.error}

Pergunta original: {user_query}

Por favor, tente um approach diferente ou analise o erro. Se o erro persistir após 
uma nova tentativa, responda com uma explicação clara do problema."""

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

