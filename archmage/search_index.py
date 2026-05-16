# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
#
# Build a client-side full-text search index from extracted CHM HTML files.
#
# This module is part of archmage and is licensed under the same terms
# (GNU General Public License v2 or later).
#

from __future__ import annotations

import json
import os
import re
from html.parser import HTMLParser
from typing import List

# Template/frame files that aren't content pages.
SKIP_FILES = {
    "arch_contents.html",
    "arch_frameset.html",
    "arch_header.html",
    "index.html",
}


def _normspace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


class _Extractor(HTMLParser):
    """Pull title, headings, and visible body text from one HTML page."""

    SKIP_TAGS = {"script", "style", "noscript"}
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: List[str] = []
        self.heading_parts: List[str] = []
        self.body_parts: List[str] = []
        self._skip_depth = 0
        self._in_title = False
        self._heading_tag = None
        self._heading_buf: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in self.HEADING_TAGS and self._heading_tag is None:
            self._heading_tag = tag
            self._heading_buf = []

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "title":
            self._in_title = False
        elif tag == self._heading_tag:
            text = _normspace("".join(self._heading_buf))
            if text:
                self.heading_parts.append(text)
            self._heading_tag = None
            self._heading_buf = []

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        if self._in_title:
            self.title_parts.append(data)
            return
        if self._heading_tag is not None:
            self._heading_buf.append(data)
        self.body_parts.append(data)

    @property
    def title(self) -> str:
        return _normspace("".join(self.title_parts))

    @property
    def headings(self) -> str:
        return " | ".join(self.heading_parts)

    @property
    def body(self) -> str:
        return _normspace(" ".join(self.body_parts))


def _iter_html_files(destdir: str):
    """Yield (relpath, abspath) for every content HTML file under destdir."""
    for root, _dirs, files in os.walk(destdir):
        for name in sorted(files):
            if not name.lower().endswith((".html", ".htm")):
                continue
            if name in SKIP_FILES:
                continue
            abspath = os.path.join(root, name)
            relpath = os.path.relpath(abspath, destdir).replace(os.sep, "/")
            yield relpath, abspath


def build_search_index(destdir: str, max_body: int = 3000) -> str:
    """Scan ``destdir`` and write ``search_index.js`` into it.

    The output assigns ``window.SEARCH_INDEX`` to a JSON array of
    ``{id, title, headings, text}`` records. Body text is capped at
    ``max_body`` characters per page to keep the index small.

    Returns the path to the written file.
    """
    docs = []
    for relpath, abspath in _iter_html_files(destdir):
        try:
            with open(abspath, "rb") as fh:
                raw = fh.read()
        except OSError:
            continue
        try:
            html = raw.decode("utf-8")
        except UnicodeDecodeError:
            html = raw.decode("latin-1", errors="replace")
        ext = _Extractor()
        try:
            ext.feed(html)
            ext.close()
        except Exception:  # noqa: BLE001 - never fail extraction on a bad page
            continue
        docs.append({
            "id": relpath,
            "title": ext.title or os.path.splitext(os.path.basename(relpath))[0],
            "headings": ext.headings,
            "text": ext.body[:max_body],
        })

    payload = json.dumps(docs, ensure_ascii=False, separators=(",", ":"))
    out_path = os.path.join(destdir, "search_index.js")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("window.SEARCH_INDEX = ")
        fh.write(payload)
        fh.write(";\n")
    return out_path
