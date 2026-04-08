"""
add_resource.py
---------------
Two ways to add a resource card to resources.html:

1. TXT file  — drop a .txt file in resources/, run this script.
   The file is moved to resources/processed/ after being added.

2. HTML file — drop a .html resource page in resources/, add a metadata
   comment block at the top (see resources/resource_template.html), run
   this script. The HTML file stays in place (it is served by the site);
   only its filename is recorded in resources/processed/html_added.txt.

TXT format (see resources/template.txt):
    title:       Resource title
    description: Description text (can span multiple lines)
    link:        https://...
    comment:     Extra note shown in the grey box (optional)
    date:        e.g. "2026-04-05 · Chemistry · JEE Advanced"

HTML metadata block (must appear near the top of the .html file):
    <!--resource
    title: Resource Title
    description: First paragraph.
    Continuation of description.
    date: 2026-04-08 · Subject · Category
    comment: Optional footnote note
    -->
"""

import os
import re
import shutil

ROOT_DIR       = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR  = os.path.join(ROOT_DIR, 'resources')
PROCESSED_DIR  = os.path.join(RESOURCES_DIR, 'processed')
HTML_ADDED_LOG = os.path.join(PROCESSED_DIR, 'html_added.txt')
HTML_FILE      = os.path.join(ROOT_DIR, 'resources.html')
INSERT_MARKER  = '<!-- Resource blocks -->'
SITE_BASE      = 'https://www.sarveshpatil.in'

# ── TXT helpers ──────────────────────────────────────────────────────────────

def parse_txt(filepath):
    fields = {'title': '', 'description': '', 'link': '', 'comment': '', 'date': ''}
    current_key = None
    current_lines = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            m = re.match(r'^(title|description|link|comment|date)\s*:\s*(.*)', line, re.IGNORECASE)
            if m:
                if current_key is not None:
                    fields[current_key] = '\n'.join(current_lines).strip()
                current_key = m.group(1).lower()
                current_lines = [m.group(2)]
            elif current_key is not None:
                current_lines.append(line)

    if current_key is not None:
        fields[current_key] = '\n'.join(current_lines).strip()

    return fields


# ── HTML helpers ─────────────────────────────────────────────────────────────

def parse_html_metadata(filepath):
    """Extract fields from a <!--resource ... --> comment near the top."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(4096)  # only read the first 4 KB

    m = re.search(r'<!--resource\s*\n(.*?)-->', content, re.DOTALL | re.IGNORECASE)
    if not m:
        return None

    block = m.group(1)
    fields = {'title': '', 'description': '', 'comment': '', 'date': ''}
    current_key = None
    current_lines = []

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        km = re.match(r'^(title|description|comment|date)\s*:\s*(.*)', line, re.IGNORECASE)
        if km:
            if current_key is not None:
                fields[current_key] = '\n'.join(current_lines).strip()
            current_key = km.group(1).lower()
            current_lines = [km.group(2)]
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        fields[current_key] = '\n'.join(current_lines).strip()

    return fields


def load_html_added():
    if not os.path.exists(HTML_ADDED_LOG):
        return set()
    with open(HTML_ADDED_LOG, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}


def record_html_added(filename):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(HTML_ADDED_LOG, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')


# ── HTML block builder ───────────────────────────────────────────────────────

def build_html_block(fields, link):
    title       = fields.get('title', 'Untitled').strip()
    description = fields.get('description', '').strip()
    comment     = fields.get('comment', '').strip()
    date        = fields.get('date', '').strip()

    desc_html = ''
    for para in description.splitlines():
        para = para.strip()
        if para:
            desc_html += (
                f'\n        <p style="font-size:.92rem;color:var(--ink2);'
                f'line-height:1.7;margin:0 0 .75rem;">{para}</p>'
            )

    comment_html = ''
    if comment:
        comment_html = (
            f'\n        <div style="background:var(--bg);border:1px solid var(--border);'
            f'border-radius:10px;padding:.85rem 1rem;">'
            f'\n          <p style="font-size:.82rem;color:var(--ink3);margin:0;">{comment}</p>'
            f'\n        </div>'
        )

    link_html = ''
    if link:
        link_html = (
            f'<a href="{link}" target="_blank" rel="noopener noreferrer" '
            f'style="display:inline-flex;align-items:center;gap:.4rem;background:var(--gold);'
            f'color:#000;font-size:.78rem;font-weight:700;padding:.45rem 1rem;border-radius:8px;'
            f'text-decoration:none;white-space:nowrap;flex-shrink:0;">Open resource ↗</a>'
        )

    block = f"""
      <!-- {title} -->
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:2rem;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;">
          <div>
            <p style="font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);font-weight:600;margin-bottom:.5rem;">{date}</p>
            <h3 style="font-size:1.2rem;font-weight:700;color:var(--ink);margin:0 0 1rem;">{title}</h3>
          </div>
          {link_html}
        </div>{desc_html}{comment_html}
      </div>
"""
    return block


# ── Main ─────────────────────────────────────────────────────────────────────

def process_all():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    if INSERT_MARKER not in html:
        print(f"ERROR: Could not find '{INSERT_MARKER}' in resources.html.")
        return

    added = []

    # ── 1. TXT files ──────────────────────────────────────────────────────────
    txt_files = sorted([
        f for f in os.listdir(RESOURCES_DIR)
        if f.endswith('.txt') and f != 'template.txt'
    ])

    for filename in txt_files:
        filepath = os.path.join(RESOURCES_DIR, filename)
        fields   = parse_txt(filepath)
        link     = fields.get('link', '').strip()
        block    = build_html_block(fields, link)
        html     = html.replace(INSERT_MARKER, INSERT_MARKER + block, 1)
        added.append(('txt', filepath, fields.get('title', filename)))
        print(f"  + Added (txt): {fields.get('title', filename)}")

    # ── 2. HTML resource files ────────────────────────────────────────────────
    already_added = load_html_added()
    skip = {'resource_template.html'}

    html_files = sorted([
        f for f in os.listdir(RESOURCES_DIR)
        if f.endswith('.html') and f not in skip and f not in already_added
    ])

    for filename in html_files:
        filepath = os.path.join(RESOURCES_DIR, filename)
        fields   = parse_html_metadata(filepath)
        if fields is None:
            print(f"  ! Skipping {filename}: no <!--resource --> block found.")
            continue
        link  = f"{SITE_BASE}/resources/{filename}"
        block = build_html_block(fields, link)
        html  = html.replace(INSERT_MARKER, INSERT_MARKER + block, 1)
        added.append(('html', filepath, fields.get('title', filename)))
        record_html_added(filename)
        print(f"  + Added (html): {fields.get('title', filename)}")

    if not added:
        print("No new resources found.")
        return

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    # Move processed TXT files
    for kind, filepath, title in added:
        if kind == 'txt':
            dest = os.path.join(PROCESSED_DIR, os.path.basename(filepath))
            shutil.move(filepath, dest)

    print(f"\nDone! {len(added)} resource(s) added to resources.html.")
    print("Now git add, commit, and push when you're ready.")


if __name__ == '__main__':
    process_all()
