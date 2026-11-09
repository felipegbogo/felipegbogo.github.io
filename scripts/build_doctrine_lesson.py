#!/usr/bin/env python3
"""Build the inline doctrine lessons from their original Markdown.

Run from any directory with Python 3.10 or newer:
    python3 scripts/build_doctrine_lesson.py

This dependency-free renderer supports the Markdown used in the lessons:
headings, paragraphs, blockquotes, sequential ordered lists with single-line
items, emphasis, links, inline code, and numbered footnotes.
Raw HTML is escaped. Only HTTP(S) links are emitted as external links. The
original Markdown stays in docs/doctrine/; no browser fetch or Markdown library
is needed to read the generated lesson. The script also updates index.html with
a content hash in the lesson script URL, so a new lesson cannot reuse the old
JavaScript file from the browser's cache after the page is reloaded.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/doctrine-lesson.js"
ENTRY = ROOT / "index.html"
LESSONS = (
    (0, "Como_fazer_perguntas_lendo_livros", "How to ask questions while reading books?"),
    (1, "O_fim_da_existencia_do_homem", "The Purpose of Human Existence"),
)
FOOTNOTE = re.compile(r"\[\^([A-Za-z0-9_-]+)\]")
DEFINITION = re.compile(r"^\[\^([A-Za-z0-9_-]+)\]:\s*(.*)$")
LINK = re.compile(r"\[([^\]\n]+)\]\(([^\s)]+)\)")
ORDERED_ITEM = re.compile(r"([0-9]+)\.\s+(.+)")


class LessonRenderer:
    def __init__(self, number: int, definitions: dict[str, str]) -> None:
        self.prefix = f"lesson-{number}-"
        self.definitions = definitions
        self.references: Counter[str] = Counter()
        self.reference_ids: dict[str, list[str]] = {}
        self.heading_ids: set[str] = set()

    def inline(self, text: str, *, footnotes: bool = True) -> str:
        parts = []
        index = 0
        while index < len(text):
            if text[index] == "\\" and index + 1 < len(text):
                parts.append(html.escape(text[index + 1]))
                index += 2
                continue

            note = FOOTNOTE.match(text, index) if footnotes else None
            if note:
                label = note.group(1)
                if label not in self.definitions:
                    raise ValueError(f"Missing definition for footnote {label}")
                self.references[label] += 1
                occurrence = self.references[label]
                reference_id = f"{self.prefix}ref-{label}-{occurrence}"
                self.reference_ids.setdefault(label, []).append(reference_id)
                parts.append(
                    f'<sup class="bogo-lesson-note-ref"><a id="{reference_id}" '
                    f'href="#{self.prefix}note-{label}" role="doc-noteref" '
                    f'aria-label="Nota {html.escape(label)}">{html.escape(label)}</a></sup>'
                )
                index = note.end()
                continue

            link = LINK.match(text, index)
            if link:
                label, destination = link.groups()
                parsed = urlsplit(destination)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError(f"Unsupported link destination: {destination}")
                parts.append(
                    f'<a href="{html.escape(destination, quote=True)}" '
                    f'target="_blank" rel="noopener noreferrer">'
                    f'{self.inline(label, footnotes=False)}</a>'
                )
                index = link.end()
                continue

            delimiter = "**" if text.startswith("**", index) else "*" if text[index] == "*" else "`" if text[index] == "`" else None
            if delimiter:
                end = text.find(delimiter, index + len(delimiter))
                if end > index + len(delimiter):
                    content = text[index + len(delimiter):end]
                    tag = {"**": "strong", "*": "em", "`": "code"}[delimiter]
                    rendered = html.escape(content) if tag == "code" else self.inline(content, footnotes=footnotes)
                    parts.append(f"<{tag}>{rendered}</{tag}>")
                    index = end + len(delimiter)
                    continue

            parts.append(html.escape(text[index]))
            index += 1
        return "".join(parts)

    def heading(self, level: int, text: str) -> str:
        slug = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-") or "section"
        base_id = self.prefix + slug
        heading_id, occurrence = base_id, 1
        while heading_id in self.heading_ids:
            occurrence += 1
            heading_id = f"{base_id}-{occurrence}"
        self.heading_ids.add(heading_id)
        # The site supplies the course h1 and the lesson's h2 in its summary.
        level = min(6, level + 1)
        return f'<h{level} id="{heading_id}">{self.inline(text)}</h{level}>'

    def blocks(self, lines: list[str]) -> str:
        blocks, paragraph = [], []

        def flush() -> None:
            if paragraph:
                blocks.append(f'<p>{self.inline(" ".join(paragraph))}</p>')
                paragraph.clear()

        index = 0
        while index < len(lines):
            stripped = lines[index].strip()
            if not stripped:
                flush()
            elif stripped.startswith(">"):
                flush()
                quoted = []
                while index < len(lines) and lines[index].lstrip().startswith(">"):
                    quoted.append(lines[index].lstrip()[1:].lstrip())
                    index += 1
                blocks.append(f"<blockquote>\n{self.blocks(quoted)}\n</blockquote>")
                continue
            elif first_item := ORDERED_ITEM.fullmatch(stripped):
                flush()
                start = int(first_item.group(1))
                items = []
                while index < len(lines):
                    item = ORDERED_ITEM.fullmatch(lines[index].strip())
                    if not item:
                        break
                    if int(item.group(1)) != start + len(items):
                        raise ValueError("An ordered list must use sequential numbering.")
                    items.append(f"<li>{self.inline(item.group(2))}</li>")
                    index += 1
                start_attribute = f' start="{start}"' if start != 1 else ""
                blocks.append(f"<ol{start_attribute}>\n" + "\n".join(items) + "\n</ol>")
                continue
            elif heading := re.fullmatch(r"(#{1,6})\s+(.+?)\s*", stripped):
                flush()
                blocks.append(self.heading(len(heading.group(1)), heading.group(2)))
            else:
                if re.match(r"^(?:```|~~~|[-+*]\s|\d+[.)]\s)", stripped):
                    raise ValueError("Unsupported block Markdown; extend this renderer before regenerating the lessons.")
                paragraph.append(stripped)
            index += 1
        flush()
        return "\n".join(blocks)

    def notes(self) -> str:
        if set(self.reference_ids) != set(self.definitions):
            raise ValueError("Every footnote definition must have a matching reference in the lesson.")
        notes = []
        for label, text in self.definitions.items():
            backlinks = " ".join(
                f'<a class="bogo-lesson-note-back" href="#{reference_id}" '
                f'aria-label="Voltar à referência {html.escape(label)}">↩</a>'
                for reference_id in self.reference_ids[label]
            )
            notes.append(
                f'<li id="{self.prefix}note-{label}" role="doc-endnote">'
                f'{self.inline(text, footnotes=False)} {backlinks}</li>'
            )
        return '<ol class="bogo-lesson-notes">\n' + "\n".join(notes) + "\n</ol>"


def build_lesson(number: int, basename: str, title_en: str) -> tuple[dict[str, object], dict[str, object]]:
    source = ROOT / f"docs/doctrine/Capitulo_{number}_{basename}.md"
    pdf = ROOT / f"docs/doctrine/Aula_{number}_{basename}.pdf"
    source_bytes = source.read_bytes()
    pdf_bytes = pdf.read_bytes()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError(f"The lesson {number} download must be a PDF file.")
    pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    lines = source_bytes.decode("utf-8").splitlines()
    definitions: dict[str, str] = {}
    body = []
    for line in lines:
        note = DEFINITION.match(line)
        if note:
            label, text = note.groups()
            if label in definitions:
                raise ValueError(f"Duplicate footnote definition: {label}")
            definitions[label] = text
        else:
            body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    if not body or not body[0].startswith("# "):
        raise ValueError("The lesson must start with a Markdown h1 title.")
    document_title = body.pop(0)[2:].strip()
    title_match = re.fullmatch(rf"Capítulo\s+{number}\s*[—–-]\s*(\S.*)", document_title)
    if not title_match:
        raise ValueError(f"The title must start with 'Capítulo {number} —'.")
    title = title_match.group(1)
    renderer = LessonRenderer(number, definitions)
    rendered = renderer.blocks(body) + "\n" + renderer.notes()
    data = {
        "number": number,
        "title": title,
        "titleEn": title_en,
        "documentTitle": document_title,
        "language": "pt-BR",
        "sourcePath": source.relative_to(ROOT).as_posix(),
        "sourceSha256": hashlib.sha256(source_bytes).hexdigest(),
        "pdfUrl": pdf.relative_to(ROOT).as_posix() + "?v=" + pdf_sha256[:12],
        "pdfFilename": pdf.name,
        "html": rendered,
    }
    report = {
        "number": number,
        "source": str(source),
        "title": title,
        "source_bytes": len(source_bytes),
        "source_sha256": data["sourceSha256"],
        "pdf_bytes": len(pdf_bytes),
        "pdf_sha256": pdf_sha256,
        "footnotes": len(definitions),
        "footnote_references": sum(renderer.references.values()),
    }
    return data, report


def build() -> dict[str, object]:
    numbers = [number for number, _, _ in LESSONS]
    if len(set(numbers)) != len(numbers) or 0 not in numbers:
        raise ValueError("Each lesson needs a unique number, including the original lesson 0.")
    results = [build_lesson(*lesson) for lesson in sorted(LESSONS, reverse=True)]
    payload = json.dumps([data for data, _ in results], ensure_ascii=False, indent=2).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    javascript = (
        "/* Generated from the original lesson Markdown by scripts/build_doctrine_lesson.py. */\n"
        "window.BogoDoctrineLessons = Object.freeze(" + payload + ".map(lesson => Object.freeze(lesson)));\n"
        "window.BogoDoctrineLesson = window.BogoDoctrineLessons.find(lesson => lesson.number === 0);\n"
    )
    asset_version = hashlib.sha256(javascript.encode("utf-8")).hexdigest()[:12]
    entry = ENTRY.read_text(encoding="utf-8")
    updated_entry, count = re.subn(
        r'(<script src="assets/doctrine-lesson\.js)(?:\?[^\"]*)?(\"></script>)',
        lambda match: f"{match.group(1)}?v={asset_version}{match.group(2)}",
        entry,
    )
    if count != 1:
        raise ValueError("Expected exactly one lesson script tag in index.html; no files were written.")
    OUTPUT.write_text(javascript, encoding="utf-8")
    if updated_entry != entry:
        ENTRY.write_text(updated_entry, encoding="utf-8")
    return {
        "output": str(OUTPUT),
        "entry": str(ENTRY),
        "asset_version": asset_version,
        "lessons": [report for _, report in results],
        "output_bytes": OUTPUT.stat().st_size,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
