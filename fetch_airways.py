#!/usr/bin/env python3
"""
Fetch ALL Brazilian airways from OpenStreetMap Overpass API and convert to GeoJSON.
Airways in OSM are tagged as relations with type=route, route=flight.
We also fetch navaids/waypoints used as fixes along these routes.
Output: airways_brazil.json (GeoJSON FeatureCollection)
"""
import json
import urllib.request
import urllib.parse
import sys
import time

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Query for all flight routes (airways) that pass through Brazil's bounding box
# Brazil bbox: lat -33.8 to 5.3, lon -73.9 to -34.7
QUERY = """
[out:json][timeout:120];
(
  // Get all airways (ATS routes) as ways within Brazil
  way["aeroway"="navigationaid"]({{bbox}});
  // Get all relations of type route=flight within Brazil
  relation["type"="route"]["route"="flight"]({{bbox}});
  // Also try the ARINC-style tagging
  way["airway"]({{bbox}});
  // And any navigational aids
  node["aeroway"="navigationaid"]({{bbox}});
  node["aeroway"="fix"]({{bbox}});
  node["aeroway"="waypoint"]({{bbox}});
  node["aeroway"="navigational_aid"]({{bbox}});
);
out body;
>;
out skel qt;
""".replace("{{bbox}}", "-33.8,-73.9,5.3,-34.7")

# Alternative: use a simpler query that gets named airways
QUERY_SIMPLE = """
[out:json][timeout:180];
area["ISO3166-1"="BR"][admin_level=2]->.brazil;
(
  relation["type"="route"]["route"="flight"](area.brazil);
  relation["type"="route"]["route"="aerialway"](area.brazil);
);
out body;
>;
out skel qt;
"""

def fetch_overpass(query):
    """Fetch data from Overpass API."""
    data = urllib.parse.urlencode({'data': query}).encode('utf-8')
    req = urllib.request.Request(OVERPASS_URL, data=data)
    req.add_header('User-Agent', 'OKFlyRadar/1.0')
    
    print(f"[*] Fetching from Overpass API...")
    try:
        with urllib.request.urlopen(req, timeout=200) as resp:
            raw = resp.read()
            print(f"[*] Received {len(raw)} bytes")
            return json.loads(raw)
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def osm_to_geojson(osm_data):
    """Convert OSM Overpass response to GeoJSON FeatureCollection."""
    if not osm_data or 'elements' not in osm_data:
        return {"type": "FeatureCollection", "features": []}
    
    elements = osm_data['elements']
    nodes = {}
    ways = {}
    relations = []
    
    # Index nodes and ways
    for el in elements:
        if el['type'] == 'node':
            nodes[el['id']] = (el.get('lon', 0), el.get('lat', 0))
        elif el['type'] == 'way':
            ways[el['id']] = el
        elif el['type'] == 'relation':
            relations.append(el)
    
    features = []
    
    # Process relations (airways are usually relations)
    for rel in relations:
        tags = rel.get('tags', {})
        name = tags.get('ref', tags.get('name', f"AWY-{rel['id']}"))
        airway_type = tags.get('airway_type', 'L')  # L=lower, H=upper
        
        # Build coordinates from member ways
        coords = []
        for member in rel.get('members', []):
            if member['type'] == 'way' and member['ref'] in ways:
                way = ways[member['ref']]
                way_nodes = way.get('nodes', [])
                for nid in way_nodes:
                    if nid in nodes:
                        coords.append(list(nodes[nid]))
            elif member['type'] == 'node' and member['ref'] in nodes:
                coords.append(list(nodes[member['ref']]))
        
        if len(coords) >= 2:
            feature = {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "type": "H" if "upper" in str(tags).lower() or name.startswith("U") else "L"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                }
            }
            features.append(feature)
    
    # Also process standalone ways tagged as airways
    for wid, way in ways.items():
        tags = way.get('tags', {})
        if 'airway' in tags or tags.get('aeroway') == 'navigationaid':
            name = tags.get('ref', tags.get('name', f"W-{wid}"))
            coords = []
            for nid in way.get('nodes', []):
                if nid in nodes:
                    coords.append(list(nodes[nid]))
            if len(coords) >= 2:
                features.append({
                    "type": "Feature",
                    "properties": {"name": name, "type": "L"},
                    "geometry": {"type": "LineString", "coordinates": coords}
                })
    
    return {"type": "FeatureCollection", "features": features}

def main():
    print("=" * 60)
    print("  EXTRATOR DE AEROVIAS BRASILEIRAS - OpenStreetMap Overpass")
    print("=" * 60)
    
    # Try the simple query first
    print("\n[1/2] Tentando consulta por relações de rota aérea...")
    result = fetch_overpass(QUERY_SIMPLE)
    
    if result:
        geojson = osm_to_geojson(result)
        count = len(geojson['features'])
        print(f"[*] Encontradas {count} aerovias na consulta de relações.")
    else:
        geojson = {"type": "FeatureCollection", "features": []}
        count = 0
    
    if count < 10:
        print(f"\n[2/2] Poucas aerovias encontradas ({count}). Tentando consulta expandida...")
        time.sleep(2)  # Rate limiting
        result2 = fetch_overpass(QUERY)
        if result2:
            geojson2 = osm_to_geojson(result2)
            count2 = len(geojson2['features'])
            print(f"[*] Encontradas {count2} aerovias na consulta expandida.")
            # Merge
            geojson['features'].extend(geojson2['features'])
    
    total = len(geojson['features'])
    print(f"\n[RESULTADO] Total de aerovias extraídas: {total}")
    
    # Save
    outpath = 'airways_brazil.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)
    print(f"[*] Salvo em: {outpath}")
    
    # Also print stats
    lower = sum(1 for f in geojson['features'] if f['properties']['type'] == 'L')
    upper = sum(1 for f in geojson['features'] if f['properties']['type'] == 'H')
    print(f"    Inferiores (L): {lower}")
    print(f"    Superiores (H): {upper}")

if __name__ == '__main__':
    main()
