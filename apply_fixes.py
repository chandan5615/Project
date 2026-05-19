#!/usr/bin/env python3
"""Comprehensive fix script for dashboard"""
import re

with open('dashboard/web_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============= FIX 1: Add import time at the top =============
if 'import time' not in content:
    content = content.replace(
        'from pathlib import Path\n\n# Add parent',
        'from pathlib import Path\nimport time\n\n# Add parent'
    )

# ============= FIX 2: Update get_blocked_ips() query =============
old_query = '''query = """
                SELECT 
                    source_ip,
                    threat_type,
                    COUNT(*) as block_count,
                    MAX(timestamp) as last_seen,
                    action
                FROM incidents
                GROUP BY source_ip, threat_type
                ORDER BY block_count DESC, last_seen DESC
                LIMIT ?
            """'''

new_query = '''query = """
                SELECT 
                    source_ip,
                    GROUP_CONCAT(DISTINCT threat_type) as threat_types,
                    COUNT(*) as total_incidents,
                    MAX(timestamp) as last_seen,
                    MAX(action) as last_action
                FROM incidents
                GROUP BY source_ip
                ORDER BY total_incidents DESC, last_seen DESC
                LIMIT ?
            """'''

content = content.replace(old_query, new_query)

# ============= FIX 2b: Update render_wall_of_shame() column rename =============
old_rename = '''display_df = display_df.rename(columns={
            'source_ip': 'IP Address',
            'threat_type': 'Threat Type',
            'block_count': 'Block Count',
            'last_seen': 'Last Seen',
            'action': 'Action'
        })'''

new_rename = '''display_df = display_df.rename(columns={
            'source_ip': 'IP Address',
            'threat_types': 'Threat Types',
            'total_incidents': 'Total Incidents',
            'last_seen': 'Last Seen',
            'last_action': 'Last Action'
        })'''

content = content.replace(old_rename, new_rename)

# ============= FIX 2c: Add deduplication to IP blocking list =============
old_block_display = '''    if blocked_ips:
        blocked_df = pd.DataFrame(blocked_ips)
        st.dataframe(blocked_df, hide_index=True, use_container_width=True)'''

new_block_display = '''    if blocked_ips:
        blocked_df = pd.DataFrame(blocked_ips)
        # Deduplicate — keep only first occurrence of each IP
        if 'ip' in blocked_df.columns:
            blocked_df = blocked_df.drop_duplicates(subset=['ip'], keep='first')
        st.dataframe(blocked_df, hide_index=True, use_container_width=True)'''

content = content.replace(old_block_display, new_block_display)

# ============= FIX 1: Update auto-refresh logic =============
old_refresh = '''    # Auto-refresh logic
    st.markdown(f"*Dashboard auto-refreshes every {refresh_interval} seconds*")'''

new_refresh = '''    # Auto-refresh logic
    st.markdown(f"*Dashboard auto-refreshes every {refresh_interval} seconds*")
    
    # Store last refresh time
    if st.session_state.get("last_refresh") is None:
        st.session_state.last_refresh = time.time()
    
    # Check if it's time to refresh
    elapsed = time.time() - st.session_state.last_refresh
    if elapsed >= refresh_interval:
        st.session_state.last_refresh = time.time()
        st.rerun()
    else:
        # Show countdown
        remaining = int(refresh_interval - elapsed)
        st.caption(f"Next refresh in {remaining}s")
        time.sleep(1)
        st.rerun()'''

content = content.replace(old_refresh, new_refresh)

# ============= FIX 3: Remove all emojis =============
emoji_map = {
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
    '❓': '[Help]',
}

for emoji, replacement in emoji_map.items():
    content = content.replace(emoji, replacement)

# Remove variation selectors
content = re.sub(r'[\uFE0F\u200B\u200D]', '', content)

# Remove st.balloons() calls
content = re.sub(r'\s*st\.balloons\(\)\s*', ' ', content)

# Clean up multiple spaces but preserve indentation
lines = content.split('\n')
cleaned = []
for line in lines:
    # Clean up trailing spaces
    line = line.rstrip()
    # Only clean multiple spaces if not at beginning of line (preserve indentation)
    stripped = line.lstrip()
    indent = line[:len(line) - len(stripped)]
    if stripped:
        stripped = re.sub(r'  +', ' ', stripped)
    cleaned.append(indent + stripped)

content = '\n'.join(cleaned)

# ============= FIX 4: Add export state to session_defaults =============
old_defaults = '''    session_defaults = {
        "authenticated": False,
        "username": None,
        "auth_token": None,
        "auth_initialized": False,
        "authenticator": None,
        "db_path": DEFAULT_DB_PATH,
        "apache_stats": None,
        "blocked_ips": [],
        "last_refresh": None,
        "selected_tab": "overview"
    }'''

new_defaults = '''    session_defaults = {
        "authenticated": False,
        "username": None,
        "auth_token": None,
        "auth_initialized": False,
        "authenticator": None,
        "db_path": DEFAULT_DB_PATH,
        "apache_stats": None,
        "blocked_ips": [],
        "last_refresh": None,
        "selected_tab": "overview",
        "export_csv": None,
        "export_csv_name": None,
        "export_csv_count": 0,
        "export_json": None,
        "export_json_name": None,
        "export_json_count": 0
    }'''

content = content.replace(old_defaults, new_defaults)

with open('dashboard/web_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] All fixes applied successfully')
