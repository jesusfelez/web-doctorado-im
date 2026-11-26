#!/usr/bin/env python3
"""Listados de la web <-> Excel.

  python3 scripts/datos_excel.py importar   Excel  -> data/*.yaml   (lo ejecuta GitHub Actions al publicar)
  python3 scripts/datos_excel.py exportar   data/*.yaml -> Excel     (para regenerar el Excel desde la web)

El Excel es excel/Datos_web_doctorado_IM.xlsx. Hojas: Investigadores, Tesis, Cursos, Estancias.
Necesita: pip install openpyxl pyyaml
"""
import sys, json, unicodedata, os
import openpyxl, yaml
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(RAIZ, 'excel', 'Datos_web_doctorado_IM.xlsx')
D = lambda n: os.path.join(RAIZ, 'data', n)

LINEAS = ['1 · Mecánica computacional e ingeniería sísmica', '2 · Ingeniería acústica', '3 · Ingeniería de fabricación',
          '4 · Ingeniería de vehículos y transportes', '5 · Ingeniería de máquinas y desarrollo de productos',
          '6 · Ingeniería y aplicaciones del láser']
MENCIONES = ['', 'Internacional', 'Industrial', 'Internacional e Industrial']
HOJAS = {
    'Investigadores': ['Nombre', 'Apellidos', 'Grupo (UPM / Otras instituciones)', 'Institución', 'Línea 1', 'Línea 2',
                       'Portal Científico (URL)', 'ORCID (URL)'],
    'Tesis': ['Año de defensa', 'Doctorando/a (Apellidos, Nombre)', 'Título', 'Dirección', 'Mención', 'Enlace Archivo Digital UPM'],
    'Cursos': ['Actividades (p. ej. 1 o 1, 3)', 'Curso o seminario', 'Organiza / plataforma', 'Horas (castellano)', 'Horas (inglés)',
               '¿Cubre 1 ECTS por sí solo? (Sí/No)', 'Enlace'],
    'Estancias': ['País (castellano)', 'País (inglés)', 'Centro (castellano)', 'Centro (inglés)'],
}

def q(v):
    return json.dumps('' if v is None else str(v).strip(), ensure_ascii=False)

def clave(apellidos):
    s = unicodedata.normalize('NFD', apellidos).encode('ascii', 'ignore').decode().lower()
    for p in ('de la ', 'del ', 'de '):
        if s.startswith(p): s = s[len(p):]; break
    return s

def filas(ws):
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r and any(c not in (None, '') for c in r):
            yield [('' if c is None else c) for c in r]

def num_linea(v):
    v = str(v).strip()
    return int(v.split('·')[0].strip()) if v else None

