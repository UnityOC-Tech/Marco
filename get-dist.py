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
UNIT_LABELS = {"km": "km", "mi": "mi", "nm": "nm"}

# --- Airline Hub Registry (>10M Annual Passengers) ---
AIRLINE_HUBS = {
    # North America
    "AA": {"CLT", "DFW", "MIA", "PHL", "PHX", "DCA", "ORD", "LGA", "LAX", "JFK"},
    "DL": {"ATL", "DTW", "MSP", "SLC", "CVG", "JFK", "LGA", "BOS", "LAX", "SEA"},
    "UA": {"ORD", "SFO", "EWR", "DEN", "IAH", "LAX", "IAD", "GUM"},
    "WN": {"ATL", "BWI", "MDW", "DAL", "DEN", "FLL", "HOU", "LAS", "LAX", "MCO", "OAK", "PHX", "SAN"},
    "AS": {"SEA", "ANC", "PDX", "SFO", "LAX"},
    "B6": {"JFK", "BOS", "FLL", "MCO", "LGB"},
    "NK": {"FLL", "MCO", "LAS", "DTW", "ORD"},
    "F9": {"DEN", "MCO", "PHL", "LAS"},
    "AC": {"YYZ", "YUL", "YVR", "YYC"},
    "WS": {"YYC", "YYZ", "YVR"},

    # Europe
    "LH": {"FRA", "MUC"},
    "AF": {"CDG", "ORY"},
    "KL": {"AMS"},
    "BA": {"LHR", "LGW"},
    "IB": {"MAD"},
    "FR": {"DUB", "STN", "BGY", "CRL", "MAD", "BCN", "CPH", "LIS"},
    "U2": {"LGW", "LTN", "MAN", "AMS", "CDG", "MXP"},
    "W6": {"BUD", "WAW", "LTN", "VIE", "OTP"},
    "VY": {"BCN", "FCO", "ORY"},
    "EI": {"DUB"},
    "LX": {"ZRH", "GVA"},
    "OS": {"VIE"},

    # Asia-Pacific
    "QF": {"SYD", "MEL", "BNE", "PER", "ADL", "DRW"},
    "VA": {"BNE", "MEL", "SYD", "ADL", "PER"},
    "JQ": {"MEL", "SYD", "BNE", "OOL", "AKL", "ADL", "CHC", "CNS", "PER"},
    "SQ": {"SIN"},
    "NZ": {"AKL", "CHC", "WLG"},
    "CX": {"HKG"},
    "KE": {"ICN", "GMP"},
    "NH": {"HND", "NRT", "ITM", "KIX"},
    "JL": {"HND", "NRT", "ITM", "KIX"},
    "6E": {"DEL", "BOM", "BLR", "CCU", "HYD", "MAA"},
    "AI": {"DEL", "BOM"},
    "MH": {"KUL"},
    "TG": {"BKK"},
    "VN": {"HAN", "SGN"},

    # China
    "CA": {"PEK", "PKX", "CTU", "TFU", "PVG", "SZX", "HGH", "WUH"},
    "CZ": {"CAN", "PKX", "PEK", "CKG", "SZX", "WUH"},
    "MU": {"PVG", "SHA", "PKX", "KMG", "XIY"},
    "HU": {"HAK", "PEK", "XIY", "SZX"},

    # Middle East & Africa
    "EK": {"DXB"},
    "TK": {"IST", "ESB"},
    "QR": {"DOH"},
    "EY": {"AUH"},
    "SV": {"RUH", "JED", "DMM"},
    "ET": {"ADD"},

    # Latin America
    "LA": {"SCL", "GRU", "LIM", "BOG", "AEP", "EZE"},
    "AV": {"BOG", "SAL"},
    "CM": {"PTY"},
    "AM": {"MEX"},
}

HARDCODED_AIRPORTS = {
    "WSI": {
        "ident": "YSWS", "iata_code": "WSI", "type": "large_airport",
        "name": "Western Sydney International Airport",
        "latitude_deg": -33.8833, "longitude_deg": 150.716
    }
}

class PrettierParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'Error: {message}\n\n')
        self.print_help()
        sys.exit(2)

def download_data():
    if not os.path.exists(DATA_FILE):
        print(">> Initial setup: Downloading airport database...")
        urlretrieve(AIRPORTS_URL, DATA_FILE)

