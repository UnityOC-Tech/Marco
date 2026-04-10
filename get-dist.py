import csv
import math
import os
import argparse
from urllib.request import urlretrieve

# --- Configuration ---
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
DATA_FILE = "airports.csv"

EARTH_RADII = {"km": 6371.0, "mi": 3958.8, "nm": 3440.1}

# --- City Name Overrides ---
CITY_OVERRIDES = {
    # Japan
    "HND": "Tokyo", "NRT": "Tokyo",
    "ITM": "Osaka", "KIX": "Osaka", "UKB": "Kobe",
    "NGO": "Nagoya", "NKM": "Nagoya",
    "CTS": "Sapporo", "OKD": "Sapporo",
    "FUK": "Fukuoka", "OKA": "Okinawa",

    # Korea
    "ICN": "Seoul", "GMP": "Seoul", "PUS": "Busan",

    # Taiwan
    "TPE": "Taipei", "TSA": "Taipei", "KHH": "Kaohsiung",
    
    # Southeast Asia
    "BKK": "Bangkok", "DMK": "Bangkok",
    "MNL": "Manila", "CRK": "Manila",
    "CGK": "Jakarta", "HLP": "Jakarta",
    "KUL": "Kuala Lumpur", "SZB": "Kuala Lumpur",
    "SGN": "Ho Chi Minh City", "HAN": "Hanoi",
    "CEB": "Cebu", "DPS": "Bali",

    # Mainland China
    "PEK": "Beijing", "PKX": "Beijing",
    "PVG": "Shanghai", "SHA": "Shanghai",
    "CAN": "Guangzhou", "SZX": "Shenzhen",
    "CTU": "Chengdu", "TFU": "Chengdu",
    "KMG": "Kunming", "XIY": "Xi'an",
    "HAK": "Haikou", "XMN": "Xiamen",
    
    # Asia & Oceania
    "SYD": "Sydney", "WSI": "Sydney",
    "MEL": "Melbourne", "AVV": "Melbourne",
    "SIN": "Singapore", "HKG": "Hong Kong",
    "POM": "Port Moresby", "NOU": "Noumea",
    "NAN": "Nadi", "SUV": "Suva", "PPT": "Papeete",
    "RAR": "Rarotonga", "HIR": "Honiara", "VLI": "Port Vila",
    
    # Scandinavia & Nordics
    "CPH": "Copenhagen", "ARN": "Stockholm", "BMA": "Stockholm",
    "OSL": "Oslo", "HEL": "Helsinki", "KEF": "Reykjavik",
    "RKV": "Reykjavik", "FAE": "Vágar", "BGO": "Bergen",
    
    # Baltics
    "RIX": "Riga", "TLL": "Tallinn", "VNO": "Vilnius",

    # Greenland
    "GOH": "Nuuk", "SFJ": "Kangerlussuaq", "JAV": "Ilulissat",
    
    # Atlantic & Azores
    "PDL": "Ponta Delgada", "TER": "Terceira", "HOR": "Horta",
    "SID": "Sal", "RAI": "Praia",

    # Indian Ocean
    "MRU": "Mauritius", "RUN": "Saint-Denis", "SEZ": "Victoria",
    "MLE": "Malé", "TNR": "Antananarivo",
    
    # Africa
    "JNB": "Johannesburg", "CPT": "Cape Town", "NBO": "Nairobi",
    "ADD": "Addis Ababa", "CAI": "Cairo", "CMN": "Casablanca",
    "LFW": "Lomé",

    # Middle East
    "DXB": "Dubai", "DWC": "Dubai", "DOH": "Doha", "AUH": "Abu Dhabi",
    "JED": "Jeddah", "RUH": "Riyadh", "DMM": "Dammam", "MED": "Medina",
    "BAH": "Bahrain", "MCT": "Muscat", "BEY": "Beirut", "AMM": "Amman",
    "KWI": "Kuwait City", "SHJ": "Sharjah",
    
    # Americas & Hawaii
    "HNL": "Honolulu", "OGG": "Kahului", "LIH": "Lihue", "KOA": "Kona",
    "GUM": "Guam", "SJU": "San Juan",
    "JFK": "New York", "EWR": "New York", "LGA": "New York",
    "ORD": "Chicago", "MDW": "Chicago",
    "IAD": "Washington", "DCA": "Washington", "BWI": "Washington",
    "LAX": "Los Angeles", "BUR": "Los Angeles", "LGB": "Los Angeles", "ONT": "Los Angeles", "SNA": "Los Angeles",
    "HOU": "Houston", "IAH": "Houston",
    "YYZ": "Toronto", "YTZ": "Toronto",
    "MEX": "Mexico City", "NLU": "Mexico City",
    
    # Europe
    "LHR": "London", "LGW": "London", "STN": "London", "LCY": "London", "LTN": "London",
    "CDG": "Paris", "ORY": "Paris",
    "FCO": "Rome", "CIA": "Rome"
}

# --- Alliance Registry ---
ALLIANCES = {
    "oneworld": {"AA", "BA", "IB", "QF", "CX", "JL", "QR", "AY", "AS", "AT", "MH", "UL", "HA", "WY", "RJ", "FJ"},
    "star": {"UA", "LH", "SQ", "NZ", "AC", "NH", "OZ", "TK", "LX", "OS", "SN", "TP", "AI", "ET", "LO", "AZ", "LG", "AV", "CA", "ZH", "TG", "BR", "SA", "MS"},
    "skyteam": {"DL", "AF", "KL", "KE", "AM", "SV", "VN", "GA", "ME", "SK", "MU", "MF", "CI", "KQ"}
}

