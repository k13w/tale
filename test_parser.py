#!/usr/bin/env python3
"""
Script de teste para validar o parsing de tool calls
"""

import re
import json
from typing import Optional, Dict, Any

def parse_tool_call(text: str) -> Optional[Dict[str, Any]]:
    """Parse de chamadas de tool no formato <tool>{...}</tool>"""
    # Tenta primeiro o padrão padrão
    pattern = r'<tool>(.*?)</tool>'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️  Erro ao fazer parse de JSON: {e}")
            print(f"   JSON string: {json_str[:100]}...")
            return None

    # Se não encontrou, tenta extrair JSON entre chaves
    # Padrão alternativo: procura por { ... } mesmo sem <tool> tags
    json_pattern = r'\{.*?"tool".*?"action".*?\}'
    json_match = re.search(json_pattern, text, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None

# Testes
test_cases = [
    # Caso 1: Tool call correto
    '''<tool>{"tool": "api", "action": "call_api", "url": "http://example.com", "method": "GET"}</tool>''',

    # Caso 2: Tool call com explicação antes
    '''Para corrigir a divergência de saldo da sua conta, precisarei chamar o endpoint do Balance Ledger da Conta Azul que realiza um bloqueio judicial. Por favor, veja abaixo a chamada cURL para este endpoint:

```bash
curl --location 'http://cb-balance-ledger.dev.contaazul.local/private-api/rest/v1/accounts/jud-block' \\
--header 'X-TenantId: 36' \\
--header 'X-UserId: 12' \\
--header 'Content-Type: application/json' \\
--data '{
    "transactionId": "bfe877fd-1007-4712-be2e-283088e83265",
    "amount": 0.4
}'
```

Em seguida, chamaremos a API utilizando a tool `api.call_api`. A resposta da API será processada e retornada para o usuário.

<tool>{"tool": "api", "action": "call_api", "url": "http://cb-balance-ledger.dev.contaazul.local/private-api/rest/v1/accounts/jud-block", "method": "POST", "headers": {'X-TenantId': '36', 'X-UserId': '12', 'Content-Type': 'application/json'}, "data": {"transactionId": "bfe877fd-1007-4712-be2e-283088e83265", "amount": 0.4}}</tool>''',

    # Caso 3: JSON sem tags
    '''A API deve ser chamada assim:
{"tool": "api", "action": "call_api", "url": "https://api.example.com", "method": "GET"}''',
]

print("🧪 Testando parser de tool calls\n")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n[Teste {i}]")
    print(f"Input (primeiros 150 chars): {test[:150]}...")

    result = parse_tool_call(test)

    if result:
        print(f"✅ Sucesso!")
        print(f"   Tool: {result.get('tool')}")
        print(f"   Action: {result.get('action')}")
        print(f"   Keys: {list(result.keys())}")
    else:
        print(f"❌ Falha ao fazer parse")

    print("-" * 80)

print("\n✅ Testes completados!")

