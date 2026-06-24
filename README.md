# Galaxia · Limpieza de Incendios

Web estática B2B para **limpieza de incendios** y **limpieza post incendio**, preparada para hosting estático y para publicación desde GitHub.

## Estado de generación

| Elemento | Resultado |
| --- | ---: |
| URLs totales generadas | 769 |
| Landings SEO locales | 734 |
| Páginas estructurales | 35 |
| Landings ciudad pura | 292 |
| Landings servicio + provincia | 442 |
| Sitemap | `sitemap.xml` |

## Datos temporales pendientes

Las imágenes de `/galeria/` son provisionales generadas para la maqueta y deben sustituirse por fotos reales de trabajos cuando estén disponibles. Teléfono y WhatsApp operativos: `614 24 87 33`.

## Cómo desplegar

Suba todo el contenido público del repositorio a la raíz del hosting estático, de modo que `index.html` quede directamente en `public_html`, `www` o carpeta equivalente. Si se usa GitHub Pages, configure la rama `main` como origen de publicación.

## Cómo añadir provincias o ciudades

Edite `build_site.py`, amplíe las listas `PROVINCES` o `CITIES` y ejecute `python3.11 build_site.py`. Después revise `sitemap.xml`, enlaces internos y páginas generadas.

## Cómo añadir un caso de éxito

Cree una nueva página estructural o sección dentro de `/casos-de-exito/`, añada imágenes optimizadas en `assets/img/` y mantenga siempre `width`, `height`, `loading="lazy"` y texto alternativo descriptivo.
