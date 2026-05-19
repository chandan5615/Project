#!/usr/bin/env python3
import re

with open('dashboard/web_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Emoji replacement map
replacements = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    'ℹ️': '[INFO]',
    'ℹ': '[INFO]',
    '🔄': '',
    '📥': '',
    '💾': '',
    '🔍': '',
    '📊': '',
    '📈': '',
    '🔐': '',
    '👤': '',
    '🚪': '',
    '💡': '',
    '⚙️': '',
    '⚙': '',
    '🟢': 'SECURE',
    '🟡': 'CAUTION',
    '🔴': 'CRITICAL',
    '🛡️': '',
    '🛡': '',
}

# Apply replacements
for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

# Remove st.balloons() call
content = re.sub(r'\s*st\.balloons\(\)\s*', '', content)

# Clean up spaces around brackets and tags
content = re.sub(r'\[\s+\]', '', content)  # Remove empty brackets with spaces
content = re.sub(r' +', ' ', content)  # Replace multiple spaces with single

# Write back
with open('dashboard/web_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ All emojis removed and text equivalents applied')
print('✓ st.balloons() calls removed')
