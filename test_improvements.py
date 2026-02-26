#!/usr/bin/env python3
"""
Script de teste para validar o parsing com single quotes e transaction ID
"""

import re
import json
from typing import Optional, Dict, Any

def try_parse_json(json_str: str) -> Optional[Dict[str, Any]]:
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
    return None

def extract_transaction_id(text: str) -> Optional[str]:
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

# Testes de parsing JSON com single quotes
json_test_cases = [
    # Caso 1: Double quotes (correto)
    '{"tool": "api", "action": "call_api", "url": "http://example.com", "method": "GET"}',

    # Caso 2: Single quotes (LLM incorreto)
    "{'tool': 'api', 'action': 'call_api', 'url': 'http://cb-balance-ledger.dev.contaazul.local/private-api/rest/v1/accounts/jud-block', 'method': 'POST', 'headers': {'X-TenantId': '36', 'X-UserId': '12', 'Content-Type': 'application/json'}, 'data': {'transactionId': 'bfe877fd-1007-4712-be2e-283088e83265', 'amount': 0.4}}",

    # Caso 3: Misto
    '{"tool": "api", \'action\': "call_api", "url": "https://api.example.com", "method": "GET"}',
]

# Testes de extração de transaction ID
id_test_cases = [
    ("corriga meu tenant 36, userid 12, transaction id:bfe877fd-1007-4712-be2e-283088e83265, amount: 0.40", "bfe877fd-1007-4712-be2e-283088e83265"),
    ("tenant 36 user 12 txn:123e4567-e89b-12d3-a456-426614174000 amount 100", "123e4567-e89b-12d3-a456-426614174000"),
    ("corriga tenant 36 sem ID", None),  # Sem ID
]

print("=" * 80)
print("🧪 TESTE 1: Parser JSON com Single Quotes")
print("=" * 80)

for i, json_str in enumerate(json_test_cases, 1):
    print(f"\n[JSON Teste {i}]")
    print(f"Input: {json_str[:80]}...")

    result = try_parse_json(json_str)

    if result:
        print(f"✅ Sucesso!")
        print(f"   Tool: {result.get('tool')}")
        print(f"   Action: {result.get('action')}")
    else:
        print(f"❌ Falha ao fazer parse")

print("\n" + "=" * 80)
print("🧪 TESTE 2: Extração de Transaction ID")
print("=" * 80)

for i, (query, expected) in enumerate(id_test_cases, 1):
    print(f"\n[ID Teste {i}]")
    print(f"Query: {query}")

    result = extract_transaction_id(query)

    if result == expected:
        print(f"✅ Sucesso! ID: {result}")
    else:
        print(f"❌ Falha! Esperado: {expected}, Obtido: {result}")

print("\n" + "=" * 80)
print("✅ Testes completados!")
print("=" * 80)

