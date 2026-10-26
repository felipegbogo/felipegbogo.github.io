#!/usr/bin/env python3
"""Build the inline Aula 0 document from its original Markdown.

Run from any directory with Python 3.10 or newer:
    python3 scripts/build_doctrine_lesson.py

This dependency-free renderer supports the Markdown used in the source lesson:
headings, paragraphs, emphasis, links, inline code, and numbered footnotes.
Raw HTML is escaped. Only HTTP(S) links are emitted as external links. The
original Markdown stays in docs/doctrine/; no browser fetch or Markdown library
is needed to read the generated lesson.
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
SOURCE = ROOT / "docs/doctrine/Capitulo_0_Como_fazer_perguntas_lendo_livros.md"
OUTPUT = ROOT / "assets/doctrine-lesson.js"
PREFIX = "lesson-0-"
FOOTNOTE = re.compile(r"\[\^([A-Za-z0-9_-]+)\]")
DEFINITION = re.compile(r"^\[\^([A-Za-z0-9_-]+)\]:\s*(.*)$")
LINK = re.compile(r"\[([^\]\n]+)\]\(([^\s)]+)\)")


class LessonRenderer:
    def __init__(self, definitions: dict[str, str]) -> None:
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
                reference_id = f"{PREFIX}ref-{label}-{occurrence}"
                self.reference_ids.setdefault(label, []).append(reference_id)
                parts.append(
                    f'<sup class="bogo-lesson-note-ref"><a id="{reference_id}" '
                    f'href="#{PREFIX}note-{label}" role="doc-noteref" '
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
        base_id = PREFIX + slug
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

        for line in lines:
            stripped = line.strip()
            if not stripped:
                flush()
                continue
            heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
            if heading:
                flush()
                blocks.append(self.heading(len(heading.group(1)), heading.group(2)))
            else:
                if re.match(r"^(?:```|~~~|>|[-+*]\s|\d+[.)]\s)", stripped):
                    raise ValueError("Unsupported block Markdown; extend this renderer before regenerating the lesson.")
                paragraph.append(stripped)
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
                f'<li id="{PREFIX}note-{label}" role="doc-endnote">'
                f'{self.inline(text, footnotes=False)} {backlinks}</li>'
            )
        return '<ol class="bogo-lesson-notes">\n' + "\n".join(notes) + "\n</ol>"


def build() -> dict[str, object]:
    source_bytes = SOURCE.read_bytes()
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
    title = re.sub(r"^Capítulo\s+0\s*[—–-]\s*", "", document_title)
    renderer = LessonRenderer(definitions)
    rendered = renderer.blocks(body) + "\n" + renderer.notes()
    data = {
        "title": title,
        "documentTitle": document_title,
        "language": "pt-BR",
        "sourcePath": SOURCE.relative_to(ROOT).as_posix(),
        "sourceSha256": hashlib.sha256(source_bytes).hexdigest(),
        "html": rendered,
    }
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    OUTPUT.write_text(
        "/* Generated from the original Aula 0 Markdown by scripts/build_doctrine_lesson.py. */\n"
        "window.BogoDoctrineLesson = Object.freeze(" + payload + ");\n",
        encoding="utf-8",
    )
    return {
        "source": str(SOURCE),
        "output": str(OUTPUT),
        "title": title,
        "source_bytes": len(source_bytes),
        "source_sha256": data["sourceSha256"],
        "footnotes": len(definitions),
        "footnote_references": sum(renderer.references.values()),
        "output_bytes": OUTPUT.stat().st_size,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
