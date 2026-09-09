# -*- coding: utf-8 -*-
"""Inject screenshot galleries into autotest-docs test pages."""
from __future__ import annotations

import re
from pathlib import Path

PAGES = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\pages")
MEDIA = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\media")

# page file stem without test- -> slug used in T_{slug}_*
FILE_TO_SLUG = {
    "test-overload": "overload",
    "test-flicker": "flicker",
    "test-harmonic": "harmonic",
    "test-fixedpf": "fixedpf",
    "test-dcinj": "dcinj",
    "test-reconnect": "reconnect",
    "test-ovuf": "ovuf",
    "test-static-cos": "static-cos",
    "test-static-qu": "static-qu",
    "test-active-p": "active-p",
    "test-overfreq": "overfreq",
    "test-underfreq": "underfreq",
    "test-fixed-q": "fixed-q",
    "test-qin": "qin",
    "test-qacc": "qacc",
    "test-qcap": "qcap",
    "test-dyn-cos": "dyn-cos",
    "test-dyn-qu": "dyn-qu",
    "test-pu": "pu",
    "test-rocof": "rocof",
    "test-freq-adapt": "freq-adapt",
    "test-volt-adapt": "volt-adapt",
    "test-rapid-volt": "rapid-volt",
    "test-volt10min": "volt10min",
    "test-immun": "immun",
    "test-static-mppt": "static-mppt",
}


def gallery_html(slug: str) -> str:
    shots = sorted(MEDIA.glob(f"T_{slug}_*.png"))
    if not shots:
        return ""
    parts = ['<h2>界面截图（对照填写）</h2>', '<p class="muted">以下为软件对话框各步骤实拍，可与左侧文字对照。</p>']
    for p in shots:
        name = p.name
        if "_00_overview" in name:
            cap = "对话框总览（步骤①）"
        else:
            m = re.search(r"_(\d+)_step", name)
            n = m.group(1) if m else "?"
            cap = f"步骤 {int(n)}"
        parts.append(
            f'<figure>\n  <img src="media/{name}" alt="{cap}" />\n'
            f"  <figcaption>{cap}</figcaption>\n</figure>"
        )
    return "\n".join(parts) + "\n"


def inject(path: Path, slug: str) -> bool:
    text = path.read_text(encoding="utf-8")
    # Remove previous auto gallery if re-run
    text = re.sub(
        r"\n?<h2>界面截图（对照填写）</h2>[\s\S]*?(?=\n<h2>①|\n<h2>②|\n<div class=\"callout ok\">\n<strong>示例一套|\Z)",
        "\n",
        text,
        count=1,
    )
    gal = gallery_html(slug)
    if not gal:
        print("no shots", slug)
        return False

    # Insert after first </ol> that follows 本试验步骤一览
    m = re.search(r"(<h2>本试验步骤一览</h2>\s*<ol>[\s\S]*?</ol>)", text)
    if m:
        pos = m.end()
        text = text[:pos] + "\n\n" + gal + text[pos:]
    else:
        # after first callout
        m2 = re.search(r'(<div class="callout ok">[\s\S]*?</div>)', text)
        if m2:
            pos = m2.end()
            text = text[:pos] + "\n\n" + gal + text[pos:]
        else:
            text = gal + "\n" + text

    # For overload: keep old figures too but gallery is enough; strip duplicate old media refs optional
    path.write_text(text, encoding="utf-8")
    print("updated", path.name, "shots", len(list(MEDIA.glob(f"T_{slug}_*.png"))))
    return True


def main() -> None:
    n = 0
    for stem, slug in FILE_TO_SLUG.items():
        path = PAGES / f"{stem}.html"
        if not path.exists():
            print("missing page", path.name)
            continue
        if inject(path, slug):
            n += 1
    print("DONE pages", n)


if __name__ == "__main__":
    main()
