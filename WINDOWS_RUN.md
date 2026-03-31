# Rodando no Windows (Python 3.13)

Este pacote foi ajustado para rodar localmente com SQLite por padrão, sem precisar de PostgreSQL.

## Passos
1. Crie e ative o ambiente:
   python -m venv venv
   venv\Scripts\Activate.ps1

2. Instale as dependências:
   pip install -r requirements.txt

3. Reindexe os documentos:
   python -m app.main --reindex

4. Suba o dashboard:
   uvicorn app.api.server:app --reload

5. Abra:
   http://127.0.0.1:8000

## PostgreSQL opcional
Para usar PostgreSQL localmente depois, instale:
   pip install psycopg[binary]

O Docker Compose continua sendo a forma mais simples de rodar com PostgreSQL.
