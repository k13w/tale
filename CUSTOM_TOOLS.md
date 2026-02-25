# Guia: Criar Tools Customizadas

## Como estender o Agent com suas próprias ações

### Passo 1: Abra `tools.py`

Adicione sua nova Tool class:

```python
class DatabaseTool:
    """Tool para operações com banco de dados"""
    
    @staticmethod
    def query_database(query: str, database: str = "main.db") -> ToolResult:
        """Executa query SQL"""
        try:
            import sqlite3
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            return ToolResult(
                success=True,
                data={"rows": results, "count": len(results)}
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

### Passo 2: Registre em `TOOLS`

```python
TOOLS = {
    "api": APITool,
    "file": FileTool,
    "json": JsonTool,
    "debug": DebugTool,
    "system": SystemTool,
    "database": DatabaseTool,  # ← Adicione aqui
}
```

### Passo 3: Use no Agent

O Agent agora pode chamar:

```
<tool>{"tool": "database", "action": "query_database", "query": "SELECT * FROM users"}</tool>
```

---

## Exemplos de Tools Úteis

### 1. Shell Commands

```python
class ShellTool:
    @staticmethod
    def run_command(command: str) -> ToolResult:
        """Executa comando no shell"""
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return ToolResult(
                success=result.returncode == 0,
                data=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

Uso:
```
<tool>{"tool": "shell", "action": "run_command", "command": "ls -la"}</tool>
```

### 2. Web Scraping

```python
class ScrapingTool:
    @staticmethod
    def scrape_webpage(url: str) -> ToolResult:
        """Faz scrape de conteúdo web"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Extrai texto principal
            text = soup.get_text()
            
            return ToolResult(success=True, data={"text": text[:2000]})
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

### 3. Envio de Email

```python
class EmailTool:
    @staticmethod
    def send_email(to: str, subject: str, body: str) -> ToolResult:
        """Envia email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            # Configure com suas credenciais
            smtp_server = "smtp.gmail.com"
            sender = "seu-email@gmail.com"
            password = "sua-senha-de-app"
            
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = to
            
            with smtplib.SMTP_SSL(smtp_server, 465) as server:
                server.login(sender, password)
                server.sendmail(sender, [to], msg.as_string())
            
            return ToolResult(success=True, data=f"Email enviado para {to}")
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

### 4. Processamento de Imagens

```python
class ImageTool:
    @staticmethod
    def describe_image(image_path: str) -> ToolResult:
        """Descreve conteúdo de imagem"""
        try:
            from PIL import Image
            import os
            
            if not os.path.exists(image_path):
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Arquivo não encontrado: {image_path}"
                )
            
            img = Image.open(image_path)
            
            return ToolResult(
                success=True,
                data={
                    "size": img.size,
                    "format": img.format,
                    "mode": img.mode
                }
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

### 5. Tradução

```python
class TranslationTool:
    @staticmethod
    def translate_text(text: str, target_lang: str = "en") -> ToolResult:
        """Traduz texto"""
        try:
            from googletrans import Translator
            
            translator = Translator()
            result = translator.translate(text, dest_lang=target_lang)
            
            return ToolResult(
                success=True,
                data={"original": text, "translated": result['text']}
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

---

## Padrão para suas Tools

Sempre siga este padrão:

```python
class MyTool:
    """Descrição clara da ferramenta"""
    
    @staticmethod
    def my_action(param1: str, param2: int = 10) -> ToolResult:
        """
        Descrição da ação
        
        Args:
            param1: descrição do param1
            param2: descrição do param2
        
        Returns:
            ToolResult com success, data e error
        """
        try:
            # Sua lógica aqui
            result = fazer_algo(param1, param2)
            
            return ToolResult(
                success=True,
                data=result  # Sempre um dict ou value serializable
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)  # Sempre string
            )
```

---

## Update para o Prompt

Quando adicionar Tools, atualize o prompt em `agent.py`:

```python
def _format_tools_description(self) -> str:
    return """
## Tools Disponíveis:

### Sua Nova Tool
- **mytool.my_action(param1, param2)**: Descrição clara
  Exemplo: {"tool": "mytool", "action": "my_action", "param1": "valor"}

[... outras tools ...]
"""
```

---

## Testando sua Tool

Faça testes rápidos:

```python
# No Python REPL
from tools import execute_tool

# Testar sua tool
result = execute_tool("mytool", "my_action", param1="teste", param2=20)
print(result)
```

---

## Tools Integradas (já disponíveis)

| Tool | Actions | Exemplo |
|------|---------|---------|
| `api` | `call_api` | GET, POST, PUT, DELETE |
| `file` | `read_file`, `write_file` | Ler/escrever arquivos |
| `json` | `parse_json`, `validate_json` | Parse e validação |
| `debug` | `analyze_error` | Sugerir soluções |
| `system` | `get_timestamp`, `get_env_var` | Info do sistema |

---

## Instalações Necessárias

Dependendo da Tool, instale com pip:

```bash
# Scraping
pip install beautifulsoup4

# Imagens
pip install Pillow

# Tradução
pip install google-cloud-translate

# Excel
pip install openpyxl

# Database
pip install sqlalchemy

# Email (gmail)
# Gere "App Password" em: https://myaccount.google.com/apppasswords
```

---

## Security Best Practices

⚠️ **Nunca** coloque credenciais no código!

Use `.env`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

password = os.getenv("EMAIL_PASSWORD")
api_key = os.getenv("API_KEY")
```

Arquivo `.env`:
```
EMAIL_PASSWORD=sua-senha-aqui
API_KEY=sua-chave-aqui
```

---

## Exemplo Completo: Tool de Crypto

```python
class CryptoTool:
    """Tool para consultar preços de criptomoedas"""
    
    @staticmethod
    def get_crypto_price(symbol: str = "BTC") -> ToolResult:
        """Obtém preço atual de criptomoeda"""
        try:
            import requests
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd"
            }
            
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            price = data.get(symbol.lower(), {}).get("usd")
            
            return ToolResult(
                success=True,
                data={"symbol": symbol, "price_usd": price}
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
```

Registre:
```python
TOOLS = {
    ...
    "crypto": CryptoTool,
}
```

Use:
```
Agent: <tool>{"tool": "crypto", "action": "get_crypto_price", "symbol": "ETH"}</tool>
```

---

Agora você pode expandir seu Agent com qualquer funcionalidade! 🚀

