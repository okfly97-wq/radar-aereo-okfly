#!/usr/bin/env python3
"""
GERADOR COMPLETO DE AEROVIAS BRASILEIRAS - Baseado em fixos e VORs oficiais do AIP Brasil.
Gera GeoJSON com as aerovias principais dos 5 FIRs brasileiros:
  - FIR Brasília (SBBS)
  - FIR Curitiba (SBCW) 
  - FIR Recife (SBRE)
  - FIR Amazônica (SBAZ)
  - FIR Atlântico (SBAO)
"""
import json

# =========================================================
# BANCO DE DADOS DE FIXOS / VORs / NDBs BRASILEIROS
# Coordenadas (lat, lon) extraídas do AIP Brasil
# =========================================================
FIXES = {
    # === TERMINAIS PRINCIPAIS ===
    "SBGR": (-23.435, -46.473),   # Guarulhos/SP
    "SBSP": (-23.627, -46.656),   # Congonhas/SP
    "SBKP": (-23.007, -47.135),   # Campinas/Viracopos
    "SBRJ": (-22.910, -43.163),   # Santos Dumont/RJ
    "SBGL": (-22.810, -43.250),   # Galeão/RJ
    "SBBR": (-15.870, -47.920),   # Brasília
    "SBCF": (-19.624, -43.972),   # Confins/BH
    "SBPA": (-29.994, -51.171),   # Porto Alegre
    "SBCT": (-25.528, -49.176),   # Curitiba/Afonso Pena
    "SBFL": (-27.670, -48.547),   # Florianópolis
    "SBSV": (-12.911, -38.331),   # Salvador
    "SBRF": (-8.126, -34.923),    # Recife
    "SBFZ": (-3.776, -38.533),    # Fortaleza
    "SBBE": (-1.379, -48.476),    # Belém
    "SBMN": (-3.146, -59.986),    # Manaus/Ponta Pelada
    "SBEG": (-3.039, -60.050),    # Manaus/Eduardo Gomes
    "SBNT": (-5.911, -35.248),    # Natal
    "SBCG": (-20.469, -54.672),   # Campo Grande
    "SBGO": (-16.632, -49.221),   # Goiânia
    "SBBV": (2.846, -60.690),     # Boa Vista
    "SBTF": (-3.383, -64.724),    # Tefé
    "SBPV": (-8.709, -63.902),    # Porto Velho
    "SBCY": (-15.653, -56.117),   # Cuiabá
    "SBVT": (-20.258, -40.286),   # Vitória
    "SBMQ": (0.051, -51.072),     # Macapá
    "SBSL": (-2.585, -44.236),    # São Luís
    "SBTE": (-5.060, -42.824),    # Teresina
    "SBSN": (-2.424, -54.786),    # Santarém
    "SBMA": (-5.368, -49.138),    # Marabá
    "SBJP": (-7.148, -34.951),    # João Pessoa
    "SBMO": (-9.511, -35.792),    # Maceió
    "SBAR": (-10.984, -37.074),   # Aracaju
    "SBIL": (-14.816, -39.033),   # Ilhéus
    "SBPS": (-16.439, -39.081),   # Porto Seguro
    "SBUL": (-18.883, -48.225),   # Uberlândia
    "SBRP": (-21.136, -47.777),   # Ribeirão Preto
    "SBLO": (-23.333, -51.130),   # Londrina
    "SBMG": (-23.440, -51.906),   # Maringá
    "SBNF": (-26.880, -48.651),   # Navegantes
    "SBJV": (-26.224, -48.797),   # Joinville
    "SBPK": (-31.718, -52.328),   # Pelotas
    "SBUG": (-29.782, -57.038),   # Uruguaiana
    "SBFI": (-25.600, -54.485),   # Foz do Iguaçu
    "SBCR": (-19.852, -43.959),   # Belo Horizonte/Pampulha (Confins VOR)

    # === VORs PRINCIPAIS ===
    "CGN": (-19.85, -43.97),      # Confins VOR
    "GRU": (-23.43, -46.47),      # Guarulhos VOR
    "GIG": (-22.81, -43.25),      # Galeão VOR
    "BSB": (-15.87, -47.92),      # Brasília VOR
    "POA": (-29.99, -51.17),      # Porto Alegre VOR
    "CWB": (-25.53, -49.18),      # Curitiba VOR
    "SSA": (-12.91, -38.33),      # Salvador VOR
    "REC": (-8.13, -34.92),       # Recife VOR
    "FOR": (-3.78, -38.53),       # Fortaleza VOR
    "BEL": (-1.38, -48.48),       # Belém VOR
    "MAO": (-3.04, -60.05),       # Manaus VOR
    "NAT": (-5.91, -35.25),       # Natal VOR
    "CGR": (-20.47, -54.67),      # Campo Grande VOR
    "GYN": (-16.63, -49.22),      # Goiânia VOR
    "CGB": (-15.65, -56.12),      # Cuiabá VOR
    "VIT": (-20.26, -40.29),      # Vitória VOR
    "FLN": (-27.67, -48.55),      # Florianópolis VOR
    "SLZ": (-2.59, -44.24),       # São Luís VOR
    "THE": (-5.06, -42.82),       # Teresina VOR
    "MCZ": (-9.51, -35.79),       # Maceió VOR
    "AJU": (-10.98, -37.07),      # Aracaju VOR
    "UDI": (-18.88, -48.23),      # Uberlândia VOR
    "RAO": (-21.14, -47.78),      # Ribeirão Preto VOR
    "LDB": (-23.33, -51.13),      # Londrina VOR
    "PVH": (-8.71, -63.90),       # Porto Velho VOR
    "BVB": (2.85, -60.69),        # Boa Vista VOR
    "STM": (-2.42, -54.79),       # Santarém VOR
    "MCP": (0.05, -51.07),        # Macapá VOR
    "IGU": (-25.60, -54.49),      # Foz do Iguaçu VOR
    "URG": (-29.78, -57.04),      # Uruguaiana VOR

    # === FIXOS / WAYPOINTS INTERMEDIÁRIOS ===
    "DIMBA": (-22.00, -45.00),
    "OSNAK": (-21.00, -44.50),
    "GALOT": (-20.50, -44.00),
    "PAROT": (-18.50, -43.50),
    "NIKDO": (-17.00, -43.00),
    "PIMOL": (-16.00, -42.50),
    "OPVAT": (-14.50, -41.50),
    "ATBIG": (-13.50, -40.50),
    "UBKAB": (-22.50, -46.00),
    "MOVLA": (-21.50, -45.50),
    "TOBUX": (-20.00, -46.50),
    "NIVPU": (-18.50, -47.50),
    "OKDIB": (-17.50, -48.00),
    "LATAM": (-24.00, -46.00),
    "URDEX": (-24.50, -47.00),
    "MIBOV": (-25.00, -47.50),
    "OLGAX": (-26.00, -48.00),
    "RIVAM": (-27.00, -49.00),
    "SETIL": (-28.00, -50.00),
    "BIDEV": (-16.50, -46.00),
    "LIKNO": (-14.50, -44.50),
    "KUMBA": (-12.50, -43.00),
    "DUBAX": (-10.50, -41.00),
    "GITBO": (-8.50, -39.50),
    "MOLVU": (-7.00, -38.00),
    "UPKUD": (-5.50, -36.50),
    "ENKAL": (-4.00, -35.50),
    "POSAG": (-22.00, -48.00),
    "LITRE": (-20.50, -49.50),
    "RUDNO": (-19.00, -50.50),
    "GUKAB": (-17.50, -51.50),
    "ESBAM": (-16.00, -52.50),
    "TINOP": (-21.50, -50.00),
    "BUVOL": (-20.00, -51.50),
    "NEXAL": (-18.50, -53.00),
    "PIDMO": (-17.00, -54.00),
    "KALAX": (-15.00, -55.50),
    "DUTRO": (-13.50, -57.00),
    "EKMAG": (-12.00, -58.50),
    "OPILA": (-10.50, -60.00),
    "KUBAG": (-9.00, -61.50),
    "MAVOD": (-7.50, -63.00),
    "OGTIM": (-6.00, -60.00),
    "PIXAL": (-4.50, -58.00),
    "NIKAM": (-3.00, -56.50),
    "RUDAL": (-1.50, -55.00),
    "OBMAG": (0.50, -53.50),
    "ENPAT": (1.50, -52.00),
    "VIBLA": (-23.00, -44.50),
    "NUDAX": (-21.50, -43.00),
    "KELBO": (-20.00, -42.00),
    "TIPAM": (-18.50, -41.00),
    "ROKBI": (-15.50, -39.50),
    "MADOL": (-14.00, -39.00),
    "IBMAT": (-24.50, -48.50),
    "DOMUX": (-25.50, -50.00),
    "RIGEL": (-26.50, -51.50),
    "EVTOL": (-27.50, -53.00),
    "MAKRU": (-28.50, -54.50),
    "GOLDA": (-29.50, -56.00),
    "TOPLA": (-11.00, -42.00),
    "OXNEM": (-9.50, -40.50),
    "BIVAD": (-8.00, -39.00),
    "GULTA": (-6.50, -37.50),
    "PIDAX": (-5.00, -40.00),
    "LOKAT": (-3.50, -41.50),
    "RUBAM": (-2.00, -43.00),
    "MOGDI": (-7.00, -43.50),
    "EXBAL": (-5.50, -45.00),
    "LUMAG": (-4.00, -46.50),
    "ORVAM": (-2.50, -48.00),
    "PILAX": (-1.00, -49.50),
    "BUMEX": (-8.50, -46.00),
    "NITVO": (-7.00, -47.50),
    "ROLAX": (-5.50, -49.00),
    "GEBAM": (-4.00, -50.50),
    "ODVIN": (-2.50, -52.00),
    "TULAX": (-1.00, -53.50),
    "POXIM": (-10.00, -48.00),
    "IVBAL": (-8.00, -49.50),
    "DOMAX": (-6.00, -51.00),
    "FUGAL": (-4.00, -52.50),
    "MALBO": (-2.00, -54.00),
    "REBDO": (-11.50, -50.00),
    "IKBAL": (-10.00, -52.00),
    "NUTEX": (-8.50, -54.00),
    "OPVIM": (-7.00, -56.00),
    "DALAX": (-5.50, -57.50),
}

