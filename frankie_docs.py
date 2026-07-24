"""
frankie_docs.py — Extract ## doc-comments from .fk source and render to Markdown.

Doc-comment syntax:
    ## This is a doc comment for the function below.
    ## Supports **markdown** inline formatting.
    ## @param name  Description of parameter
    ## @return      What the function returns
    ## @example
    ##   result = my_func(42)
    ##   puts result
    def my_func(name)
      ...
    end

Usage (via frankiec):
    frankiec docs <file.fk>              # print Markdown to stdout
    frankiec docs --output out.md <file> # write to file
    frankiec docs .                      # scan all .fk in current dir
"""

import os
import sys
import re


def _extract_docs(source: str, filename: str) -> list:
    """
    Parse source lines and extract doc-comment blocks paired with their
    following definition (def / record).

    Returns a list of dicts:
      { 'name': str, 'kind': 'def'|'record', 'params': str,
        'doc_lines': [str], 'source_line': int }
    """
    lines = source.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('## ') or stripped == '##':
            # Collect consecutive ## lines
            doc_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith('## '):
                    doc_lines.append(s[3:])
                elif s == '##':
                    doc_lines.append('')
                else:
                    break
                i += 1
            # Skip blank lines between doc block and def/record
            j = i
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                next_line = lines[j].strip()
                m_def = re.match(r'^def\s+(\w[\w?!]*)\s*(\([^)]*\))?', next_line)
                m_rec = re.match(r'^record\s+(\w+)\s*(\([^)]*\))?', next_line)
                if m_def:
                    entries.append({
                        'name':        m_def.group(1),
                        'kind':        'def',
                        'params':      m_def.group(2) or '()',
                        'doc_lines':   doc_lines,
                        'source_line': j + 1,
                    })
                elif m_rec:
                    entries.append({
                        'name':        m_rec.group(1),
                        'kind':        'record',
                        'params':      m_rec.group(2) or '()',
                        'doc_lines':   doc_lines,
                        'source_line': j + 1,
                    })
            # i is already advanced past the doc block
        else:
            i += 1
    return entries


def _render_entry(entry: dict, filename: str) -> str:
    """Render a single doc entry to Markdown."""
    lines = []
    kind_icon = '🔧' if entry['kind'] == 'def' else '📦'
    sig = f"{entry['name']}{entry['params']}"
    lines.append(f"### {kind_icon} `{sig}`")
    lines.append(f"*Defined in `{os.path.basename(filename)}`, line {entry['source_line']}*")
    lines.append("")

    # Process doc lines — handle @param / @return / @example tags
    in_example = False
    example_lines = []
    plain_lines = []
    params = []
    returns = []

    for dl in entry['doc_lines']:
        if dl.startswith('@param '):
            rest = dl[7:].strip()
            params.append(rest)
            if in_example:
                in_example = False
        elif dl.startswith('@return'):
            rest = dl[7:].strip()
            returns.append(rest)
            if in_example:
                in_example = False
        elif dl.strip() == '@example':
            if plain_lines:
                lines.append(' '.join(plain_lines).strip())
                plain_lines = []
            in_example = True
        elif in_example:
            example_lines.append(dl)
        else:
            plain_lines.append(dl)

    if plain_lines:
        lines.append(' '.join(plain_lines).strip())
        lines.append("")

    if params:
        lines.append("**Parameters:**")
        for p in params:
            # Split first word as param name
            parts = p.split(None, 1)
            if len(parts) == 2:
                lines.append(f"- `{parts[0]}` — {parts[1]}")
            else:
                lines.append(f"- `{p}`")
        lines.append("")

    if returns:
        lines.append(f"**Returns:** {' '.join(returns)}")
        lines.append("")

    if example_lines:
        lines.append("**Example:**")
        lines.append("```ruby")
        for el in example_lines:
            # Strip leading two spaces of indentation if present
            lines.append(el[2:] if el.startswith('  ') else el)
        lines.append("```")
        lines.append("")

    return '\n'.join(lines)


def generate_docs(fk_file: str) -> str:
    """Parse a .fk file and return a Markdown documentation string."""
    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    entries = _extract_docs(source, fk_file)
    if not entries:
        return f"# {os.path.basename(fk_file)}\n\n*No doc-comments found. Add `## Description` above your `def` or `record` definitions.*\n"

    basename = os.path.basename(fk_file)
    module_name = os.path.splitext(basename)[0]
    md_lines = [
        f"# {module_name}",
        "",
        f"*Auto-generated from `{basename}` by `frankiec docs`*",
        "",
        "---",
        "",
    ]

    defs     = [e for e in entries if e['kind'] == 'def']
    records  = [e for e in entries if e['kind'] == 'record']

    if records:
        md_lines.append("## Record Types")
        md_lines.append("")
        for e in records:
            md_lines.append(_render_entry(e, fk_file))
            md_lines.append("---")
            md_lines.append("")

    if defs:
        md_lines.append("## Functions")
        md_lines.append("")
        for e in defs:
            md_lines.append(_render_entry(e, fk_file))
            md_lines.append("---")
            md_lines.append("")

    return '\n'.join(md_lines)


def docs_file(fk_file: str, output: str = None) -> bool:
    """Generate docs for a single file, writing to output or stdout."""
    if not os.path.exists(fk_file):
        print(f"[docs] File not found: {fk_file}", file=sys.stderr)
        return False
    try:
        md = generate_docs(fk_file)
    except Exception as e:
        print(f"[docs] Error: {e}", file=sys.stderr)
        return False

    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"[docs] ✓  {fk_file} → {output}")
    else:
        print(md, end='')
    return True


