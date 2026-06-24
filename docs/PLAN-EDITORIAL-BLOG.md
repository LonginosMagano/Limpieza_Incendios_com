# Plan editorial · Blog Galaxia

Roadmap de contenidos del blog `/blog/` alineado con la keyword principal
**Limpieza de humo y hollín** y el cluster secundario (ver CLAUDE.md §4).

Objetivos:
1. Capturar long-tail informacional ("qué hacer después de un incendio",
   "cómo eliminar olor a humo", "limpiar casa quemada").
2. Reforzar autoridad temática de la landing madre `/servicios/` y de las
   ~611 landings locales mediante interlinking.
3. Dar respuestas útiles a particulares afectados (recordar: aunque
   Galaxia es B2B, gran parte de las búsquedas informacionales son B2C
   y derivan en contacto con aseguradora → siniestro → empresa técnica).

---

## 1. Estado actual

Artículos publicados (5):

| Slug | Keyword principal | Estado |
|---|---|---|
| `hollin-en-naves` | limpieza de hollín | publicado |
| `ozono-industrial` | descontaminación tras incendio | publicado |
| `hepa-h14` | filtración HEPA post-incendio | publicado |
| `hielo-seco` | hielo seco CO₂ superficies carbonizadas | publicado |
| `informe-pericial` | informe técnico post-incendio | publicado |

**Pendiente**: todos los artículos actuales usan la plantilla `simple_page()`
con copy boilerplate. Para que la indexación sea sólida, **cada uno debe
ampliarse a ≥ 1.200 palabras** con estructura H2/H3, FAQ, imágenes y
schema `Article` + `FAQPage` + `HowTo` cuando proceda.

## 2. Calendario propuesto (4 fases × 4 artículos = 16 nuevos)

Una entrega por fase quincenal. Cada fase combina 1 pilar de alta intención
(transaccional/comercial) + 1 informacional + 1 técnico-pericial + 1 local.

### Fase 1 — Pilares de intención comercial (semanas 1-2)

#### 1.1 `que-hacer-despues-de-un-incendio` *(prioritario)*
- **KW principal**: qué hacer después de un incendio
- **KW secundarias**: limpieza después de incendio en casa, limpieza tras
  siniestro, empresa urgente por incendio.
- **Outline**:
  - Las primeras 24 h: seguridad, corte de suministros, no pisar zonas
    afectadas, ventilar con criterio.
  - Avisar a la aseguradora antes que a nada: parte, peritación, lucro.
  - Por qué **no limpiar nada por tu cuenta** (el hollín ácido empeora
    superficies en horas).
  - Llamar a una empresa técnica de limpieza (Galaxia → CTA tel/WhatsApp).
  - Qué documentación pedir: informe técnico para perito.
- **Schemas**: `Article` + `HowTo` (los pasos) + `FAQPage`.
- **Interlink**: `/servicios/`, `/contacto/`, `/peritos/`,
  blog `informe-pericial`, landing local más cercana.

#### 1.2 `eliminar-olor-a-humo-vivienda`
- **KW principal**: eliminar olor a humo.
- **KW secundarias**: quitar humo después de incendio, limpieza después
  de incendio en casa.
- **Outline**:
  - Por qué el olor persiste tras limpiar a fondo (partículas en porosidad).
  - Técnicas eficaces: ozono industrial vs hidroxilo vs encapsulado.
  - Lo que NO funciona (ambientadores, vinagre, bicarbonato superficial).
  - Cuándo es necesario contratar a una empresa técnica.
- **Schemas**: `Article` + `FAQPage`.
- **Interlink**: blog `ozono-industrial`, `/servicios/`, landings de
  hoteles/restaurantes (sectores con olor crítico).

#### 1.3 `limpieza-de-hollin-en-paredes`
- **KW principal**: limpieza de hollín en paredes.
- **KW secundarias**: limpieza de hollín, limpieza de hollín después
  de incendio.