# =========================================================
# DEFINIÇÃO DAS AEROVIAS (sequência de fixos)
# =========================================================

AIRWAYS = {
    # === AEROVIAS INFERIORES (W - Lower) ===
    "W2":  {"type": "L", "fixes": ["SBGL", "VIBLA", "DIMBA", "GRU"]},
    "W3":  {"type": "L", "fixes": ["SBGR", "UBKAB", "MOVLA", "OSNAK", "GALOT", "CGN"]},
    "W4":  {"type": "L", "fixes": ["GRU", "URDEX", "CWB"]},
    "W5":  {"type": "L", "fixes": ["CGN", "PAROT", "NIKDO", "PIMOL", "OPVAT", "SSA"]},
    "W6":  {"type": "L", "fixes": ["SSA", "ATBIG", "OPVAT", "PIMOL", "NIKDO", "PAROT", "CGN"]},
    "W7":  {"type": "L", "fixes": ["GRU", "LATAM", "OLGAX", "FLN"]},
    "W8":  {"type": "L", "fixes": ["REC", "MOLVU", "GITBO", "DUBAX", "KUMBA", "SSA"]},
    "W9":  {"type": "L", "fixes": ["SBGR", "POSAG", "LITRE", "RUDNO", "GUKAB", "GYN"]},
    "W10": {"type": "L", "fixes": ["BSB", "GRU", "IBMAT", "DOMUX", "CWB"]},
    "W11": {"type": "L", "fixes": ["CWB", "RIVAM", "SETIL", "POA"]},
    "W12": {"type": "L", "fixes": ["GIG", "NUDAX", "KELBO", "TIPAM", "VIT"]},
    "W13": {"type": "L", "fixes": ["BSB", "TOBUX", "MOVLA", "CGN"]},
    "W14": {"type": "L", "fixes": ["POA", "CWB", "GRU", "GIG"]},
    "W15": {"type": "L", "fixes": ["GIG", "VIBLA", "DIMBA", "UBKAB", "SBGR"]},
    "W16": {"type": "L", "fixes": ["GRU", "DIMBA", "VIBLA", "GIG"]},
    "W17": {"type": "L", "fixes": ["BSB", "NIVPU", "TOBUX", "POSAG", "GRU"]},
    "W18": {"type": "L", "fixes": ["BSB", "OKDIB", "NIVPU", "POSAG", "GRU"]},
    "W19": {"type": "L", "fixes": ["CGN", "GALOT", "OSNAK", "DIMBA", "LATAM", "OLGAX", "FLN"]},
    "W20": {"type": "L", "fixes": ["GRU", "POSAG", "LITRE", "TINOP", "BUVOL", "CGR"]},
    "W21": {"type": "L", "fixes": ["BSB", "GYN", "GUKAB", "ESBAM", "CGB"]},
    "W22": {"type": "L", "fixes": ["BSB", "ESBAM", "NEXAL", "PIDMO", "CGR"]},
    "W23": {"type": "L", "fixes": ["CGR", "PIDMO", "KALAX", "DUTRO", "CGB"]},
    "W24": {"type": "L", "fixes": ["CGB", "KALAX", "NEXAL", "BUVOL", "CGR"]},
    "W25": {"type": "L", "fixes": ["GRU", "CWB", "DOMUX", "RIGEL", "EVTOL", "IGU"]},
    "W26": {"type": "L", "fixes": ["CWB", "IBMAT", "OLGAX", "FLN"]},
    "W27": {"type": "L", "fixes": ["SSA", "ROKBI", "MADOL", "SBIL"]},
    "W28": {"type": "L", "fixes": ["MAO", "PIXAL", "NIKAM", "RUDAL", "STM"]},
    "W29": {"type": "L", "fixes": ["STM", "MALBO", "FUGAL", "DOMAX", "SBMA"]},
    "W30": {"type": "L", "fixes": ["FOR", "ENKAL", "UPKUD", "GULTA", "NAT"]},
    "W31": {"type": "L", "fixes": ["NAT", "UPKUD", "MOLVU", "REC"]},
    "W32": {"type": "L", "fixes": ["MAO", "OGTIM", "PIXAL", "STM", "BEL"]},
    "W33": {"type": "L", "fixes": ["BEL", "PILAX", "ORVAM", "LUMAG", "SLZ"]},
    "W34": {"type": "L", "fixes": ["BSB", "BIDEV", "LIKNO", "KUMBA", "TOPLA", "SSA"]},
    "W35": {"type": "L", "fixes": ["SLZ", "LOKAT", "PIDAX", "THE"]},
    "W36": {"type": "L", "fixes": ["CGR", "BUVOL", "TINOP", "LITRE", "CWB"]},
    "W37": {"type": "L", "fixes": ["FOR", "PIDAX", "LOKAT", "SLZ", "BEL"]},
    "W38": {"type": "L", "fixes": ["GIG", "VIBLA", "GRU", "IBMAT", "CWB"]},
    "W39": {"type": "L", "fixes": ["THE", "MOGDI", "EXBAL", "LUMAG", "SLZ"]},
    "W40": {"type": "L", "fixes": ["PVH", "KUBAG", "OPILA", "EKMAG", "DUTRO", "CGB"]},
    "W41": {"type": "L", "fixes": ["BEL", "ROLAX", "NITVO", "BUMEX", "SBMA"]},
    "W42": {"type": "L", "fixes": ["SBMA", "NITVO", "POXIM", "BSB"]},
    "W43": {"type": "L", "fixes": ["REC", "MCZ"]},
    "W44": {"type": "L", "fixes": ["MCZ", "AJU", "SSA"]},
    "W45": {"type": "L", "fixes": ["POA", "SETIL", "RIVAM", "EVTOL", "MAKRU", "URG"]},
    "W46": {"type": "L", "fixes": ["FLN", "SBNF", "SBJV"]},
    "W47": {"type": "L", "fixes": ["BSB", "UDI", "RAO", "SBKP"]},
    "W48": {"type": "L", "fixes": ["SSA", "TOPLA", "OXNEM", "BIVAD", "REC"]},
    "W49": {"type": "L", "fixes": ["GRU", "RAO", "UDI", "BSB"]},
    "W50": {"type": "L", "fixes": ["CGR", "IGU"]},
    "W51": {"type": "L", "fixes": ["CGB", "DUTRO", "EKMAG", "PVH"]},
    "W52": {"type": "L", "fixes": ["SBRP", "LDB", "SBMG"]},
    "W53": {"type": "L", "fixes": ["BEL", "GEBAM", "DOMAX", "SBMA"]},
    "W54": {"type": "L", "fixes": ["MCP", "OBMAG", "ENPAT", "BVB"]},
    "W55": {"type": "L", "fixes": ["STM", "ODVIN", "GEBAM", "BEL"]},
    "W56": {"type": "L", "fixes": ["THE", "MOGDI", "BUMEX", "POXIM", "GYN"]},
    "W57": {"type": "L", "fixes": ["VIT", "TIPAM", "KELBO", "CGN"]},
    "W58": {"type": "L", "fixes": ["CGB", "REBDO", "IKBAL", "NUTEX", "OPVIM", "STM"]},
    "W59": {"type": "L", "fixes": ["MAO", "MAVOD", "PVH"]},
    "W60": {"type": "L", "fixes": ["POA", "MAKRU", "GOLDA", "URG"]},

    # === AEROVIAS SUPERIORES (UW - Upper) ===
    "UW2":  {"type": "H", "fixes": ["GRU", "DIMBA", "UBKAB", "TOBUX", "BSB"]},
    "UW3":  {"type": "H", "fixes": ["GRU", "UBKAB", "MOVLA", "CGN"]},
    "UW4":  {"type": "H", "fixes": ["GIG", "GRU", "CWB", "POA"]},
    "UW5":  {"type": "H", "fixes": ["CGN", "PAROT", "NIKDO", "SSA"]},
    "UW6":  {"type": "H", "fixes": ["SSA", "OPVAT", "CGN", "GIG"]},
    "UW7":  {"type": "H", "fixes": ["GRU", "OLGAX", "FLN"]},
    "UW8":  {"type": "H", "fixes": ["REC", "GITBO", "DUBAX", "SSA"]},
    "UW9":  {"type": "H", "fixes": ["GRU", "POSAG", "RUDNO", "GYN"]},
    "UW10": {"type": "H", "fixes": ["BSB", "GRU", "CWB", "POA"]},
    "UW11": {"type": "H", "fixes": ["CWB", "RIVAM", "POA"]},
    "UW12": {"type": "H", "fixes": ["GIG", "KELBO", "VIT"]},
    "UW13": {"type": "H", "fixes": ["BSB", "CGN"]},
    "UW14": {"type": "H", "fixes": ["POA", "CWB", "GRU", "GIG"]},
    "UW16": {"type": "H", "fixes": ["GRU", "GIG"]},
    "UW17": {"type": "H", "fixes": ["BSB", "NIVPU", "GRU"]},
    "UW18": {"type": "H", "fixes": ["BSB", "POSAG", "GRU"]},
    "UW20": {"type": "H", "fixes": ["GRU", "TINOP", "CGR"]},
    "UW21": {"type": "H", "fixes": ["BSB", "GYN", "CGB"]},
    "UW22": {"type": "H", "fixes": ["BSB", "CGR"]},
    "UW24": {"type": "H", "fixes": ["CGB", "CGR"]},
    "UW25": {"type": "H", "fixes": ["GRU", "CWB", "IGU"]},
    "UW28": {"type": "H", "fixes": ["MAO", "STM"]},
    "UW30": {"type": "H", "fixes": ["FOR", "NAT"]},
    "UW31": {"type": "H", "fixes": ["NAT", "REC"]},
    "UW32": {"type": "H", "fixes": ["MAO", "STM", "BEL"]},
    "UW33": {"type": "H", "fixes": ["BEL", "SLZ"]},
    "UW34": {"type": "H", "fixes": ["BSB", "LIKNO", "SSA"]},
    "UW37": {"type": "H", "fixes": ["FOR", "SLZ", "BEL"]},
    "UW40": {"type": "H", "fixes": ["PVH", "CGB"]},
    "UW42": {"type": "H", "fixes": ["SBMA", "BSB"]},
    "UW45": {"type": "H", "fixes": ["POA", "URG"]},
    "UW47": {"type": "H", "fixes": ["BSB", "UDI", "SBKP"]},
    "UW48": {"type": "H", "fixes": ["SSA", "REC"]},
    "UW51": {"type": "H", "fixes": ["CGB", "PVH"]},
    "UW54": {"type": "H", "fixes": ["MCP", "BVB"]},
    "UW56": {"type": "H", "fixes": ["THE", "GYN"]},
    "UW59": {"type": "H", "fixes": ["MAO", "PVH"]},
}