def calculate_distance(lat1, lon1, lat2, lon2, unit="km"):
    radius = EARTH_RADII.get(unit, EARTH_RADII["km"])
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_airports_in_range(center_code, min_dist, max_dist, unit="km", filter_mode="large", hub_airline=None):
    download_data()
    airports_data = []
    center_coords = None
    center_code = center_code.upper()

    with open(DATA_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            airports_data.append(row)
            if not center_coords:
                if row['iata_code'] == center_code or row['ident'] == center_code:
                    center_coords = (float(row['latitude_deg']), float(row['longitude_deg']))
    
    if not center_coords and center_code in HARDCODED_AIRPORTS:
        entry = HARDCODED_AIRPORTS[center_code]
        center_coords = (entry['latitude_deg'], entry['longitude_deg'])

    if not center_coords: return None

    for _, data in HARDCODED_AIRPORTS.items():
        if not any(r['iata_code'] == data['iata_code'] for r in airports_data):
            airports_data.append(data)

    ga_types = {'large_airport', 'medium_airport', 'small_airport'}
    
    # Logic for default "ALL" hub search
    if hub_airline and hub_airline.upper() == "ALL":
        hub_set = set().union(*AIRLINE_HUBS.values())
    else:
        hub_set = AIRLINE_HUBS.get(hub_airline.upper(), set()) if hub_airline else set()

    results = []
    for row in airports_data:
        if not row['latitude_deg'] or not row['longitude_deg']: continue
        
        dist = calculate_distance(center_coords[0], center_coords[1],
                                float(row['latitude_deg']), float(row['longitude_deg']), unit=unit)

        if min_dist <= dist <= max_dist:
            if filter_mode == "hub":
                if row['iata_code'] not in hub_set: continue
            elif filter_mode == "large" and row['type'] != 'large_airport':
                continue
            elif filter_mode == "ga" and row['type'] not in ga_types:
                continue

            results.append({
                "code": row['iata_code'] if row['iata_code'] else row['ident'],
                "name": row['name'], "distance": round(dist, 2), "type": row['type']
            })

    unique_results = {res['code']: res for res in results}.values()
    return sorted(unique_results, key=lambda x: x['distance'])

def main():
    parser = PrettierParser(
        description="✈️  Airport Proximity Finder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get-dist.py SYD 1000 --hub      # Show ALL hubs in registry within 1000km
  python get-dist.py SYD 1000 --hub QF   # Show only Qantas hubs
  python get-dist.py LHR 500 --ga        # Show General Aviation nearby
        """
    )

    parser.add_argument("code", help="IATA/ICAO code (e.g., SYD, PEK)")
    parser.add_argument("max_dist", type=float, help="Max search radius")
    parser.add_argument("-u", "--unit", choices=["km", "mi", "nm"], default="km")
    
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument("--ga", action="store_true", help="Include General Aviation")
    filter_group.add_argument("--hub", nargs='?', const='ALL', metavar="AIRLINE", 
                        help="Only show hubs. Specify airline code or leave blank for all.")
    filter_group.add_argument("--include-all", action="store_true", help="Show all airfields")

    args = parser.parse_args()

    mode = "large"
    if args.include_all: mode = "all"
    elif args.ga: mode = "ga"
    elif args.hub: 
        mode = "hub"
        if args.hub.upper() != "ALL" and args.hub.upper() not in AIRLINE_HUBS:
            print(f"❌ Error: Airline '{args.hub.upper()}' not found in the registry.")
            return

    nearby = get_airports_in_range(args.code, 0, args.max_dist, unit=args.unit, 
                                   filter_mode=mode, hub_airline=args.hub)

    if nearby is None:
        print(f"Error: Could not find '{args.code.upper()}'.")
    elif not nearby:
        print("No matches found.")
    else:
        label = "ALL REGISTRY HUBS" if args.hub.upper() == "ALL" else f"{args.hub.upper()} HUBS"
        unit_str = UNIT_LABELS[args.unit]
        print(f"Found {len(nearby)} {label} within {args.max_dist} {unit_str}:")
        print("-" * 80)
        for a in nearby:
            if a['distance'] == 0: continue
            print(f"{a['code']:<10} | {a['name'][:45]:<45} | {a['distance']} {unit_str}")

if __name__ == "__main__":
    main()