# --- Airline Hub Registry ---
AIRLINE_HUBS = {
    # Pacific Islands (Oceania)
    "FJ": {"NAN", "SUV"},
    "TN": {"PPT"},
    "VT": {"PPT"},
    "SB": {"NOU"},
    "PX": {"POM"},
    "GZ": {"RAR"},
    "IE": {"HIR"},
    "NF": {"VLI"},
    "ON": {"INU"},

    # Hawaii & US Territories
    "HA": {"HNL", "OGG", "LIH", "KOA"},
    "MW": {"HNL", "OGG", "LIH", "KOA"},
    "UA": {"GUM", "HNL", "ORD", "SFO", "EWR", "DEN", "IAH", "LAX", "IAD"},

    # Atlantic Islands & Azores
    "S4": {"PDL", "TER", "LIS"},
    "SP": {"PDL", "HOR", "TER"},
    "VR": {"SID", "RAI"},

    # Indian Ocean
    "MK": {"MRU"},
    "UU": {"RUN"},
    "HM": {"SEZ"},
    "Q2": {"MLE"},
    "MD": {"TNR"},

    # Scandinavia & Nordics
    "SK": {"CPH", "ARN", "OSL"},
    "AY": {"HEL"},
    "DY": {"OSL", "ARN", "CPH"},
    "FI": {"KEF", "RKV"},
    "RC": {"FAE"},
    "WF": {"BGO", "OSL", "TRF"},

    # Baltics
    "BT": {"RIX", "TLL", "VNO"},

    # Greenland
    "GL": {"GOH", "SFJ", "JAV"},

    # Japan & Korea & Taiwan
    "JL": {"HND", "NRT", "ITM", "KIX", "FUK", "CTS", "OKA"}, 
    "NH": {"HND", "NRT", "ITM", "KIX", "FUK", "CTS", "NGO"}, 
    "KE": {"ICN", "GMP", "PUS", "CJU"},                     
    "OZ": {"ICN", "GMP"},                                   
    "BR": {"TPE", "KHH"},                                   
    "CI": {"TPE", "KHH"},                                   
    "JX": {"TPE"},                                          

    # Southeast Asia
    "TG": {"BKK"},                                          
    "FD": {"DMK", "BKK", "HKT", "CNX"},                     
    "VN": {"HAN", "SGN", "DAD"},                            
    "GA": {"CGK", "DPS", "SUB"},                            
    "MH": {"KUL"},                                          
    "SQ": {"SIN"},                                          

    # Middle East
    "EK": {"DXB"},                                          
    "QR": {"DOH"},                                          
    "EY": {"AUH"},                                          
    "SV": {"JED", "RUH", "MED", "DMM"},                     
    "WY": {"MCT"},                                          
    "ME": {"BEY"},                                          
    "GF": {"BAH"},                                          
    "RJ": {"AMM"},                                          

    # North & South America
    "AA": {"CLT", "DFW", "MIA", "PHL", "PHX", "DCA", "ORD", "LGA", "LAX", "JFK"},
    "DL": {"ATL", "DTW", "MSP", "SLC", "JFK", "LGA", "BOS", "LAX", "SEA", "HNL"},
    "LA": {"SCL", "GRU", "LIM", "BOG", "AEP"},               
    "AV": {"BOG", "SAL", "LIM"}
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

def get_airports_in_range(center_code, max_dist, unit="km", alliance=None, country=None, hub_only=False, same_country=False, same_continent=False):
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
    
    if not origin:
        return None

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
        if country and row['iso_country'].upper() != country.upper(): continue

        dist = calculate_distance(float(origin['latitude_deg']), float(origin['longitude_deg']),
                                float(row['latitude_deg']), float(row['longitude_deg']), unit=unit)

        if (unit not in ["country", "continent"]) and dist > max_dist: continue
        
        iata = row['iata_code']
        if hub_only and iata not in all_known_hubs:
            continue
        if alliance and iata not in alliance_hubs:
            continue
        if not (hub_only or alliance) and row['type'] != 'large_airport': continue

        display_airlines = get_filtered_airlines(iata, alliance_limit=alliance)
        if (hub_only or alliance) and not display_airlines: 
            continue

        if iata in CITY_OVERRIDES:
            display_city = CITY_OVERRIDES[iata]
        else:
            full_city = row['municipality'] or "Unknown"
            display_city = full_city.split()[0].replace(',', '').replace('-', '')

        results.append({
            "code": iata if iata else row['ident'],
            "name": row['name'],
            "city": display_city,
            "distance": int(round(dist)),
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
    parser.add_argument("--country", help="Filter by ISO country code (e.g., JP, KR, TW)")
    parser.add_argument("--hub-only", action="store_true")

    args = parser.parse_args()
    res = get_airports_in_range(args.code, args.max_dist, unit=args.unit, 
                                 alliance=args.alliance, country=args.country,
                                 hub_only=args.hub_only,
                                 same_country=(args.unit=="country" or args.same_country),
                                 same_continent=(args.unit=="continent" or args.same_continent))

    if not res:
        print("No matches found.")
        return

    active_filters = []
    if args.alliance: active_filters.append(args.alliance.upper())
    if args.country: active_filters.append(args.country.upper())
    label = " ".join(active_filters) + " " if active_filters else ""
    label += "HUBS" if args.hub_only or args.alliance else "LARGE AIRPORTS"
    print(f"\nFound {len(res)} {label} for {args.code.upper()}:")
    print("=" * 135)
    print(f"{'Code':<8} | {'City':<18} | {'Name':<40} | {'Distance':<14} | {'Airlines'}")
    print("-" * 135)
    for a in res:
        if a['distance'] == 0: continue
        dist_str = f"{a['distance']:,} {args.unit}"
        print(f"{a['code']:<8} | {a['city']:<18} | {a['name'][:40]:<40} | {dist_str:>10} | {a['airlines']}")

if __name__ == "__main__":
    main()