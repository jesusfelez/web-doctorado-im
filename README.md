# Web del Programa de Doctorado en Ingeniería Mecánica (UPM)

Web estática hecha con **Hugo** y con un **panel de edición (Decap CMS)** para que cualquiera pueda actualizar contenidos sin tocar código.

---

## 1. Probarla en tu ordenador (macOS)

### Requisitos (una sola vez)

```bash
brew install hugo          # versión 0.120 o superior
brew install node          # solo si quieres probar el panel de edición
```

### Ver la web

```bash
cd web-doctorado
hugo server
```

Abre **http://localhost:1313/**. Cada vez que guardes un archivo, la página se recarga sola.

> En modo local verás unos **recuadros rojos «REVISAR»** con los datos pendientes de confirmar.
> **No aparecen en la web publicada**: sirven como lista de tareas.

### Probar el panel de edición

Abre **dos terminales** en la carpeta `web-doctorado`:

```bash
# Terminal 1
npx decap-server

# Terminal 2
hugo server
```

Abre **http://localhost:1313/admin/** y entra con «Login» (en local no pide contraseña).
Los cambios que guardes en el panel se escriben directamente en los archivos de la carpeta.

---

## 2. Tareas habituales

| Quiero… | Panel (/admin) | O editando el archivo |
|---|---|---|
| **Dar de alta o de baja a un investigador** | Datos del programa → Investigadores | `data/investigadores.yaml` |
| Añadir una tesis defendida | Datos del programa → Tesis defendidas | `data/tesis.yaml` |
| Cambiar la composición de la CAPD | Datos del programa → Comisión Académica | `data/comisiones.yaml` |
| Añadir centros de estancias | Datos del programa → Centros de estancias | `data/estancias.yaml` |
| Añadir enlaces a Portal Científico y ORCID | Datos del programa → Investigadores | `data/investigadores.yaml` (campos `perfil` y `orcid`) |
| Publicar una noticia | Noticias (castellano) y Noticias (inglés), con el mismo «Identificador común» | `content/noticias/AAAA-MM-DD-titulo.es.md` y `.en.md` |
| Cambiar cifras, aviso o botones de la portada | Datos del programa → Portada | `data/portada.yaml` |
| Editar el texto de una página | Páginas (castellano) / Páginas (inglés) | `content/…/*.es.md` y `*.en.md` |
| Añadir o quitar enlaces útiles | Datos del programa → Enlaces útiles | `data/enlaces.yaml` |
| Cambiar el menú | — | `hugo.toml` (bloques `[[languages.es.menus.main]]` y `[[languages.en.menus.main]]`) |
| Cambiar textos fijos del diseño (botones, cabeceras de tablas…) | — | `i18n/es.yaml` e `i18n/en.yaml` |
| Cambiar colores o logotipos | — | `static/css/main.css` (variables `:root`) y `static/img/logo-upm.png`, `logo-etsii.png` |

### Cajas de normativa en las páginas

Las páginas distinguen visualmente dos tipos de información:

```markdown
{{< general fuente="RD 99/2011, art. 3" enlace="https://www.boe.es/..." >}}
Texto de la normativa general (Real Decreto / UPM).
{{< /general >}}

{{< programa >}}
Requisito específico de nuestro programa.
{{< /programa >}}

{{< clave >}}Mensaje clave destacado.{{< /clave >}}

{{< revisar >}}Nota interna: solo se ve en local.{{< /revisar >}}
```

---

## 3. Publicar en el servidor

```bash
hugo --minify
```

Se genera la carpeta **`public/`**, que contiene la web completa en HTML. Basta con copiar su contenido al servidor web (por ejemplo, a la carpeta de `dimec.etsii.upm.es/doctorado/`). Las rutas son relativas, así que funciona tanto en la raíz como en una subcarpeta.

### Panel de edición en producción

El panel guarda los cambios en un repositorio **Git**. Opciones:

1. **GitLab de la UPM o GitHub, con despliegue automático (recomendada).** El código vive en un repositorio, y cada cambio hecho en `/admin` crea un *commit* que reconstruye y publica la web automáticamente (GitLab CI, GitHub Actions o Netlify). En `static/admin/config.yml`, cambia `backend` por `name: gitlab` o `name: github` e indica el repositorio.
2. **Sin panel en el servidor.** Los editores modifican los archivos `.yaml` y `.md` (o usan el panel en local), ejecutan `hugo --minify` y suben `public/` por SFTP.

Conviene concretarlo con el servicio de informática de la ETSII.

---

## 3 bis. Web en dos idiomas (castellano e inglés)

- El castellano está en la raíz (`/`) y el inglés en `/en/`. El selector **ES | EN** de la barra superior lleva a la misma página en el otro idioma.
- Cada página tiene dos archivos: `pagina.es.md` y `pagina.en.md`. Si cambias una, actualiza también la otra. En la versión inglesa, los enlaces internos empiezan por `/en/`.
- **Investigadores y tesis defendidas son comunes** a los dos idiomas: se editan una sola vez.
- Portada, líneas, Comisión Académica, centros de estancias y enlaces útiles tienen versión inglesa (`data/*_en.yaml`, en el panel «… (inglés)»). Si falta un archivo `_en`, la web inglesa usa el castellano.

## 4. Estructura

```
web-doctorado/
├── hugo.toml              Configuración y menú
├── content/               Textos de las páginas (Markdown): *.es.md y *.en.md
│   ├── programa/          Presentación, líneas, investigadores, internacionalización
│   ├── admision/          Requisitos, perfiles, criterios, matrícula
│   ├── doctorandos/       Permanencia, seguimiento, formación, movilidad, industrial, ayudas
│   ├── tesis/             Dirección, requisitos, depósito, mención, defendidas, normativa
│   ├── calidad/           Comisiones, SGIC, resultados
│   ├── noticias/
│   └── contacto.md
├── data/                  Listados editables (investigadores, tesis, comisiones…); *_en.yaml = inglés
├── i18n/                  Textos fijos del diseño en cada idioma
├── layouts/               Plantillas HTML (diseño)
└── static/                CSS, JS, imágenes y panel /admin
```

## 5. Fuentes de los contenidos

- Real Decreto 99/2011, texto consolidado tras el RD 576/2023 (BOE-A-2011-2541).
- Memoria de verificación original del programa.
- Memoria modificada (julio de 2026) e informe final **favorable** de la Fundación Madri+d (7/09/2026).
- Normativa de doctorado de la UPM: https://www.upm.es/Estudiantes/Estudios_Titulaciones/Estudios_Doctorado/normativa
- Web anterior del programa (listados de profesorado, tesis y CAPD).
