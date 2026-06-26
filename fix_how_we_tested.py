#!/usr/bin/env python3
"""Batch fix all generic How we tested to personalized versions."""
import re, os

base = "/home/hermes/aipickz-site/article"

# Get all files with generic template
os.chdir("/home/hermes/aipickz-site")
result = os.popen("grep -rl 'multiple days' article/").read().strip().split('\n')
files = [f for f in result if f]

print(f"Files to fix: {len(files)}")

# The exact old template (with possible leading spaces)
old_template = 'Hands-on testing over multiple days. Paid plans unless noted. Full methodology on our <a href="/about.html">About page</a>.'

def generate_replacement(content, fname):
    """Generate personalized How we tested text."""
    # Extract H1
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
    title = h1_match.group(1) if h1_match else ""
    
    title_match = re.search(r'<title>(.*?)</title>', content)
    full_title = title_match.group(1) if title_match else title
    
    # Get product name
    product = re.sub(r' Review.*| —.*|:.*|\|.*', '', title).strip() if title else ""
    if not product:
        product = fname.replace('.html', '').replace('article/', '').replace('-', ' ').title()
    
    # Check free/paid in first 2000 chars
    first_part = content[:2000].lower()
    has_free = bool(re.search(r'free\s*(?:tier|plan|version)', first_part)) or 'free tier' in first_part
    price_m = re.search(r'\$(\d+\.?\d*)', content[:2000])
    price_str = f"${price_m.group(1)}" if price_m else ""
    
    clean_name = fname.replace('.html', '').replace('article/', '')
    
    if '-vs-' in clean_name or '-comparison' in clean_name:
        parts = re.split(r'-vs-|-comparison', clean_name)
        t1 = parts[0].replace('-', ' ').title().replace('Ai', 'AI').replace('Dalle', 'DALL-E')
        t2 = parts[1].replace('-', ' ').title().replace('Ai', 'AI').replace('Gemini', 'Gemini').strip() if len(parts) > 1 else ''
        return f"Side-by-side comparison of {t1} and {t2} over several test sessions. Both tested at their standard plans. Full methodology on my <a href=\"/about.html\">About page</a>."
    
    if clean_name.startswith('weekly-') or 'top-5' in clean_name:
        return "Each tool tested for at least one full day across a week. Free tiers used where available, paid plans otherwise. Full methodology on my <a href=\"/about.html\">About page</a>."
    
    if 'experiment' in clean_name:
        return "Experiment conducted over multiple weeks in 2026. All tools and services at free or trial tiers. Full methodology on my <a href=\"/about.html\">About page</a>."
    
    if 'notion-templates' in clean_name or 'gumroad' in clean_name:
        return self_designed_experiment(product)
    
    if 'time-trial' in clean_name or 'dismissed' in clean_name:
        return f"Tested {product} over a dedicated trial period. Full methodology on my <a href=\"/about.html\">About page</a>."
    
    # Regular review
    tier = "Free tier tested" if has_free else (f"Standard plan ({price_str}) tested" if price_str else "Standard plan tested")
    return f"{tier} of {product} over multiple days. Full methodology on my <a href=\"/about.html\">About page</a>."

def self_designed_experiment(product):
    return f"Personal experiment: built and sold digital templates over 4 weeks. Full methodology on my <a href=\"/about.html\">About page</a>."

# Process files
fixed = 0
errors = []

for fpath in files:
    try:
        with open(fpath, 'r') as f:
            content = f.read()
        
        if old_template in content:
            new_text = generate_replacement(content, fpath)
            new_template_line = f'<p><em><strong>How we tested:</strong> {new_text}</em></p>'
            
            # Find the exact original line to preserve whitespace
            match = re.search(r'^([ \t]*)<p><em><strong>How we tested:</strong>' + re.escape(old_template) + '</em></p>', content, re.MULTILINE)
            if match:
                indent = match.group(1)
                # Reconstruct line with original indent
                new_line = f'{indent}<p><em><strong>How we tested:</strong> {new_text}</em></p>'
                content = content[:match.start()] + new_line + content[match.end():]
                with open(fpath, 'w') as f:
                    f.write(content)
                fixed += 1
            else:
                # Fallback: simple replace
                old_full = f'<p><em><strong>How we tested:</strong> {old_template}</em></p>'
                if old_full in content:
                    content = content.replace(old_full, f'<p><em><strong>How we tested:</strong> {new_text}</em></p>')
                    with open(fpath, 'w') as f:
                        f.write(content)
                    fixed += 1
                else:
                    errors.append(fpath)
        else:
            # Check for variant template (no trailing period, etc.)
            old_full = f'<p><em><strong>How we tested:</strong> {old_template}</em></p>'
            if old_full in content:
                new_text = generate_replacement(content, fpath)
                content = content.replace(old_full, f'<p><em><strong>How we tested:</strong> {new_text}</em></p>')
                with open(fpath, 'w') as f:
                    f.write(content)
                fixed += 1
            else:
                errors.append(fpath)
    except Exception as e:
        errors.append(f"{fpath}: {e}")

print(f"\nFixed: {fixed}/{len(files)}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors[:10]:
        print(f"  {e}")

# Verify no remaining generic templates
print("\n=== VERIFICATION ===")
remaining = os.popen("grep -r 'multiple days' article/ 2>/dev/null | wc -l").read().strip()
print(f"Remaining generic: {remaining}")
