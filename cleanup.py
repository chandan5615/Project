import re
with open('dashboard/web_dashboard.py', 'r', encoding='utf-8') as f:
    s = f.read()
replacements = {'✅':'[OK]','❌':'[ERROR]','⚠':'[WARNING]','ℹ':'[INFO]','🔄':'','📥':'','💾':'','🔍':'','📊':'','📈':'','🔐':'','👤':'','🚪':'','💡':'','⚙':'','🟢':'SECURE','🟡':'CAUTION','🔴':'CRITICAL','🛡':''}
for k, v in replacements.items():
    s = s.replace(k, v)
s = re.sub(r'st\.balloons\(\)', '', s)
s = re.sub(r'  +', ' ', s)
with open('dashboard/web_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(s)
print('Cleanup complete')
