"""
DEMO VISUAL - Como o Agent Funciona
Mostra fluxo passo-a-passo com exemplos reais
"""

# =============================================================================
# EXEMPLO 1: Consultando Documentação
# =============================================================================

INPUT:
>>> python main.py "Como faço uma requisição POST na API?"

PROCESSO:
1. Agent recebe pergunta
2. Busca em docs/ com RAG → encontra "api.md"
3. Envia prompt para LLM Mistral com contexto
4. Retorna resposta baseada na documentação

OUTPUT:
┌──────────────────────────────────────────────────┐
│ Agent:                                           │
│                                                  │
│ Baseado na documentação, para fazer uma          │
│ requisição POST na API:                          │
│                                                  │
│ POST /users                                      │
│ Body: {"name": "John", "email": "john@..."}    │
│ Response: 201 Created                            │
└──────────────────────────────────────────────────┘


# =============================================================================
# EXEMPLO 2: Chamar API + Processar Resposta
# =============================================================================

INPUT:
>>> python main.py "Busque dados do usuário ID 1 em https://jsonplaceholder.typicode.com/users/1"

PROCESSO:
1. Agent lê pergunta
2. Recogniza que precisa chamar API
3. Gera prompt para LLM: "Você deve chamar uma API"
4. LLM responde com:
   <tool>{"tool": "api", "action": "call_api", "url": "...", "method": "GET"}</tool>
5. Agent executa a tool
6. Recebe JSON com dados do usuário
7. Passa resultado de volta para LLM processar
8. LLM formata resposta final

OUTPUT:
┌──────────────────────────────────────────────────┐
│ Agent:                                           │
│                                                  │
│ [Iteração 1] Executando call_api...            │
│ ✓ Sucesso! Dados recuperados                    │
│                                                  │
│ Usuário ID 1:                                    │
│ - Nome: Leanne Graham                            │
│ - Email: Bret@april.biz                          │
│ - Empresa: Romaguera-Crona                       │
│ ...                                              │
└──────────────────────────────────────────────────┘


# =============================================================================
# EXEMPLO 3: Debugging Automático
# =============================================================================

INPUT:
>>> python main.py "Tentei chamar a API e recebi erro 401"

PROCESSO:
1. Agent lê sobre erro 401
2. Procura em docs/ → encontra troubleshooting.md
3. Executa debug.analyze_error("401")
4. Recebe sugestões automáticas
5. Combina documentação + análise
6. Fornece solução específica

OUTPUT:
┌──────────────────────────────────────────────────┐
│ Agent:                                           │
│                                                  │
│ [Iteração 1] Analisando erro 401...            │
│                                                  │
│ Problema: Erro 401 - Autenticação Necessária   │
│                                                  │
│ Causas possíveis:                                │
│ 1. Credenciais inválidas                         │
│ 2. Token expirado                                │
│                                                  │
│ Soluções recomendadas:                           │
│ 1. Verificar API key em .env                     │
│ 2. Renovar token de autenticação                 │
│ 3. Verificar permissões na conta                 │
│                                                  │
│ Próximas tentativas:                             │
│ - Use "Authorization: Bearer <token>"            │
│ - Adicione headers corretamente                  │
└──────────────────────────────────────────────────┘


# =============================================================================
# EXEMPLO 4: Ações em Cadeia (Múltiplas Iterações)
# =============================================================================

INPUT:
>>> python main.py "Busque dados em https://jsonplaceholder.typicode.com/posts/1, \
                    valide o JSON e salve em post.json"

PROCESSO:
[Iteração 1] Agent decide chamar API
   └─> Executa: api.call_api("https://...")
   └─> Recebe: {"userId": 1, "id": 1, "title": "..."}

[Iteração 2] Agent decide validar JSON
   └─> Executa: json.validate_json(response)
   └─> Recebe: {"valid": True}

[Iteração 3] Agent decide salvar arquivo
   └─> Executa: file.write_file("post.json", json_content)
   └─> Recebe: "Arquivo salvo: post.json"

[Iteração 4] Agent valida sucesso e retorna resposta final

