import csv
import math
import os
import sys
import argparse
from urllib.request import urlretrieve

# --- Configuration ---
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
DATA_FILE = "airports.csv"

EARTH_RADII = {"km": 6371.0, "mi": 3958.8, "nm": 3440.1}

# --- City Name Overrides ---
# Unified Toronto entries to remove the false dichotomy
CITY_OVERRIDES = {
    "YYZ": "Toronto", 
    "YTZ": "Toronto", 
    "YVR": "Vancouver",
    "YUL": "Montreal", "YYC": "Calgary", "YOW": "Ottawa",
    "YEG": "Edmonton", "YWG": "Winnipeg", "YHZ": "Halifax",
    "JFK": "New-York", "EWR": "New-York", "LGA": "New-York",
    "MEX": "Mexico-City", "NLU": "Mexico-City (AIFA)",
    "BOS": "Boston", "FLL": "Fort-Lauderdale", "MCO": "Orlando",
    "LYS": "Lyon", "CDG": "Paris", "ORY": "Paris",
    "LHR": "London", "LGW": "London", "WSI": "Sydney",
    "NRT": "Tokyo", "HND": "Tokyo", "ICN": "Seoul"
}

# --- Alliance Registry ---
ALLIANCES = {
    "oneworld": {"AA", "BA", "IB", "QF", "CX", "JL", "QR", "AY", "AS", "AT", "MH", "UL", "HA"},
    "star": {"UA", "LH", "SQ", "NZ", "AC", "NH", "OZ", "TK", "LX", "OS", "SN", "TP", "AI", "ET", "LO", "AZ", "LG"},
    "skyteam": {"DL", "AF", "KL", "KE", "AM", "SV", "VN", "GA", "ME", "SK"}
}

# --- Airline Hub Registry ---
AIRLINE_HUBS = {
    "AC": {"YYZ", "YVR", "YUL", "YYC", "YOW", "YHZ"}, 
    "WS": {"YYC", "YYZ", "YVR", "YEG", "YWG"},       
    "TS": {"YUL", "YYZ", "YVR"},                     
    "PD": {"YTZ", "YYZ", "YOW", "YUL"},             
    "B6": {"JFK", "BOS", "FLL", "MCO", "LGB", "SJU", "PBI"},
    "AM": {"MEX", "MTY", "GDL", "CUN", "TIJ"}, 
    "Y4": {"MEX", "TIJ", "GDL", "CUN", "MTY", "BJX"}, 
    "VB": {"MTY", "MEX", "GDL", "CUN", "TIJ"}, 
    "LG": {"LUX"}, "DY": {"OSL", "ARN", "CPH", "BGO", "SVG", "TRD", "HEL"}, 
    "SK": {"CPH", "ARN", "OSL"}, "AY": {"HEL"}, "LX": {"ZRH", "GVA"},
    "AZ": {"FCO", "LIN", "MXP"}, "LO": {"WAW"}, "TP": {"LIS", "OPO"},
    "BT": {"RIX", "VNO", "TLL"}, "AF": {"CDG", "ORY", "NCE", "LYS"},
    "KL": {"AMS"}, "BA": {"LHR", "LGW", "LCY"}, "IB": {"MAD", "BCN"},
    "OS": {"VIE"}, "LH": {"FRA", "MUC", "BER", "DUS", "HAM", "STR", "HAJ"},
    "VA": {"BNE", "MEL", "SYD", "ADL", "PER"}, 
    "QF": {"SYD", "MEL", "BNE", "PER", "ADL", "DRW", "TMW", "CNS", "TSV", "CBR", "WSI"},
    "NZ": {"AKL", "CHC", "WLG", "ZQN", "NSN", "DUD"},
    "HA": {"HNL", "OGG", "KOA", "LIH"}, "AS": {"SEA", "ANC", "PDX", "SFO", "LAX", "HNL"},
    "KE": {"ICN", "GMP", "PUS"}, "OZ": {"ICN", "GMP", "PUS"},
    "JL": {"HND", "NRT", "ITM", "KIX"}, "NH": {"HND", "NRT", "ITM", "KIX"},
    "CX": {"HKG"}, "SQ": {"SIN"}, "EI": {"DUB", "SNN", "ORK"},
    "UA": {"ORD", "SFO", "EWR", "DEN", "IAH", "LAX", "IAD", "HNL"},
    "AA": {"CLT", "DFW", "MIA", "PHL", "PHX", "DCA", "ORD", "LGA", "LAX", "JFK"},
    "DL": {"ATL", "DTW", "MSP", "SLC", "JFK", "LGA", "BOS", "LAX", "SEA", "HNL"}
}