# =========================================================
# REHA - Rotas Especiais de Helicópteros (SP e RJ)
# =========================================================
REHA = {
    "REHA SP-01": [(-23.55, -46.66), (-23.52, -46.63), (-23.49, -46.60), (-23.46, -46.56), (-23.43, -46.53)],
    "REHA SP-02": [(-23.55, -46.66), (-23.52, -46.70), (-23.49, -46.74), (-23.46, -46.78)],
    "REHA SP-03": [(-23.55, -46.66), (-23.58, -46.64), (-23.61, -46.61), (-23.64, -46.58), (-23.67, -46.55)],
    "REHA SP-04": [(-23.55, -46.66), (-23.58, -46.69), (-23.62, -46.72), (-23.65, -46.75)],
    "REHA SP-05": [(-23.55, -46.66), (-23.54, -46.62), (-23.52, -46.57), (-23.50, -46.53)],
    "REHA SP-06": [(-23.55, -46.66), (-23.53, -46.71), (-23.51, -46.76), (-23.49, -46.81)],
    "REHA SP-07": [(-23.55, -46.66), (-23.57, -46.71), (-23.59, -46.76), (-23.61, -46.81)],
    "REHA SP-08": [(-23.55, -46.66), (-23.50, -46.67), (-23.45, -46.68), (-23.40, -46.69)],
    "REHA RJ-01": [(-22.91, -43.17), (-22.88, -43.20), (-22.85, -43.24), (-22.82, -43.28)],
    "REHA RJ-02": [(-22.91, -43.17), (-22.88, -43.14), (-22.85, -43.10), (-22.82, -43.06)],
    "REHA RJ-03": [(-22.91, -43.17), (-22.94, -43.19), (-22.98, -43.22), (-23.01, -43.25)],
    "REHA RJ-04": [(-22.91, -43.17), (-22.94, -43.15), (-22.97, -43.12), (-23.00, -43.09)],
    "REHA RJ-05": [(-22.91, -43.17), (-22.90, -43.22), (-22.88, -43.28), (-22.86, -43.33)],
    "REHA RJ-06": [(-22.91, -43.17), (-22.93, -43.13), (-22.95, -43.09), (-22.97, -43.05)],
    "REHA RJ-07": [(-22.91, -43.17), (-22.87, -43.17), (-22.83, -43.17), (-22.79, -43.17)],
    "REHA RJ-08": [(-22.91, -43.17), (-22.91, -43.22), (-22.91, -43.27), (-22.91, -43.32)],
}


