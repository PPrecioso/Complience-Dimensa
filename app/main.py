from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app.config import OUTPUTS_DIR
from app.ingestion.index_rules import rebuild_index
from app.ingestion.pdf_loader import extract_document_pages
from app.retrieval.retriever import RuleRetriever
from app.services.analysis_service import analyze_image
from app.utils.company import infer_company_from_filename, normalize_company_name
from app.utils.paths import list_documents, list_images


console = Console()

# Cores do terminal
COLOR_PRIMARY = "bright_green"
COLOR_TEXT = "white"
COLOR_MUTED = "grey70"
COLOR_BORDER = "bright_green"
COLOR_WARN = "yellow"
COLOR_ERROR = "red"

# Cores das telas geradas
BG_COLOR = "#DDE3D7"
CARD_COLOR = "#EEF2EB"
CARD_BORDER = "#C9D1C4"
ACCENT_GREEN = "#B9E600"
TEXT_DARK = "#151515"
TEXT_MUTED_DARK = "#4A4A4A"

LOGO_PATH = Path("app/assets/dimensa_logo.png")


def render_header() -> None:
    title = Text()
    title.append("DIMENSA | COMPLIANCE AI\n", style=f"bold {COLOR_PRIMARY}")
    title.append(
        "Sistema Inteligente de Verificação de Conformidade Visual",
        style=COLOR_TEXT
    )

    console.print(
        Panel.fit(
            title,
            border_style=COLOR_BORDER,
            box=box.ROUNDED,
            padding=(1, 3),
        )
    )


def render_section_title(title: str) -> None:
    console.print()
    console.print(
        Panel.fit(
            f"[bold {COLOR_PRIMARY}]{title}[/bold {COLOR_PRIMARY}]",
            border_style=COLOR_BORDER,
            box=box.ROUNDED,
        )
    )


def render_success(message: str) -> None:
    console.print(f"[bold {COLOR_PRIMARY}]✓[/bold {COLOR_PRIMARY}] {message}")


def render_warning(message: str) -> None:
    console.print(f"[bold {COLOR_WARN}]![/bold {COLOR_WARN}] {message}")


def render_error(message: str) -> None:
    console.print(f"[bold {COLOR_ERROR}]✗[/bold {COLOR_ERROR}] {message}")


def render_info(label: str, value: str) -> None:
    console.print(
        f"[bold {COLOR_TEXT}]{label}:[/bold {COLOR_TEXT}] "
        f"[{COLOR_PRIMARY}]{value}[/{COLOR_PRIMARY}]"
    )


def ask_choice(title: str, options: list[str]) -> Optional[int]:
    render_section_title(title)

    if not options:
        render_warning("Nenhuma opção encontrada.")
        return None

    table = Table(
        box=box.ROUNDED,
        border_style=COLOR_BORDER,
        header_style=f"bold {COLOR_PRIMARY}",
    )
    table.add_column("Nº", width=6, style=COLOR_PRIMARY)
    table.add_column("Arquivo", style=COLOR_TEXT)

    for i, option in enumerate(options, start=1):
        table.add_row(str(i), Path(option).name)

    console.print(table)

    while True:
        raw = console.input(
            f"[bold {COLOR_TEXT}]Digite o número desejado (ou 0 para cancelar): [/bold {COLOR_TEXT}]"
        ).strip()

        if raw == "0":
            return None

        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return idx - 1

        render_warning("Opção inválida. Tente novamente.")


def ask_text(label: str, default: str) -> str:
    raw = console.input(
        f"[bold {COLOR_TEXT}]{label}[/bold {COLOR_TEXT}] "
        f"[{COLOR_MUTED}][{default}][/{COLOR_MUTED}]: "
    ).strip()
    return raw if raw else default


def get_status_colored(status: str) -> str:
    if status == "Conforme":
        return "[green]Conforme[/green]"
    if status == "Não conforme":
        return "[red]Não conforme[/red]"
    return "[yellow]Indeterminado[/yellow]"