# ---------------------------------------------------------------- importar
def importar():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    # Investigadores
    inv = []
    for r in filas(wb['Investigadores']):
        nombre, apellidos, grupo, inst, l1, l2, perfil, orcid = (list(r) + [''] * 8)[:8]
        if not apellidos: continue
        ls = [n for n in (num_linea(l1), num_linea(l2)) if n]
        inv.append((clave(apellidos), f'  - nombre: {q(nombre)}\n    apellidos: {q(apellidos)}\n'
                    f'    grupo: {q("nucleo" if str(grupo).startswith("UPM") else "colab")}\n    afiliacion: {q(inst or "UPM")}\n'
                    f'    lineas: {json.dumps(ls)}\n    perfil: {q(perfil)}\n    orcid: {q(orcid)}\n'))
    inv.sort(key=lambda x: x[0])
    open(D('investigadores.yaml'), 'w').write(
        '# GENERADO AUTOMÁTICAMENTE desde excel/Datos_web_doctorado_IM.xlsx (hoja Investigadores). No editar aquí.\n'
        'investigadores:\n' + ''.join(b for _, b in inv))
    # Tesis
    tes = []
    for r in filas(wb['Tesis']):
        anio, autor, titulo, dire, men, enl = (list(r) + [''] * 6)[:6]
        if not autor: continue
        tes.append(f'  - anio: {int(anio)}\n    autor: {q(autor)}\n    titulo: {q(titulo)}\n    direccion: {q(dire)}\n'
                   f'    mencion: {q(men)}\n    enlace: {q(enl)}\n')
    open(D('tesis.yaml'), 'w').write('# GENERADO AUTOMÁTICAMENTE desde excel/Datos_web_doctorado_IM.xlsx (hoja Tesis). No editar aquí.\n'
                                     'tesis:\n' + ''.join(tes))
    # Cursos
    cur = []
    for r in filas(wb['Cursos']):
        act, nom, org, h, hen, comp, url = (list(r) + [''] * 7)[:7]
        if not nom: continue
        acts = [int(x) for x in str(act).replace(';', ',').split(',') if str(x).strip()]
        completa = 'true' if str(comp).strip().lower() in ('sí', 'si', 'yes', 'true', '1') else 'false'
        cur.append(f'  - {{actividad: {json.dumps(acts)}, nombre: {q(nom)}, organiza: {q(org)}, horas: {q(h)}, '
                   f'horas_en: {q(hen or h)}, completa: {completa}, url: {q(url)}}}\n')
    open(D('cursos.yaml'), 'w').write('# GENERADO AUTOMÁTICAMENTE desde excel/Datos_web_doctorado_IM.xlsx (hoja Cursos). No editar aquí.\n'
                                      'cursos:\n' + ''.join(cur))
    # Estancias (castellano e inglés, agrupadas por país y ordenadas alfabéticamente)
    es, en = {}, {}
    for r in filas(wb['Estancias']):
        pes, pen, ces, cen = (list(r) + [''] * 4)[:4]
        if not ces: continue
        es.setdefault(str(pes).strip(), []).append(str(ces).strip())
        en.setdefault(str(pen or pes).strip(), []).append(str(cen or ces).strip())
    for nombre, dic in (('estancias.yaml', es), ('estancias_en.yaml', en)):
        txt = '# GENERADO AUTOMÁTICAMENTE desde excel/Datos_web_doctorado_IM.xlsx (hoja Estancias). No editar aquí.\npaises:\n'
        for p in sorted(dic, key=clave):
            txt += f'  - pais: {q(p)}\n    centros: [{", ".join(q(c) for c in dic[p])}]\n'
        open(D(nombre), 'w').write(txt)
    print(f'Importado: {len(inv)} investigadores, {len(tes)} tesis, {len(cur)} cursos, '
          f'{sum(map(len, es.values()))} centros de estancia')

