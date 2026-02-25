import os
import json
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Tools disponíveis que o agent pode chamar
class ToolResult(BaseModel):
    """Resultado da execução de uma tool"""
    success: bool
    data: Any
    error: Optional[str] = None

class APITool:
    """Tool para chamar endpoints HTTP"""

    @staticmethod
    def call_api(
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> ToolResult:
        """Chama um endpoint HTTP"""
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                resp = requests.post(url, headers=headers, json=data, params=params, timeout=10)
            elif method == "PUT":
                resp = requests.put(url, headers=headers, json=data, params=params, timeout=10)
            elif method == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=10)
            else:
                return ToolResult(success=False, data=None, error=f"Método {method} não suportado")

            resp.raise_for_status()
            return ToolResult(success=True, data=resp.json() if resp.text else resp.status_code)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))

class FileTool:
    """Tool para ler/escrever arquivos"""

    @staticmethod
    def read_file(filepath: str) -> ToolResult:
        """Lê um arquivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return ToolResult(success=True, data=content)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))

    @staticmethod
    def write_file(filepath: str, content: str) -> ToolResult:
        """Escreve em um arquivo"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return ToolResult(success=True, data=f"Arquivo salvo: {filepath}")
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))

class JsonTool:
    """Tool para processar JSON"""

    @staticmethod
    def parse_json(content: str) -> ToolResult:
        """Faz parse de JSON"""
        try:
            data = json.loads(content)
            return ToolResult(success=True, data=data)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))

    @staticmethod
    def validate_json(content: str) -> ToolResult:
        """Valida JSON"""
        try:
            json.loads(content)
            return ToolResult(success=True, data={"valid": True})
        except json.JSONDecodeError as e:
            return ToolResult(success=False, data=None, error=f"JSON inválido: {str(e)}")

class DebugTool:
    """Tool para debugging e resolução de problemas"""

    @staticmethod
    def analyze_error(error_message: str) -> ToolResult:
        """Analisa uma mensagem de erro"""
        # Aqui você pode adicionar lógica para analisar e sugerir soluções
        suggestions = {
            "timeout": "Aumentar o tempo de espera ou verificar conectividade",
            "404": "Recurso não encontrado, verificar URL",
            "401": "Autenticação necessária, verificar credenciais",
            "500": "Erro no servidor, tentar novamente mais tarde",
            "connection": "Problema de conexão, verificar internet",
            "json": "Problema ao processar JSON, verificar formato",
        }

        matching_suggestion = None
        for key, suggestion in suggestions.items():
            if key.lower() in error_message.lower():
                matching_suggestion = suggestion
                break

        return ToolResult(
            success=True,
            data={
                "error": error_message,
                "suggestion": matching_suggestion or "Erro desconhecido, tente fornecer mais contexto"
            }
        )

class SystemTool:
    """Tool para informações do sistema"""

    @staticmethod
    def get_timestamp() -> ToolResult:
        """Retorna timestamp atual"""
        return ToolResult(success=True, data=datetime.now().isoformat())

    @staticmethod
    def get_env_var(var_name: str) -> ToolResult:
        """Lê uma variável de ambiente"""
        value = os.getenv(var_name)
        if value:
            return ToolResult(success=True, data=value)
        return ToolResult(success=False, data=None, error=f"Variável {var_name} não encontrada")


# Registry das tools disponíveis
TOOLS = {
    "api": APITool,
    "file": FileTool,
    "json": JsonTool,
    "debug": DebugTool,
    "system": SystemTool,
}

def execute_tool(tool_name: str, action: str, **kwargs) -> ToolResult:
    """Executa uma tool e action específica"""
    if tool_name not in TOOLS:
        return ToolResult(success=False, data=None, error=f"Tool {tool_name} não encontrada")

    tool_class = TOOLS[tool_name]
    action_method = getattr(tool_class, action, None)

    if not action_method:
        return ToolResult(success=False, data=None, error=f"Action {action} não existe em {tool_name}")

    try:
        result = action_method(**kwargs)
        return result
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))