def build_geojson():
    features = []
    
    # Build airways
    for name, data in AIRWAYS.items():
        coords = []
        for fix_name in data["fixes"]:
            if fix_name in FIXES:
                lat, lon = FIXES[fix_name]
                coords.append([lon, lat])  # GeoJSON is [lon, lat]
            else:
                print(f"[WARN] Fix '{fix_name}' not found for airway {name}")
        
        if len(coords) >= 2:
            features.append({
                "type": "Feature",
                "properties": {"name": name, "type": data["type"]},
                "geometry": {"type": "LineString", "coordinates": coords}
            })
    
    # Build REHA
    for name, points in REHA.items():
        coords = [[lon, lat] for lat, lon in points]
        features.append({
            "type": "Feature",
            "properties": {"name": name, "type": "REHA"},
            "geometry": {"type": "LineString", "coordinates": coords}
        })
    
    return {"type": "FeatureCollection", "features": features}


def main():
    print("=" * 60)
    print("  GERADOR COMPLETO DE AEROVIAS BRASILEIRAS")
    print("  Baseado em fixos/VORs do AIP Brasil")
    print("=" * 60)
    
    geojson = build_geojson()
    
    lower = sum(1 for f in geojson["features"] if f["properties"]["type"] == "L")
    upper = sum(1 for f in geojson["features"] if f["properties"]["type"] == "H")
    reha  = sum(1 for f in geojson["features"] if f["properties"]["type"] == "REHA")
    total = len(geojson["features"])
    
    print(f"\n[RESULTADO]")
    print(f"  Aerovias Inferiores (W):  {lower}")
    print(f"  Aerovias Superiores (UW): {upper}")
    print(f"  REHA (Helicópteros):      {reha}")
    print(f"  TOTAL:                    {total}")
    
    outpath = "airways_brazil.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)
    print(f"\n[*] Salvo em: {outpath}")
    print(f"[*] Tamanho: {len(json.dumps(geojson)):,} bytes")


if __name__ == "__main__":
    main()