- **Outline**:
  - Composición del hollín y por qué reacciona con yeso/pintura.
  - Técnicas profesionales: aspiración HEPA, esponjas químicas
    (chemical sponge), hielo seco CO₂, encapsulado.
  - Cuándo conviene NO limpiar y dejarlo a la obra posterior.
- **Schemas**: `Article` + `HowTo` + `FAQPage`.
- **Interlink**: blog `hielo-seco`, `hepa-h14`, landing madre.

#### 1.4 `limpieza-de-casa-quemada-pasos`
- **KW principal**: limpieza de casa quemada.
- **KW secundarias**: limpiar casa quemada, limpieza vivienda quemada,
  empresa para casa quemada.
- **Outline**:
  - 7 pasos antes de volver a pisar la vivienda.
  - Protocolo Galaxia para vivienda quemada.
  - Errores típicos del propietario.
- **Schemas**: `Article` + `HowTo` + `FAQPage`.
- **Interlink**: `/casos-de-exito/`, `/contacto/`.

### Fase 2 — Cluster técnico-pericial (semanas 3-4)

#### 2.1 `descontaminacion-tras-incendio`
- KW: descontaminación tras incendio, limpieza post incendio.
- Foco: por qué la limpieza sin filtración HEPA H14 redistribuye
  partículas. Caso técnico.
- Schema: `Article` + `FAQPage`.

#### 2.2 `limpieza-tras-siniestro-aseguradora`
- KW: limpieza tras siniestro, limpieza de siniestros.
- Foco: coordinación con perito, parte, alcance documental, lucro cesante.
- Interlink fuerte con `/peritos/` y `informe-pericial`.

#### 2.3 `rehabilitacion-tras-incendio-fases`
- KW: rehabilitación tras incendio *(uso contextual: la rehabilitación
  posterior la ejecutan empresas de obra; Galaxia hace la limpieza previa)*.
- ⚠️ Atención a no posicionarse como servicio propio (ver CLAUDE.md §3).
- Foco: explicar las fases de un siniestro (limpieza → peritación → obras
  → reapertura) y dónde encaja Galaxia.

#### 2.4 `humo-vs-hollin-diferencia`
- KW: limpieza de humo, limpieza de hollín, limpieza de humo y hollín.
- Foco: pillar artículo educativo que enlaza a toda la familia.

### Fase 3 — Sectorial B2B (semanas 5-6)

#### 3.1 `limpieza-local-post-incendio`
- KW: limpieza local post incendio.
- Foco: reapertura controlada de comercio/restaurante. Tiempos, lucro
  cesante, certificación de habitabilidad.

#### 3.2 `limpieza-vivienda-post-incendio`
- KW: limpieza vivienda post incendio, limpieza tras incendio en vivienda.
- Foco: protocolo en piso/casa unifamiliar; relación con comunidad de vecinos.

#### 3.3 `empresa-urgente-por-incendio`
- KW: empresa urgente por incendio, empresa de limpieza de incendios.
- Foco: qué exigir en las primeras 48 h. Checklist para administradores
  de fincas y peritos.

#### 3.4 `limpieza-incendio-hotel-reapertura`
- KW: limpieza por incendio en vivienda (variante hotelera + cluster
  específico de hoteles).
- Apoya el sector hoteles (uno de los más rentables del B2B).

### Fase 4 — Long-tail informacional (semanas 7-8)

#### 4.1 `cuanto-tarda-limpieza-post-incendio`
- Long-tail "cuánto tarda".
- Tabla orientativa por tamaño/carga contaminante.

#### 4.2 `precio-limpieza-post-incendio-orientativo`
- Long-tail "precio limpieza incendios".
- Tabla orientativa SIN cerrar precios (cada siniestro es una visita técnica).

#### 4.3 `seguro-hogar-cubre-limpieza-incendio`
- KW long-tail "seguro hogar incendio".
- Foco: cómo activar la cobertura, plazos, peritación.

