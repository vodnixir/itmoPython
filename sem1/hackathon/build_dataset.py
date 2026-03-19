#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds a training dataset from a JSON file (NOT jsonl) and prefixes each sample's text
with lightweight meta tags, e.g.:
[TOPIC=...] [DOC=1] [HAS_ATTACH=1] [ADDRESSEE=1] [LEN=M]
<original text>

Input format (JSON):
[
  {"idx": 0, "label": "...", "text": "..."},
  ...
]

Output format (JSON): same list, but "text" is prefixed with meta tags.

Usage:
  python build_dataset_with_meta.py --input train_hackathon_dataset.json --output train_with_meta.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from typing import Any, Dict, List, Tuple


# -----------------------------
# Heuristics (tune if needed)
# -----------------------------

def _len_bucket(text: str) -> str:
    n = len(text)
    if n < 800:
        return "S"
    if n < 1800:
        return "M"
    return "L"


_DOC_PATTERNS = [
    r"\bПРИКАЗ\b",
    r"\bРАСПОРЯЖЕНИЕ\b",
    r"\bУКАЗАНИЕ\b",
    r"\bСЛУЖЕБНАЯ\s+ЗАПИСКА\b",
    r"\bПРОТОКОЛ\b",
    r"\bАКТ\b",
    r"\bДОВЕРЕННОСТЬ\b",
    r"\bДОГОВОР\b",
    r"\bДОПОЛНИТЕЛЬНОЕ\s+СОГЛАШЕНИЕ\b",
    r"\bНАРЯД-ЗАКАЗ\b",
    r"\bЗАЯВКА\b",
    r"\bОТЧ[ЁЕ]Т\b",
    r"\bПИСЬМО\b",
]
_DOC_RE = re.compile("|".join(_DOC_PATTERNS), flags=re.IGNORECASE)

_ATTACH_RE = re.compile(r"(Приложен(ие|ия)\s*:|Прил\.\s*:|в\s+приложени[ия])", flags=re.IGNORECASE)

_ADDRESSEE_RE = re.compile(
    r"(Уважаем(ый|ая|ые)\b|Руководител[юя]\b|Директор(у|ам)\b|Начальник(у|ам)\b|Исполнительн(ому|ому)\s+директор(у|ам)\b|Генеральн(ому|ому)\s+директор(у|ам)\b)",
    flags=re.IGNORECASE,
)

_PLACEHOLDER_RE = re.compile(r"\[[A-ZА-Я0-9_]+\]")


def _detect_doc(text: str) -> int:
    # Usually document type is in the header; search the first ~700 chars.
    return 1 if _DOC_RE.search(text[:700]) else 0


def _detect_attach(text: str) -> int:
    return 1 if _ATTACH_RE.search(text) else 0


def _detect_addressee(text: str) -> int:
    return 1 if _ADDRESSEE_RE.search(text[:800]) else 0


def _too_many_placeholders(s: str, threshold: float = 0.5) -> bool:
    """Reject topics that are mostly placeholders like [ORGANIZATION] [ID] ..."""
    if not s:
        return False
    ph = len(_PLACEHOLDER_RE.findall(s))
    if ph == 0:
        return False
    tokens = re.findall(r"\S+", s)
    if not tokens:
        return False
    return (ph / len(tokens)) >= threshold


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _extract_topic(text: str) -> str:
    """
    Practical (high-recall) topic extraction:
    - take first few lines of the header
    - remove contact/identifier-heavy lines
    - stop before "Уважаемый..."
    - join into one string, cap length
    """
    head = text[:2000]

    # drop leading placeholder-only prefixes like "[ORGANIZATION] [ID] ..."
    head = re.sub(r"^(?:\s*\[[A-ZА-Я0-9_]+\]\s*)+", "", head)

    # cut before greeting
    head = re.split(r"\bУважаем(ый|ая|ые)\b", head, maxsplit=1, flags=re.IGNORECASE)[0]

    lines = [_normalize_line(l) for l in head.splitlines()[:6]]
    lines = [l for l in lines if l]

    cleaned: List[str] = []
    for l in lines:
        # skip boilerplate lines (contacts, ids, addresses, urls)
        if re.search(r"(тел\.|e-?mail|факс|ОКПО|ОГРН|ИНН|КПП|Адрес|www\.|http)", l, flags=re.IGNORECASE):
            continue
        cleaned.append(l)

    if not cleaned:
        cleaned = lines

    topic = " ".join(cleaned)
    topic = re.sub(r"\s+", " ", topic).strip(" -;:,\t")

    if len(topic) > 220:
        topic = topic[:217].rstrip() + "…"
    return topic