# ---------------------------------------------------------------- exportar
def exportar():
    Y = lambda n: yaml.safe_load(open(D(n)))
    inv, tes, cur = Y('investigadores.yaml')['investigadores'], Y('tesis.yaml')['tesis'], Y('cursos.yaml')['cursos']
    pes, pen = Y('estancias.yaml')['paises'], Y('estancias_en.yaml')['paises']
    PAIS_EN = {'Alemania': 'Germany', 'Austria': 'Austria', 'Corea del Sur': 'South Korea', 'Estados Unidos': 'United States',
               'Francia': 'France', 'Irlanda': 'Ireland', 'Italia': 'Italy', 'Japón': 'Japan', 'Noruega': 'Norway',
               'Países Bajos': 'Netherlands', 'Portugal': 'Portugal', 'Reino Unido': 'United Kingdom'}
    en_por_pais = {p['pais']: p['centros'] for p in pen}
    datos = {
        'Investigadores': [[x['nombre'], x['apellidos'], 'UPM' if x['grupo'] == 'nucleo' else 'Otras instituciones',
                            x.get('afiliacion', ''), *([LINEAS[n - 1] for n in x['lineas']] + ['', ''])[:2],
                            x.get('perfil', ''), x.get('orcid', '')] for x in inv],
        'Tesis': [[t['anio'], t['autor'], t['titulo'], t['direccion'], t['mencion'], t['enlace']] for t in tes],
        'Cursos': [[', '.join(map(str, c['actividad'])), c['nombre'], c['organiza'], c['horas'], c['horas_en'],
                    'Sí' if c['completa'] else 'No', c['url']] for c in cur],
        'Estancias': [[p['pais'], PAIS_EN.get(p['pais'], p['pais']), c,
                       (en_por_pais.get(PAIS_EN.get(p['pais'], p['pais']), []) + [''] * 20)[i] or c]
                      for p in pes for i, c in enumerate(p['centros'])],
    }
    A, AB = Font(name='Arial', size=10), Font(name='Arial', size=10, bold=True, color='FFFFFF')
    az, ama = PatternFill('solid', fgColor='00467F'), PatternFill('solid', fgColor='FFF2CC')
    th = Side(style='thin', color='B7C3D0'); bd = Border(left=th, right=th, top=th, bottom=th)
    anchos = {'Investigadores': [18, 26, 20, 22, 42, 42, 52, 40], 'Tesis': [10, 34, 70, 40, 24, 50],
              'Cursos': [14, 60, 22, 18, 18, 16, 60], 'Estancias': [18, 18, 55, 55]}
    wb = openpyxl.Workbook()
    le = wb.active; le.title = 'Léeme'
    texto = [
        ('DATOS DE LA WEB · Programa de Doctorado en Ingeniería Mecánica (UPM)', Font(name='Arial', size=13, bold=True, color='00467F')),
        ('Este Excel es la fuente de cuatro listados de la web. Al subirlo a GitHub, la web se actualiza sola en 1-2 minutos.', A),
        ('', A),
        ('Hojas', Font(name='Arial', size=11, bold=True)),
        ('· Investigadores: altas, bajas, líneas, enlaces a Portal Científico y ORCID. Se ordenan solos por apellido.', A),
        ('· Tesis: tesis defendidas. La web las ordena por año, de la más reciente a la más antigua.', A),
        ('· Cursos: cursos recomendados para las actividades formativas (1, 2, 3 y 5).', A),
        ('· Estancias: centros extranjeros donde han hecho estancias los doctorandos, por país.', A),
        ('', A),
        ('Reglas', Font(name='Arial', size=11, bold=True)),
        ('· Una fila por elemento. No cambies los encabezados ni el nombre de las hojas.', A),
        ('· Para dar de baja, borra la fila entera (clic derecho en el número de fila > Eliminar).', A),
        ('· Usa los desplegables donde los hay (grupo, líneas, mención, Sí/No).', A),
        ('· Las URL deben empezar por https://', A),
        ('· El archivo debe llamarse siempre Datos_web_doctorado_IM.xlsx.', A),
    ]
    for i, (t, f) in enumerate(texto, 1):
        le.cell(i, 1, t).font = f
    le.column_dimensions['A'].width = 120
    for hoja, cab in HOJAS.items():
        ws = wb.create_sheet(hoja)
        for j, h in enumerate(cab, 1):
            c = ws.cell(1, j, h); c.font = AB; c.fill = az; c.border = bd
            c.alignment = Alignment(wrap_text=True, vertical='center')
        ws.row_dimensions[1].height = 30
        for i, fila in enumerate(datos[hoja], 2):
            for j, v in enumerate(fila, 1):
                c = ws.cell(i, j, v); c.font = A; c.border = bd
                c.alignment = Alignment(wrap_text=j in (3,) and hoja == 'Tesis', vertical='top')
        for j, w in enumerate(anchos[hoja], 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = 'A2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(cab))}{max(2, len(datos[hoja]) + 1)}'
    lst = wb.create_sheet('Listas'); lst.sheet_state = 'hidden'
    for i, v in enumerate(LINEAS, 1): lst.cell(i, 1, v)
    for i, v in enumerate(MENCIONES[1:], 1): lst.cell(i, 2, v)
    def dv(ws, f, rango):
        v = DataValidation(type='list', formula1=f, allow_blank=True); ws.add_data_validation(v); v.add(rango)
    dv(wb['Investigadores'], '"UPM,Otras instituciones"', 'C2:C1000')
    dv(wb['Investigadores'], f'Listas!$A$1:$A${len(LINEAS)}', 'E2:F1000')
    dv(wb['Tesis'], f'Listas!$B$1:$B${len(MENCIONES) - 1}', 'E2:E1000')
    dv(wb['Cursos'], '"Sí,No"', 'F2:F1000')
    wb.save(XLSX)
    print('Exportado a', XLSX)

if __name__ == '__main__':
    {'importar': importar, 'exportar': exportar}[sys.argv[1] if len(sys.argv) > 1 else 'importar']()