def docs_directory(directory: str, output_dir: str = None) -> bool:
    """Generate docs for all .fk files in a directory."""
    fk_files = [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.endswith('.fk') and not f.startswith('_')
    ]
    if not fk_files:
        print(f"[docs] No .fk files found in {directory!r}")
        return True

    ok = True
    for fk in fk_files:
        out = None
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base = os.path.splitext(os.path.basename(fk))[0]
            out = os.path.join(output_dir, base + '.md')
        ok = docs_file(fk, out) and ok
    return ok


# ─── v1.19: HTML rendering ────────────────────────────────────────────────────

_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} — Frankie docs</title>
<style>
  :root {{ --bg:#0b0f0c; --panel:#111712; --border:#1e2a20; --green:#39ff6a;
          --dim:#5f7a66; --text:#d7e4da; --amber:#ffbd2e; }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); margin:0 auto; max-width:820px;
         padding:2.5rem 1.5rem; font-family:'Courier New',monospace; line-height:1.55; }}
  h1 {{ color:var(--green); letter-spacing:.06em; }}
  h1 span {{ color:var(--dim); font-size:.55em; letter-spacing:.12em; }}
  .entry {{ background:var(--panel); border:1px solid var(--border); border-radius:4px;
           padding:1.1rem 1.3rem; margin:1.2rem 0; }}
  .sig {{ color:var(--green); font-weight:bold; font-size:1.02rem; }}
  .loc {{ color:var(--dim); font-size:.75rem; margin:.2rem 0 .7rem; }}
  .desc {{ margin:.4rem 0; }}
  .tag {{ color:var(--amber); font-size:.8rem; letter-spacing:.1em;
         text-transform:uppercase; margin-top:.8rem; }}
  ul {{ margin:.3rem 0 .3rem 1.2rem; padding:0; }}
  code, pre {{ background:#0a120c; border:1px solid var(--border); border-radius:3px; }}
  code {{ padding:.08rem .3rem; color:var(--green); }}
  pre {{ padding:.7rem .9rem; overflow-x:auto; color:var(--text); }}
  footer {{ color:var(--dim); font-size:.75rem; margin-top:2.5rem;
           border-top:1px solid var(--border); padding-top:1rem; }}
</style>
</head>
<body>
<h1>🧟 {title} <span>FRANKIE DOCS</span></h1>
{body}
<footer>Auto-generated by <code>frankiec docs --html</code> — zero dependencies, as always.</footer>
</body>
</html>
"""


def _html_escape(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def _render_entry_html(entry, filename):
    e = _html_escape
    icon = '🔧' if entry['kind'] == 'def' else '📦'
    parts = [f"<div class=\"entry\">",
             f"<div class=\"sig\">{icon} {e(entry['name'] + entry['params'])}</div>",
             f"<div class=\"loc\">{e(os.path.basename(filename))}:{entry['source_line']}</div>"]
    plain, params, returns, example, in_ex = [], [], [], [], False
    for dl in entry['doc_lines']:
        if dl.startswith('@param '):
            params.append(dl[7:].strip()); in_ex = False
        elif dl.startswith('@return'):
            returns.append(dl[7:].strip()); in_ex = False
        elif dl.strip() == '@example':
            in_ex = True
        elif in_ex:
            example.append(dl[2:] if dl.startswith('  ') else dl)
        else:
            plain.append(dl)
    if plain:
        parts.append(f"<div class=\"desc\">{e(' '.join(plain).strip())}</div>")
    if params:
        parts.append('<div class="tag">Parameters</div><ul>')
        for pr in params:
            bits = pr.split(None, 1)
            if len(bits) == 2:
                parts.append(f"<li><code>{e(bits[0])}</code> — {e(bits[1])}</li>")
            else:
                parts.append(f"<li><code>{e(pr)}</code></li>")
        parts.append('</ul>')
    if returns:
        parts.append(f"<div class=\"tag\">Returns</div><div class=\"desc\">{e(' '.join(returns))}</div>")
    if example:
        parts.append('<div class="tag">Example</div><pre>' + e('\n'.join(example)) + '</pre>')
    parts.append('</div>')
    return '\n'.join(parts)


def generate_docs_html(fk_file):
    """Parse a .fk file and return a styled single-page HTML string (v1.19)."""
    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()
    entries = _extract_docs(source, fk_file)
    module_name = os.path.splitext(os.path.basename(fk_file))[0]
    if not entries:
        body = "<p>No doc-comments found. Add <code>## Description</code> above your <code>def</code> or <code>record</code> definitions.</p>"
    else:
        chunks = []
        records = [x for x in entries if x['kind'] == 'record']
        defs = [x for x in entries if x['kind'] == 'def']
        if records:
            chunks.append('<h2>Record Types</h2>')
            chunks += [_render_entry_html(x, fk_file) for x in records]
        if defs:
            chunks.append('<h2>Functions</h2>')
            chunks += [_render_entry_html(x, fk_file) for x in defs]
        body = '\n'.join(chunks)
    return _HTML_TEMPLATE.format(title=module_name, body=body)


def docs_file_html(fk_file, output=None):
    """Generate HTML docs for one file (v1.19)."""
    if not os.path.exists(fk_file):
        print(f"[docs] File not found: {fk_file}", file=sys.stderr)
        return False
    html = generate_docs_html(fk_file)
    if output is None:
        output = os.path.splitext(os.path.basename(fk_file))[0] + '_docs.html'
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[docs] ✓  {fk_file} → {output}")
    return True
