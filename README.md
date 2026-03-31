# Compliance AI - versão terminal

Projeto pronto para rodar em terminal, sem precisar de Docker.

## O que esta versão faz

- permite escolher no terminal qual **imagem** analisar
- mostra no terminal:
  - **Empresa**
  - **Setor**
  - **quantidade de pessoas detectadas**
  - **bounding boxes**
  - **status e justificativa**
  - **trechos relevantes recuperados**
- gera **recortes individuais** de cada pessoa detectada
- monta um **painel com todos os recortes** e tenta abrir na tela automaticamente
- permite escolher no terminal qual **documento PDF/DOCX** analisar
- no caso do documento, mostra no terminal:
  - **Empresa**
  - **Setor**
  - **quantidade de páginas/blocos extraídos**
  - **quantidade de trechos relevantes**
  - **trechos relevantes do RAG**
- reindexa os documentos pelo terminal

## Como rodar

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main --reindex
python -m app.main --interactive
```

## Fluxo no terminal

Ao abrir o menu:

- `[1] Analisar imagem`
- `[2] Analisar documento (RAG)`
- `[3] Reindexar documentos`

### Análise de imagem
O sistema:
- recebe uma imagem contendo uma ou mais pessoas
- detecta todas as pessoas presentes
- gera recortes individuais
- mostra no terminal quantas pessoas existem na imagem
- salva os recortes em `outputs/crops`
- salva um painel com os recortes em `outputs/*_crops_sheet.png`

### Análise de documento
Dado um contexto como:
- Empresa: ConstruTech
- Setor: Operacional

o sistema:
- localiza apenas os trechos relevantes
- ignora regras de outras empresas/setores quando possível
- lida com variações semânticas e sinônimos com busca TF-IDF

## Pastas principais

- `data/docs`: documentos iniciais
- `data/images`: imagens iniciais
- `uploads/docs`: novos documentos
- `uploads/images`: novas imagens
- `outputs`: JSONs e recortes

## Observação
Esta versão mantém a mesma base de projeto, mas está preparada para uso direto no terminal.