def infer_company_from_document_name(file_path: str) -> str:
    name = Path(file_path).name.lower()

    if "vitalcare" in name:
        return "VitalCare"
    if "vitalis" in name:
        return "Rede Vitalis"
    if "construtiva" in name:
        return "Construtiva Engenharia"
    if "logitrans" in name:
        return "LogiTrans Global"

    stem = Path(file_path).stem.replace("_", " ").replace("-", " ").strip()
    return normalize_company_name(stem)


def get_font(size: int, bold: bool = False):
    candidates = [
        "app/assets/fonts/Dimensa-Bold.ttf" if bold else "app/assets/fonts/Dimensa-Regular.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue

    return ImageFont.load_default()


def wrap_text_pixels(text: str, draw: ImageDraw.ImageDraw, font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def clean_preview_text(text: str) -> str:
    text = text.replace("\n", " ").strip()
    return re.sub(r"\s+", " ", text)


def load_logo(max_width: int = 320, max_height: int = 90) -> Optional[Image.Image]:
    if not LOGO_PATH.exists():
        return None

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((max_width, max_height))
    return logo


def draw_header_block(
    draw: ImageDraw.ImageDraw,
    canvas: Image.Image,
    width: int,
    title: str,
    subtitle: str,
) -> None:
    title_font = get_font(60, bold=True)
    subtitle_font = get_font(26, bold=False)

    logo = load_logo(max_width=320, max_height=90)
    if logo:
        canvas.paste(logo, (60, 32), logo)

    bar_y = 128
    draw.rounded_rectangle(
        [(60, bar_y), (width - 60, bar_y + 12)],
        radius=6,
        fill=ACCENT_GREEN,
    )

    draw.text(
        (60, 152),
        title,
        fill=ACCENT_GREEN,
        font=title_font,
    )

    draw.text(
        (60, 214),
        subtitle,
        fill=TEXT_DARK,
        font=subtitle_font,
    )


def build_contact_sheet(crop_paths: list[str], image_name: str) -> Optional[Path]:
    if not crop_paths:
        return None

    thumb_w, thumb_h = 320, 380
    cols = min(3, len(crop_paths))
    rows = math.ceil(len(crop_paths) / cols)

    padding_x = 60
    padding_y = 40
    header_h = 250
    gap = 28

    width = padding_x * 2 + cols * thumb_w + (cols - 1) * gap
    height = header_h + padding_y + rows * thumb_h + (rows - 1) * gap + 60

    sheet = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(sheet)

    draw_header_block(
        draw=draw,
        canvas=sheet,
        width=width,
        title="Pessoas detectadas",
        subtitle=f"Imagem: {Path(image_name).name}",
    )

    card_title_font = get_font(24, bold=True)

    for i, crop_path in enumerate(crop_paths, start=1):
        img = Image.open(crop_path).convert("RGB")
        img.thumbnail((thumb_w - 44, thumb_h - 100))

        card = Image.new("RGB", (thumb_w, thumb_h), CARD_COLOR)
        card_draw = ImageDraw.Draw(card)

        card_draw.rounded_rectangle(
            [(0, 0), (thumb_w - 1, thumb_h - 1)],
            radius=30,
            fill=CARD_COLOR,
            outline=CARD_BORDER,
            width=2,
        )

        card_draw.text(
            (24, 20),
            f"Pessoa {i}",
            fill=ACCENT_GREEN,
            font=card_title_font,
        )

        x = (thumb_w - img.width) // 2
        y = 82 + (thumb_h - 110 - img.height) // 2
        card.paste(img, (x, y))

        row = (i - 1) // cols
        col = (i - 1) % cols
        px = padding_x + col * (thumb_w + gap)
        py = header_h + padding_y + row * (thumb_h + gap)

        sheet.paste(card, (px, py))

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUTS_DIR / f"{Path(image_name).stem}_crops_sheet.png"
    sheet.save(out_path)
    return out_path


def build_rules_sheet(rules: list[dict], company: str, sector: str, base_name: str) -> Optional[Path]:
    if not rules:
        return None

    width = 1700
    top_h = 250
    side_margin = 60
    card_gap = 28
    bottom_margin = 70

    temp_canvas = Image.new("RGB", (width, 3000), BG_COLOR)
    temp_draw = ImageDraw.Draw(temp_canvas)

    card_title_font = get_font(25, bold=True)
    card_text_font = get_font(24, bold=False)
    small_font = get_font(20, bold=False)

    card_layouts = []
    total_height = top_h

    for i, rule in enumerate(rules, start=1):
        meta = rule.get("metadata", {})
        source = meta.get("source_file", "desconhecido")
        page = meta.get("page", "-")
        score = rule.get("score", 0.0)
        text = clean_preview_text(rule.get("text", ""))

        text_max_width = width - (side_margin * 2) - 48
        lines = wrap_text_pixels(
            text=text,
            draw=temp_draw,
            font=card_text_font,
            max_width=text_max_width,
        )

        preview_lines = lines[:7]
        preview_text = "\n".join(preview_lines)

        if preview_text:
            bbox = temp_draw.multiline_textbbox(
                (0, 0),
                preview_text,
                font=card_text_font,
                spacing=10,
            )
            text_block_h = bbox[3] - bbox[1]
        else:
            text_block_h = 40

        card_h = 120 + text_block_h + 34

        card_layouts.append(
            {
                "idx": i,
                "source": source,
                "page": page,
                "score": score,
                "preview_text": preview_text,
                "card_h": card_h,
            }
        )

        total_height += card_h + card_gap

    total_height += bottom_margin

    canvas = Image.new("RGB", (width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    draw_header_block(
        draw=draw,
        canvas=canvas,
        width=width,
        title="Trechos mais relevantes",
        subtitle=f"Empresa: {company}   |   Setor: {sector}",
    )

    y = top_h

    for item in card_layouts:
        x1, y1 = side_margin, y
        x2, y2 = width - side_margin, y + item["card_h"]

        draw.rounded_rectangle(
            [(x1, y1), (x2, y2)],
            radius=30,
            fill=CARD_COLOR,
            outline=CARD_BORDER,
            width=2,
        )

        draw.text(
            (x1 + 24, y1 + 22),
            f"Trecho {item['idx']}",
            fill=ACCENT_GREEN,
            font=card_title_font,
        )

        meta_text = f"Fonte: {item['source']}  |  página: {item['page']}  |  score: {item['score']:.4f}"
        draw.text(
            (x1 + 24, y1 + 64),
            meta_text,
            fill=TEXT_MUTED_DARK,
            font=small_font,
        )

        draw.multiline_text(
            (x1 + 24, y1 + 108),
            item["preview_text"],
            fill=TEXT_DARK,
            font=card_text_font,
            spacing=10,
        )

        y += item["card_h"] + card_gap

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUTS_DIR / f"{Path(base_name).stem}_rules_sheet.png"
    canvas.save(out_path)
    return out_path


def print_rules_panel(rules: list[dict], company: str, sector: str, base_name: str) -> None:
    render_section_title("Trechos relevantes do manual")

    if not rules:
        render_warning("Nenhum trecho relevante encontrado.")
        return

    for i, rule in enumerate(rules, start=1):
        meta = rule.get("metadata", {})
        text = clean_preview_text(rule.get("text", ""))
        short = text[:350] + ("..." if len(text) > 350 else "")

        title = (
            f"[bold {COLOR_PRIMARY}]"
            f"[{i}] {meta.get('source_file')} | página {meta.get('page')} | score {rule.get('score', 0):.4f}"
            f"[/bold {COLOR_PRIMARY}]"
        )

        console.print(
            Panel(
                short or "Sem conteúdo.",
                title=title,
                title_align="left",
                border_style=COLOR_BORDER,
                box=box.ROUNDED,
            )
        )

    sheet_path = build_rules_sheet(rules, company, sector, base_name)
    if sheet_path:
        render_success(f"Painel visual dos trechos salvo em: {sheet_path}")
        try:
            Image.open(sheet_path).show()
            render_success("Os trechos relevantes foram abertos na tela pelo visualizador padrão do sistema.")
        except Exception as exc:
            render_warning(f"Não foi possível abrir automaticamente o painel de trechos: {exc}")


def print_people_table(result: dict) -> list[str]:
    render_section_title("Pessoas encontradas e recortes gerados")

    console.print(
        Panel.fit(
            f"[bold {COLOR_PRIMARY}]{result['people_count']} pessoas detectadas[/bold {COLOR_PRIMARY}]",
            border_style=COLOR_BORDER,
            box=box.ROUNDED,
        )
    )

    table = Table(
        box=box.ROUNDED,
        border_style=COLOR_BORDER,
        header_style=f"bold {COLOR_PRIMARY}",
        show_lines=True,
    )
    table.add_column("Pessoa", style=COLOR_PRIMARY, width=8)
    table.add_column("Bounding Box", style=COLOR_TEXT)
    table.add_column("Status", style=COLOR_TEXT, width=16)
    table.add_column("Crop", style=COLOR_MUTED)

    crop_paths = []

    for person in result["resultado"]:
        bbox = person["bbox"]
        bbox_text = f"({bbox['x1']}, {bbox['y1']}, {bbox['x2']}, {bbox['y2']})"
        crop_name = Path(person["crop_path"]).name
        status_colored = get_status_colored(person["status"])

        table.add_row(
            str(person["pessoa_id"]),
            bbox_text,
            status_colored,
            crop_name
        )
        crop_paths.append(person["crop_path"])

    console.print(table)

    for person in result["resultado"]:
        console.print(
            f"[bold {COLOR_PRIMARY}]Pessoa {person['pessoa_id']}[/bold {COLOR_PRIMARY}] "
            f"- justificativa: [{COLOR_TEXT}]{person['justificativa']}[/{COLOR_TEXT}]"
        )

    return crop_paths


def print_image_analysis(result: dict, output_path: str, company: str, sector: str) -> None:
    render_section_title("Análise de imagem")

    render_info("Empresa", company)
    render_info("Setor", sector)
    render_info("Imagem", result["image_name"])
    render_info("Pessoas detectadas", str(result["people_count"]))
    render_info("Trechos relevantes recuperados", str(result["rules_count"]))
    render_info("JSON salvo em", output_path)

    console.print()
    console.print(
        Panel.fit(
            json.dumps(result["status_summary"], ensure_ascii=False, indent=2),
            title=f"[bold {COLOR_PRIMARY}]Resumo de status[/bold {COLOR_PRIMARY}]",
            border_style=COLOR_BORDER,
            box=box.ROUNDED,
        )
    )

    print_rules_panel(
        result["regras_recuperadas"],
        company=company,
        sector=sector,
        base_name=result["image_name"],
    )

    crop_paths = print_people_table(result)

    sheet_path = build_contact_sheet(crop_paths, result["image_name"])
    if sheet_path:
        render_success(f"Painel com os recortes salvo em: {sheet_path}")
        try:
            Image.open(sheet_path).show()
            render_success("Os recortes foram abertos na tela pelo visualizador padrão do sistema.")
        except Exception as exc:
            render_warning(f"Não foi possível abrir automaticamente os recortes: {exc}")


def print_document_analysis(document_path: str, company: str, sector: str) -> None:
    retriever = RuleRetriever()
    results = retriever.search(company=company, sector=sector)

    render_section_title("Análise de documento / RAG")

    render_info("Documento selecionado", Path(document_path).name)
    render_info("Empresa", company)
    render_info("Setor", sector)

    objective = (
        "- Localizar apenas os trechos relevantes nos documentos.\n"
        "- Ignorar regras de outras empresas ou setores.\n"
        "- Lidar com variações semânticas e sinônimos."
    )

    console.print(
        Panel(
            objective,
            title=f"[bold {COLOR_PRIMARY}]Objetivo[/bold {COLOR_PRIMARY}]",
            border_style=COLOR_BORDER,
            box=box.ROUNDED,
        )
    )

    pages = extract_document_pages(Path(document_path))

    render_info("Páginas/blocos extraídos", str(len(pages)))
    render_info("Trechos relevantes encontrados", str(len(results)))

    if not results:
        render_warning("Nenhum trecho relevante encontrado.")
        return

    print_rules_panel(
        results,
        company=company,
        sector=sector,
        base_name=document_path,
    )


def show_menu() -> None:
    table = Table(
        title=f"[bold {COLOR_PRIMARY}]Menu principal[/bold {COLOR_PRIMARY}]",
        box=box.ROUNDED,
        border_style=COLOR_BORDER,
        header_style=f"bold {COLOR_PRIMARY}",
    )
    table.add_column("Opção", style=COLOR_PRIMARY, width=8)
    table.add_column("Descrição", style=COLOR_TEXT)

    table.add_row("1", "Analisar imagem")
    table.add_row("2", "Analisar documento (RAG)")
    table.add_row("3", "Reindexar documentos")
    table.add_row("0", "Sair")

    console.print(table)


def interactive_cli() -> None:
    console.clear()
    render_header()

    while True:
        show_menu()
        choice = console.input(f"[bold {COLOR_TEXT}]Opção: [/bold {COLOR_TEXT}]").strip()

        if choice == "0":
            render_success("Encerrando.")
            return

        if choice == "3":
            payload = rebuild_index()
            render_success("Índice reconstruído com sucesso.")
            console.print(
                Panel.fit(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    border_style=COLOR_BORDER,
                    box=box.ROUNDED,
                )
            )
            continue

        if choice == "1":
            images = [str(p) for p in list_images()]
            idx = ask_choice("Selecione a imagem para análise", images)
            if idx is None:
                continue

            image_path = images[idx]
            inferred_company = infer_company_from_filename(image_path)
            company = normalize_company_name(ask_text("Empresa", inferred_company))
            sector = ask_text("Setor", "Operacional")

            result, output_path = analyze_image(image_path, company, sector)
            print_image_analysis(result, output_path, company, sector)
            continue

        if choice == "2":
            documents = [str(p) for p in list_documents()]
            idx = ask_choice("Selecione o documento para análise", documents)
            if idx is None:
                continue

            document_path = documents[idx]
            inferred_company = infer_company_from_document_name(document_path)
            company = normalize_company_name(ask_text("Empresa", inferred_company))
            sector = ask_text("Setor", "Operacional")
            print_document_analysis(document_path, company, sector)
            continue

        render_warning("Opção inválida. Tente novamente.")


def main():
    parser = argparse.ArgumentParser(description="Compliance AI CLI")
    parser.add_argument("--company", default=None)
    parser.add_argument("--sector", default="Operacional")
    parser.add_argument("--image", default=None)
    parser.add_argument("--doc", default=None)
    parser.add_argument("--reindex", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    if args.reindex:
        payload = rebuild_index()
        console.print(
            Panel.fit(
                json.dumps(payload, ensure_ascii=False, indent=2),
                title=f"[bold {COLOR_PRIMARY}]Reindexação[/bold {COLOR_PRIMARY}]",
                border_style=COLOR_BORDER,
                box=box.ROUNDED,
            )
        )

    if args.interactive or (not args.image and not args.doc):
        interactive_cli()
        return

    if args.image:
        company = normalize_company_name(args.company) if args.company else infer_company_from_filename(args.image)
        result, output_path = analyze_image(args.image, company, args.sector)
        print_image_analysis(result, output_path, company, args.sector)
        return

    if args.doc:
        inferred_company = infer_company_from_document_name(args.doc)
        company = normalize_company_name(args.company or inferred_company)
        print_document_analysis(args.doc, company, args.sector)


if __name__ == "__main__":
    main()