def download_data():
    if not os.path.exists(DATA_FILE):
        urlretrieve(AIRPORTS_URL, DATA_FILE)

def calculate_distance(lat1, lon1, lat2, lon2, unit="km"):
    radius = EARTH_RADII.get(unit if unit in EARTH_RADII else "km")
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_filtered_airlines(iata_code, alliance_limit=None):
    if not iata_code: return ""
    matches = [air for air, hubs in AIRLINE_HUBS.items() if iata_code.upper() in hubs]
    if alliance_limit:
        members = ALLIANCES.get(alliance_limit.lower(), set())
        matches = [m for m in matches if m in members]
    return ", ".join(sorted(set(matches)))

def get_airports_in_range(center_code, max_dist, unit="km", alliance=None, hub_only=False, same_country=False, same_continent=False):
    download_data()
    airports_data = []
    origin = None
    center_code = center_code.upper()

    with open(DATA_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            airports_data.append(row)
            if not origin and (row['iata_code'] == center_code or row['ident'] == center_code):
                origin = row
    
    if not origin: return None

    all_known_hubs = set().union(*AIRLINE_HUBS.values())
    alliance_hubs = set()
    if alliance:
        for member in ALLIANCES[alliance.lower()]:
            alliance_hubs.update(AIRLINE_HUBS.get(member, set()))

    results = []
    for row in airports_data:
        if not row['latitude_deg'] or not row['longitude_deg']: continue
        if same_country and row['iso_country'] != origin['iso_country']: continue
        if same_continent and row['continent'] != origin['continent']: continue

        dist = calculate_distance(float(origin['latitude_deg']), float(origin['longitude_deg']),
                                float(row['latitude_deg']), float(row['longitude_deg']), unit=unit)

        if (unit not in ["country", "continent"]) and dist > max_dist: continue
        iata = row['iata_code']
        
        if hub_only and iata not in all_known_hubs: continue
        if alliance and iata not in alliance_hubs: continue
        if not (hub_only or alliance) and row['type'] != 'large_airport': continue

        display_airlines = get_filtered_airlines(iata, alliance_limit=alliance)
        if (hub_only or alliance) and not display_airlines: continue

        if iata in CITY_OVERRIDES:
            short_city = CITY_OVERRIDES[iata]
        else:
            full_city = row['municipality'] or "Unknown"
            short_city = full_city.split()[0].replace(',', '').replace('-', '')

        results.append({
            "code": iata if iata else row['ident'],
            "name": row['name'],
            "city": short_city,
            "distance": round(dist, 2),
            "airlines": display_airlines
        })

    return sorted({res['code']: res for res in results}.values(), key=lambda x: x['distance'])

def main():
    parser = argparse.ArgumentParser(description="✈️ Airport Hub & Alliance Finder")
    parser.add_argument("code", help="Origin IATA code")
    parser.add_argument("max_dist", type=float, help="Radius")
    parser.add_argument("-u", "--unit", choices=["km", "mi", "nm", "country", "continent"], default="km")
    parser.add_argument("-c", "--same-country", action="store_true")
    parser.add_argument("-K", "--same-continent", action="store_true")
    parser.add_argument("--alliance", choices=["oneworld", "star", "skyteam"])
    parser.add_argument("--hub-only", action="store_true")

    args = parser.parse_args()
    
    res = get_airports_in_range(args.code, args.max_dist, unit=args.unit, 
                                 alliance=args.alliance, hub_only=args.hub_only,
                                 same_country=(args.unit=="country" or args.same_country),
                                 same_continent=(args.unit=="continent" or args.same_continent))

    if not res:
        print("No matches found.")
        return

    mode_label = f"{args.alliance.upper()} " if args.alliance else ""
    mode_label += "HUBS" if args.hub_only or args.alliance else "LARGE AIRPORTS"
    
    print(f"\nFound {len(res)} {mode_label} for {args.code.upper()}:")
    print("=" * 125)
    print(f"{'Code':<8} | {'City':<15} | {'Name':<40} | {'Distance':<12} | {'Airlines'}")
    print("-" * 125)
    for a in res:
        if a['distance'] == 0: continue
        print(f"{a['code']:<8} | {a['city']:<15} | {a['name'][:40]:<40} | {a['distance']:>6} {args.unit:<3} | {a['airlines']}")

if __name__ == "__main__":
    main()