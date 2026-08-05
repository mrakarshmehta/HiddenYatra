"""Fix all created_at[:10] patterns in templates for MySQL datetime compatibility."""
import os
import re

template_dir = r"D:\HiddenYatra\templates"
count = 0

for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
            
            new_content = content
            
            # Handle: X.created_at[:10] if X.created_at else '...'
            new_content = re.sub(
                r'(\w+)\.created_at\[:10\]\s+if\s+\1\.created_at\s+else\s+',
                lambda m: m.group(1) + '.created_at.strftime(\'%Y-%m-%d\') if ' + m.group(1) + '.created_at else ',
                new_content
            )
            
            # Handle remaining standalone: X.created_at[:10]
            new_content = re.sub(
                r'(\w+)\.created_at\[:10\]',
                lambda m: m.group(1) + '.created_at.strftime(\'%Y-%m-%d\') if ' + m.group(1) + '.created_at else \'\'',
                new_content
            )
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as fh:
                    fh.write(new_content)
                fixes = content.count('[:10]') - new_content.count('[:10]')
                rel = os.path.relpath(fp, template_dir)
                print(f"  Fixed {fixes} in {rel}")
                count += fixes

print(f"\nTotal: {count} datetime slicing fixes applied")
