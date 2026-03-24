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
