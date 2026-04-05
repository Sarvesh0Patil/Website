"""
add_resource.py
---------------
Drop a .txt file in the resources/ folder, run this script,
and a new block is prepended to the Resources page in index.html.

TXT file format (use resources/template.txt as a starting point):
    title:       Resource title
    description: Description text (can span multiple lines)
    link:        https://...
    comment:     Extra note shown in the grey box (optional)
    date:        e.g. "2026-04-05 · Chemistry · JEE Advanced"

Processed files are moved to resources/processed/ automatically.
"""

import os
import re
import shutil

ROOT_DIR      = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources')
PROCESSED_DIR = os.path.join(RESOURCES_DIR, 'processed')
HTML_FILE     = os.path.join(ROOT_DIR, 'resources.html')
INSERT_MARKER = '<!-- Resource blocks -->'


def parse_txt(filepath):
    """Parse a resource .txt file into a dict of fields."""
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


def build_html_block(fields):
    """Build the HTML block string matching the existing resource card style."""
    title       = fields.get('title', 'Untitled').strip()
    description = fields.get('description', '').strip()
    link        = fields.get('link', '').strip()
    comment     = fields.get('comment', '').strip()
    date        = fields.get('date', '').strip()

    # Description: each non-empty line becomes its own paragraph
    desc_html = ''
    for para in description.splitlines():
        para = para.strip()
        if para:
            desc_html += (
                f'\n        <p style="font-size:.92rem;color:var(--ink2);'
                f'line-height:1.7;margin:0 0 .75rem;">{para}</p>'
            )

    # Comment box (only if provided)
    comment_html = ''
    if comment:
        comment_html = (
            f'\n        <div style="background:var(--bg);border:1px solid var(--border);'
            f'border-radius:10px;padding:.85rem 1rem;">'
            f'\n          <p style="font-size:.82rem;color:var(--ink3);margin:0;">{comment}</p>'
            f'\n        </div>'
        )

    # Link button (only if provided)
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


def process_all():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    txt_files = sorted([
        f for f in os.listdir(RESOURCES_DIR)
        if f.endswith('.txt') and f != 'template.txt'
    ])

    if not txt_files:
        print("No new .txt files found in resources/  (template.txt is skipped).")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    if INSERT_MARKER not in html:
        print(f"ERROR: Could not find '{INSERT_MARKER}' in index.html.")
        print("Make sure the marker exists right above the first resource block.")
        return

    added = []
    for filename in txt_files:
        filepath = os.path.join(RESOURCES_DIR, filename)
        fields = parse_txt(filepath)
        block  = build_html_block(fields)

        # Insert the new block immediately after the marker
        html = html.replace(INSERT_MARKER, INSERT_MARKER + block, 1)
        added.append((filepath, fields.get('title', filename)))
        print(f"  + Added: {fields.get('title', filename)}")

    # Write updated HTML
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    # Move processed files
    for filepath, title in added:
        dest = os.path.join(PROCESSED_DIR, os.path.basename(filepath))
        shutil.move(filepath, dest)

    print(f"\nDone! {len(added)} resource(s) added to index.html.")
    print("Now git add, commit, and push when you're ready.")


if __name__ == '__main__':
    process_all()