def _build_meta_prefix(text: str) -> Tuple[str, str]:
    fields: List[str] = []

    topic = _extract_topic(text)
    if topic and not _too_many_placeholders(topic, threshold=0.5):
        fields.append(f"TOPIC={topic}")

    # ВОТ ЭТОТ БЛОК НЕЛЬЗЯ ТЕРЯТЬ — иначе DOC станет 0/...
    if _detect_doc(text):
        fields.append("DOC=1")

    if _detect_attach(text):
        fields.append("HAS_ATTACH=1")

    if _detect_addressee(text):
        fields.append("ADDRESSEE=1")

    fields.append(f"LEN={_len_bucket(text)}")

    prefix = " ".join(f"[{f}]" for f in fields)
    return prefix, topic


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to JSON dataset (list of objects).")
    ap.add_argument("--output", required=True, help="Path to save JSON with meta prefixes.")
    ap.add_argument("--debug", action="store_true", help="Print coverage stats and examples.")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    meta_counts = Counter()
    topic_accept = 0
    topic_reject = 0
    reject_reasons = Counter()
    label_counts = Counter()

    out: List[Dict[str, Any]] = []
    for ex in data:
        text = ex["text"]
        label = ex["label"]
        label_counts[label] += 1

        prefix, topic = _build_meta_prefix(text)

        if "[ADDRESSEE=1]" in prefix:
            meta_counts["ADDRESSEE"] += 1
        if "[DOC=1]" in prefix:
            meta_counts["DOC"] += 1
        if "[HAS_ATTACH=1]" in prefix:
            meta_counts["HAS_ATTACH"] += 1
        if "[TOPIC=" in prefix:
            meta_counts["TOPIC"] += 1

        if topic:
            if _too_many_placeholders(topic, threshold=0.5):
                topic_reject += 1
                reject_reasons["too_many_bad_placeholders"] += 1
            else:
                topic_accept += 1
        else:
            topic_reject += 1
            reject_reasons["none_or_empty"] += 1

        out.append(
            {
                "idx": ex.get("idx"),
                "label": label,
                "text": f"{prefix}\n{text}",
            }
        )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    if args.debug:
        n = len(data)
        print("== LABEL DISTRIBUTION ==")
        print(f"Total labels: {len(label_counts)}")
        print("Rarest labels:")
        for lbl, c in label_counts.most_common()[::-1][:12]:
            print(f"  {lbl}: {c}")

        print("\n== META COVERAGE ==")
        for k in ["ADDRESSEE", "TOPIC", "DOC", "HAS_ATTACH"]:
            print(f"  {k}: {meta_counts[k]}/{n} ({(100.0*meta_counts[k]/n):.1f}%)")
        print(f"  LEN_BUCKET: {n}/{n} (100.0%)")

        print("\n== TOPIC FILTER DEBUG ==")
        print(f"Accepted topics: {topic_accept}")
        print(f"Rejected topics: {topic_reject}")
        total = topic_accept + topic_reject
        print(f"Acceptance rate: {(100.0*topic_accept/total):.1f}%")
        print("\n-- Reject reasons --")
        for r, c in reject_reasons.most_common():
            print(f"  {r}: {c}")


if __name__ == "__main__":
    main()