OUTPUT:
┌──────────────────────────────────────────────────┐
│ Agent:                                           │
│                                                  │
│ ✓ Dados recuperados com sucesso                 │
│ ✓ JSON validado como correto                    │
│ ✓ Arquivo salvo em post.json                    │
│                                                  │
│ Resumo:                                          │
│ - URL: https://jsonplaceholder.typicode.com/... │
│ - Status: 200 OK                                │
│ - Tamanho: 2.3 KB                               │
│ - Localização: ./post.json                      │
└──────────────────────────────────────────────────┘


# =============================================================================
# EXEMPLO 5: RAG + Tools Combinados
# =============================================================================

INPUT:
>>> python main.py "Como fazer login na API? Depois tente chamar o endpoint"

PROCESSO:
[Step 1] Consulta docs/ com RAG
   └─> Encontra: "POST /login com credentials"

[Step 2] Agent formula resposta com instruções

[Step 3] Agent sugere próxima ação:
   └─> "Vou tentar fazer login agora"

[Step 4] Agent executa api.call_api(...)
   └─> Recebe token: "eyJhbGc..."

[Step 5] Agent usa token em nova requisição
   └─> api.call_api(..., headers={"Authorization": "Bearer ..."})

[Step 6] Retorna resposta final autenticada

OUTPUT:
┌──────────────────────────────────────────────────┐
│ Agent:                                           │
│                                                  │
│ Conforme a documentação, para fazer login:      │
│                                                  │
│ POST /login                                      │
│ Body: {                                          │
│   "email": "seu-email@example.com",              │
│   "password": "sua-senha"                        │
│ }                                                │
│                                                  │
│ [Executando login...]                           │
│ ✓ Login bem-sucedido!                           │
│ Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... │
│                                                  │
│ [Usando token para chamar API...]               │
│ ✓ Requisição autenticada bem-sucedida!          │
│                                                  │
│ Resultado: {...dados protegidos...}             │
└──────────────────────────────────────────────────┘


# =============================================================================
# COMPARAÇÃO: Agent vs ChatGPT
# =============================================================================

                    ChatGPT               │  Seu Agent Local
────────────────────────────────────────┼──────────────────────────────
Internet requerido  │ ✓ Sim                 │ ✗ Não (100% local)
Custo               │ $ Subscription       │ $ Grátis
Privacidade         │ Dados na OpenAI      │ Dados no seu PC
Velocidade          │ Depende da internet  │ Rápido + local
Documentos próprios │ Limited context      │ ✓ RAG ilimitado
Ações (APIs, etc)   │ ✗ Não               │ ✓ Sim (Tools)
Controle            │ ✗ Nenhum             │ ✓ Total
Customização        │ ✗ Limited            │ ✓ Total

# =============================================================================
# ARQUITETURA INTERNA
# =============================================================================

Pergunta do Usuário
        │
        ▼
    ┌─────────────────────────────────┐
    │  Agent.chat()                   │
    │  - Parse pergunta               │
    │  - Busca em docs (RAG)          │
    │  - Constrói prompt              │
    └──────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  LLM (Mistral)       │
        │  - Processa prompt   │
        │  - Gera resposta     │
        │  - Detecta tools     │
        └──────────┬───────────┘
                   │
            ┌──────┴───────┐
            │              │
       Tem tool?      Sem tool?
            │              │
        Sim ▼          Não ▼
            │           Resposta
            │           Final
    ┌───────▼─────────┐
    │ Tool Executor   │
    │ - Parse {..}    │
    │ - Execute       │
    │ - Retorna res   │
    └────────┬────────┘
             │
             ▼
      Feedback ao LLM
      (próxima iteração)
      ou resposta final

# =============================================================================
# FLUXO COMPLETO COM TIMING
# =============================================================================

user@mac:~/tale$ python main.py "Sua pergunta"

[00:00] 🤖 Agent recebido
[00:01] 📚 Carregando documentos
[00:02] 🔍 Buscando contexto relevante (RAG)
[00:03] 💭 Enviando para LLM...
[00:05] 🔧 Detectou tool necessária
[00:06] ⚙️  Executando ferramenta...
[00:08] 📊 Processando resultado
[00:09] 💭 Refinando resposta
[00:10] ✓ Pronto!

Resposta Final:
[resultado processado e formatado]

Total: ~10 segundos (primeira execução)
       ~5 segundos (cache carregado)

