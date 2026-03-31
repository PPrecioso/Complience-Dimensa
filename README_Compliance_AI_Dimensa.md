
# Compliance AI – Dimensa Challenge

## 📌 Visão Geral

Este projeto implementa um **sistema inteligente de verificação de conformidade visual e documental**, desenvolvido como solução para o desafio técnico da Dimensa.

O sistema combina **visão computacional**, **recuperação semântica de documentos (RAG)** e **interface de terminal interativa** para analisar imagens e documentos corporativos, identificando possíveis violações de regras operacionais definidas em manuais.

O objetivo é simular um **sistema de auditoria automatizada**, capaz de:

- Detectar pessoas em imagens
- Avaliar se a situação está conforme normas operacionais
- Recuperar trechos relevantes de manuais corporativos
- Apresentar os resultados de forma visual e estruturada

---

# 🧠 Arquitetura do Projeto

```
app/
│
├── main.py                # Interface principal (CLI)
│
├── ingestion/
│   ├── pdf_loader.py      # Extração de texto dos manuais
│   └── index_rules.py     # Indexação vetorial dos documentos
│
├── retrieval/
│   └── retriever.py       # Busca semântica (RAG)
│
├── reasoning/
│   └── engine.py          # Motor de decisão
│
├── services/
│   └── analysis_service.py # Pipeline de análise de imagens
│
├── utils/
│   ├── company.py         # Inferência de empresa
│   └── paths.py           # Gerenciamento de caminhos
│
└── assets/
    └── dimensa_logo.png
```

---

# 🔎 Funcionalidades

## Detecção de Pessoas

O sistema utiliza **YOLOv8** para detectar pessoas em imagens.

Fluxo:

1. Usuário seleciona uma imagem
2. O modelo detecta pessoas
3. Recortes individuais são gerados
4. Resultados são exibidos no terminal

Saída:

- número de pessoas detectadas
- bounding boxes
- recortes das pessoas

---

## Recuperação de Regras (RAG)

Os documentos são indexados usando **TF‑IDF**.

O sistema busca:

- empresa
- setor

E retorna os trechos mais relevantes.

---

## Visualização

O sistema gera duas telas:

### Trechos relevantes
Mostra os trechos mais importantes dos manuais.

### Pessoas detectadas
Mostra os recortes das pessoas detectadas.

---

# 💻 Tecnologias

- Python
- YOLOv8
- OpenCV
- Pillow
- Scikit‑learn
- PyMuPDF
- python‑docx
- Rich

---

# ⚙️ Como Rodar

## Clonar

```
git clone https://github.com/PPrecioso/Complience-Dimensa.git
cd Complience-Dimensa
```

## Criar ambiente

Windows:

```
python -m venv venv
venv\Scripts\activate
```

## Instalar dependências

```
pip install -r requirements.txt
```

## Indexar documentos

```
python -m app.main --reindex
```

## Executar

```
python -m app.main
```

---

# 👨‍💻 Autor

Paola Precioso Figueiredo Alves
