from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DOMAIN = 'https://longinosmagano.github.io/Galaxia'
issues = []
warnings = []

html_files = sorted(ROOT.glob('**/index.html'))
html_rel = {'/' + (p.relative_to(ROOT).as_posix().replace('index.html','')).lstrip('./') for p in html_files}
html_rel = {('/' if x == '/' else x) for x in html_rel}

sitemap = ROOT / 'sitemap.xml'
sitemap_locs = []
if sitemap.exists():
    sitemap_locs = re.findall(r'<loc>(.*?)</loc>', sitemap.read_text(encoding='utf-8'))
else:
    issues.append('No existe sitemap.xml')

for path in html_files:
    text = path.read_text(encoding='utf-8', errors='ignore')
    rel_url = '/' + path.relative_to(ROOT).as_posix().replace('index.html','').lstrip('./')
    if rel_url == '/.':
        rel_url = '/'
    if not re.search(r'<title>[^<]{20,70}</title>', text):
        warnings.append(f'Título ausente o longitud atípica: {rel_url}')
    meta = re.search(r"<meta\s+name=['\"]description['\"]\s+content=['\"]([^'\"]+)['\"]", text)
    if not meta or len(meta.group(1)) < 80:
        warnings.append(f'Meta description corta o ausente: {rel_url}')
    fiscal_marker = 'C' + 'IF'
    phone_marker = 'NUEVO_' + 'TELEFONO'
    whatsapp_marker = 'NUEVO_' + 'WHATSAPP'
    if re.search(r'<<[^>]+>>|' + phone_marker + '|' + whatsapp_marker + '|' + fiscal_marker, text):
        issues.append(f'Marcador no permitido visible: {rel_url}')
    visible = re.sub(r'<script[^>]*>.*?</script>|<style[^>]*>.*?</style>', '', text, flags=re.S|re.I)
    if re.search(r'\{[^{}<>]{0,240}\|[^{}<>]{0,240}\}', visible):
        issues.append(f'Spintax visible: {rel_url}')
    for src in re.findall(r'<img[^>]+src=["\']([^"\']+)', text):
        if src.startswith(('http://','https://','data:')):
            continue
        local = (path.parent / src).resolve()
        try:
            local.relative_to(ROOT)
        except ValueError:
            issues.append(f'Ruta de imagen sale del proyecto: {rel_url} -> {src}')
            continue
        if not local.exists():
            issues.append(f'Imagen rota: {rel_url} -> {src}')
    for href in re.findall(r'<a[^>]+href=["\']([^"\']+)', text):
        if href.startswith(('http://','https://','mailto:','tel:','#','javascript:')):
            continue
        if href.startswith('/'):
            target = href.split('#')[0]
        else:
            target_path = (path.parent / href.split('#')[0]).resolve()
            try:
                target = '/' + target_path.relative_to(ROOT).as_posix().rstrip('/') + '/'
                target = target.replace('/index.html/', '/')
            except ValueError:
                issues.append(f'Enlace sale del proyecto: {rel_url} -> {href}')
                continue
        if target and not (ROOT / target.lstrip('/') / 'index.html').exists() and not (ROOT / target.lstrip('/')).exists():
            issues.append(f'Enlace interno roto: {rel_url} -> {href}')

robots = (ROOT / 'robots.txt').read_text(encoding='utf-8') if (ROOT / 'robots.txt').exists() else ''
if 'Sitemap:' not in robots:
    issues.append('robots.txt no declara sitemap')

report = []
report.append('# Auditoría técnica Galaxia\n')
report.append(f'- HTML indexados: {len(html_files)}')
report.append(f'- URLs en sitemap: {len(sitemap_locs)}')
report.append(f'- Coincidencia HTML/sitemap: {len(html_files) == len(sitemap_locs)}')
report.append(f'- Incidencias críticas: {len(issues)}')
report.append(f'- Advertencias SEO: {len(warnings)}')
report.append('\n## Incidencias críticas\n')
report.extend(f'- {i}' for i in issues[:200])
if len(issues) > 200:
    report.append(f'- ... {len(issues)-200} más')
report.append('\n## Advertencias\n')
report.extend(f'- {w}' for w in warnings[:200])
if len(warnings) > 200:
    report.append(f'- ... {len(warnings)-200} más')
(ROOT / 'qa-report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
print('\n'.join(report[:8]))
raise SystemExit(1 if issues else 0)