#### 4.4 `como-prevenir-incendios-domesticos`
- Long-tail prevención (atrae tráfico no-siniestro, branding).
- CTA secundaria: "si pese a todo ocurre, llámanos".

---

## 3. Reglas comunes para todos los artículos

### 3.1 Estructura
- H1 = título exacto con KW principal.
- Lead 2-3 frases con KW + propuesta de valor.
- 4-6 H2 con KW secundarias variadas (sin canibalizar).
- 1 sección "Cuándo llamar a una empresa técnica" (CTA blando).
- 1 sección FAQ (3-5 Q&A) → schema `FAQPage`.
- Cierre con CTA fuerte (tel + WhatsApp + email).

### 3.2 Longitud
- Pilares de intención comercial: 1.500-2.000 palabras.
- Técnicos: 1.200-1.500 palabras.
- Long-tail: 900-1.200 palabras.

### 3.3 Posicionamiento (recordatorio crítico — CLAUDE.md §3)
- ❌ "reparamos / reformamos / restauramos / rehabilitamos"
- ✅ "limpiamos / descontaminamos / desodorizamos / coordinamos con
   empresas de obra"
- Aclarar siempre que las obras posteriores las ejecutan las empresas
  designadas por la aseguradora.

### 3.4 Interlinking
Cada artículo debe enlazar a:
- 1 landing madre de servicio (`/servicios/`).
- 1-2 landings locales (ej. la más cercana a Madrid, o la del sector
  tratado).
- 2-3 artículos del propio blog relacionados.
- 1 página estructural (`/contacto/`, `/peritos/`, `/casos-de-exito/`).

### 3.5 Imágenes
- 1 imagen `hero` (1600×900) por artículo, formato webp.
- 2-3 imágenes secundarias inline.
- Reutilizar la pool de `/assets/img/` (existen `service-*.webp`,
  `gallery-*.jpg`) o subir nuevas tras shoot real.
- `width`, `height`, `loading="lazy"` (excepto hero, `eager`).
- `alt` con KW natural (no keyword stuffing).

### 3.6 Schemas Schema.org
- Todos: `Article` + `BreadcrumbList`.
- Si tiene FAQ: `FAQPage`.
- Si es "cómo hacer X": `HowTo` (pasos).
- Author: `Organization` → Galaxia.

### 3.7 Snippet de meta-description
- Máx. 158 caracteres.
- KW principal en los primeros 60 caracteres.
- 1 CTA implícita ("Guía técnica", "Protocolo profesional").

---

## 4. Cómo añadir un artículo nuevo a `build_site.py`

1. Crear el contenido completo (HTML enriquecido) en una función nueva,
   p.ej. `def blog_que_hacer_despues_incendio(prefix) -> str`.
2. Añadir la entrada a `blog_articles` en `build_site.py`:

   ```python
   blog_articles = [
       ...
       ('que-hacer-despues-de-un-incendio',
        'Qué hacer después de un incendio: guía profesional'),
   ]
   ```

3. Si el artículo necesita HTML personalizado más allá del boilerplate,
   ampliar `simple_page()` con un `elif url == '/blog/que-hacer-...':`
   que inyecte el cuerpo real y el schema `Article` + `HowTo` + `FAQPage`.
4. Actualizar `len(pages) == ...` assert si cambia el total.
5. Ejecutar `python build_site.py && python qa_site.py`.
6. Confirmar que `sitemap.xml` incluye la nueva URL.

## 5. Priorización

Si solo hay capacidad para 4 artículos en el corto plazo:

1. `que-hacer-despues-de-un-incendio` (alto volumen, alta intención).
2. `eliminar-olor-a-humo-vivienda` (alto volumen, retorno B2C → B2B).
3. `limpieza-de-casa-quemada-pasos` (long-tail comercial, conversión).
4. `descontaminacion-tras-incendio` (cluster técnico — refuerza autoridad).

Última actualización: 2026-05-21.
