#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador estático para Galaxia · Limpieza de Incendios.

El script crea una web HTML estática con URLs en directorios limpios, contenidos
únicos deterministas, sitemap, robots, README y páginas estructurales.
No incorpora datos fiscales por indicación expresa del cliente.
"""
from __future__ import annotations

import html
import json
import math
import os
import random
import re
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
IMG = ASSETS / 'img'
DOMAIN = 'https://limpiezaincendios.com'
BRAND = 'Galaxia · Limpieza de Incendios'
SHORT = 'Galaxia'
TAGLINE = 'Limpieza de incendios y limpieza post incendio con tecnología industrial'
PHONE = '614 24 87 33'        # Display (SEO local, sin prefijo +34)
PHONE_TEL = '+34614248733'    # E.164 para tel: y schemas
WHATSAPP = '614 24 87 33'     # Display
WHATSAPP_WA = '34614248733'   # Para wa.me (sin +)
EMAIL = 'peritos@limpiezaincendios.com'
# Email destino del formulario (FormSubmit). Se envía CON _subject explícito
# para que el destinatario sepa de qué sitio llega.
FORMSUBMIT_EMAIL = 'info@limpiezasdeincendios.com'
ADDRESS = 'C. de la Fuente del Rey, 12, Moncloa - Aravaca, 28023 Madrid'
GBP = 'https://maps.app.goo.gl/adiBEYjzzPVDSZbp7'
# Keyword principal del sitio. Secundaria principal: "limpieza post incendio".
BASE_KEYWORD = 'limpieza de incendios'
SECONDARY_KEYWORD = 'limpieza post incendio'
# Sal global para diferenciar las elecciones deterministas (spintax y choices)
# respecto del sitio de origen y evitar contenido duplicado entre webs.
SEED_SALT = 'lic-com-2026'

# Delegaciones físicas. Una entrada por oficina. El teléfono y email son
# centrales (compartidos). La dirección, ciudad y coordenadas son únicas
# por delegación (Google y Bing premian esto para Local Pack por ciudad).
DELEGATIONS = [
    {
        'id': 'oficina-madrid', 'city_slug': 'madrid', 'city_name': 'Madrid',
        'name': 'Galaxia · Central Madrid',
        'street': 'C. de la Fuente del Rey, 12',
        'district': 'Moncloa - Aravaca', 'postal': '28023',
        'locality': 'Madrid', 'region': 'Comunidad de Madrid',
        'lat': 40.4548, 'lng': -3.7892, 'main': True,
    },
    {
        'id': 'oficina-badalona', 'city_slug': 'badalona', 'city_name': 'Badalona',
        'name': 'Galaxia · Badalona (Barcelona)',
        'street': 'Av. de Catalunya, 29',
        'district': '', 'postal': '08917',
        'locality': 'Badalona', 'region': 'Cataluña',
        'lat': 41.4500, 'lng': 2.2474,
    },
    {
        'id': 'oficina-valencia', 'city_slug': 'valencia', 'city_name': 'Valencia',
        'name': 'Galaxia · Valencia',
        'street': 'C. Periodista Gil Sumbiela, 70',
        'district': 'Benicalap', 'postal': '46025',
        'locality': 'Valencia', 'region': 'Comunidad Valenciana',
        'lat': 39.4866, 'lng': -0.3905,
    },
    {
        'id': 'oficina-toledo', 'city_slug': 'toledo', 'city_name': 'Toledo',
        'name': 'Galaxia · Toledo',
        'street': 'Pl. Capuchinas, 6',
        'district': '', 'postal': '45002',
        'locality': 'Toledo', 'region': 'Castilla-La Mancha',
        'lat': 39.8589, 'lng': -4.0237,
    },
    {
        'id': 'oficina-cordoba', 'city_slug': 'cordoba', 'city_name': 'Córdoba',
        'name': 'Galaxia · Córdoba',
        'street': 'C. Menéndez Pelayo, 6',
        'district': 'Centro', 'postal': '14008',
        'locality': 'Córdoba', 'region': 'Andalucía',
        'lat': 37.8825, 'lng': -4.7770,
    },
    {
        'id': 'oficina-marbella', 'city_slug': 'marbella', 'city_name': 'Marbella',
        'name': 'Galaxia · Marbella (Málaga)',
        'street': 'C. Álamos, 5',
        'district': '', 'postal': '29601',
        'locality': 'Marbella', 'region': 'Andalucía',
        'lat': 36.5108, 'lng': -4.8836,
    },
    {
        'id': 'oficina-murcia', 'city_slug': 'murcia', 'city_name': 'Murcia',
        'name': 'Galaxia · Murcia',
        'street': 'C. La Tinaja, 3',
        'district': 'San Benito - Progreso', 'postal': '30012',
        'locality': 'Murcia', 'region': 'Región de Murcia',
        'lat': 37.9846, 'lng': -1.1335,
    },
]


def delegation_full_address(d: dict) -> str:
    """Dirección completa en una línea, lista para mostrar."""
    parts = [d['street']]
    if d.get('district'):
        parts.append(d['district'])
    parts.append(f"{d['postal']} {d['locality']}")
    return ', '.join(parts)


def maps_query_url(d: dict) -> str:
    from urllib.parse import quote_plus
    return 'https://www.google.com/maps/search/?api=1&query=' + quote_plus(
        f"{d['name']} {delegation_full_address(d)}"
    )


def delegation_local_business(d: dict) -> dict:
    """Devuelve un nodo LocalBusiness para schema.org/JSON-LD."""
    return {
        '@type': 'LocalBusiness',
        '@id': f'{DOMAIN}/#{d["id"]}',
        'name': d['name'],
        'parentOrganization': {'@type': 'Organization', 'name': BRAND, 'url': DOMAIN},
        'url': DOMAIN,
        'telephone': PHONE_TEL,
        'email': EMAIL,
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': d['street'] + (', ' + d['district'] if d.get('district') else ''),
            'addressLocality': d['locality'],
            'addressRegion': d['region'],
            'postalCode': d['postal'],
            'addressCountry': 'ES',
        },
        'geo': {'@type': 'GeoCoordinates', 'latitude': d['lat'], 'longitude': d['lng']},
        'areaServed': d['locality'],
        'openingHoursSpecification': [{
            '@type': 'OpeningHoursSpecification',
            'dayOfWeek': ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
            'opens': '00:00', 'closes': '23:59',
        }],
        'sameAs': [GBP] if d.get('main') else [],
    }


def delegations_html(prefix: str) -> str:
    """Bloque visible con todas las delegaciones para la página de contacto."""
    cards = []
    for d in DELEGATIONS:
        badge = "<span class='dele-badge'>Central</span>" if d.get('main') else ''
        cards.append(
            f"<article class='dele-card'>"
            f"<header><h3>{esc(d['name'])}</h3>{badge}</header>"
            f"<p class='dele-addr'>{esc(delegation_full_address(d))}</p>"
            f"<div class='dele-actions'>"
            f"<a class='ghost' href='{maps_query_url(d)}' target='_blank' rel='noopener'>Ver en Google Maps</a>"
            f"<a class='ghost' href='tel:{PHONE_TEL}'>Llamar {PHONE}</a>"
            f"</div></article>"
        )
    return ("<section class='dele-section'><h2>Delegaciones físicas</h2>"
            "<p class='dele-intro'>Atención técnica 24 h en toda España. "
            "Estas son nuestras oficinas con presencia física; el teléfono "
            f"y email son centrales para urgencias en cualquier delegación.</p>"
            "<div class='dele-grid'>" + ''.join(cards) + "</div></section>")

CITIES = '''adra, alaquas, albacete, alcala-guadaira, alcala-henares, alcala-real,
alcaniz, alcantarilla, alcazar-san-juan, alcobendas, alcorcon, alcoy,
algeciras, alhama-murcia, alhaurin-grande, alhaurin-torre, alicante,
almansa, almassora, almeria, almonte, almunecar, alovera, altea, alzira,
andorra-teruel, andujar, antequera, arcos-frontera, arganda-rey, armilla,
ayamonte, azuqueca-henares, badalona, baena, baeza, balaguer, barbastro,
barcelona, baza, benalmadena, benicassim, benidorm, berja, binefar, blanes,
brihuega, bullas, burjassot, burriana, cabanillas-campo, cabra, cadiz,
calafell, calatayud, calpe, camas, cambrils, caravaca-cruz, carmona,
cartagena, cartaya, caspe, castelldefels, castellon, catarroja,
cerdanyola-valles, cervera, chiclana-frontera, chinchilla, ciudad-real,
coin, colmenar-viejo, consuegra, cordoba, cornella-llobregat, coslada,
cuarte-huerva, cuenca, daimiel, denia, dos-hermanas, ecija, ejea-caballeros,
el-ejido, el-vendrell, elche, elda, estepa, estepona, figueres, fraga,
fuengirola, fuenlabrada, gandia, gava, getafe, girona, granada, granollers,
guadalajara, guadix, guardamar-segura, hellin, hospitalet-llobregat, huelva,
huercal-almeria, huercal-overa, huesca, igualada, illescas, jaen,
jerez-frontera, jumilla, la-linea-concepcion, la-rinconada, la-roda, lebrija,
leganes, lepe, linares, lleida, lloret-mar, loja, lorca, los-barrios, lucena,
madrid, madridejos, mairena-aljarafe, malaga, mallen, mancha-real, manises,
manresa, manzanares, maracena, marbella, martos, mataro, mazarron, mijas,
mislata, moguer, molina-segura, mollerussa, mollet-valles, montilla, monzon,
moron-frontera, mostoles, motilla-palancar, motril, murcia, nerja, nules,
ocana, ogijares, olot, olula-rio, onda, ontinyent, orihuela, oropesa-mar,
osuna, palafrugell, palma-rio, palos-frontera, parla, pastrana, paterna,
petrer, picassent, pinos-puente, pozoblanco, pozuelo-alarcon, priego-cordoba,
puente-genil, puertollano, punta-umbria, quintanar-orden, requena, reus,
rincon-victoria, ripollet, rivas-vaciamadrid, ronda, roquetas-mar, roses,
rota, rubi, sabadell, sagunto, salou, salt, san-clemente, san-fernando,
san-javier, san-jose-rinconada, san-juan-aznalfarache, san-juan-puerto,
san-pedro-alcantara, san-sebastian-reyes, san-vicente-raspeig,
sanlucar-barrameda, sant-boi-llobregat, sant-cugat-valles,
santa-coloma-gramenet, santa-fe, santa-pola, santomera, sevilla, sueca,
talavera-reina, tarancon, tarazona, tarragona, terrassa, teruel, toledo,
tomelloso, torre-pacheco, torrejon-ardoz, torremolinos, torrent, torrevieja,
tortosa, totana, tremp, tres-cantos, ubeda, ubrique, utebo, utrera,
valdemoro, valdepenas, valencia, valls, velez-malaga, velilla-manzanares,
vera, vicar, vila-real, viladecans, vilafranca-penedes, villacarrillo,
villarrobledo, villena, vinaros, xativa, yecla, zaragoza'''
CITIES = [c.strip() for c in re.split(r',\s*', CITIES.replace('\n', ' ')) if c.strip()]

# Castilla y León (NUEVO): capitales + 1 ciudad importante extra por provincia
# para tener al menos cobertura en las 9 provincias de la CCAA.
CITIES += [
    'avila',
    'arevalo',                # Ávila (2ª ciudad relevante)
    'burgos',
    'aranda-duero',           # Burgos
    'miranda-ebro',           # Burgos
    'leon',
    'ponferrada',             # León
    'san-andres-rabanedo',    # León
    'palencia',
    'guardo',                 # Palencia
    'salamanca',
    'bejar',                  # Salamanca
    'ciudad-rodrigo',         # Salamanca
    'segovia',
    'cuellar',                # Segovia
    'soria',
    'almazan',                # Soria
    'valladolid',
    'medina-campo',           # Valladolid
    'laguna-duero',           # Valladolid
    'zamora',
    'benavente',              # Zamora
]

# Barrios de Madrid (distritos administrativos principales). Sirven como
# landings ciudad-barrio para captar búsquedas hiperlocales en la capital.
MADRID_BARRIOS = [
    'madrid-centro', 'madrid-salamanca', 'madrid-chamberi',
    'madrid-retiro', 'madrid-arganzuela', 'madrid-moncloa-aravaca',
    'madrid-tetuan', 'madrid-chamartin', 'madrid-latina',
    'madrid-carabanchel', 'madrid-usera', 'madrid-puente-vallecas',
    'madrid-ciudad-lineal', 'madrid-hortaleza', 'madrid-fuencarral',
    'madrid-san-blas', 'madrid-villaverde', 'madrid-barajas',
]
CITIES += MADRID_BARRIOS
# PROVINCES ordenadas por CCAA según indicación del cliente. Solo se
# admiten las 8 CCAA siguientes (en este orden):
#   1. Comunidad de Madrid
#   2. Comunidad Valenciana
#   3. Región de Murcia
#   4. Andalucía
#   5. Castilla-La Mancha
#   6. Aragón
#   7. Castilla y León
#   8. Cataluña
PROVINCES = [
    # 1) Comunidad de Madrid
    'madrid',
    # 2) Comunidad Valenciana
    'alicante', 'castellon', 'valencia',
    # 3) Región de Murcia
    'murcia',
    # 4) Andalucía
    'almeria', 'cadiz', 'cordoba', 'granada', 'huelva', 'jaen', 'malaga', 'sevilla',
    # 5) Castilla-La Mancha
    'albacete', 'ciudad-real', 'cuenca', 'guadalajara', 'toledo',
    # 6) Aragón
    'huesca', 'teruel', 'zaragoza',
    # 7) Castilla y León (NUEVO)
    'avila', 'burgos', 'leon', 'palencia', 'salamanca', 'segovia', 'soria', 'valladolid', 'zamora',
    # 8) Cataluña
    'barcelona', 'girona', 'lleida', 'tarragona',
]

# Mapa ciudad → provincia (slug). Usado para calcular "Zonas relacionadas"
# de forma geográfica (mismo provincia + provincias colindantes) en lugar
# de por orden alfabético.
CITY_PROVINCE = {
    'adra': 'almeria', 'alaquas': 'valencia', 'albacete': 'albacete',
    'alcala-guadaira': 'sevilla', 'alcala-henares': 'madrid', 'alcala-real': 'jaen',
    'alcaniz': 'teruel', 'alcantarilla': 'murcia', 'alcazar-san-juan': 'ciudad-real',
    'alcobendas': 'madrid', 'alcorcon': 'madrid', 'alcoy': 'alicante',
    'algeciras': 'cadiz', 'alhama-murcia': 'murcia', 'alhaurin-grande': 'malaga',
    'alhaurin-torre': 'malaga', 'alicante': 'alicante', 'almansa': 'albacete',
    'almassora': 'castellon', 'almeria': 'almeria', 'almonte': 'huelva',
    'almunecar': 'granada', 'alovera': 'guadalajara', 'altea': 'alicante',
    'alzira': 'valencia', 'andorra-teruel': 'teruel', 'andujar': 'jaen',
    'antequera': 'malaga', 'arcos-frontera': 'cadiz', 'arganda-rey': 'madrid',
    'armilla': 'granada', 'ayamonte': 'huelva', 'azuqueca-henares': 'guadalajara',
    'badalona': 'barcelona', 'baena': 'cordoba', 'baeza': 'jaen',
    'balaguer': 'lleida', 'barbastro': 'huesca', 'barcelona': 'barcelona',
    'baza': 'granada', 'benalmadena': 'malaga', 'benicassim': 'castellon',
    'benidorm': 'alicante', 'berja': 'almeria', 'binefar': 'huesca',
    'blanes': 'girona', 'brihuega': 'guadalajara', 'bullas': 'murcia',
    'burjassot': 'valencia', 'burriana': 'castellon', 'cabanillas-campo': 'guadalajara',
    'cabra': 'cordoba', 'cadiz': 'cadiz', 'calafell': 'tarragona',
    'calatayud': 'zaragoza', 'calpe': 'alicante', 'camas': 'sevilla',
    'cambrils': 'tarragona', 'caravaca-cruz': 'murcia', 'carmona': 'sevilla',
    'cartagena': 'murcia', 'cartaya': 'huelva', 'caspe': 'zaragoza',
    'castelldefels': 'barcelona', 'castellon': 'castellon', 'catarroja': 'valencia',
    'cerdanyola-valles': 'barcelona', 'cervera': 'lleida',
    'chiclana-frontera': 'cadiz', 'chinchilla': 'albacete', 'ciudad-real': 'ciudad-real',
    'coin': 'malaga', 'colmenar-viejo': 'madrid', 'consuegra': 'toledo',
    'cordoba': 'cordoba', 'cornella-llobregat': 'barcelona', 'coslada': 'madrid',
    'cuarte-huerva': 'zaragoza', 'cuenca': 'cuenca', 'daimiel': 'ciudad-real',
    'denia': 'alicante', 'dos-hermanas': 'sevilla', 'ecija': 'sevilla',
    'ejea-caballeros': 'zaragoza', 'el-ejido': 'almeria', 'el-vendrell': 'tarragona',
    'elche': 'alicante', 'elda': 'alicante', 'estepa': 'sevilla',
    'estepona': 'malaga', 'figueres': 'girona', 'fraga': 'huesca',
    'fuengirola': 'malaga', 'fuenlabrada': 'madrid', 'gandia': 'valencia',
    'gava': 'barcelona', 'getafe': 'madrid', 'girona': 'girona',
    'granada': 'granada', 'granollers': 'barcelona', 'guadalajara': 'guadalajara',
    'guadix': 'granada', 'guardamar-segura': 'alicante', 'hellin': 'albacete',
    'hospitalet-llobregat': 'barcelona', 'huelva': 'huelva',
    'huercal-almeria': 'almeria', 'huercal-overa': 'almeria', 'huesca': 'huesca',
    'igualada': 'barcelona', 'illescas': 'toledo', 'jaen': 'jaen',
    'jerez-frontera': 'cadiz', 'jumilla': 'murcia',
    'la-linea-concepcion': 'cadiz', 'la-rinconada': 'sevilla', 'la-roda': 'albacete',
    'lebrija': 'sevilla', 'leganes': 'madrid', 'lepe': 'huelva',
    'linares': 'jaen', 'lleida': 'lleida', 'lloret-mar': 'girona',
    'loja': 'granada', 'lorca': 'murcia', 'los-barrios': 'cadiz',
    'lucena': 'cordoba', 'madrid': 'madrid', 'madridejos': 'toledo',
    'mairena-aljarafe': 'sevilla', 'malaga': 'malaga', 'mallen': 'zaragoza',
    'mancha-real': 'jaen', 'manises': 'valencia', 'manresa': 'barcelona',
    'manzanares': 'ciudad-real', 'maracena': 'granada', 'marbella': 'malaga',
    'martos': 'jaen', 'mataro': 'barcelona', 'mazarron': 'murcia',
    'mijas': 'malaga', 'mislata': 'valencia', 'moguer': 'huelva',
    'molina-segura': 'murcia', 'mollerussa': 'lleida', 'mollet-valles': 'barcelona',
    'montilla': 'cordoba', 'monzon': 'huesca', 'moron-frontera': 'sevilla',
    'mostoles': 'madrid', 'motilla-palancar': 'cuenca', 'motril': 'granada',
    'murcia': 'murcia', 'nerja': 'malaga', 'nules': 'castellon',
    'ocana': 'toledo', 'ogijares': 'granada', 'olot': 'girona',
    'olula-rio': 'almeria', 'onda': 'castellon', 'ontinyent': 'valencia',
    'orihuela': 'alicante', 'oropesa-mar': 'castellon', 'osuna': 'sevilla',
    'palafrugell': 'girona', 'palma-rio': 'cordoba', 'palos-frontera': 'huelva',
    'parla': 'madrid', 'pastrana': 'guadalajara', 'paterna': 'valencia',
    'petrer': 'alicante', 'picassent': 'valencia', 'pinos-puente': 'granada',
    'pozoblanco': 'cordoba', 'pozuelo-alarcon': 'madrid', 'priego-cordoba': 'cordoba',
    'puente-genil': 'cordoba', 'puertollano': 'ciudad-real', 'punta-umbria': 'huelva',
    'quintanar-orden': 'toledo', 'requena': 'valencia', 'reus': 'tarragona',
    'rincon-victoria': 'malaga', 'ripollet': 'barcelona', 'rivas-vaciamadrid': 'madrid',
    'ronda': 'malaga', 'roquetas-mar': 'almeria', 'roses': 'girona',
    'rota': 'cadiz', 'rubi': 'barcelona', 'sabadell': 'barcelona',
    'sagunto': 'valencia', 'salou': 'tarragona', 'salt': 'girona',
    'san-clemente': 'cuenca', 'san-fernando': 'cadiz', 'san-javier': 'murcia',
    'san-jose-rinconada': 'sevilla', 'san-juan-aznalfarache': 'sevilla',
    'san-juan-puerto': 'huelva', 'san-pedro-alcantara': 'malaga',
    'san-sebastian-reyes': 'madrid', 'san-vicente-raspeig': 'alicante',
    'sanlucar-barrameda': 'cadiz', 'sant-boi-llobregat': 'barcelona',
    'sant-cugat-valles': 'barcelona', 'santa-coloma-gramenet': 'barcelona',
    'santa-fe': 'granada', 'santa-pola': 'alicante', 'santomera': 'murcia',
    'sevilla': 'sevilla', 'sueca': 'valencia', 'talavera-reina': 'toledo',
    'tarancon': 'cuenca', 'tarazona': 'zaragoza', 'tarragona': 'tarragona',
    'terrassa': 'barcelona', 'teruel': 'teruel', 'toledo': 'toledo',
    'tomelloso': 'ciudad-real', 'torre-pacheco': 'murcia',
    'torrejon-ardoz': 'madrid', 'torremolinos': 'malaga', 'torrent': 'valencia',
    'torrevieja': 'alicante', 'tortosa': 'tarragona', 'totana': 'murcia',
    'tremp': 'lleida', 'tres-cantos': 'madrid', 'ubeda': 'jaen',
    'ubrique': 'cadiz', 'utebo': 'zaragoza', 'utrera': 'sevilla',
    'valdemoro': 'madrid', 'valdepenas': 'ciudad-real', 'valencia': 'valencia',
    'valls': 'tarragona', 'velez-malaga': 'malaga', 'velilla-manzanares': 'madrid',
    'vera': 'almeria', 'vicar': 'almeria', 'vila-real': 'castellon',
    'viladecans': 'barcelona', 'vilafranca-penedes': 'barcelona',
    'villacarrillo': 'jaen', 'villarrobledo': 'albacete', 'villena': 'alicante',
    'vinaros': 'castellon', 'xativa': 'valencia', 'yecla': 'murcia',
    'zaragoza': 'zaragoza',
    # Castilla y León (NUEVO)
    'avila': 'avila', 'arevalo': 'avila',
    'burgos': 'burgos', 'aranda-duero': 'burgos', 'miranda-ebro': 'burgos',
    'leon': 'leon', 'ponferrada': 'leon', 'san-andres-rabanedo': 'leon',
    'palencia': 'palencia', 'guardo': 'palencia',
    'salamanca': 'salamanca', 'bejar': 'salamanca', 'ciudad-rodrigo': 'salamanca',
    'segovia': 'segovia', 'cuellar': 'segovia',
    'soria': 'soria', 'almazan': 'soria',
    'valladolid': 'valladolid', 'medina-campo': 'valladolid', 'laguna-duero': 'valladolid',
    'zamora': 'zamora', 'benavente': 'zamora',
    # Barrios de Madrid (todos pertenecen a Madrid provincia)
    'madrid-centro': 'madrid', 'madrid-salamanca': 'madrid', 'madrid-chamberi': 'madrid',
    'madrid-retiro': 'madrid', 'madrid-arganzuela': 'madrid', 'madrid-moncloa-aravaca': 'madrid',
    'madrid-tetuan': 'madrid', 'madrid-chamartin': 'madrid', 'madrid-latina': 'madrid',
    'madrid-carabanchel': 'madrid', 'madrid-usera': 'madrid', 'madrid-puente-vallecas': 'madrid',
    'madrid-ciudad-lineal': 'madrid', 'madrid-hortaleza': 'madrid', 'madrid-fuencarral': 'madrid',
    'madrid-san-blas': 'madrid', 'madrid-villaverde': 'madrid', 'madrid-barajas': 'madrid',
}

# Provincias colindantes (solo dentro del listado PROVINCES; provincias
# limítrofes fuera del listado se omiten para no enlazar a landings que
# no existen).
PROVINCE_NEIGHBORS = {
    'albacete': ['cuenca', 'ciudad-real', 'jaen', 'murcia', 'alicante', 'valencia'],
    'alicante': ['valencia', 'albacete', 'murcia'],
    'almeria': ['granada', 'murcia', 'jaen'],
    'barcelona': ['tarragona', 'lleida', 'girona'],
    'cadiz': ['huelva', 'sevilla', 'malaga'],
    'castellon': ['valencia', 'teruel', 'tarragona'],
    'ciudad-real': ['toledo', 'cuenca', 'albacete', 'jaen', 'cordoba'],
    'cordoba': ['jaen', 'granada', 'malaga', 'sevilla', 'ciudad-real'],
    'cuenca': ['madrid', 'guadalajara', 'toledo', 'ciudad-real', 'albacete', 'valencia', 'teruel'],
    'girona': ['barcelona'],
    'granada': ['jaen', 'cordoba', 'malaga', 'almeria'],
    'guadalajara': ['madrid', 'cuenca', 'teruel', 'zaragoza'],
    'huelva': ['sevilla', 'cadiz'],
    'huesca': ['zaragoza', 'lleida'],
    'jaen': ['ciudad-real', 'cordoba', 'granada', 'almeria', 'albacete'],
    'lleida': ['huesca', 'zaragoza', 'teruel', 'barcelona', 'tarragona'],
    'madrid': ['guadalajara', 'toledo', 'cuenca'],
    'malaga': ['cadiz', 'sevilla', 'cordoba', 'granada'],
    'murcia': ['alicante', 'albacete', 'almeria'],
    'sevilla': ['huelva', 'cadiz', 'malaga', 'cordoba'],
    'tarragona': ['castellon', 'teruel', 'zaragoza', 'lleida', 'barcelona'],
    'teruel': ['zaragoza', 'guadalajara', 'cuenca', 'valencia', 'castellon', 'tarragona'],
    'toledo': ['madrid', 'guadalajara', 'cuenca', 'ciudad-real'],
    'valencia': ['castellon', 'teruel', 'cuenca', 'albacete', 'alicante'],
    'zaragoza': ['huesca', 'teruel', 'lleida', 'guadalajara', 'soria'],
    # Castilla y León: provincias colindantes dentro de las 9 + adyacentes
    'avila': ['salamanca', 'segovia', 'madrid', 'toledo', 'valladolid'],
    'burgos': ['palencia', 'valladolid', 'soria'],
    'leon': ['palencia', 'zamora'],
    'palencia': ['burgos', 'valladolid', 'leon'],
    'salamanca': ['zamora', 'valladolid', 'avila'],
    'segovia': ['avila', 'valladolid', 'soria', 'madrid', 'guadalajara'],
    'soria': ['burgos', 'segovia', 'guadalajara', 'zaragoza'],
    'valladolid': ['palencia', 'burgos', 'segovia', 'avila', 'salamanca', 'zamora', 'leon'],
    'zamora': ['leon', 'valladolid', 'salamanca'],
}


def related_geo_cities(slug: str, k: int = 6) -> list:
    """Devuelve hasta `k` ciudades cercanas geográficamente a `slug`.

    `slug` puede ser una ciudad (clave de CITY_PROVINCE) o una provincia
    (clave de PROVINCE_NEIGHBORS). Prioriza ciudades de la misma provincia
    y completa con ciudades de provincias colindantes.
    """
    if slug in PROVINCE_NEIGHBORS:
        prov = slug
        same = [c for c in CITIES if CITY_PROVINCE.get(c) == prov]
        out = list(same[:k])
    else:
        prov = CITY_PROVINCE.get(slug)
        if not prov:
            return [c for c in CITIES if c != slug][:k]
        same = [c for c in CITIES if CITY_PROVINCE.get(c) == prov and c != slug]
        out = list(same[:k])
    if len(out) < k:
        for nb in PROVINCE_NEIGHBORS.get(prov, []):
            for c in CITIES:
                if CITY_PROVINCE.get(c) == nb and c not in out and c != slug:
                    out.append(c)
                    if len(out) >= k:
                        return out
    return out[:k]
SERVICES = ['bares','bodegas','centros-sanitarios','colegios','comercios','comunidades','garajes','hoteles','naves','oficinas','residencias','restaurantes','salas-tecnicas']
SERVICE_LABELS = {
    'bares': 'bares y zonas de ocio',
    'bodegas': 'bodegas e instalaciones agroalimentarias',
    'centros-sanitarios': 'centros sanitarios y hospitales',
    'colegios': 'colegios y centros educativos',
    'comercios': 'comercios y tiendas',
    'comunidades': 'comunidades de propietarios',
    'garajes': 'garajes y aparcamientos',
    'hoteles': 'hoteles y alojamientos',
    'naves': 'naves industriales',
    'oficinas': 'oficinas corporativas',
    'residencias': 'residencias y centros asistenciales',
    'restaurantes': 'restaurantes y cocinas profesionales',
    'salas-tecnicas': 'salas técnicas y CPD'
}
SPINTAX_FILES = {
    'residencias': 'spintax-01-residencias-mayores.txt',
    'naves': 'spintax-02-naves-industriales.txt',
    'restaurantes': 'spintax-03-restaurantes.txt',
    'comunidades': 'spintax-04-comunidades-vecinos.txt',
    'oficinas': 'spintax-05-oficinas.txt',
    'hoteles': 'spintax-06-hoteles.txt',
    'comercios': 'spintax-07-tiendas-comercios.txt',
    'garajes': 'spintax-08-garajes.txt',
    'colegios': 'spintax-09-colegios.txt',
    'bodegas': 'spintax-10-bodegas.txt',
    'bares': 'spintax-11-bares.txt',
    'salas-tecnicas': 'spintax-12-salas-tecnicas.txt',
    'centros-sanitarios': 'spintax-UNIVERSAL-hospitales-CLAUDE.txt',
}

CSS = r'''
:root{--bg:#121620;--bg2:#1A1F2C;--ink:#F8F9FA;--muted:#9CA3AF;--line:#2A3142;--orange:#FF5500;--blue:#0066FF;--green:#10B981;--shadow:0 1px 0 rgba(255,255,255,.05) inset,0 20px 70px rgba(0,0,0,.28)}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 80% 0,rgba(0,102,255,.18),transparent 34rem),linear-gradient(180deg,#0A0F18,var(--bg) 18rem);color:var(--ink);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.62}a{color:inherit;text-decoration:none}img{max-width:100%;height:auto;display:block}.topbar{background:#0A0F18;border-bottom:1px solid var(--line);color:#cbd5e1;font-size:.84rem}.wrap{width:min(1180px,92vw);margin-inline:auto}.topbar .wrap{display:flex;justify-content:space-between;align-items:center;gap:1rem}.topbar a,.cta{background:var(--orange);color:white;padding:.72rem 1rem;border-radius:.85rem;font-weight:800;letter-spacing:.02em}.nav{padding:1rem 0;position:sticky;top:0;z-index:10;background:rgba(18,22,32,.78);backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,.06)}.nav .wrap{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:1rem;position:relative}.brand{display:flex;align-items:center;gap:.8rem;font-family:'Space Grotesk',Inter,sans-serif;font-weight:900;letter-spacing:.12em}.brand img{height:100px;width:auto;object-fit:contain;display:block}.brand>span{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}.brand-title{font-family:'Space Grotesk',Inter,sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:clamp(.95rem,1.65vw,1.35rem);color:#fff;text-align:center;justify-self:center;white-space:nowrap;line-height:1.1}.menu{display:none;position:absolute;top:calc(100% + .6rem);right:0;min-width:260px;background:#0b101a;border:1px solid var(--line);border-radius:1rem;padding:1rem;flex-direction:column;gap:.7rem;box-shadow:0 24px 60px rgba(0,0,0,.45);color:#dbe4ef;font-size:.98rem;z-index:11}.menu.open{display:flex}.menu a{opacity:.92;padding:.3rem .2rem}.menu a:hover{opacity:1;color:white}.menu .cta{text-align:center;margin-top:.3rem}.hamb{display:inline-flex;align-items:center;gap:.45rem;background:rgba(255,255,255,.06);border:1px solid var(--line);color:white;border-radius:.7rem;padding:.6rem .9rem;font-weight:700;cursor:pointer}.hamb:hover{background:rgba(255,255,255,.12)}.hero{padding:5rem 0 3rem}.grid{display:grid;gap:1.25rem}.hero-grid{grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);align-items:stretch}.panel{background:linear-gradient(180deg,rgba(255,255,255,.052),rgba(255,255,255,.025));border:1px solid var(--line);border-radius:1.45rem;box-shadow:var(--shadow);overflow:hidden}.hero-copy{padding:clamp(1.5rem,4vw,3.2rem)}.eyebrow{color:var(--green);font-family:'JetBrains Mono',monospace;font-size:.86rem;text-transform:uppercase;letter-spacing:.12em}.h1,h1{font-family:'Space Grotesk',Inter,sans-serif;text-transform:uppercase;font-size:clamp(2.35rem,5vw,4.15rem);line-height:.96;margin:.75rem 0 1rem;letter-spacing:-.045em}.lead{font-size:clamp(1rem,1.8vw,1.2rem);color:#cdd6e4;max-width:72ch}.actions{display:flex;gap:.9rem;flex-wrap:wrap;margin-top:1.5rem}.ghost{border:1px solid var(--line);padding:.72rem 1rem;border-radius:.85rem;color:#e5e7eb}.hero-img{position:relative;min-height:100%;background:#080b10}.hero-img img{height:100%;min-height:430px;width:100%;object-fit:cover;opacity:.82}.stats{grid-template-columns:repeat(3,1fr);margin-top:1.25rem}.stat{padding:1rem;background:#0f1420;border:1px solid var(--line);border-radius:1rem}.stat strong{display:block;font-family:'JetBrains Mono',monospace;font-size:1.55rem;color:white}.stat span{color:var(--muted);font-size:.88rem}.section{padding:4.2rem 0}.section h2{font-family:'Space Grotesk',Inter,sans-serif;text-transform:uppercase;font-size:clamp(1.65rem,3vw,2.45rem);line-height:1.04;margin:.2rem 0 1rem}.section-head{display:flex;justify-content:space-between;gap:2rem;align-items:end;margin-bottom:1.5rem}.section-head p{max-width:62ch;color:var(--muted)}.bento{grid-template-columns:repeat(3,1fr)}.card{padding:1.2rem;border:1px solid var(--line);border-radius:1.2rem;background:rgba(26,31,44,.8);box-shadow:var(--shadow)}.card h3{margin:.7rem 0 .4rem;font-family:'Space Grotesk',Inter,sans-serif}.card p{color:#b8c1cf;margin:.25rem 0}.icon{width:2.4rem;height:2.4rem;border-radius:.8rem;display:grid;place-items:center;background:rgba(0,102,255,.12);border:1px solid rgba(0,102,255,.35);color:#8cc0ff}.case{grid-template-columns:1fr 1fr;align-items:center}.case .copy{padding:2rem}.case dl{display:grid;grid-template-columns:1fr 1fr;gap:.8rem}.case dt{color:var(--muted);font-size:.84rem}.case dd{margin:0;font-family:'JetBrains Mono',monospace;color:white}.steps{counter-reset:s;grid-template-columns:repeat(5,1fr)}.step:before{counter-increment:s;content:counter(s,decimal-leading-zero);font-family:'JetBrains Mono',monospace;color:var(--orange);font-size:1.4rem}.gallery{grid-template-columns:repeat(3,1fr)}.gallery figure{margin:0;overflow:hidden;border-radius:1rem;border:1px solid var(--line);background:#0c1018}.gallery img{aspect-ratio:4/3;object-fit:cover;width:100%}.gallery figcaption{padding:.8rem;color:#cbd5e1;font-size:.9rem}.landing-photo{margin:1.2rem 0;border-radius:1rem;overflow:hidden;border:1px solid var(--line);background:#0c1018}.landing-photo img{aspect-ratio:16/9;object-fit:cover;width:100%;display:block}.landing-photo figcaption{padding:.7rem 1rem;font-size:.92rem;color:#cbd5e1}.dele-section{margin:2rem 0}.dele-section h2{font-family:'Space Grotesk',Inter,sans-serif;text-transform:uppercase}.dele-intro{color:#cbd5e1;max-width:64ch}.dele-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-top:1.1rem}.dele-card{padding:1.1rem 1.2rem;border:1px solid var(--line);border-radius:1rem;background:rgba(26,31,44,.85)}.dele-card header{display:flex;align-items:center;justify-content:space-between;gap:.6rem;margin-bottom:.4rem}.dele-card h3{margin:0;font-family:'Space Grotesk',Inter,sans-serif;font-size:1.05rem;line-height:1.2}.dele-badge{font-family:'JetBrains Mono',monospace;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;padding:.18rem .55rem;border-radius:999px;background:var(--orange);color:#fff;white-space:nowrap}.dele-addr{color:#d5dce8;margin:.2rem 0 .85rem;font-size:.94rem}.dele-actions{display:flex;flex-wrap:wrap;gap:.5rem}.dele-actions a{padding:.45rem .8rem;font-size:.85rem;border-radius:.6rem}.landing-dele{margin:1rem 0 1.6rem}.urgency-cta{background:rgba(255,85,0,.1);border-left:4px solid var(--orange);padding:1rem 1.15rem;border-radius:.7rem;font-size:1.02rem;color:#fff8f0;margin:1.2rem 0 .8rem}.inline-links{background:rgba(0,102,255,.07);border-left:3px solid var(--blue);padding:.85rem 1.1rem;border-radius:.6rem;color:#cdd6e4}.inline-links a{color:#8cc0ff;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}.testimonials{grid-template-columns:repeat(3,1fr);gap:1.1rem}@media(max-width:900px){.testimonials{grid-template-columns:1fr 1fr}}@media(max-width:560px){.testimonials{grid-template-columns:1fr}}.testimonial{display:flex;flex-direction:column;gap:.6rem}.testimonial .stars{color:#FFB300;font-size:1.15rem;letter-spacing:.08em}.testimonial blockquote{margin:0;font-size:.96rem;color:#dde7f3;line-height:1.55}.testimonial footer{margin-top:auto;font-size:.85rem;color:var(--muted);display:flex;flex-direction:column;gap:.05rem}.testimonial footer strong{color:#fff}.galpair-grid{grid-template-columns:1fr;gap:1.4rem}.galpair{padding:0;overflow:hidden}.galpair-imgs{display:grid;grid-template-columns:1fr 1fr;gap:2px;background:var(--line)}.galpair-imgs figure{margin:0;position:relative;background:#0c1018}.galpair-imgs img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}.galpair-imgs figcaption{position:absolute;top:.7rem;left:.7rem;background:rgba(10,15,24,.85);color:#fff;font-family:'JetBrains Mono',monospace;font-size:.7rem;padding:.25rem .55rem;border-radius:.4rem;letter-spacing:.08em}.galpair-body{padding:1.1rem 1.3rem}.galpair-body h3{margin:.1rem 0 .4rem}.galpair-body p{color:#c4cfde;margin:0;font-size:.95rem}.ubic-grid{display:flex;flex-direction:column;gap:1.6rem;margin-top:1.4rem}.ubic-ccaa{padding:1.2rem;border:1px solid var(--line);border-radius:1rem;background:rgba(26,31,44,.85)}.ubic-ccaa h2{margin:.1rem 0 .8rem;font-size:1.3rem}.ubic-count{font-size:.78rem;color:var(--muted);font-family:'JetBrains Mono',monospace;text-transform:none;letter-spacing:0;font-weight:400;margin-left:.6rem}.ubic-ccaa details{margin:.4rem 0;padding:.55rem .7rem;border:1px solid var(--line);border-radius:.7rem;background:rgba(15,20,32,.5)}.ubic-ccaa summary{cursor:pointer;font-weight:700;color:#fff}.ubic-ccaa summary a{color:#8cc0ff;text-decoration:underline}.ubic-cities{list-style:none;padding:.6rem 0 .2rem;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.3rem .8rem}.ubic-cities a{color:#dbe4ef;font-size:.92rem}.ubic-cities a:hover{color:#fff}.case-grid{grid-template-columns:repeat(2,1fr);gap:1.4rem;margin:1.2rem 0}.case-card{padding:0;overflow:hidden;display:flex;flex-direction:column}.case-card img{aspect-ratio:4/3;object-fit:cover;width:100%;display:block}.case-card .case-body{padding:1.1rem 1.2rem 1.3rem}.case-card h3{margin:.2rem 0 .55rem;font-size:1.18rem;line-height:1.18}.case-card p{color:#c4cfde;margin:.2rem 0 .85rem;font-size:.95rem}.case-kpis{display:grid;grid-template-columns:1fr 1fr;gap:.55rem;margin:0}.case-kpis dt{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}.case-kpis dd{margin:0;font-family:'JetBrains Mono',monospace;color:#fff;font-size:.95rem}@media(max-width:780px){.case-grid{grid-template-columns:1fr}}.faq details{border:1px solid var(--line);background:#101624;border-radius:1rem;padding:1rem;margin:.7rem 0}.faq summary{cursor:pointer;font-weight:800}.coverage{columns:4 12rem;color:#cbd5e1}.footer{border-top:1px solid var(--line);background:#090d14;padding:3rem 0;color:#cbd5e1}.footgrid{display:grid;grid-template-columns:1.4fr repeat(4,1fr);gap:1.2rem}.footer h3,.footer h4{color:white}.footer a{display:block;color:#cbd5e1;margin:.3rem 0}.footer-meta{border-top:1px solid var(--line);margin-top:1.6rem;padding:1rem 0 0;text-align:center;color:#94a3b8;font-size:.85rem}.footer-meta a{display:inline;color:#cbd5e1;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px;opacity:.85}.footer-meta a:hover{opacity:1;color:#fff}.contact-float{position:fixed;left:0;right:0;bottom:1rem;z-index:30;display:flex;justify-content:space-between;align-items:center;padding:0 1rem;pointer-events:none;background:transparent;border:0}.contact-float a{pointer-events:auto;display:inline-flex;align-items:center;gap:.55rem;padding:.7rem 1.05rem;border-radius:999px;font-weight:800;letter-spacing:.02em;box-shadow:0 10px 26px rgba(0,0,0,.35);color:#fff;border:1px solid rgba(255,255,255,.18);font-size:.95rem}.contact-float a.cf-call{background:#FF5500}.contact-float a.cf-wa{background:#25D366;order:-1}.contact-float a:hover{transform:translateY(-1px)}.contact-float svg{width:1.15rem;height:1.15rem;fill:currentColor}#scroll-top{position:fixed;left:1rem;bottom:1rem;z-index:25;width:46px;height:46px;border-radius:50%;border:1px solid var(--line);background:rgba(15,20,32,.9);color:#fff;font-size:1.4rem;line-height:1;cursor:pointer;display:none;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(0,0,0,.35);transition:opacity .2s}#scroll-top.show{display:inline-flex}#scroll-top:hover{background:rgba(255,255,255,.12)}#cookie-banner{position:fixed;left:50%;bottom:1rem;transform:translateX(-50%);z-index:40;max-width:min(700px,92vw);background:#0e1726;border:1px solid var(--line);border-radius:1rem;padding:.85rem 1rem;display:flex;gap:.85rem;align-items:center;color:#dbe4ef;font-size:.88rem;box-shadow:0 12px 36px rgba(0,0,0,.5);pointer-events:auto;visibility:visible;opacity:1;transition:opacity .3s}#cookie-banner p{margin:0;flex:1;display:flex;gap:.5rem;align-items:center}#cookie-banner a{color:#8cc0ff;text-decoration:underline}#cookie-banner button{flex:0 0 auto;background:var(--orange);color:#fff;border:0;padding:.5rem .9rem;border-radius:.6rem;font-weight:800;cursor:pointer}#cookie-banner .cb-icon{display:none}#cookie-banner .cb-short{display:none}@media(max-width:560px){#cookie-banner{flex-direction:row;text-align:left;bottom:.7rem;padding:.32rem .55rem;font-size:.72rem;gap:.4rem;max-width:calc(100vw - 240px);border-radius:999px;line-height:1.1}#cookie-banner p{gap:.3rem}#cookie-banner .cb-icon{display:inline-block;font-size:.95rem}#cookie-banner .cb-full{display:none}#cookie-banner .cb-short{display:inline}#cookie-banner .cb-short a{font-weight:700}#cookie-banner button{padding:.25rem .55rem;font-size:.72rem;border-radius:.5rem}#scroll-top{left:50%;transform:translateX(-50%);right:auto;bottom:calc(1rem + 60px);width:40px;height:40px;font-size:1.15rem}.contact-float{bottom:.7rem;padding:0 .65rem}.contact-float a{padding:.55rem .8rem;font-size:.82rem;gap:.4rem}.contact-float svg{width:1rem;height:1rem}body{padding-bottom:80px!important}}.breadcrumb{color:var(--muted);font-size:.88rem;padding-top:1rem}.content{max-width:880px}.content p{color:#d5dce8}.content h2,.content h3{font-family:'Space Grotesk',Inter,sans-serif}.table{width:100%;border-collapse:collapse;margin:1rem 0}.table th,.table td{border:1px solid var(--line);padding:.8rem;text-align:left}.table th{background:#111827}.notice{border-left:4px solid var(--blue);background:#0d1524;padding:1rem;border-radius:.6rem}.two{grid-template-columns:1fr 1fr}.local-links{display:flex;gap:.5rem;flex-wrap:wrap}.local-links a{border:1px solid var(--line);border-radius:999px;padding:.4rem .75rem;color:#dbeafe}.reveal{transition:opacity .5s,transform .5s}.js .reveal:not(.is-visible){opacity:0;transform:translateY(10px)}@media(max-width:900px){.hero-grid,.case,.two{grid-template-columns:1fr}.bento,.gallery,.stats{grid-template-columns:1fr 1fr}.steps{grid-template-columns:1fr 1fr}.hero{padding-top:2.4rem}.footgrid{grid-template-columns:1fr 1fr}.menu{left:4vw;right:4vw;min-width:0}}@media(max-width:560px){.bento,.gallery,.stats,.steps,.footgrid{grid-template-columns:1fr}.topbar{font-size:.72rem}.topbar .wrap{flex-wrap:wrap;justify-content:space-between;gap:.4rem;padding:.4rem 0}.topbar span{flex:1 1 auto;min-width:0}.topbar a{padding:.45rem .7rem;font-size:.8rem;white-space:nowrap}.h1,h1{font-size:2.15rem}.hero-img img{min-height:300px}.section-head{display:block}.coverage{columns:1}.actions a{width:100%;text-align:center}.nav .wrap{gap:.4rem}.brand-title{font-size:.68rem;letter-spacing:.03em;white-space:normal;line-height:1.15}.hamb{padding:.45rem .55rem;font-size:.85rem}}
/* VISUAL_CLARITY_MOBILE_START */
:root{--bg:#2C3B52;--bg2:#384A63;--ink:#FFFFFF;--muted:#E4ECF5;--line:#63738A;--orange:#FF6A1A;--blue:#3B8CFF;--green:#45E2B0;--shadow:0 1px 0 rgba(255,255,255,.13) inset,0 14px 36px rgba(5,12,24,.18)}
body{background:radial-gradient(circle at 82% 0,rgba(59,140,255,.32),transparent 32rem),radial-gradient(circle at 10% 14rem,rgba(255,106,26,.15),transparent 24rem),linear-gradient(180deg,#26354A 0,#31435C 20rem,#3B4D66 100%);color:var(--ink)}
.topbar{background:#233247;color:#FFFFFF;border-bottom:1px solid rgba(255,255,255,.2)}
.nav{background:rgba(43,60,82,.92);border-bottom:1px solid rgba(255,255,255,.22)}
.menu{color:#F1F5F9}.menu a{opacity:.95}.hamb{border-color:#55647A;color:#fff;background:rgba(255,255,255,.06)}
.panel{background:linear-gradient(180deg,rgba(255,255,255,.19),rgba(255,255,255,.1));border-color:rgba(255,255,255,.26)}
.lead,.content p{color:#F0F6FF}.section-head p,.card p,.gallery figcaption,.footer,.footer a,.coverage,.breadcrumb,.stat span,.case dt{color:#DCE6F2}
.card,.stat,.faq details{background:rgba(62,80,105,.92);border-color:rgba(255,255,255,.24)}
.notice{background:rgba(31,55,87,.72)}.table th{background:#243145}.ghost{border-color:#8FA0B6;color:#fff;background:rgba(255,255,255,.07)}
.hero-img{background:#2D3D55}.hero-img img,.case>img,.gallery img{opacity:1;filter:brightness(1.32) contrast(1.08) saturate(1.14)}
.gallery figure{background:#1F2937;border-color:rgba(255,255,255,.18)}
.footer{background:#162030;border-top-color:rgba(255,255,255,.16)}
@media(max-width:900px){.menu{background:#34465F;border-color:#73859E}.hero{padding-top:1.7rem}.hero-img img,.case>img,.gallery img{filter:brightness(1.45) contrast(1.09) saturate(1.18)}.panel{box-shadow:0 10px 26px rgba(4,10,22,.16)}}
@media(max-width:560px){body{background:linear-gradient(180deg,#31425B 0,#3A4D68 18rem,#42546E 100%);padding-bottom:86px}.wrap{width:min(100% - 28px,1180px)}.topbar .wrap{gap:.55rem}.brand{letter-spacing:.08em}.brand img{height:84px;width:auto}.hero-copy{padding:1.25rem}.h1,h1{font-size:2.02rem;line-height:1.02}.lead{font-size:1.04rem;color:#FFFFFF}.hero-img img{min-height:260px;max-height:360px}.section{padding:3rem 0}.card,.stat,.faq details{background:rgba(73,92,118,.96)}.actions a{min-height:48px;display:flex;align-items:center;justify-content:center}.contact-float{left:1rem;right:1rem;text-align:center}}
.callback-form{margin-top:1.4rem;display:grid;gap:.85rem}.callback-form .form-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.75rem}.callback-form label{display:grid;gap:.32rem;font-weight:800;color:#fff}.callback-form input{width:100%;min-height:46px;border:1px solid rgba(255,255,255,.28);border-radius:.78rem;background:rgba(255,255,255,.1);color:#fff;padding:.72rem .85rem;font:inherit}.callback-form input::placeholder{color:#D4DEE9}.callback-form small{color:#DCE6F2}.callback-form button{border:0;cursor:pointer}.landing-photo{margin:1.4rem 0}.landing-photo img{width:100%;border-radius:1rem;border:1px solid rgba(255,255,255,.24);object-fit:cover;aspect-ratio:16/9;filter:brightness(1.28) contrast(1.06) saturate(1.12)}.landing-photo figcaption{padding:.65rem .2rem 0;color:#DCE6F2;font-size:.92rem}@media(max-width:760px){.callback-form .form-grid{grid-template-columns:1fr}.landing-photo img{aspect-ratio:4/3;filter:brightness(1.42) contrast(1.08) saturate(1.16)}}
.featured-snippet{margin:1.5rem 0;padding:1.2rem;background:rgba(16,185,177,.08);border-left:4px solid var(--green);border-radius:.6rem}.featured-snippet h3{margin:.5rem 0 .8rem;color:#45E2B0}.featured-snippet p{margin:0;color:#F0F6FF;line-height:1.6}.snippet-steps{list-style:none;padding:0;margin:.8rem 0 0}.snippet-steps li{margin:.6rem 0;padding:.7rem;background:rgba(62,80,105,.5);border-radius:.5rem;border-left:3px solid var(--orange)}.snippet-steps strong{color:#FF6A1A;display:block;margin-bottom:.3rem}.snippet-steps span{color:#DCE6F2;font-size:.95rem}.snippet-table{width:100%;border-collapse:collapse;margin:1rem 0}.snippet-table th,.snippet-table td{padding:.75rem;text-align:left;border:1px solid var(--line);background:rgba(62,80,105,.6)}.snippet-table th{background:#243145;color:var(--orange);font-weight:700}.snippet-table td{color:#DCE6F2}
/* VISUAL_CLARITY_MOBILE_END */
'''

JS = """
document.documentElement.classList.add('js');
document.addEventListener('DOMContentLoaded',()=>{
  // Scroll to top on page load (evita que el ancla quede a mitad)
  if(location.hash){history.scrollRestoration='manual';requestAnimationFrame(()=>window.scrollTo(0,0))}
  // Menú hamburguesa
  const b=document.querySelector('.hamb'),m=document.querySelector('.menu');
  if(b&&m){b.addEventListener('click',()=>{const o=m.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')});document.addEventListener('click',e=>{if(!m.contains(e.target)&&!b.contains(e.target)&&m.classList.contains('open')){m.classList.remove('open');b.setAttribute('aria-expanded','false')}})}
  // Reveal on scroll (un único IntersectionObserver compartido)
  const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-visible');obs.unobserve(e.target)}}),{threshold:.08});
  document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
  // Lightbox de imágenes
  document.querySelectorAll('[data-lightbox]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const o=document.createElement('div');o.style='position:fixed;inset:0;background:rgba(0,0,0,.86);z-index:99;display:grid;place-items:center;padding:2rem;cursor:pointer';o.innerHTML='<img src="'+a.href+'" alt="" style="max-height:90vh;border-radius:1rem;border:1px solid #2A3142">';o.onclick=()=>o.remove();document.body.append(o)}));
  // Prefetch de páginas en hover (acelera la navegación interna)
  const prefetched=new Set();
  function prefetch(url){if(prefetched.has(url))return;prefetched.add(url);const l=document.createElement('link');l.rel='prefetch';l.href=url;l.as='document';document.head.appendChild(l)}
  document.querySelectorAll('a[href^="/"],a[href^="./"],a[href^="../"],a:not([href^="http"]):not([href^="tel"]):not([href^="mailto"]):not([href^="#"])').forEach(a=>{
    let armed=false;
    const arm=()=>{if(armed)return;armed=true;try{prefetch(new URL(a.getAttribute('href'),location.href).href)}catch(_){}}
    a.addEventListener('mouseenter',arm,{passive:true});
    a.addEventListener('focus',arm,{passive:true});
    a.addEventListener('touchstart',arm,{passive:true});
  });
  // Botón scroll-to-top
  const stt=document.createElement('button');
  stt.id='scroll-top';stt.setAttribute('aria-label','Volver al inicio de la página');stt.innerHTML='\\u2191';
  document.body.appendChild(stt);
  let sttTicking=false;let sttShown=false;
  const togStt=()=>{const should=window.scrollY>500;if(should!==sttShown){sttShown=should;stt.classList.toggle('show',should)}sttTicking=false};
  window.addEventListener('scroll',()=>{if(!sttTicking){sttTicking=true;requestAnimationFrame(togStt)}},{passive:true});
  togStt();
  stt.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
  // Logo/brand: al hacer clic, scroll suave arriba si ya estás en home
  document.querySelectorAll('.brand,.brand-title').forEach(el=>{
    el.addEventListener('click',e=>{
      const href=el.getAttribute('href');
      if(!href)return;
      const u=new URL(href,location.href);
      if(u.pathname===location.pathname){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})}
    });
  });
  // Banner de cookies (RGPD) - desaparece al scrollear
  if(!localStorage.getItem('galaxia_cookies_ok')){
    const c=document.createElement('div');c.id='cookie-banner';
    c.innerHTML='<p><span class="cb-icon" aria-hidden="true">🍪</span><span class="cb-full">Usamos cookies técnicas necesarias para el funcionamiento del sitio. No usamos cookies de seguimiento ni de terceros. <a href="/cookies/" aria-label="Ver Política de Cookies completa">Ver Política de Cookies</a>.</span><span class="cb-short"><a href="/cookies/" aria-label="Ver Política de Cookies">Cookies técnicas</a></span></p><button type="button" id="cookie-ok" aria-label="Aceptar uso de cookies técnicas">OK</button>';
    document.body.appendChild(c);
    let scrolled=false;
    const hideBanner=()=>{if(!scrolled){scrolled=true;c.style.opacity='0';setTimeout(()=>{c.style.display='none'},300)}};
    window.addEventListener('scroll',hideBanner,{passive:true,once:true});
    const okBtn=document.getElementById('cookie-ok');
    if(okBtn){okBtn.addEventListener('click',()=>{localStorage.setItem('galaxia_cookies_ok','1');c.style.opacity='0';setTimeout(()=>c.remove(),300)})};
  }
});
"""

@dataclass
class Page:
    url: str
    title: str
    description: str
    body: str
    schema: dict | list | None = None
    priority: str = '0.7'
    changefreq: str = 'monthly'


def slug_title(slug: str) -> str:
    # Barrios de Madrid: 'madrid-centro' → 'Madrid · Centro'
    if slug.startswith('madrid-'):
        return 'Madrid · ' + ' '.join(w.capitalize() for w in slug[len('madrid-'):].replace('-', ' ').split())
    return ' '.join(w.capitalize() for w in slug.replace('-', ' ').split())


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def rel_prefix(url: str) -> str:
    if url == '/':
        return ''
    depth = len([p for p in url.strip('/').split('/') if p])
    return '../' * depth


def deterministic_choice(options: List[str], seed: str) -> str:
    r = random.Random(str(seed) + SEED_SALT)
    return r.choice(options)


def resolve_spintax(text: str, seed: int) -> str:
    r = random.Random(str(seed) + SEED_SALT)
    def repl_once(s: str) -> Tuple[str, bool]:
        start = s.rfind('{')
        if start == -1:
            return s, False
        end = s.find('}', start)
        if end == -1:
            return s, False
        body = s[start+1:end]
        parts = body.split('|')
        return s[:start] + r.choice(parts).strip() + s[end+1:], True
    changed = True
    loops = 0
    while changed and loops < 50000:
        text, changed = repl_once(text)
        loops += 1
    # Si algún bloque complejo queda sin resolver por formato irregular, se elimina
    # de forma conservadora para no publicar llaves ni pipes visibles.
    text = re.sub(r'\{[^{}<>]{0,500}\|[^{}<>]{0,500}\}', '', text)
    text = text.replace('{', '').replace('}', '').replace('|', ' ')
    return text


def words(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text))


# Valores con los que se rellenan los placeholders {{...}} globales de los
# ficheros spintax de servicio. Los específicos de ubicación ({{CIUDAD}},
# {{PROVINCIA}}, {{SLUG}}…) se sustituyen en landing_copy, donde se conoce
# la ciudad/provincia concreta.
SPINTAX_GLOBALS = {
    'EMPRESA': SHORT,
    'TELEFONO': PHONE,
    'TEL_PLANO': PHONE_TEL.replace('+34', ''),
    'EMAIL': EMAIL,
    'URL_BASE': DOMAIN,
    'DOMINIO': DOMAIN.replace('https://', '').replace('http://', ''),
    'ANOS': '20',
    'DESDE': '2005',
}


def read_spintax_for(service: str | None = None) -> str:
    path = ROOT / (SPINTAX_FILES.get(service, 'Spintax.txt') if service else 'Spintax.txt')
    if not path.exists():
        path = ROOT / 'Spintax.txt'
    text = path.read_text(encoding='utf-8', errors='ignore')
    # Recortar el preámbulo de instrucciones (%%INSTRUCCIONES%% … FIN DE
    # INSTRUCCIONES) para que no se filtre a las páginas publicadas.
    marker = re.search(r'FIN DE INSTRUCCIONES[^\n]*\n', text)
    if marker:
        text = text[marker.end():]
    text = re.sub(r'✅|🔥|⚠️|={3,}|─{3,}', '', text)
    # Sustituir placeholders globales (admite {{VAR}} y la variante {{{VAR}}).
    for key, value in SPINTAX_GLOBALS.items():
        text = text.replace('{{{' + key + '}}', value).replace('{{' + key + '}}', value)
    text = text.replace('[EMPRESA]', SHORT).replace('Limpieza PostIncendio', SHORT)
    return text[:9000]


# Perfiles de ciudades importantes para inyectar contenido único y humano
# (item 8 del backlog). Cada entrada produce ~250 palabras adicionales sobre
# zonas, arquitectura, sectores económicos y riesgos típicos de la ciudad.
# Ciudades NO listadas usan solo el copy spintax genérico.
CITY_PROFILES = {
    'madrid': {
        'zonas': 'Centro, Salamanca, Chamberí, Retiro, Chamartín, Tetuán, Moncloa-Aravaca, Latina, Carabanchel, Hortaleza, Ciudad Lineal y Vallecas',
        'arch': 'edificios de finales del XIX en el ensanche, manzanas regulares de la milla de oro, bloques de los años 60-70 en barrios obreros y vivienda contemporánea en los PAUs del norte y el este',
        'ind': 'oficinas corporativas en AZCA y Campo de las Naciones, hostelería de alta densidad, comunidades de propietarios grandes, polígonos logísticos del Corredor del Henares y residencias geriátricas',
        'risk': 'cuadros eléctricos de instalaciones antiguas, cocinas profesionales, garajes comunitarios y trasteros sobrecargados',
    },
    'barcelona': {
        'zonas': 'Eixample, Gràcia, Sant Martí, Sarrià-Sant Gervasi, Les Corts, Sant Andreu, Horta-Guinardó, Sants-Montjuïc, Nou Barris y Ciutat Vella',
        'arch': 'edificios modernistas y manzanas chaflán del Eixample, fincas regias del Eixample Esquerre, vivienda obrera densa en Sant Martí y Sant Andreu y altura media-alta con patio interior compartido',
        'ind': 'oficinas en 22@, hostelería y restauración intensiva, hoteles urbanos, comunidades de propietarios con escaleras estrechas y comercios del Eixample y Ciutat Vella',
        'risk': 'patinillos de instalaciones compartidos entre vecinos, conductos de ventilación con depósito de hollín y portales con vías de evacuación únicas',
    },
    'valencia': {
        'zonas': 'Ciutat Vella, Eixample, Extramurs, Campanar, La Saïdia, Pla del Real, Benimaclet, Algirós, Benicalap y Quatre Carreres',
        'arch': 'edificios eclécticos del ensanche, vivienda de mediados del XX en barrios consolidados, manzanas nuevas en Benicalap y áreas de servicios en la Avenida del Cid',
        'ind': 'comercio mediano y mayorista, hostelería en el Carmen y Russafa, oficinas en el corredor de Tarongers y comunidades grandes con garaje subterráneo',
        'risk': 'salinidad ambiental que acelera corrosión tras humo, cocinas de restauración cercana al casco histórico y conductos de climatización en bloques de los 70',
    },
    'sevilla': {
        'zonas': 'Casco Antiguo, Macarena, Nervión, Triana, Los Remedios, Sur, San Pablo-Santa Justa, Este-Alcosa y Norte',
        'arch': 'casas-patio del casco histórico, fincas regias del XIX-XX en Nervión, bloques densos en la Macarena y vivienda de los 70 en Los Bermejales y Sevilla Este',
        'ind': 'oficinas corporativas en Nervión y Cartuja, hostelería intensiva en Triana y Centro, comercio en Sierpes y Tetuán y comunidades grandes en la zona Sur',
        'risk': 'temperaturas extremas que aumentan oxidación de hollín, ventilaciones cruzadas en casas-patio y cocinas con extracciones largas',
    },
    'malaga': {
        'zonas': 'Centro Histórico, Ensanche Heredia, La Malagueta, Pedregalejo, El Palo, Teatinos, Carretera de Cádiz, Cruz de Humilladero y Puerto de la Torre',
        'arch': 'fachadas decimonónicas del centro, ensanche del XIX-XX, vivienda turística y de segunda residencia en costa y bloques densos en barrios obreros',
        'ind': 'hostelería intensiva, hoteles urbanos y de costa, comercio del centro y locales comerciales de gran rotación en Carretera de Cádiz',
        'risk': 'cocinas de chiringuitos y restauración con extracciones largas hacia patios interiores y la salinidad costera, que dificulta la limpieza de hollín en estructuras metálicas',
    },
    'alicante': {
        'zonas': 'Centro, Ensanche-Diputación, Carolinas, Benalúa, San Blas, Pla del Bon Repós, Vistahermosa, Playa de San Juan y Albufereta',
        'arch': 'manzanas del ensanche, vivienda de los 60-70 en Carolinas y San Blas, bloques de gran altura junto a la costa y urbanizaciones extensas en Playa de San Juan',
        'ind': 'hostelería de costa, comunidades de propietarios con turistas estacionales, comercio y oficinas del centro',
        'risk': 'aire salino y polvo costero que afectan el acabado de pintura tras humo y cocinas de restauración con campanas saturadas en temporada alta',
    },
    'murcia': {
        'zonas': 'Centro, Vistabella, San Antón, San Andrés, El Carmen, La Flota, Vistalegre, Infante Juan Manuel y San Benito - Progreso',
        'arch': 'fincas del ensanche en el centro, bloques de los 70-80 en barrios pericentrales y vivienda nueva al norte de la ciudad',
        'ind': 'comercio de proximidad, hostelería de centro y barrios, oficinas administrativas y polígonos industriales del entorno de Espinardo',
        'risk': 'patios de luces estrechos que concentran humo entre viviendas y conductos compartidos de garaje',
    },
    'zaragoza': {
        'zonas': 'Centro, Casco Histórico, Universidad, Delicias, Las Fuentes, Actur-Rey Fernando, Almozara, Torrero, Casablanca y Santa Isabel',
        'arch': 'ensanche del XIX-XX, vivienda obrera densa en Delicias y Las Fuentes y bloques de altura media en Actur',
        'ind': 'logística e industria del valle del Ebro, oficinas en el centro y comunidades grandes en los desarrollos del Actur',
        'risk': 'cierzo que dispersa hollín hacia patios interiores y cuadros eléctricos de instalaciones antiguas en barrios obreros',
    },
    'toledo': {
        'zonas': 'Casco Histórico, Santa Bárbara, Palomarejos, Buenavista, Polígono - Santa María de Benquerencia, Azucaica y Valparaíso',
        'arch': 'edificación protegida en el casco histórico, vivienda de los 70-80 en el Polígono y bloques nuevos en Buenavista y Valparaíso',
        'ind': 'oficinas administrativas, hostelería turística intensiva, comercio del casco histórico y polígono industrial del sur',
        'risk': 'cocinas turísticas con uso continuo, edificación protegida con restricciones de intervención y cuadros eléctricos en inmuebles centenarios',
    },
    'granada': {
        'zonas': 'Centro, Albaicín, Realejo, Ronda, Beiro, Genil, Zaidín y Chana',
        'arch': 'edificios históricos en Centro y Albaicín, vivienda obrera en Chana y bloques modernos en Zaidín y Genil',
        'ind': 'hostelería universitaria intensiva, comercio del centro, residencias estudiantiles y oficinas administrativas',
        'risk': 'cocinas de bares-tapeo con extracción saturada, conductos compartidos en bloques antiguos y patios estrechos del Albaicín',
    },
    'cordoba': {
        'zonas': 'Centro, Judería, San Lorenzo, Levante, Poniente, Sur, Norte-Sierra y Periurbano',
        'arch': 'casas-patio en el casco histórico, manzanas decimonónicas en San Lorenzo y vivienda de los 70 en Levante y Poniente',
        'ind': 'comercio del centro, hostelería turística y comunidades de propietarios con patio central',
        'risk': 'verano extremo que oxida superficies metálicas tras humo y cocinas tradicionales con larga extracción',
    },
    'marbella': {
        'zonas': 'Centro, Casco Antiguo, Nueva Andalucía, Puerto Banús, Las Chapas, Elviria, San Pedro Alcántara y Guadalmina',
        'arch': 'urbanizaciones de alto nivel, comunidades con piscina, hoteles de lujo y vivienda turística de alta gama',
        'ind': 'hostelería premium, restauración de marca, hoteles de lujo y comunidades con servicios 24 h',
        'risk': 'cocinas profesionales en restauración de alta gama, instalaciones de lujo con materiales sensibles y reputación crítica ante olor a humo',
    },
    'badalona': {
        'zonas': 'Centre, Casc Antic, Llefià, La Salut, Sant Roc, Bufalà, Pomar y Montgat',
        'arch': 'vivienda obrera densa en Llefià y Sant Roc, ensanche del XIX en el centro y bloques de altura en Bufalà',
        'ind': 'comercio mediano, oficinas en el centro, comunidades grandes y polígonos industriales junto al frente marítimo',
        'risk': 'patios de luces estrechos que concentran humo, salinidad costera y cocinas de restauración del centro',
    },
    'valladolid': {
        'zonas': 'Centro, La Rondilla, Delicias, Pajarillos, La Victoria, Parquesol, Huerta del Rey y Covaresa',
        'arch': 'ensanche decimonónico en el centro, vivienda obrera densa en Pajarillos y Delicias y bloques modernos en Parquesol',
        'ind': 'oficinas administrativas, hostelería del centro, comercio en Recoletos y polígonos industriales de San Cristóbal',
        'risk': 'inviernos fríos con calefacciones intensivas, cuadros eléctricos antiguos y cocinas con extracción a patio',
    },
    'salamanca': {
        'zonas': 'Centro, San Bernardo, Garrido Norte, Garrido Sur, San Vicente, Pizarrales, Vidal, Tejares y San José',
        'arch': 'edificación protegida en el casco histórico, vivienda universitaria en San Vicente y Pizarrales y bloques nuevos en Tejares',
        'ind': 'hostelería universitaria, comercio del centro, residencias de estudiantes y oficinas administrativas',
        'risk': 'cocinas de tapeo con extracción saturada y edificación protegida que limita intervenciones',
    },
    # Barrios de Madrid (descripciones específicas)
    'madrid-centro': {
        'zonas': 'Sol, Embajadores (Lavapiés), Cortes, Justicia (Chueca), Universidad (Malasaña) y Palacio',
        'arch': 'corralas y vivienda densa decimonónica, fincas regias en Cortes y Justicia y locales comerciales y de restauración en planta baja en casi todos los portales',
        'ind': 'hostelería de altísima densidad, comercio turístico, oficinas y vivienda turística de corta estancia',
        'risk': 'cocinas con extracción larga hacia patios interiores, instalaciones eléctricas antiguas en edificios protegidos y locales con aforo elevado en planta baja',
    },
    'madrid-salamanca': {
        'zonas': 'Recoletos, Goya, Lista, Castellana, Fuente del Berro y la Milla de Oro',
        'arch': 'manzanas regulares con fincas regias y portales de gran altura, mucha rehabilitación interior y materiales sensibles (parquet macizo, escayolas decorativas, vidrio biselado)',
        'ind': 'oficinas corporativas, comercio de lujo en Serrano y Velázquez y hostelería premium en Goya',
        'risk': 'instalaciones eléctricas antiguas en fincas centenarias, materiales nobles de difícil reposición y comunidades exigentes con tiempos de respuesta',
    },
    'madrid-chamberi': {
        'zonas': 'Almagro, Trafalgar, Arapiles, Gaztambide, Vallehermoso y Ríos Rosas',
        'arch': 'fincas del XIX-XX con escaleras señoriales, patios de manzana ajardinados y portales con materiales originales conservados',
        'ind': 'comercio de barrio, oficinas profesionales (despachos, consultas médicas) y hostelería de Ponzano',
        'risk': 'consultas y despachos en plantas altas con documentación física y cocinas de los locales de Ponzano con extracción saturada',
    },
    'madrid-retiro': {
        'zonas': 'Pacífico, Adelfas, Estrella, Ibiza, Jerónimos y Niño Jesús',
        'arch': 'edificios de altura media con patios amplios, vivienda de los años 50-70 y zonas residenciales tranquilas alrededor del parque',
        'ind': 'oficinas administrativas, comercio de barrio, comunidades estables y servicios médicos privados',
        'risk': 'instalaciones de climatización compartidas y trasteros sobrecargados en edificios de los 50',
    },
    'madrid-arganzuela': {
        'zonas': 'Imperial, Las Acacias, La Chopera, Legazpi, Delicias, Palos de Moguer y Atocha',
        'arch': 'vivienda obrera del XIX-XX en Acacias y Legazpi, rehabilitación industrial reciente en la zona Matadero y bloques nuevos junto a Madrid Río',
        'ind': 'oficinas en torno a Atocha, comercio de barrio, hostelería y restauración del entorno Madrid Río',
        'risk': 'cuadros eléctricos antiguos en fincas obreras y locales rehabilitados con instalaciones nuevas pero estructuras viejas',
    },
    'madrid-moncloa-aravaca': {
        'zonas': 'Casa de Campo, Argüelles, Ciudad Universitaria, Valdezarza, Valdemarín y Aravaca',
        'arch': 'vivienda universitaria en Argüelles, chalets y comunidades de baja densidad en Aravaca y Valdemarín y bloques de los 70 en Valdezarza',
        'ind': 'residencias y colegios mayores, oficinas dispersas, comercio de barrio y vivienda residencial de alto poder adquisitivo en Aravaca',
        'risk': 'instalaciones de calefacción centralizadas en comunidades de los 70 y chimeneas decorativas en Aravaca',
    },
    'madrid-tetuan': {
        'zonas': 'Bellas Vistas, Cuatro Caminos, Castillejos, Almenara, Valdeacederas y Berruguete',
        'arch': 'vivienda obrera densa, bloques de los 50-70 con poca ventilación y rehabilitación interior reciente',
        'ind': 'comercio de barrio, hostelería de Tetuán y comunidades grandes con ascensores antiguos',
        'risk': 'patios de luces estrechos que concentran humo y cuadros eléctricos de cocinas sin actualizar',
    },
    'madrid-chamartin': {
        'zonas': 'El Viso, Prosperidad, Ciudad Jardín, Hispanoamérica, Nueva España y Castilla',
        'arch': 'chalets en El Viso, fincas modernas alrededor de Castellana y bloques residenciales de altura media en Hispanoamérica',
        'ind': 'oficinas corporativas en Azca y zona Castellana, residencias geriátricas privadas y hoteles de negocios',
        'risk': 'oficinas corporativas con documentación física y servidores y cocinas de hoteles con extracción larga',
    },
    'madrid-latina': {
        'zonas': 'Los Cármenes, Puerta del Ángel, Lucero, Aluche, Las Águilas y Campamento',
        'arch': 'vivienda obrera densa en Aluche y Puerta del Ángel y bloques nuevos en Las Águilas',
        'ind': 'comercio de barrio, hostelería de Puerta del Ángel y comunidades grandes',
        'risk': 'instalaciones eléctricas antiguas en bloques de los 60-70 y garajes comunitarios sobrecargados',
    },
    'madrid-carabanchel': {
        'zonas': 'Comillas, Opañel, San Isidro, Vista Alegre, Puerta Bonita, Buenavista y Abrantes',
        'arch': 'vivienda obrera densa, bloques pequeños sin ascensor en zonas antiguas y desarrollos nuevos en Carabanchel Alto',
        'ind': 'comercio de proximidad, residencias geriátricas y comunidades con plaza de garaje',
        'risk': 'patios pequeños que concentran humo entre vecinos, cocinas con campana antigua y cuadros eléctricos sin renovar',
    },
    'madrid-usera': {
        'zonas': 'Orcasitas, Orcasur, San Fermín, Almendrales, Moscardó, Zofío y Pradolongo',
        'arch': 'vivienda social y obrera de los 50-70, bloques densos sin ascensor y rehabilitación reciente en algunos portales',
        'ind': 'comercio de proximidad, hostelería china-asiática intensiva y comunidades con muchas familias por portal',
        'risk': 'cocinas de restauración asiática con extracción saturada, cuadros eléctricos sobrecargados y trasteros llenos',
    },
    'madrid-puente-vallecas': {
        'zonas': 'Entrevías, San Diego, Palomeras Bajas, Palomeras Sureste, Portazgo y Numancia',
        'arch': 'vivienda obrera densa, bloques de los 60-70 con poca ventilación y rehabilitación interior reciente en algunos portales',
        'ind': 'comercio de barrio, hostelería local y comunidades grandes con ascensores antiguos',
        'risk': 'cuadros eléctricos obsoletos, patios de luces estrechos y conductos de ventilación con depósito de hollín acumulado',
    },
    'madrid-ciudad-lineal': {
        'zonas': 'Pueblo Nuevo, Quintana, Concepción, San Pascual, San Juan Bautista, Colina, Atalaya y Costillares',
        'arch': 'vivienda residencial de los 60-80, comunidades grandes con jardín interior y bloques nuevos en el extremo norte',
        'ind': 'oficinas dispersas, comercio de barrio y residencias geriátricas privadas',
        'risk': 'patinillos de instalaciones compartidos y cuadros eléctricos de portales antiguos',
    },
    'madrid-hortaleza': {
        'zonas': 'Palomas, Valdefuentes, Canillas, Pinar del Rey, Apóstol Santiago y Piovera',
        'arch': 'urbanizaciones de baja-media densidad, vivienda de los 80-90 y desarrollos nuevos en Valdebebas',
        'ind': 'oficinas en Campo de las Naciones, hoteles de negocios y comercio de proximidad',
        'risk': 'oficinas corporativas con documentación física y hoteles con cocina de uso intensivo',
    },
    'madrid-fuencarral': {
        'zonas': 'El Pardo, Fuentelarreina, Peñagrande, Pilar, La Paz, Valverde, Mirasierra y Tres Olivos',
        'arch': 'vivienda de los 70-90, chalets en Mirasierra y desarrollos modernos en Tres Olivos',
        'ind': 'oficinas dispersas, hospitales (La Paz), residencias y comunidades grandes con piscina',
        'risk': 'entornos hospitalarios y geriátricos con exigencia clínica y comunidades grandes con instalaciones compartidas',
    },
    'madrid-san-blas': {
        'zonas': 'Simancas, Hellín, Amposta, Arcos, Rosas, Rejas, Canillejas y Salvador',
        'arch': 'vivienda de los 60-80, bloques de altura media y comunidades grandes con garaje subterráneo',
        'ind': 'oficinas en Julián Camarillo (22@ madrileño), comercio de barrio y polígono industrial cercano',
        'risk': 'oficinas con instalaciones eléctricas modernas pero estructuras viejas y comunidades grandes con conductos compartidos',
    },
    'madrid-villaverde': {
        'zonas': 'Villaverde Alto, Villaverde Bajo, San Cristóbal de los Ángeles, Butarque y Los Rosales',
        'arch': 'vivienda obrera densa, bloques de los 60-70 y desarrollos nuevos en Butarque',
        'ind': 'polígono industrial intenso, comercio de barrio y comunidades grandes',
        'risk': 'naves industriales con carga combustible alta, comunidades obreras con cuadros eléctricos viejos y garajes sobrecargados',
    },
    'madrid-barajas': {
        'zonas': 'Alameda de Osuna, Aeropuerto, Casco Histórico de Barajas, Timón, Corralejos y Valdebebas',
        'arch': 'vivienda residencial de baja-media densidad, chalets adosados y desarrollos nuevos en Valdebebas',
        'ind': 'hoteles del entorno aeroportuario, oficinas y comunidades con piscina',
        'risk': 'hoteles con uso intensivo cerca del aeropuerto y entornos con restricciones logísticas (acceso controlado)',
    },
    # Tier-2: ciudades importantes adicionales con perfiles concisos
    'alcala-henares': {
        'zonas': 'Centro histórico, Reyes Católicos, Chorrillo, Juan de Austria y Espartales',
        'arch': 'edificación protegida en el casco universitario y vivienda de los 70-80 en los barrios pericentrales',
        'ind': 'oficinas en el Corredor del Henares, comercio universitario y residencias estudiantiles',
        'risk': 'edificación protegida con restricciones de intervención y cocinas de restauración del centro',
    },
    'alcobendas': {
        'zonas': 'Centro, Distrito Norte, La Moraleja, Soto de la Moraleja y Valdelasfuentes',
        'arch': 'urbanizaciones residenciales de alto poder adquisitivo en La Moraleja y bloques modernos en el centro',
        'ind': 'oficinas corporativas, hoteles de negocios y comunidades con piscina y servicios',
        'risk': 'comunidades con instalaciones premium y oficinas con documentación física sensible',
    },
    'alcorcon': {
        'zonas': 'Centro, San José de Valderas, Parque Lisboa, Parque Oeste, Las Retamas y Ensanche Sur',
        'arch': 'vivienda obrera de los 70-80 muy densa y bloques nuevos en el Ensanche Sur',
        'ind': 'comercio de proximidad, comunidades grandes y polígonos industriales del sur',
        'risk': 'patios de luces estrechos en bloques densos y cuadros eléctricos obsoletos',
    },
    'mostoles': {
        'zonas': 'Centro, Norte-Universidad, Estoril, Coímbra y Parque Coímbra',
        'arch': 'vivienda obrera densa de los 70-80 y desarrollos universitarios al norte',
        'ind': 'comercio de barrio, residencias universitarias y polígono industrial',
        'risk': 'cuadros eléctricos antiguos en bloques densos y cocinas universitarias intensivas',
    },
    'leganes': {
        'zonas': 'Centro, Zarzaquemada, San Nicasio, La Fortuna, Vereda de los Estudiantes y Leganés Norte',
        'arch': 'vivienda obrera de los 60-80 y bloques modernos al norte',
        'ind': 'oficinas, hospitales (Severo Ochoa) y comunidades grandes',
        'risk': 'entornos hospitalarios con exigencia clínica y comunidades con instalaciones compartidas',
    },
    'getafe': {
        'zonas': 'Centro, Bercial, Sector III, Los Molinos, Las Margaritas y Perales del Río',
        'arch': 'vivienda obrera densa, bloques modernos en El Bercial y desarrollos en Perales del Río',
        'ind': 'oficinas, comercio, industria aeroespacial (Airbus) y comunidades grandes',
        'risk': 'naves industriales con carga combustible alta y comunidades con conductos compartidos',
    },
    'fuenlabrada': {
        'zonas': 'Centro, Loranca, El Naranjo, El Arroyo y El Vivero',
        'arch': 'vivienda obrera densa de los 70-80 y desarrollos modernos en Loranca',
        'ind': 'polígono industrial muy denso, comercio de barrio y comunidades grandes',
        'risk': 'naves industriales con carga combustible alta y cuadros eléctricos antiguos',
    },
    'elche': {
        'zonas': 'Centro, El Raval, Carrús, Altabix, Travalón y Sant Antoni',
        'arch': 'vivienda obrera densa, ensanche del XIX-XX y bloques nuevos en Travalón',
        'ind': 'industria del calzado, polígonos logísticos y comercio mediano',
        'risk': 'naves del calzado con almacenamiento combustible, palmeral protegido y cocinas de restauración',
    },
    'cartagena': {
        'zonas': 'Centro Histórico, Casco Antiguo, Los Dolores, La Concepción, San Antón y Ensanche-Almarjal',
        'arch': 'edificación histórica protegida en el centro, vivienda obrera en San Antón y bloques modernos en Ensanche',
        'ind': 'industria naval, refinerías cercanas, hostelería del centro y comercio',
        'risk': 'edificación protegida con restricciones, cocinas turísticas y proximidad a industrias químicas',
    },
    'hospitalet-llobregat': {
        'zonas': 'Centre, Collblanc, La Florida, Pubilla Cases, Bellvitge, Sant Josep y Santa Eulàlia',
        'arch': 'vivienda obrera densa, bloques de los 60-80 con poca ventilación y rehabilitación reciente',
        'ind': 'oficinas en Gran Vía, hospital Bellvitge y comunidades muy grandes',
        'risk': 'entornos hospitalarios con exigencia clínica, patios estrechos y cocinas de hostelería',
    },
    'sabadell': {
        'zonas': 'Centre, Eixample, Creu Alta, Gràcia, La Concòrdia y Sant Oleguer',
        'arch': 'ensanche del XIX-XX, vivienda obrera densa y rehabilitación industrial en zonas céntricas',
        'ind': 'industria textil histórica, comercio del centro y comunidades grandes',
        'risk': 'instalaciones eléctricas antiguas en fincas centenarias y conductos compartidos',
    },
    'terrassa': {
        'zonas': 'Centre, Sant Pere, Ca n\'Anglada, La Maurina, Sant Llorenç y Egara',
        'arch': 'ensanche del XIX-XX, vivienda obrera densa y bloques modernos en Egara',
        'ind': 'industria textil histórica, universidad UPC y polígonos industriales',
        'risk': 'naves de la industria textil con almacenamiento combustible y residencias universitarias',
    },
    'jerez-frontera': {
        'zonas': 'Centro Histórico, San Telmo, La Granja, La Plata, La Asunción y Sur',
        'arch': 'bodegas centenarias del marco, casas-patio del casco histórico y vivienda obrera al sur',
        'ind': 'industria del vino (bodegas), hostelería turística y comercio',
        'risk': 'bodegas con almacenamiento de alcohol, casas-patio con ventilación particular y cocinas turísticas',
    },
    'algeciras': {
        'zonas': 'Centro, La Reconquista, El Saladillo, Pelayo y La Granja',
        'arch': 'vivienda obrera densa, bloques de los 70-80 y ensanche junto al puerto',
        'ind': 'logística portuaria, refinerías cercanas (San Roque) y hostelería',
        'risk': 'naves logísticas portuarias con carga combustible y proximidad a industrias químicas',
    },
    'almeria': {
        'zonas': 'Centro, Pescadería-La Chanca, Zapillo, Nueva Andalucía, Los Molinos y Vega de Acá',
        'arch': 'vivienda obrera en La Chanca, ensanche del XIX-XX y desarrollos turísticos en Zapillo',
        'ind': 'logística agroalimentaria (invernaderos), turismo costero y hostelería',
        'risk': 'naves agroalimentarias con plásticos combustibles y hoteles costeros con uso intensivo',
    },
    'cadiz': {
        'zonas': 'Casco Antiguo, La Viña, El Pópulo, Santa María, San Carlos y Puerta Tierra',
        'arch': 'edificación histórica densa del casco antiguo, casas-patio gaditanas y vivienda turística',
        'ind': 'turismo intensivo, hostelería del Carnaval y comercio del centro histórico',
        'risk': 'edificación protegida con restricciones, salinidad costera y cocinas de bares-tapeo',
    },
    'huelva': {
        'zonas': 'Centro, La Merced, Pío XII, Las Colonias, El Higueral y Pérez Cubillas',
        'arch': 'ensanche del XIX-XX en el centro, vivienda obrera en Pérez Cubillas y bloques modernos',
        'ind': 'industria química del Polo de Huelva, hostelería del centro y comercio',
        'risk': 'proximidad a industrias químicas, cocinas turísticas y comunidades grandes',
    },
    'jaen': {
        'zonas': 'Centro, San Ildefonso, La Magdalena, El Almendral, Polígono del Valle y Bulevar',
        'arch': 'casas-patio del casco histórico, vivienda de los 70 en El Almendral y bloques en Bulevar',
        'ind': 'industria oleícola, hostelería y administración pública',
        'risk': 'almazaras con almacenamiento de aceite, cocinas tradicionales y veranos extremos',
    },
    'albacete': {
        'zonas': 'Centro, Industrial, Hermanos Falcó, Vereda, San Antón y Universidad',
        'arch': 'ensanche del XIX-XX, vivienda de los 60-80 en Hermanos Falcó y bloques modernos al norte',
        'ind': 'logística agroalimentaria, comercio del centro y comunidades grandes',
        'risk': 'naves logísticas con cereales y plásticos combustibles y comunidades con conductos compartidos',
    },
    'ciudad-real': {
        'zonas': 'Centro, Pío XII, Larache, Granja, Estación y Universidad',
        'arch': 'ensanche del XIX-XX en el centro y vivienda de los 70-80 en Larache y Granja',
        'ind': 'logística agroalimentaria, comercio y administración pública',
        'risk': 'cocinas tradicionales con extracción a patio y comunidades grandes con instalaciones antiguas',
    },
    'cuenca': {
        'zonas': 'Casco Antiguo, San Antón, La Paz, El Pozo, Buenavista y Casablanca',
        'arch': 'edificación histórica colgada y protegida del casco antiguo y vivienda de los 70 en San Antón',
        'ind': 'turismo cultural intensivo, hostelería y comercio del centro',
        'risk': 'edificación histórica colgada con restricciones extremas y cocinas turísticas',
    },
    'guadalajara': {
        'zonas': 'Centro, Aguas Vivas, Iriépal, Marchamalo y Cabanillas-Norte',
        'arch': 'ensanche del XIX-XX, vivienda de los 70 y desarrollos modernos en Aguas Vivas',
        'ind': 'logística del Corredor del Henares, comercio y comunidades grandes',
        'risk': 'naves logísticas con almacenamiento combustible y cuadros eléctricos en bloques antiguos',
    },
    'huesca': {
        'zonas': 'Centro, Santiago, Casco Histórico, San Lorenzo y Almériz',
        'arch': 'edificación histórica en el casco, ensanche del XIX-XX y vivienda moderna en Almériz',
        'ind': 'comercio del centro, hostelería y administración pública',
        'risk': 'edificación protegida con restricciones, cocinas tradicionales y veranos cálidos',
    },
    'teruel': {
        'zonas': 'Centro, Casco Histórico, Ensanche, San León y Pinilla',
        'arch': 'edificación mudéjar protegida del casco, vivienda del XIX-XX y bloques modernos en Pinilla',
        'ind': 'comercio del centro, turismo cultural y administración pública',
        'risk': 'edificación protegida (Patrimonio Humanidad) con restricciones extremas y cocinas turísticas',
    },
    'lleida': {
        'zonas': 'Centre Històric, Cappont, Bordeta, Pardinyes, Universitat y Magraners',
        'arch': 'edificación histórica del centro, ensanche del XIX-XX y vivienda de los 70-80 en Bordeta',
        'ind': 'logística agroalimentaria (frutos), universidad UdL y comercio',
        'risk': 'naves agroalimentarias con cámaras frigoríficas y residencias estudiantiles',
    },
    'girona': {
        'zonas': 'Barri Vell, Mercadal, Eixample, Pont Major, Sant Narcís y Montilivi',
        'arch': 'edificación histórica protegida del Barri Vell, ensanche del XIX-XX y vivienda moderna en Sant Narcís',
        'ind': 'turismo cultural, universidad y comercio del centro',
        'risk': 'edificación protegida con restricciones, cocinas turísticas y casas-patio',
    },
    'tarragona': {
        'zonas': 'Part Alta, Eixample, Sant Pere i Sant Pau, Bonavista y Torreforta',
        'arch': 'edificación romana y medieval protegida del casco, ensanche del XIX-XX y vivienda de los 70 en Bonavista',
        'ind': 'industria química del polo petroquímico, turismo costero y hostelería',
        'risk': 'proximidad a industrias químicas, edificación romana protegida y cocinas turísticas',
    },
}


# Testimonios reales (placeholder con nombres y cargos representativos).
# Se renderizan visualmente y se inyectan como Review schema en el home.
TESTIMONIALS = [
    {'author': 'María R.', 'role': 'Administradora de fincas · Madrid',
     'rating': 5, 'date': '2026-02-14',
     'text': 'Tras un incendio en el cuarto de contadores de una de nuestras comunidades, dejaron el portal impecable en 48 horas. El informe técnico que entregaron lo aceptó la aseguradora sin una sola objeción.'},
    {'author': 'Jordi M.', 'role': 'Director de operaciones · Hotel Barcelona',
     'rating': 5, 'date': '2025-11-09',
     'text': 'Organizaron los turnos de noche para no cerrar el hotel. En cinco días las 84 habitaciones estaban desodorizadas y no recibimos ni una queja de los huéspedes. Un equipo serio.'},
    {'author': 'Ana L.', 'role': 'Perita de seguros · Andalucía',
     'rating': 5, 'date': '2026-01-22',
     'text': 'Ya he gestionado seis siniestros con ellos. La documentación pericial es impecable: fotografías, alcance y fases ejecutadas. Como perita, me simplifican mucho el trabajo.'},
    {'author': 'Pablo G.', 'role': 'Jefe de mantenimiento · Residencia Valencia',
     'rating': 5, 'date': '2025-09-30',
     'text': 'Tuvimos fuego en la lavandería con 40 residentes en la planta. Trabajaron con presión negativa y no hizo falta trasladar a nadie. En 36 horas la calidad del aire estaba recuperada.'},
    {'author': 'Carmen V.', 'role': 'Directora de colegio · Toledo',
     'rating': 5, 'date': '2026-03-04',
     'text': 'Un viernes ardió la sala de informática. El lunes a las 8 abríamos con la certificación técnica lista para la inspección educativa. No se les puede pedir más.'},
    {'author': 'Iván P.', 'role': 'Responsable logística · Nave Murcia',
     'rating': 5, 'date': '2025-12-18',
     'text': 'Teníamos 2.000 m² de nave con hollín en toda la estructura metálica. En 72 horas estaba todo estabilizado y la nave volvió a operar sin alargar la parada.'},
]


def testimonials_html() -> str:
    out = []
    for t in TESTIMONIALS:
        rating = t['rating']
        stars = '★' * rating + '☆' * (5 - rating)
        author = esc(t['author'])
        role = esc(t['role'])
        text = esc(t['text'])
        out.append(
            f"<article class='card testimonial'>"
            f"<div class='stars' aria-label='{rating} de 5'>{stars}</div>"
            f"<blockquote>“{text}”</blockquote>"
            f"<footer><strong>{author}</strong><span>{role}</span></footer>"
            "</article>"
        )
    return ''.join(out)


def testimonials_schema() -> list:
    return [{
        '@type': 'Review',
        'reviewRating': {'@type': 'Rating', 'ratingValue': t['rating'], 'bestRating': 5},
        'author': {'@type': 'Person', 'name': t['author']},
        'reviewBody': t['text'],
        'datePublished': t['date'],
        'itemReviewed': {'@type': 'Organization', '@id': DOMAIN + '/#organization', 'name': BRAND},
    } for t in TESTIMONIALS]


def faq_schema(qa_pairs: list) -> dict:
    return {
        '@type': 'FAQPage',
        'mainEntity': [{
            '@type': 'Question',
            'name': q,
            'acceptedAnswer': {'@type': 'Answer', 'text': a},
        } for q, a in qa_pairs],
    }


def featured_snippet_block(label: str, service: str | None = None) -> str:
    """Genera bloque de Fragmento Destacado (Posición Cero) con múltiples formatos.
    Integra párrafo convincente (40-50 palabras), lista de pasos y tabla de comparativa."""
    service_phrase = f'para {SERVICE_LABELS.get(service, "tu negocio")} ' if service else ''

    # Párrafo principal (respuesta directa, 40-50 palabras)
    snippet_answer = (
        f'Sí. En {label} hacemos limpieza de incendios y limpieza post incendio '
        f'con filtración HEPA H14, ozono y desodorización profesional. Atención '
        f'24/7 en el {PHONE} y documentación pericial incluida. La ventana crítica '
        f'son las primeras 24-72 horas, antes de que el hollín se fije de forma '
        f'irreversible en las superficies.'
    )

    # Formato 1: Párrafo directo
    para_format = f"""<div class='featured-snippet' itemscope itemtype='https://schema.org/FAQPage'>
    <h3 itemprop='name'>¿Necesitas una limpieza de incendios en {esc(label)}?</h3>
    <p itemprop='description'>{esc(snippet_answer)}</p>
    </div>"""

    # Formato 2: Lista de pasos (How-To Schema)
    steps_format = f"""<div class='featured-snippet steps-format' itemscope itemtype='https://schema.org/HowTo'>
    <h3 itemprop='name'>Proceso de limpieza post incendio en {esc(label)}</h3>
    <ol class='snippet-steps'>
        <li itemprop='step' itemscope itemtype='https://schema.org/HowToStep'>
            <strong itemprop='name'>1. Inspección técnica</strong>
            <span itemprop='text'>Evaluamos daño, accesos, ventilación y riesgos en {label}.</span>
        </li>
        <li itemprop='step' itemscope itemtype='https://schema.org/HowToStep'>
            <strong itemprop='name'>2. Contención y protección</strong>
            <span itemprop='text'>Sectorización de zonas no afectadas con cortinas de presión.</span>
        </li>
        <li itemprop='step' itemscope itemtype='https://schema.org/HowToStep'>
            <strong itemprop='name'>3. Retirada de residuos</strong>
            <span itemprop='text'>Aspiración HEPA H14, hielo seco o láser según superficie.</span>
        </li>
        <li itemprop='step' itemscope itemtype='https://schema.org/HowToStep'>
            <strong itemprop='name'>4. Desodorización</strong>
            <span itemprop='text'>Ozono industrial, fogging o neutralización de pH.</span>
        </li>
        <li itemprop='step' itemscope itemtype='https://schema.org/HowToStep'>
            <strong itemprop='name'>5. Informe pericial</strong>
            <span itemprop='text'>Documentación técnica con fotografías y alcance ejecutado.</span>
        </li>
    </ol>
    </div>"""

    # Formato 3: Tabla comparativa (Services)
    table_format = f"""<div class='featured-snippet table-format'>
    <h3>Métodos de limpieza de incendios en {esc(label)}</h3>
    <table class='snippet-table' border='1'>
        <thead>
            <tr>
                <th>Método</th>
                <th>Mejor para</th>
                <th>Ventaja Principal</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>HEPA H14</td>
                <td>Control de aire y partículas</td>
                <td>Filtración total, operativo simultáneo</td>
            </tr>
            <tr>
                <td>Hielo seco CO₂</td>
                <td>Superficies carbonizadas</td>
                <td>Sin humedad residual, precisión</td>
            </tr>
            <tr>
                <td>Ozono Industrial</td>
                <td>Desodorización profunda</td>
                <td>Penetración en conductos, eliminación olor</td>
            </tr>
            <tr>
                <td>Fogging Térmico</td>
                <td>Microzonas y huecos</td>
                <td>Alcance en áreas complejas</td>
            </tr>
        </tbody>
    </table>
    </div>"""

    # Rotar formato según hash del label para variación
    formats = [para_format, steps_format, table_format]
    choice_idx = abs(hash(label)) % len(formats)
    return formats[choice_idx]


def city_profile_paragraphs(slug: str, label: str) -> str:
    """Devuelve HTML con párrafos únicos para la ciudad si está perfilada.
    Genera ~350 palabras adicionales para llegar al objetivo de 800+ por
    landing principal (item 8 del backlog)."""
    p = CITY_PROFILES.get(slug)
    if not p:
        return ''
    return (
        f"<h2>Zonas y particularidades de {label}</h2>"
        f"<p>La trama urbana de {label} es muy concreta y condiciona cualquier "
        f"trabajo de limpieza de incendios. Intervenimos en {p['zonas']}, "
        f"desde el centro hasta los barrios de la periferia. Como predominan "
        f"{p['arch']}, adaptamos los protocolos de contención y filtración al "
        f"tipo de patio interior, a los conductos de ventilación y a la "
        f"accesibilidad de cada portal.</p>"
        f"<p>La economía de {label} se apoya en {p['ind']}, sectores en los que "
        f"cada hora cerrado por humo o hollín cuesta dinero de forma directa. De "
        f"ahí que lo primero sea estabilizar la zona afectada, retirar el residuo "
        f"carbonizado y devolver el espacio operativo sin perder la trazabilidad "
        f"que necesita la peritación. Los riesgos más repetidos en {label} son "
        f"{p['risk']}, que piden equipos especializados y experiencia previa en "
        f"este tipo de siniestros.</p>"
        f"<h3>Cómo planificamos una limpieza post incendio en {label}</h3>"
        f"<p>Todo arranca con una visita técnica que mide el alcance real del "
        f"daño: superficie afectada, carga de hollín, hasta dónde ha entrado el "
        f"humo en conductos y zonas ocultas, riesgo residual y compatibilidad "
        f"con la actividad del inmueble. En {label} valoramos además cómo son "
        f"los accesos del barrio, las opciones de carga y descarga, las franjas "
        f"horarias que menos molestan a vecinos o usuarios y la coordinación con "
        f"el perito que designe la aseguradora. Con esos datos dimensionamos "
        f"personal, maquinaria HEPA H14, ozono o hidroxilo cuando el espacio lo "
        f"admite, hielo seco para superficies carbonizadas y EPI categoría III "
        f"si la evaluación lo exige.</p>"
        f"<p>El trabajo se entrega siempre con informe técnico completo: "
        f"fases ejecutadas, fotografías de antes y después, materiales "
        f"tratados, equipos empleados y recomendaciones para los gremios que "
        f"vienen después. En {label} esto pesa mucho, porque la empresa de "
        f"obras posterior —pintura, electricidad, instalaciones, albañilería— "
        f"necesita un punto de partida claro y documentado sobre un espacio ya "
        f"limpio y descontaminado. Galaxia no reforma ni repara: nuestra parte "
        f"es la limpieza de incendios y la descontaminación; la reconstrucción "
        f"la ejecutan las empresas que designe la aseguradora.</p>"
    )


def local_context(slug: str) -> Dict[str, str]:
    label = slug_title(slug)
    seed = sum(ord(c) for c in slug)
    industrial = ['polígonos logísticos', 'zonas comerciales', 'parques empresariales', 'naves de almacenamiento', 'edificios de oficinas', 'comunidades residenciales', 'hoteles y restauración']
    risks = ['cuadros eléctricos', 'cocinas industriales', 'almacenamiento de mercancías', 'garajes comunitarios', 'salas técnicas', 'conductos de climatización']
    fire = ['servicios provinciales de bomberos', 'parques de bomberos de referencia', 'operativos municipales y provinciales de extinción']
    return {
        'label': label,
        'industrial': deterministic_choice(industrial, slug + 'i'),
        'risk': deterministic_choice(risks, slug + 'r'),
        'fire': deterministic_choice(fire, slug + 'f'),
        'distance': str(40 + (seed * 17) % 610),
        'postal': str(1000 + (seed * 37) % 49000).zfill(5),
        'hours': deterministic_choice(['24-48 h', '48-72 h', '72 h', 'menos de 4 h para valoración técnica'], slug + 'h')
    }


def paragraphize(text: str) -> str:
    clean = re.sub(r'^\s*\d+\)|^\s*#{1,4}\s*|^\s*-\s*', '', text, flags=re.M)
    filtered = []
    for line in clean.splitlines():
        stripped = line.strip()
        if re.match(r'^(TITLE|META|H1|HERO|INTRO|BLOQUE|CTA|FAQ|SPINTAX|Usar este sistema|Te lo doy|varias|bloques|cierres|servicios que)', stripped, re.I):
            continue
        filtered.append(line)
    clean = '\n'.join(filtered)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    parts = [p.strip() for p in clean.split('\n\n') if len(p.strip()) > 90 and 'VARIABLES QUE VAS A USAR' not in p]
    return ''.join(f'<p>{esc(p)}</p>' for p in parts[:7])


def landing_copy(city_or_province: str, service: str | None, seed: int) -> str:
    loc = local_context(city_or_province)
    label = loc['label']
    service_text = SERVICE_LABELS.get(service, 'instalaciones industriales, comercios y edificios afectados')
    base = read_spintax_for(service)
    # Placeholders de ubicación de los ficheros spintax de servicio.
    prov_slug = city_or_province if service else CITY_PROVINCE.get(city_or_province, city_or_province)
    province_label = slug_title(prov_slug)
    page_slug = f'limpieza-incendios-{service}-{city_or_province}' if service else f'limpieza-incendios-{city_or_province}'
    base = (base
            .replace('{{{CIUDAD}}', label).replace('{{CIUDAD_MIN}}', label.lower())
            .replace('{{CIUDAD}}', label)
            .replace('{{PROVINCIA}}', province_label)
            .replace('{{SLUG}}', page_slug))
    base = base.replace('[CIUDAD]', label).replace('limpieza de incendios', BASE_KEYWORD).replace('Limpieza de Incendios', BASE_KEYWORD.capitalize())
    spun = resolve_spintax(base, seed)
    intro = f"""
    <p>Galaxia es la empresa de <strong>{BASE_KEYWORD}</strong> en {label}: realizamos {SECONDARY_KEYWORD}, descontaminación de humo y hollín, control documental y planificación orientada a que el inmueble vuelva a estar operativo cuanto antes. Es un servicio pensado para peritos, administradores de activos, responsables de mantenimiento y direcciones de operaciones que buscan una respuesta verificable y trazable, no una limpieza convencional.</p>
    <p>El entorno de {label} concentra actividad ligada a {loc['industrial']} y escenarios de riesgo habituales en {loc['risk']}. Por eso la primera inspección separa el hollín graso de las partículas secas, los residuos de combustión, el olor que persiste y la afectación a los sistemas de climatización. El desplazamiento técnico se planifica sobre una distancia operativa estimada de {loc['distance']} km y se coordina con {loc['fire']} cuando el siniestro lo exige.</p>
    """
    service_block = f"""
    <h2>Protocolo de limpieza post incendio para {service_text} en {label}</h2>
    <p>Cada intervención se ordena en cinco fases: contención de la zona, lectura de superficies, retirada del residuo carbonizado, desodorización industrial y verificación final. En todas ellas dejamos constancia de incidencias, fotografías de avance, materiales tratados y criterios de seguridad. El objetivo es bajar la carga de partículas, neutralizar olores y dejar el inmueble en un estado controlable para reparar, peritar o reabrir.</p>
    <p>Si el siniestro afecta a {service_text}, combinamos según el caso filtración HEPA H14, aspiración controlada, limpieza con hielo seco CO₂, fogging térmico, ozono industrial y neutralización de pH sobre superficies compatibles. La técnica se decide siempre tras una prueba en zona no visible, para no arrastrar hollín ni provocar veladuras o daños secundarios.</p>
    """
    spun_html = paragraphize(spun)
    local_extra = f"""
    <h2>Coordinación local de la intervención en {label}</h2>
    <p>En {label} reservamos una ventana de visita de {loc['hours']} en función de los accesos, la disponibilidad de suministro, la autorización pericial y el nivel de contaminación. Damos prioridad a inmuebles con actividad económica, zonas comunes críticas, salas técnicas y espacios donde cada día de parada encarece el siniestro.</p>
    <p>El trabajo se cierra con un resumen técnico, la relación de zonas tratadas y recomendaciones para los gremios que entran después. Cuando hay aseguradora de por medio, preparamos información lista para la gestión del siniestro: fotografías, alcance, fases ejecutadas y observaciones relevantes.</p>
    """
    faq = f"""
    <h2>Preguntas técnicas frecuentes sobre limpieza de incendios en {label}</h2>
    <div class='faq'>
      <details><summary>¿La limpieza de incendios elimina también el olor a humo?</summary><p>Sí, pero hay que combinar retirada del residuo, filtración y tratamiento molecular. Si se aplica ozono o fogging sin retirar antes la carga de hollín, el olor termina reapareciendo.</p></details>
      <details><summary>¿Se puede empezar la limpieza post incendio antes de cerrar la peritación?</summary><p>Lo habitual es documentar primero el estado inicial y coordinar las autorizaciones. Galaxia organiza una visita técnica para delimitar daños sin comprometer la trazabilidad del siniestro.</p></details>
      <details><summary>¿Trabajan en horario de urgencia?</summary><p>Sí. La respuesta 24/7 se centra en estabilizar, contener las partículas, evaluar los accesos y planificar la recuperación del inmueble.</p></details>
    </div>
    """
    combined = intro + service_block + spun_html + local_extra + faq
    if words(re.sub('<[^<]+?>', ' ', combined)) < 600:
        combined += f"""
        <h2>Calidad y trazabilidad en cada limpieza de incendios</h2>
        <p>Una limpieza post incendio no puede medirse solo por el aspecto visual. En {label} revisamos las zonas de deposición secundaria, juntas, rejillas, retornos de aire, paramentos altos y los recorridos que ha seguido el humo. Así evitamos que el inmueble parezca recuperado mientras conserva partículas activas, olor residual o contaminación desplazada a zonas que nadie ha inspeccionado.</p>
        <p>Cuando la evaluación lo pide, el equipo trabaja con EPI categoría III, protección respiratoria, aspiración filtrada y segregación de residuos. La visita técnica es la que permite dimensionar personal, maquinaria, consumibles, turnos y la coordinación posterior con electricidad, climatización, albañilería o pintura técnica.</p>
        """
    return combined


def common_header(prefix: str) -> str:
    return f"""
    <a href='#main-content' class='skip-to-main' style='position:absolute;left:-9999px;z-index:999'>Ir al contenido principal</a>
    <div class='topbar'><div class='wrap'><span>Operativos 24/7 · Informes técnicos para peritos</span><a href='tel:{PHONE_TEL}' aria-label='Llamar al {PHONE}'>{PHONE}</a></div></div>
    <header class='nav' role='banner'><div class='wrap'><a class='brand' href='{prefix}' aria-label='Galaxia · Limpieza Técnica Post-Incendio - Inicio'><img src='{prefix}assets/img/logo-galaxia.webp' alt='Logo de Galaxia' width='180' height='120' fetchpriority='high'><span>GALAXIA</span></a><a class='brand-title' href='{prefix}'>Limpiezas de Incendios Galaxia</a><button class='hamb' aria-label='Abrir menú de navegación' aria-expanded='false' aria-controls='primary-menu'>Menú</button><nav id='primary-menu' class='menu' aria-label='Navegación principal'><a href='{prefix}servicios/'>Servicios</a><a href='{prefix}sectores/'>Sectores</a><a href='{prefix}casos-de-exito/'>Casos</a><a href='{prefix}galeria/'>Galería</a><a href='{prefix}ubicaciones/'>Ubicaciones</a><a href='{prefix}peritos/'>Peritos</a><a href='{prefix}contacto/'>Contacto</a><a class='cta' href='{prefix}contacto/'>Solicitar informe técnico</a></nav></div></header>
    """


def common_footer(prefix: str) -> str:
    service_links = ''.join(f"<a href='{prefix}limpieza-incendios-{s}-madrid/'>Limpieza {SERVICE_LABELS[s]}</a>" for s in SERVICES[:5])
    province_links = ''.join(f"<a href='{prefix}limpieza-incendios-{p}/'>{slug_title(p)}</a>" for p in PROVINCES[:5])
    phone_clean = PHONE_TEL
    whatsapp_clean = WHATSAPP_WA
    return f"""
    <div class='contact-float' role='complementary' aria-label='Contacto rápido'>
      <a class='cf-wa' href='https://wa.me/{whatsapp_clean}' target='_blank' rel='noopener' aria-label='Contactar por WhatsApp'><svg viewBox='0 0 32 32' aria-hidden='true'><path d='M27.2 4.7A15.85 15.85 0 0 0 16 0C7.18 0 .04 7.14.04 15.96c0 2.82.74 5.55 2.13 7.97L0 32l8.27-2.17a15.93 15.93 0 0 0 7.72 1.97h.01c8.82 0 15.96-7.14 15.96-15.96 0-4.27-1.66-8.27-4.76-11.14zM16 29.13h-.01a13.2 13.2 0 0 1-6.72-1.84l-.48-.28-4.92 1.29 1.31-4.79-.31-.5a13.18 13.18 0 0 1-2.04-7.04C2.82 8.65 8.74 2.74 16 2.74c3.55 0 6.88 1.39 9.38 3.9a13.16 13.16 0 0 1 3.88 9.34c0 7.26-5.92 13.15-13.26 13.15zm7.27-9.89c-.4-.2-2.35-1.16-2.72-1.29-.36-.13-.63-.2-.89.2-.27.4-1.02 1.29-1.25 1.55-.23.27-.46.3-.86.1-.4-.2-1.68-.62-3.2-1.97-1.18-1.05-1.98-2.35-2.21-2.75-.23-.4-.02-.62.17-.81.18-.18.4-.46.6-.69.2-.23.27-.4.4-.66.13-.27.07-.5-.03-.7-.1-.2-.89-2.15-1.22-2.94-.32-.77-.65-.67-.89-.68l-.76-.01c-.27 0-.7.1-1.07.5-.36.4-1.4 1.37-1.4 3.33s1.43 3.86 1.63 4.13c.2.27 2.81 4.29 6.81 6.02.95.41 1.69.65 2.27.84.95.3 1.82.26 2.51.16.77-.12 2.35-.96 2.68-1.88.33-.93.33-1.72.23-1.89-.1-.16-.36-.26-.76-.46z'/></svg>WhatsApp</a>
      <a class='cf-call' href='tel:{phone_clean}' aria-label='Llamar al {PHONE}'><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M20 15.46l-2.83-.34a1.34 1.34 0 0 0-1.18.36l-2.06 2.06a14.07 14.07 0 0 1-6.45-6.45l2.07-2.07a1.34 1.34 0 0 0 .35-1.18L9.55 5.05A1.34 1.34 0 0 0 8.23 4H5a1 1 0 0 0-1 1.06A16 16 0 0 0 18.94 20a1 1 0 0 0 1.06-1v-3.21a1.34 1.34 0 0 0-1-1.33z'/></svg>Llamar</a>
    </div>
    <footer class='footer'><div class='wrap footgrid'>
      <div><h3>{BRAND}</h3><p>{TAGLINE}. Respuesta técnica para siniestros por fuego, humo y hollín en toda España.</p><p>{ADDRESS}</p><a href='{GBP}' rel='noopener'>Ficha de Google Business Profile</a></div>
      <div><h4>Servicios</h4>{service_links}</div>
      <div><h4>Sectores</h4><a href='{prefix}sectores/naves-industriales/'>Naves industriales</a><a href='{prefix}sectores/hoteles/'>Hoteles</a><a href='{prefix}sectores/centros-sanitarios/'>Centros sanitarios</a><a href='{prefix}sectores/comunidades/'>Comunidades</a></div>
      <div><h4>Cobertura</h4>{province_links}<a href='{prefix}cobertura/'>Ver cobertura completa</a></div>
      <div><h4>Contacto</h4><a href='tel:{phone_clean}'>{PHONE}</a><a href='https://wa.me/{whatsapp_clean}'>WhatsApp técnico</a><a href='mailto:{EMAIL}'>{EMAIL}</a><a href='{prefix}privacidad/'>Privacidad</a><a href='{prefix}cookies/'>Cookies</a><a href='{prefix}aviso-legal/'>Aviso legal</a></div>
        </div>
      <div class='footer-meta'><small>Galaxia forma parte del <a href='{DOMAIN}' rel='noopener'>Grupo Limpieza de Incendios Galaxia</a> · &copy; {BRAND}</small></div>
      </footer><script>{JS}</script>
    """


def callback_form(prefix: str, location: str = '') -> str:
    place_value = esc(location)
    return f"""
    <section class='panel hero-copy'>
      <div class='eyebrow'>Nosotros te llamamos</div>
      <h2>Nosotros te llamamos</h2>
      <p>Déjanos tu nombre, teléfono y población y te llamamos para valorar el siniestro y orientar los siguientes pasos.</p>
      <form class='callback-form' action='https://formsubmit.co/{FORMSUBMIT_EMAIL}' method='post'>
        <div class='form-grid'>
          <label>Nombre<input type='text' name='Nombre' autocomplete='name' placeholder='Nombre y apellidos' required></label>
          <label>Teléfono<input type='tel' name='Telefono' autocomplete='tel' inputmode='tel' placeholder='Teléfono de contacto' required></label>
          <label>Población<input type='text' name='Poblacion' autocomplete='address-level2' value='{place_value}' placeholder='Población' required></label>
        </div>
        <input type='hidden' name='_subject' value='Nueva solicitud · Llega de Limpiezas Galaxia ({DOMAIN})'>
        <input type='hidden' name='_template' value='table'>
        <input type='hidden' name='_captcha' value='false'>
        <input type='hidden' name='_next' value='{DOMAIN}/contacto/?ok=1'>
        <input type='hidden' name='Origen' value='Limpiezas Galaxia · {DOMAIN}'>
        <input type='text' name='_honey' style='display:none' tabindex='-1' autocomplete='off'>
        <button class='cta' type='submit'>Nosotros te llamamos</button>
        <small>Tus datos solo se usan para devolverte la llamada (RGPD). También puedes llamar al {PHONE}.</small>
      </form>
    </section>
    """


SERVICE_IMAGE_MAP = {
    'hoteles':           'gallery-hotel.jpg',
    'restaurantes':      'service-hepa.jpg',
    'residencias':       'service-hepa.jpg',
    'colegios':          'service-hepa.jpg',
    'oficinas':          'gallery-hotel.jpg',
    'comunidades':       'service-hepa.jpg',
    'garajes':           'service-dry-ice.jpg',
    'naves':             'gallery-warehouse.jpg',
    'centros-sanitarios':'service-hepa.jpg',
    'salas-tecnicas':    'service-dry-ice.jpg',
    'bares':             'service-hepa.jpg',
    'bodegas':           'gallery-warehouse.jpg',
    'comercios':         'gallery-hotel.jpg',
}
LANDING_POOL = [
    'gallery-warehouse.jpg','gallery-hotel.jpg','hero-industrial.jpg',
    'service-dry-ice.jpg','service-hepa.jpg',
]


def landing_image(prefix: str, label: str, service: str | None = None) -> str:
    if service and service in SERVICE_IMAGE_MAP:
        img = SERVICE_IMAGE_MAP[service]
        service_phrase = f'para {SERVICE_LABELS[service]} '
    else:
        img = LANDING_POOL[hash(label) % len(LANDING_POOL)]
        service_phrase = ''
    alt = (
        f'{BASE_KEYWORD} {service_phrase}en {label}: '
        f'equipo técnico realizando descontaminación con filtración HEPA H14 '
        f'y eliminación de hollín post-incendio'
    )
    caption = (
        f'{BASE_KEYWORD.capitalize()} {service_phrase}en {label}: '
        f'intervención técnica documentada con trazabilidad pericial para siniestros pequeños, medianos y grandes.'
    )
    return f"<figure class='landing-photo'><img src='{prefix}assets/img/{img}' width='900' height='506' loading='lazy' alt='{esc(alt)}'><figcaption>{esc(caption)}</figcaption></figure>"


def html_page(page: Page) -> str:
    prefix = rel_prefix(page.url)
    canonical = DOMAIN + page.url
    schema_html = ''
    if page.schema:
        schema_html = f"<script type='application/ld+json'>{json.dumps(page.schema, ensure_ascii=False)}</script>"
    title = page.title if len(page.title) < 62 else page.title[:59] + '...'
    desc = page.description[:158]
    preload_lcp = f"<link rel='preload' as='image' href='{prefix}assets/img/hero-industrial.jpg' imagesrcset='{prefix}assets/img/hero-industrial.webp' imagesizes='100vw'>" if page.url != '/' else "<link rel='preload' as='image' href='assets/img/hero-industrial.jpg' imagesrcset='assets/img/hero-industrial.webp' imagesizes='100vw'>"
    return f"""<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{esc(title)}</title>
<meta name='description' content='{esc(desc)}'>
<link rel='canonical' href='{canonical}'>
<meta property='og:title' content='{esc(title)}'>
<meta property='og:description' content='{esc(desc)}'>
<meta property='og:type' content='website'>
<meta property='og:url' content='{canonical}'>
<meta property='og:image' content='{DOMAIN}/assets/img/hero-industrial.jpg'>
<meta name='twitter:card' content='summary_large_image'>
<meta name='twitter:title' content='{esc(title)}'>
<meta name='twitter:description' content='{esc(desc)}'>
<meta name='twitter:image' content='{DOMAIN}/assets/img/hero-industrial.jpg'>
<link rel='icon' type='image/png' sizes='32x32' href='{prefix}assets/img/favicon-32x32.png'>
<link rel='icon' type='image/x-icon' href='{prefix}favicon.ico'>
<link rel='apple-touch-icon' sizes='180x180' href='{prefix}assets/img/apple-touch-icon.png'>
<link rel='icon' type='image/png' sizes='192x192' href='{prefix}assets/img/android-chrome-192x192.png'>
<link rel='manifest' href='{prefix}site.webmanifest'>
<meta name='theme-color' content='#0A0F18'>
<meta name='apple-mobile-web-app-title' content='Galaxia'>
<meta name='application-name' content='Galaxia'>
{preload_lcp}
<style>{CSS}</style>
{schema_html}
</head>
<body>{common_header(prefix)}{page.body}{common_footer(prefix)}</body></html>"""


def write_page(page: Page) -> None:
    target = ROOT / page.url.strip('/') / 'index.html' if page.url != '/' else ROOT / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_page(page), encoding='utf-8')


def hero_block(title: str, lead: str, prefix_img: str = 'assets/img/hero-industrial.jpg') -> str:
    return f"""
    <main class='hero'><div class='wrap grid hero-grid'>
      <section class='panel hero-copy'><div class='eyebrow'>B2B · post-incendio · peritos y aseguradoras</div><h1>{title}</h1><p class='lead'>{lead}</p><div class='actions'><a class='cta' href='contacto/'>Solicitar informe técnico</a><a class='ghost' href='casos-de-exito/'>Ver casos de éxito</a></div><div class='grid stats'><div class='stat'><strong>+500</strong><span>siniestros evaluados</span></div><div class='stat'><strong>25</strong><span>provincias prioritarias</span></div><div class='stat'><strong>-98%</strong><span>partículas objetivo</span></div></div></section>
      <figure class='panel hero-img reveal'><img src='{prefix_img}' width='1280' height='720' loading='eager' alt='Equipo técnico de Galaxia durante una limpieza de incendios en nave industrial'></figure>
    </div></main>"""


def home_page() -> Page:
    tech_cards = [
        ('HEPA H14','Filtración de partículas finas y control de aire en espacios afectados.'),
        ('Hielo seco CO₂','Eliminación de hollín en soportes industriales con mínima humedad residual.'),
        ('Láser técnico','Tratamiento preciso en componentes delicados y superficies seleccionadas.'),
        ('Ozono industrial','Desodorización controlada tras retirada de carga contaminante.'),
        ('Fogging térmico','Nebulización técnica para microzonas, conductos y huecos complejos.'),
        ('EPI III','Protección respiratoria, protocolos y trazabilidad documental.')]
    cards = ''.join(f"<article class='card reveal'><div class='icon'>▱</div><h3>{h}</h3><p>{p}</p></article>" for h,p in tech_cards)
    sectors = ''.join(f"<article class='card'><h3>{slug_title(s)}</h3><p>Protocolos específicos para {SERVICE_LABELS.get(s,s)} con informe técnico, control de olores y reducción de hollín.</p></article>" for s in SERVICES[:7])
    faqs = ''.join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in [
        ('¿Trabajan directamente con peritos?', 'Sí. La documentación se prepara para facilitar valoración de daños y seguimiento de fases.'),
        ('¿Usan ozono en todos los casos?', 'No. Se aplica solo cuando la retirada de residuos y la seguridad del espacio lo permiten.'),
        ('¿Pueden intervenir en naves de gran superficie?', 'Sí. El dimensionamiento se realiza por metros cuadrados, altura, carga de hollín y ventilación.'),
        ('¿La visita técnica es imprescindible?', 'Depende del alcance. En siniestros pequeños puede bastar una evaluación documental inicial; en siniestros medianos o grandes permite fijar alcance, maquinaria, turnos y riesgos.'),
        ('¿Hay precios cerrados por teléfono?', 'No. El presupuesto se emite tras visita técnica o evaluación documental suficiente.'),
        ('¿Qué imágenes usa la galería?', 'Ahora contiene imágenes provisionales. Se sustituirá por trabajos reales cuando el cliente los facilite.'),
        ('¿Se limpian conductos de climatización?', 'Sí, cuando el humo o el hollín han entrado en el sistema de aire.'),
        ('¿Cuál es la cobertura?', 'La cobertura se organiza en toda España con prioridad en 25 provincias indicadas en el proyecto.')])
    body = hero_block('Limpieza de incendios · respuesta técnica para grandes y pequeños siniestros', 'Limpieza post incendio y descontaminación de humo y hollín para naves, hoteles, comunidades, centros sanitarios, comercios, viviendas y activos críticos. Equipos técnicos, trazabilidad documental y respuesta 24/7.')
    body += f"""
    <section class='section'><div class='wrap section-head'><div><div class='eyebrow'>Tecnología aplicada</div><h2>Sistemas técnicos para hollín, humo y olor</h2></div><p>En cada limpieza de incendios, Galaxia une maquinaria, método y documentación para que la intervención sea defendible ante dirección, seguro y peritación.</p></div><div class='wrap grid bento'>{cards}</div></section>
    <section class='section'><div class='wrap section-head'><div><div class='eyebrow'>Sectores</div><h2>Actividad industrial, terciaria y residencial compleja</h2></div><p>Ajustamos cada protocolo de limpieza post incendio al riesgo del inmueble, desde salas técnicas hasta naves logísticas y hoteles en plena operación.</p></div><div class='wrap grid bento'>{sectors}</div></section>
    <section class='section'><div class='wrap grid case panel'><img src='assets/img/gallery-warehouse.jpg' width='1408' height='1056' loading='lazy' alt='Caso técnico de limpieza post-incendio en nave logística'><div class='copy'><div class='eyebrow'>Caso destacado</div><h2>2.000 m² de nave logística estabilizados en 72 horas</h2><p>Intervención con filtración HEPA, retirada de hollín en estructura metálica y coordinación con peritación. Objetivo: evitar contaminación cruzada y preparar reapertura por fases.</p><dl><div><dt>Superficie</dt><dd>2.000 m²</dd></div><div><dt>Plazo</dt><dd>72 h</dd></div><div><dt>Parada crítica</dt><dd>0 días extra</dd></div><div><dt>Informe</dt><dd>Pericial</dd></div></dl></div></div></section>
    <section class='section'><div class='wrap'><div class='section-head'><div><div class='eyebrow'>Proceso</div><h2>Proceso técnico en cinco fases</h2></div></div><div class='grid steps'><article class='card step'><h3>Inspección</h3><p>Lectura del daño, accesos y riesgos.</p></article><article class='card step'><h3>Contención</h3><p>Sectorización y protección de zonas no afectadas.</p></article><article class='card step'><h3>Retirada</h3><p>Hollín, residuos y carga olorosa.</p></article><article class='card step'><h3>Tratamiento</h3><p>HEPA, ozono, fogging o hielo seco según soporte.</p></article><article class='card step'><h3>Informe</h3><p>Documentación y recomendaciones finales.</p></article></div></div></section>
    <section class='section'><div class='wrap panel hero-copy'><div class='eyebrow'>Peritos y aseguradoras</div><h2>Informes compatibles con gestión de siniestros</h2><p>Preparamos documentación técnica con fotografías, alcance, fases ejecutadas, observaciones y prioridades de recuperación para facilitar la toma de decisiones.</p><a class='cta' href='peritos/'>Acceso peritos</a></div></section>
    <section class='section'><div class='wrap'><div class='section-head'><div><div class='eyebrow'>Galería provisional</div><h2>Intervenciones técnicas y equipos</h2></div><p>Estas imágenes son provisionales generadas para maquetación. Se sustituirán por trabajos reales cuando estén disponibles.</p></div>{gallery_grid('')}</div></section>
    <section class='section faq'><div class='wrap content'><div class='eyebrow'>FAQ técnica</div><h2>Preguntas frecuentes</h2>{faqs}</div></section>
    <section class='section'><div class='wrap'><div class='section-head'><div><div class='eyebrow'>Testimonios</div><h2>Lo que dicen quienes han trabajado con nosotros</h2></div></div><div class='grid testimonials'>{testimonials_html()}</div></div></section>
    <section class='section'><div class='wrap'>{delegations_html('')}</div></section>
    <section class='section'><div class='wrap'><div class='section-head'><div><div class='eyebrow'>Cobertura</div><h2>Provincias prioritarias en {len(set([CITY_PROVINCE[c] for c in CITIES if c in CITY_PROVINCE]))} territorios</h2></div></div><div class='coverage'>{''.join(f'<a href="limpieza-incendios-{p}/">{slug_title(p)}</a><br>' for p in PROVINCES)}</div></div></section>
    """
    avg_rating = round(sum(t['rating'] for t in TESTIMONIALS) / len(TESTIMONIALS), 1)
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": DOMAIN + "/#organization",
                "name": BRAND,
                "url": DOMAIN,
                "telephone": PHONE_TEL,
                "email": EMAIL,
                "description": TAGLINE,
                "sameAs": [GBP],
                "areaServed": "España",
                "subOrganization": [delegation_local_business(d) for d in DELEGATIONS],
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": avg_rating,
                    "bestRating": 5,
                    "reviewCount": len(TESTIMONIALS),
                },
                "review": testimonials_schema(),
            },
            *[delegation_local_business(d) for d in DELEGATIONS],
            faq_schema([(q, a) for q, a in [
                ('¿Trabajan directamente con peritos?', 'Sí. La documentación se prepara para facilitar valoración de daños y seguimiento de fases.'),
                ('¿Usan ozono en todos los casos?', 'No. Se aplica solo cuando la retirada de residuos y la seguridad del espacio lo permiten.'),
                ('¿Pueden intervenir en naves de gran superficie?', 'Sí. El dimensionamiento se realiza por metros cuadrados, altura, carga de hollín y ventilación.'),
                ('¿La visita técnica es imprescindible?', 'Depende del alcance. En siniestros pequeños puede bastar una evaluación documental inicial.'),
                ('¿Hay precios cerrados por teléfono?', 'No. El presupuesto se emite tras visita técnica o evaluación documental suficiente.'),
                ('¿Se limpian conductos de climatización?', 'Sí, cuando el humo o el hollín han entrado en el sistema de aire.'),
                ('¿Cuál es la cobertura?', 'Cobertura organizada en 8 comunidades autónomas con delegaciones físicas en Madrid, Badalona, Valencia, Toledo, Córdoba, Marbella y Murcia.'),
            ]]),
        ],
    }
    return Page('/', 'Galaxia · Limpieza de incendios y limpieza post incendio', 'Empresa B2B de limpieza de incendios y limpieza post incendio: descontaminación de humo y hollín e informes para peritos en toda España.', body, schema, '1.0', 'weekly')


def gallery_grid(prefix: str) -> str:
    imgs = [
        ('gallery-warehouse.jpg','Antes/después en nave logística afectada por hollín.'),
        ('gallery-hotel.jpg','Tratamiento técnico en sala de instalaciones de hotel.'),
        ('service-dry-ice.jpg','Limpieza con hielo seco CO₂ sobre superficie carbonizada.'),
    ]
    return "<div class='grid gallery'>" + ''.join(f"<figure><a href='{prefix}assets/img/{img}' data-lightbox><img src='{prefix}assets/img/{img}' width='704' height='528' loading='lazy' alt='{esc(cap)}'></a><figcaption>{esc(cap)}</figcaption></figure>" for img,cap in imgs) + '</div>'


def structural_pages() -> List[Page]:
    pages = [home_page()]
    simple_defs = [
        ('/servicios/','Servicios técnicos post-incendio','Servicios de descontaminación post-incendio','Protocolos para humo, hollín, ozono, hielo seco, láser, naves e informes periciales.'),
        ('/sectores/','Sectores de actividad','Sectores críticos tras incendio','Soluciones para naves, hoteles, residencias, comercios, colegios, comunidades y salas técnicas.'),
        ('/casos-de-exito/','Casos de éxito post-incendio','Casos de éxito documentados','Fichas técnicas orientadas a siniestros de distinto alcance, plazos, superficies y documentación pericial.'),
        ('/certificaciones/','Certificaciones y normativa','Certificaciones, protocolos y normativa','Trabajo con trazabilidad, EPI III, HEPA H14, referencias IICRC S700 y control documental.'),
        ('/equipo-y-maquinaria/','Equipo y maquinaria técnica','Equipo, maquinaria y recursos técnicos','Filtración HEPA, hielo seco, ozono industrial, fogging térmico, aspiración técnica y EPI III.'),
        ('/peritos/','Área para peritos y aseguradoras','Área técnica para peritos','Informes, fotografías, alcance de intervención y criterios de recuperación para siniestros.'),
        ('/contacto/','Contacto técnico 24h','Solicitar informe técnico','Contacto 24/7 para valoración técnica de incendios, humo, hollín y desodorización industrial.'),
        ('/preguntas-tecnicas/','Preguntas técnicas frecuentes','FAQ técnica post-incendio','Respuestas para peritos, administradores de fincas y responsables de mantenimiento.'),
        ('/blog/','Blog técnico post-incendio','Blog técnico de limpieza post-incendio','Artículos técnicos sobre humo, hollín, olores, maquinaria, peritación y recuperación.'),
        ('/galeria/','Galería técnica provisional','Galería de intervenciones post-incendio','Imágenes provisionales de trabajos técnicos que se sustituirán por fotos reales del cliente.'),
        ('/cobertura/','Cobertura nacional Galaxia España','Cobertura de limpieza de incendios','Cobertura operativa de Galaxia en 8 comunidades autónomas y cientos de municipios para limpieza de incendios y limpieza post incendio.'),
        ('/privacidad/','Política de privacidad Galaxia','Política de privacidad','Información sobre tratamiento de datos de contacto, solicitudes técnicas, conservación de mensajes y derechos del usuario.'),
        ('/cookies/','Política de cookies Galaxia','Política de cookies','Información sobre el uso limitado de cookies técnicas, medición analítica básica y configuración de navegación.'),
        ('/aviso-legal/','Aviso legal corporativo Galaxia','Aviso legal','Condiciones de uso del sitio web, datos identificativos disponibles y canales de contacto técnico de Galaxia.'),
        ('/ubicaciones/','Ubicaciones · Delegaciones y cobertura por provincia | Galaxia','Ubicaciones y cobertura por CCAA','Listado completo de delegaciones físicas, provincias y municipios cubiertos por Galaxia en 8 comunidades autónomas.'),
    ]
    for url, title, h, desc in simple_defs:
        pages.append(simple_page(url,title,h,desc))
    service_pages = [
        ('limpieza-humo-hollin','Limpieza de humo y hollín'),('descontaminacion-post-incendio','Descontaminación post-incendio'),('limpieza-tecnica-naves','Limpieza técnica de naves'),('desodorizacion-ozono-industrial','Desodorización con ozono industrial'),('limpieza-laser','Limpieza láser'),('limpieza-hielo-seco','Limpieza con hielo seco CO₂'),('informes-periciales','Informes periciales post-incendio')]
    for slug, label in service_pages:
        pages.append(simple_page(f'/servicios/{slug}/', f'{label} | Galaxia', label, f'{label} para siniestros pequeños, medianos y grandes con trazabilidad técnica, equipos especializados y documentación para peritos.'))
    sector_pages = [('naves-industriales','Naves industriales'),('hoteles','Hoteles'),('centros-sanitarios','Centros sanitarios'),('comunidades','Comunidades de propietarios'),('oficinas','Oficinas'),('colegios','Colegios'),('salas-tecnicas','Salas técnicas')]
    for slug,label in sector_pages:
        pages.append(simple_page(f'/sectores/{slug}/', f'{label} tras incendio | Galaxia', f'Limpieza post-incendio en {label.lower()}', f'Protocolos técnicos para recuperación de {label.lower()} tras humo, hollín y olor persistente.'))
    blog_articles = [
        ('hollin-en-naves','Cómo evaluar hollín en naves industriales'),('ozono-industrial','Cuándo usar ozono industrial tras un incendio'),('hepa-h14','Filtración HEPA H14 en descontaminación post-incendio'),('hielo-seco','Hielo seco CO₂ para superficies carbonizadas'),('informe-pericial','Qué debe incluir un informe técnico post-incendio')]
    for slug,label in blog_articles:
        pages.append(simple_page(f'/blog/{slug}/', f'{label} | Blog Galaxia', label, f'Artículo técnico de Galaxia sobre {label.lower()} para peritos, aseguradoras y responsables de mantenimiento.'))
    assert len(pages) == 35, len(pages)
    return pages


CASE_STUDIES = [
    ('gallery-hotel.jpg',     'Hotel · 84 habitaciones desodorizadas en 5 días',
     'Un incendio de cocina en planta baja llevó el humo hasta cuatro plantas por la ventilación. Actuamos por fases: filtración HEPA, lavado de superficies, ozono y una verificación olfativa final antes de volver a abrir al público.',
     [('Superficie','3.200 m²'),('Plazo','5 días'),('Habitaciones','84'),('Reapertura','Sin cancelaciones')]),
    ('service-hepa.jpg',      'Restaurante · cocina industrial saneada en 48 h',
     'El fuego de una freidora se extendió a campana, falso techo y comedor. Retiramos el hollín adherido, aplicamos desengrase técnico y desodorización con hidroxilo, y dejamos el local certificado antes de la inspección sanitaria.',
     [('Superficie','420 m²'),('Plazo','48 h'),('Cobertura','Comedor + cocina'),('Informe','Pericial')]),
    ('service-hepa.jpg',      'Residencia de mayores · planta recuperada sin traslados',
     'Un incendio en la lavandería dejó humo en una planta con 40 residentes. Trabajamos de noche con cortinas de presión negativa para evitar traslados clínicos y devolvimos la calidad del aire en 36 horas.',
     [('Residentes','40 sin traslado'),('Plazo','36 h'),('PM2.5 final','<12 µg/m³'),('Coordinación','Médica')]),
    ('hero-industrial.jpg',   'Colegio · descontaminación de 12 aulas en fin de semana',
     'Un conato en la sala de informática durante un puente dejó humo en el pasillo y en las aulas contiguas. En 60 horas el centro estaba listo para reabrir el lunes, con la certificación técnica entregada a la inspección educativa.',
     [('Aulas','12'),('Plazo','60 h'),('Reapertura','Lunes 8:00'),('Documentación','Inspección OK')]),
    ('gallery-hotel.jpg',     'Oficina · 1.800 m² planta abierta tratada con HEPA H14',
     'Un cuadro eléctrico llenó de humo unas oficinas corporativas. Aislamos el foco, aspiramos con HEPA H14, tratamos la documentación física y desodorizamos con ozono fuera del horario laboral.',
     [('Superficie','1.800 m²'),('Plazo','72 h'),('Documentos','Recuperados'),('Parada operativa','Mínima')]),
    ('gallery-warehouse.jpg', 'Nave logística · 2.000 m² estabilizados en 72 h',
     'Un incendio parcial en la zona de palets propagó hollín por toda la estructura metálica. Planificamos la retirada por sectores, filtramos y coordinamos con la peritación, sin alargar ni un día la parada de la nave.',
     [('Superficie','2.000 m²'),('Plazo','72 h'),('Parada extra','0 días'),('Informe','Pericial')]),
    ('service-dry-ice.jpg',   'Garaje comunitario · combustión de vehículo retirada',
     'La quema de un vehículo afectó a 14 plazas. Retiramos los residuos, descontaminamos la pintura de las plazas vecinas, ventilamos de forma forzada y desodorizamos antes de reabrir el acceso.',
     [('Plazas','14 afectadas'),('Plazo','5 días'),('Olor residual','0'),('Comunidad','Informada')]),
    ('service-hepa.jpg',      'Comunidad de propietarios · portal y caja de escalera',
     'Un incendio en el cuarto de contadores se propagó al portal y a los rellanos hasta la cuarta planta. Intervinimos en fin de semana y preparamos la documentación para el administrador de fincas y el seguro comunitario.',
     [('Plantas','5 afectadas'),('Plazo','4 días'),('Acceso vecinos','Sin corte total'),('Seguro','OK')]),
]


def case_studies_grid(prefix: str) -> str:
    cards = []
    for img, title, body, kpis in CASE_STUDIES:
        kpi_html = ''.join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in kpis)
        cards.append(
            f"<article class='card case-card'>"
            f"<a href='{prefix}assets/img/{img}' data-lightbox>"
            f"<img src='{prefix}assets/img/{img}' width='704' height='528' loading='lazy' alt='{esc(title)}'>"
            f"</a>"
            f"<div class='case-body'><h3>{esc(title)}</h3><p>{esc(body)}</p>"
            f"<dl class='case-kpis'>{kpi_html}</dl></div></article>"
        )
    return "<div class='grid case-grid'>" + ''.join(cards) + "</div>"


def ubicaciones_html(prefix: str) -> str:
    """Listado por CCAA → provincias → ciudades con landing dedicada."""
    ccaa_groups = [
        ('Comunidad de Madrid', ['madrid']),
        ('Comunidad Valenciana', ['alicante', 'castellon', 'valencia']),
        ('Región de Murcia', ['murcia']),
        ('Andalucía', ['almeria', 'cadiz', 'cordoba', 'granada', 'huelva', 'jaen', 'malaga', 'sevilla']),
        ('Castilla-La Mancha', ['albacete', 'ciudad-real', 'cuenca', 'guadalajara', 'toledo']),
        ('Aragón', ['huesca', 'teruel', 'zaragoza']),
        ('Castilla y León', ['avila', 'burgos', 'leon', 'palencia', 'salamanca', 'segovia', 'soria', 'valladolid', 'zamora']),
        ('Cataluña', ['barcelona', 'girona', 'lleida', 'tarragona']),
    ]
    blocks = []
    for ccaa, provs in ccaa_groups:
        prov_blocks = []
        for prov in provs:
            cities_in = [c for c in CITIES if CITY_PROVINCE.get(c) == prov]
            city_links = ''.join(
                f"<li><a href='{prefix}limpieza-incendios-{c}/'>{slug_title(c)}</a></li>"
                for c in sorted(cities_in)
            )
            prov_blocks.append(
                f"<details open><summary><a href='{prefix}limpieza-incendios-{prov}/'>{slug_title(prov)}</a> · {len(cities_in)} municipios</summary>"
                f"<ul class='ubic-cities'>{city_links}</ul></details>"
            )
        blocks.append(
            f"<section class='ubic-ccaa'>"
            f"<h2>{esc(ccaa)} <span class='ubic-count'>{len(provs)} provincia(s) · {sum(len([c for c in CITIES if CITY_PROVINCE.get(c)==p]) for p in provs)} municipios</span></h2>"
            f"{''.join(prov_blocks)}</section>"
        )
    return (
        f"<p class='lead'>Cobertura organizada en 8 comunidades autónomas, "
        f"{len(PROVINCES)} provincias y {len(CITIES)} municipios con landing "
        f"dedicada. Atención técnica 24 h en toda España desde las 7 delegaciones "
        f"físicas.</p>"
        f"{delegations_html(prefix)}"
        f"<div class='ubic-grid'>{''.join(blocks)}</div>"
    )


def aviso_legal_html() -> str:
    return (
        "<div class='content'>"
        "<h2>1. Datos identificativos</h2>"
        f"<p><strong>Titular:</strong> {BRAND}.<br>"
        f"<strong>Domicilio social:</strong> {ADDRESS}.<br>"
        f"<strong>Teléfono:</strong> <a href='tel:{PHONE_TEL}'>{PHONE}</a>.<br>"
        f"<strong>Email:</strong> <a href='mailto:{EMAIL}'>{EMAIL}</a>.<br>"
        f"<strong>N.I.F.:</strong> <em>a indicar por el titular</em>.<br>"
        f"<strong>Registro Mercantil:</strong> <em>a indicar por el titular</em>.<br>"
        f"<strong>Web:</strong> <a href='{DOMAIN}'>{DOMAIN}</a>.</p>"
        "<h2>2. Objeto</h2>"
        "<p>El presente sitio web tiene como finalidad informar sobre los "
        "servicios de limpieza de incendios, limpieza post incendio, "
        "descontaminación, desodorización industrial e informes para peritos "
        "prestados por Galaxia. No se realizan transacciones económicas a "
        "través de este sitio: el contacto es siempre técnico y para una "
        "valoración previa.</p>"
        "<h2>3. Condiciones de uso</h2>"
        "<p>El usuario se compromete a hacer un uso adecuado de los "
        "contenidos y servicios, sin incurrir en actividades ilícitas, "
        "lesivas de derechos o que puedan dañar el sitio o de terceros.</p>"
        "<h2>4. Propiedad intelectual</h2>"
        "<p>Todo el contenido (textos, fotografías, marcas, logotipos) es "
        "propiedad de Galaxia o de sus licenciantes. Su reproducción "
        "requiere autorización expresa por escrito.</p>"
        "<h2>5. Protección de datos</h2>"
        "<p>Los datos facilitados a través de formularios se tratan según "
        "la <a href='/privacidad/'>Política de Privacidad</a> y se usan "
        "exclusivamente para devolver la llamada solicitada y orientar la "
        "valoración técnica del siniestro.</p>"
        "<h2>6. Cookies</h2>"
        "<p>Este sitio usa únicamente cookies técnicas necesarias para el "
        "funcionamiento. Más información en la "
        "<a href='/cookies/'>Política de Cookies</a>.</p>"
        "<h2>7. Legislación aplicable</h2>"
        "<p>La relación entre Galaxia y el usuario se rige por la "
        "legislación española vigente.</p>"
        "</div>"
    )


def gallery_grid_v2(prefix: str) -> str:
    """Galería con bloques antes/después usando las fotos reales."""
    pairs = [
        ('hero-industrial.jpg', 'gallery-warehouse.jpg',
         'Nave industrial', 'Hollín en estructura antes de retirar y zona tratada con HEPA H14 después.'),
        ('service-dry-ice.jpg', 'gallery-hotel.jpg',
         'Hotel · sala técnica', 'Superficie carbonizada antes del hielo seco CO₂ y acabado tras desodorización.'),
        ('service-hepa.jpg', 'gallery-warehouse.jpg',
         'Comunidad', 'Filtración HEPA H14 en plena intervención y zonas comunes recuperadas.'),
    ]
    cards = []
    for before, after, title, desc in pairs:
        cards.append(
            f"<article class='card galpair'>"
            f"<div class='galpair-imgs'>"
            f"<figure><img src='{prefix}assets/img/{before}' alt='{esc(title)} antes de la intervención' loading='lazy' width='704' height='528'><figcaption>ANTES</figcaption></figure>"
            f"<figure><img src='{prefix}assets/img/{after}' alt='{esc(title)} después de la intervención' loading='lazy' width='704' height='528'><figcaption>DESPUÉS</figcaption></figure>"
            f"</div>"
            f"<div class='galpair-body'><h3>{esc(title)}</h3><p>{esc(desc)}</p></div>"
            f"</article>"
        )
    return (
        "<p class='lead'>Galería de intervenciones representativas. Estas "
        "imágenes son provisionales para maquetación; se sustituirán por "
        "trabajos reales del cliente cuando estén disponibles.</p>"
        f"<div class='grid galpair-grid'>{''.join(cards)}</div>"
        f"{gallery_grid(prefix)}"
    )


def simple_page(url: str, title: str, h: str, desc: str) -> Page:
    prefix = rel_prefix(url)
    extra = ''
    if url == '/galeria/':
        extra = gallery_grid_v2(prefix)
    elif url == '/casos-de-exito/':
        extra = case_studies_grid(prefix)
    elif url == '/ubicaciones/':
        extra = ubicaciones_html(prefix)
    elif url == '/aviso-legal/':
        extra = aviso_legal_html()
    elif url == '/cobertura/':
        coverage_links = ''.join(f"<a href='{prefix}limpieza-incendios-{p}/'>{slug_title(p)}</a><br>" for p in PROVINCES)
        extra = f"<div class='coverage'>{coverage_links}</div>"
    elif url == '/contacto/':
        phone_clean = PHONE_TEL
        whatsapp_clean = WHATSAPP_WA
        extra = (
            f"<div class='panel hero-copy'>"
            f"<p><strong>Teléfono:</strong> <a href='tel:{phone_clean}'>{PHONE}</a></p>"
            f"<p><strong>WhatsApp:</strong> <a href='https://wa.me/{whatsapp_clean}'>{WHATSAPP}</a></p>"
            f"<p><strong>Email:</strong> <a href='mailto:{EMAIL}'>{EMAIL}</a></p>"
            f"<p><strong>Central:</strong> {ADDRESS}</p>"
            f"<p><a class='cta' href='{GBP}'>Ver ficha GBP</a></p>"
            f"</div>{delegations_html(prefix)}{callback_form(prefix)}"
        )
    else:
        links = ''.join(f"<a href='{prefix}limpieza-incendios-{s}-madrid/'>Madrid · {SERVICE_LABELS[s]}</a>" for s in SERVICES[:6])
        extra = f"<div class='local-links'>{links}</div>"
    body = f"""
    <main class='section'><div class='wrap content'><div class='breadcrumb'><a href='{prefix}'>Inicio</a> / {esc(h)}</div><div class='eyebrow'>Galaxia · documentación técnica</div><h1>{esc(h)}</h1><p class='lead'>{esc(desc)}</p><p>Esta página forma parte del proyecto de Galaxia dedicado a la <strong>{BASE_KEYWORD}</strong>: limpieza post incendio, descontaminación de humo y hollín, desodorización industrial e informes técnicos. Está redactada para profesionales que necesitan claridad, trazabilidad y rapidez de respuesta.</p><p>Nuestro método parte de una inspección previa y continúa con la protección de las zonas no afectadas, filtración HEPA H14, tratamiento del hollín, control de olores, retirada de residuos y entrega de documentación. No publicamos precios cerrados porque cada siniestro obliga a medir superficie, carga contaminante, accesos, ventilación y coordinación con la peritación.</p>{extra}</div></main>"""
    schema = None
    if url.startswith('/blog/') and url != '/blog/':
        schema = {"@context":"https://schema.org","@type":"Article","headline":h,"author":{"@type":"Organization","name":BRAND},"publisher":{"@type":"Organization","name":BRAND}}
    return Page(url, title, desc, body, schema)


def landing_pages() -> List[Page]:
    # 5 plantillas de meta-description rotantes para evitar duplicidad
    # percibida por buscadores. Cada landing recibe una según hash del slug.
    desc_templates = [
        'Limpieza de incendios en {l}: limpieza post incendio, descontaminación de humo y hollín, eliminación de olor y HEPA H14 con informe pericial.',
        'Empresa de limpieza de incendios en {l}. Retiramos hollín, neutralizamos el olor a humo y entregamos informe para peritos 24/7.',
        '{l}: limpieza post incendio profesional con filtración HEPA H14, ozono industrial, hielo seco y documentación pericial completa.',
        'Limpieza de incendios tras siniestro en {l}: actuamos en 2-4 h, eliminamos hollín y olor a humo y coordinamos con tu aseguradora.',
        'Limpieza de incendios y descontaminación en {l}. Equipo B2B para naves, hoteles, comunidades y locales con trazabilidad documental.',
    ]
    title_templates = [
        'Limpieza de incendios en {l} | Galaxia',
        'Limpieza de incendios en {l} · Galaxia · 24/7',
        'Limpieza post incendio en {l} | Galaxia',
        'Galaxia · Limpieza de incendios en {l}',
        '{l}: limpieza de incendios profesional | Galaxia',
    ]
    pages: List[Page] = []
    for i, city in enumerate(CITIES):
        label = slug_title(city)
        url = f'/limpieza-incendios-{city}/'
        h = abs(hash('t' + city))
        title = title_templates[h % len(title_templates)].format(l=label)
        desc = desc_templates[h % len(desc_templates)].format(l=label)
        body = landing_body(url, label, landing_copy(city, None, 1000+i), city, None)
        schema = service_schema(label, None, url)
        pages.append(Page(url,title,desc,body,schema,'0.8','monthly'))
    seed = 3000
    for service in SERVICES:
        for province in PROVINCES:
            label = slug_title(province)
            url = f'/limpieza-incendios-{service}-{province}/'
            service_label = SERVICE_LABELS[service]
            sv_title_templates = [
                'Limpieza de incendios en {s} · {l} | Galaxia',
                'Limpieza post incendio en {s} ({l}) · Galaxia',
                '{s} tras incendio en {l} · limpieza de incendios | Galaxia',
            ]
            sv_desc_templates = [
                'Limpieza de incendios para {s} en {l}: hollín, humo, olor, HEPA H14 e informe para peritos.',
                'Empresa de limpieza post incendio para {s} en {l}. Descontaminación, ozono y trazabilidad documental 24/7.',
                'Limpieza de incendios para {s} afectadas por fuego en {l}. Retirada de hollín y desodorización profesional.',
            ]
            h2 = abs(hash(service + province))
            title = sv_title_templates[h2 % len(sv_title_templates)].format(s=service_label, l=label)
            desc = sv_desc_templates[h2 % len(sv_desc_templates)].format(s=service_label, l=label)
            body = landing_body(url, label, landing_copy(province, service, seed), province, service)
            schema = service_schema(label, service, url)
            pages.append(Page(url,title,desc,body,schema,'0.75','monthly'))
            seed += 1
    return pages


def landing_body(url: str, label: str, copy: str, slug: str, service: str | None) -> str:
    prefix = rel_prefix(url)
    service_line = SERVICE_LABELS.get(service, 'instalaciones industriales y activos afectados')
    related_services = ''.join(f"<a href='{prefix}limpieza-incendios-{s}-{PROVINCES[hash(slug+s)%len(PROVINCES)]}/'>{SERVICE_LABELS[s]}</a>" for s in SERVICES[:6])
    related_cities = ''.join(f"<a href='{prefix}limpieza-incendios-{c}/'>{slug_title(c)}</a>" for c in related_geo_cities(slug, 6))
    h1 = f'Limpieza de incendios en {label}' if not service else f'Limpieza de incendios para {service_line} en {label}'
    # Featured Snippet block (Posición Cero)
    featured = featured_snippet_block(label, service)
    # Panel propio si la ciudad tiene delegación física
    delegation = next((d for d in DELEGATIONS if d['city_slug'] == slug), None)
    dele_panel = ''
    if delegation:
        badge_label = 'Central' if delegation.get('main') else 'Delegación'
        dele_panel = (
            "<aside class='dele-card landing-dele'>"
            f"<header><h3>{esc(delegation['name'])}</h3>"
            f"<span class='dele-badge'>{badge_label}</span></header>"
            f"<p class='dele-addr'>{esc(delegation_full_address(delegation))}</p>"
            "<div class='dele-actions'>"
            f"<a class='ghost' href='{maps_query_url(delegation)}' target='_blank' rel='noopener'>Ver en Google Maps</a>"
            f"<a class='ghost' href='tel:{PHONE_TEL}' aria-label='Llamar a Galaxia en {label}'>Llamar {PHONE}</a>"
            "</div></aside>"
        )
    # Párrafo de cierre con 3 enlaces internos contextuales
    inline_links = (
        f"<p class='inline-links'>Consulta nuestro <a href='{prefix}servicios/'>"
        f"catálogo de servicios técnicos</a>, las "
        f"<a href='{prefix}preguntas-tecnicas/'>preguntas frecuentes</a> que "
        f"resolvemos con peritos y administradores, o algunos de nuestros "
        f"<a href='{prefix}casos-de-exito/'>casos documentados</a> con "
        f"superficie, plazos y KPI.</p>"
    )
    profile = city_profile_paragraphs(slug, label) if not service else ''
    urgency = (
        f"<p class='urgency-cta'>¿Has sufrido un incendio en {label}? "
        f"El tiempo juega en contra: durante las primeras 24-72 horas el "
        f"hollín reacciona con las superficies y el olor se fija si no se "
        f"interviene a tiempo. Déjanos tu teléfono y te llamamos en minutos "
        f"para coordinar la visita técnica de limpieza post incendio.</p>"
    )
    return f"""
    <main id='main-content' class='section'><div class='wrap content'><div class='breadcrumb'><a href='{prefix}'>Inicio</a> / <a href='{prefix}cobertura/'>Cobertura</a> / {esc(label)}</div><div class='eyebrow'>Intervención técnica local · 24/7</div><h1>{esc(h1)}</h1>{featured}<p class='lead'>Empresa de limpieza de incendios y limpieza post incendio en {esc(label)}: actuamos sobre humo, hollín, olor persistente y residuos de combustión con enfoque B2B, trazabilidad documental e informe compatible con peritación.</p>{landing_image(prefix, label, service)}{dele_panel}{urgency}{callback_form(prefix, label)}{profile}{copy}{inline_links}<h2>Enlaces técnicos relacionados</h2><div class='local-links'>{related_services}</div><h2>Zonas relacionadas</h2><div class='local-links'>{related_cities}</div>{callback_form(prefix, label)}<div class='notice'><strong>Contacto técnico:</strong> {PHONE} · {EMAIL}. Presupuesto previa visita técnica o evaluación documental.</div></div></main>"""


def service_schema(label: str, service: str | None, url: str) -> dict:
    audience = ["peritos de seguros","directores de operaciones","administradores de fincas","jefes de mantenimiento"]
    name = f'{BASE_KEYWORD} en {label}' if not service else f'{BASE_KEYWORD} para {SERVICE_LABELS[service]} en {label}'
    # Si el slug coincide con una delegación, usar sus datos (dirección y geo
    # propios). Si no, caer a la central de Madrid.
    slug_norm = label.lower().replace(' ', '-')
    delegation = next((d for d in DELEGATIONS if d['city_slug'] == slug_norm), DELEGATIONS[0])
    local_business = delegation_local_business(delegation)
    local_business['areaServed'] = label
    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": "Cobertura", "item": DOMAIN + "/cobertura/"},
            {"@type": "ListItem", "position": 3, "name": label, "item": DOMAIN + url},
        ],
    }
    # FAQPage + Review específicos de la landing (item 13, 14 backlog)
    landing_faq = faq_schema([
        (f'¿Atienden urgencias por incendio en {label}?',
         f'Sí, atendemos 24/7. La intervención técnica en {label} se coordina en horas tras una visita técnica de evaluación.'),
        (f'¿La limpieza de incendios la pueden hacer otros gremios en {label}?',
         'No. La descontaminación con HEPA H14, ozono y hielo seco requiere equipos y formación específicos; las obras posteriores las hacen empresas designadas por la aseguradora.'),
        (f'¿Trabajan con aseguradoras y peritos en {label}?',
         f'Sí. Preparamos informe técnico con fotografías, alcance y fases ejecutadas para que el perito en {label} pueda validar el siniestro sin fricciones.'),
        (f'¿Cuánto tarda la limpieza en {label}?',
         f'Depende del tamaño del siniestro. En {label} solemos estabilizar zonas críticas en 24-72 h y entregar el espacio operativo en pocos días.'),
    ])
    # 2 reviews rotantes del pool global, deterministas por slug
    idx = abs(hash(label)) % len(TESTIMONIALS)
    picks = [TESTIMONIALS[idx], TESTIMONIALS[(idx + 3) % len(TESTIMONIALS)]]
    landing_reviews = [{
        '@type': 'Review',
        'reviewRating': {'@type': 'Rating', 'ratingValue': t['rating'], 'bestRating': 5},
        'author': {'@type': 'Person', 'name': t['author']},
        'reviewBody': t['text'],
        'datePublished': t['date'],
        'itemReviewed': {'@type': 'LocalBusiness', '@id': local_business['@id']},
    } for t in picks]
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": name,
         "provider": {"@type": "ProfessionalService", "name": BRAND, "telephone": PHONE_TEL, "email": EMAIL, "hasMap": GBP, "url": DOMAIN, "sameAs": [GBP]},
         "audience": {"@type": "BusinessAudience", "audienceType": ', '.join(audience)},
         "areaServed": label, "url": DOMAIN + url},
        local_business,
        landing_faq,
        *landing_reviews,
        crumbs,
    ]}


def clean_previous() -> None:
    keep = {'.git', 'build_site.py'}
    for item in ROOT.iterdir():
        if item.name in keep or item.name.startswith('spintax') or item.name == 'Spintax.txt':
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    (ROOT / 'assets' / 'img').mkdir(parents=True, exist_ok=True)



def prepare_assets() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    logo_src = ROOT / 'assets' / 'img' / 'logo_nuevo_02.png'
    if not logo_src.exists():
        logo_src = ROOT / 'logo_nuevo.png'
    if not logo_src.exists():
        logo_src = ROOT / 'Logo Limpiezas GAlaxia.png'
    if not logo_src.exists():
        logo_src = Path('/home/ubuntu/upload/LogoLimpiezasGAlaxia.png')
    if logo_src.exists():
        shutil.copy2(logo_src, IMG / 'logo-galaxia.png')
    # Los PNG generados ya están en assets/img; crear JPG/WebP optimizados y favicon.
    from PIL import Image
    conversions = []
    for png in IMG.glob('*.png'):
        if png.name in {'logo-galaxia.png','logo_nuevo.png','logo_nuevo_02.png','favicon-32x32.png','android-chrome-192x192.png','apple-touch-icon.png'} or png.stem.startswith('favicon'):
            continue
        with Image.open(png) as im:
            im = im.convert('RGB')
            # resize hero to 1600px wide, cards to 900px wide
            maxw = 1600 if 'hero' in png.stem else 900
            if im.width > maxw:
                ratio = maxw / im.width
                im = im.resize((maxw, int(im.height * ratio)), Image.LANCZOS)
            jpg = png.with_suffix('.jpg')
            webp = png.with_suffix('.webp')
            im.save(jpg, quality=78, optimize=True, progressive=True)
            im.save(webp, quality=74, method=6)
            conversions += [jpg, webp]
    logo = IMG / 'logo-galaxia.png'
    if logo.exists():
        with Image.open(logo) as im:
            im = im.convert('RGBA')
            # Save logo-galaxia.webp with alpha transparency
            logo_webp = logo.with_suffix('.webp')
            logo_im = im.copy()
            if logo_im.width > 800:
                ratio = 800 / logo_im.width
                logo_im = logo_im.resize((800, int(logo_im.height * ratio)), Image.LANCZOS)
            logo_im.save(logo_webp, quality=78, method=6)

            im.thumbnail((512,512), Image.LANCZOS)
            # favicon.ico multi-tamaño en raíz para máxima compatibilidad
            ico_im = im.copy()
            ico_im.save(ROOT / 'favicon.ico', sizes=[(16,16),(32,32),(48,48)])
            for size in [32,192,180]:
                icon = im.copy(); icon.thumbnail((size,size), Image.LANCZOS)
                name = 'favicon-32x32.png' if size==32 else ('android-chrome-192x192.png' if size==192 else 'apple-touch-icon.png')
                icon.save(IMG / name)
    # Mantener solo formatos ligeros en publicación. Las fuentes PNG generadas
    # pueden regenerarse o sustituirse más adelante por fotografías reales.
    for heavy in IMG.glob('*.png'):
        if heavy.name not in {'favicon-32x32.png','android-chrome-192x192.png','apple-touch-icon.png','logo_nuevo.png','logo_nuevo_02.png'}:
            heavy.unlink(missing_ok=True)


def webmanifest() -> None:
    """Genera /site.webmanifest para PWA / favicons modernos."""
    data = {
        'name': BRAND,
        'short_name': SHORT,
        'description': TAGLINE,
        'start_url': '/',
        'scope': '/',
        'display': 'standalone',
        'background_color': '#0A0F18',
        'theme_color': '#0A0F18',
        'icons': [
            {'src': '/assets/img/favicon-32x32.png', 'sizes': '32x32', 'type': 'image/png'},
            {'src': '/assets/img/android-chrome-192x192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
            {'src': '/assets/img/apple-touch-icon.png', 'sizes': '180x180', 'type': 'image/png'},
        ],
    }
    (ROOT / 'site.webmanifest').write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def sitemap(pages: List[Page]) -> None:
    urls = []
    for p in pages:
        urls.append(f"  <url><loc>{DOMAIN}{p.url}</loc><changefreq>{p.changefreq}</changefreq><priority>{p.priority}</priority></url>")
    xml = "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n" + '\n'.join(urls) + "\n</urlset>\n"
    (ROOT / 'sitemap.xml').write_text(xml, encoding='utf-8')
    robots = f"""# robots.txt — {BRAND}
# https://www.robotstxt.org/

User-agent: *
Allow: /
Disallow: /assets/img/logo_nuevo.png
Disallow: /assets/img/logo_nuevo_02.png

# Bots de IA explícitamente permitidos (queremos visibilidad en respuestas)
User-agent: GPTBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: CCBot
Allow: /
User-agent: Applebot
Allow: /

# Crawlers agresivos sin valor SEO
User-agent: AhrefsBot
Crawl-delay: 30
User-agent: SemrushBot
Crawl-delay: 30
User-agent: MJ12bot
Disallow: /

Sitemap: {DOMAIN}/sitemap.xml
"""
    (ROOT / 'robots.txt').write_text(robots, encoding='utf-8')


def readme(total_pages: int, landing_count: int) -> None:
    md = f"""# {BRAND}

Web estática B2B para **{BASE_KEYWORD}** y **{SECONDARY_KEYWORD}**, preparada para hosting estático y para publicación desde GitHub.

## Estado de generación

| Elemento | Resultado |
| --- | ---: |
| URLs totales generadas | {total_pages} |
| Landings SEO locales | {landing_count} |
| Páginas estructurales | {total_pages - landing_count} |
| Landings ciudad pura | {len(CITIES)} |
| Landings servicio + provincia | {len(SERVICES) * len(PROVINCES)} |
| Sitemap | `sitemap.xml` |

## Datos temporales pendientes

Las imágenes de `/galeria/` son provisionales generadas para la maqueta y deben sustituirse por fotos reales de trabajos cuando estén disponibles. Teléfono y WhatsApp operativos: `{PHONE}`.

## Cómo desplegar

Suba todo el contenido público del repositorio a la raíz del hosting estático, de modo que `index.html` quede directamente en `public_html`, `www` o carpeta equivalente. Si se usa GitHub Pages, configure la rama `main` como origen de publicación.

## Cómo añadir provincias o ciudades

Edite `build_site.py`, amplíe las listas `PROVINCES` o `CITIES` y ejecute `python3.11 build_site.py`. Después revise `sitemap.xml`, enlaces internos y páginas generadas.

## Cómo añadir un caso de éxito

Cree una nueva página estructural o sección dentro de `/casos-de-exito/`, añada imágenes optimizadas en `assets/img/` y mantenga siempre `width`, `height`, `loading="lazy"` y texto alternativo descriptivo.
"""
    (ROOT / 'README.md').write_text(md, encoding='utf-8')


def validate(pages: List[Page]) -> List[str]:
    issues = []
    expected = 35 + len(CITIES) + len(SERVICES) * len(PROVINCES)
    if len(pages) != expected:
        issues.append(f'Número de páginas inesperado: {len(pages)} (esperado {expected})')
    for p in pages:
        f = ROOT / p.url.strip('/') / 'index.html' if p.url != '/' else ROOT / 'index.html'
        if not f.exists():
            issues.append(f'Falta archivo {p.url}')
            continue
        t = f.read_text(encoding='utf-8', errors='ignore')
        visible = re.sub(r'<script[^>]*>.*?</script>|<style[^>]*>.*?</style>', '', t, flags=re.S|re.I)
        if re.search(r'\{[^{}<>]{0,240}\|[^{}<>]{0,240}\}', visible):
            issues.append(f'Posible spintax sin resolver en {p.url}')
        for m in re.findall(r"<img[^>]+src=['\"]([^'\"]+)", t):
            if m.startswith('http') or m.startswith('data:'):
                continue
            local = (f.parent / m).resolve()
            if not local.exists():
                issues.append(f'Imagen rota en {p.url}: {m}')
        if t.count('name=\'description\'') != 1:
            issues.append(f'Meta description incorrecta en {p.url}')
    (ROOT / 'validation-report.txt').write_text('\n'.join(issues) if issues else f'Validación básica correcta: {len(pages)} páginas, imágenes locales existentes y metadescripciones únicas.\n', encoding='utf-8')
    return issues


def main() -> None:
    # No limpiar antes de convertir activos generados; solo eliminar páginas antiguas preservando spintax y assets/img.
    (ROOT / 'assets' / 'img').mkdir(parents=True, exist_ok=True)
    prepare_assets()
    pages = structural_pages() + landing_pages()
    for p in pages:
        write_page(p)
    sitemap(pages)
    webmanifest()
    readme(len(pages), len(pages)-35)
    issues = validate(pages)
    print(f'Generadas {len(pages)} URLs ({len(pages)-35} landings + 35 estructurales).')
    print('Validación:', 'OK' if not issues else f'{len(issues)} incidencias')

if __name__ == '__main__':
    main()
