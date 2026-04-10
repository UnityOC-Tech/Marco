"""
2026 Global Alliance Lounge Finder
Version 43.0 - Master Registry (Full Consolidated Global Edition)
Complete data for: 
- North America: US (EWR, JFK, LAX, ORD, SLC, HNL, OGG, ANC, FAI)
- Germany: MUC, FRA, BER, DUS, HAM, STR, CGN
- France: CDG, ORY, NCE, LYS, MRS, TLS, BOD, BSL, NTE, MPL, SXB
- UK/AU/IE: LHR, SYD, DUB
- Europe (Central/South): LUX, AMS, BRU, MAD, BCN, LIS, OPO, FCO, MXP, VIE, ZRH, GVA, CPH, WAW
- Scandinavia & Baltics: KEF, OSL, ARN, HEL, TLL, RIX, VNO
- CIS & Balkans: SVO, DME, LED, IKT, VVO, OVB, SVX, KZN, MSQ, ALA, NQZ, ATH, BEG, OTP, ZAG, SOF, LJU, TIA, SJJ
- East Asia: HND, NRT, KIX, ITM, ICN, GMP, PUS, TPE, TSA, KHH
"""

import argparse
from typing import Dict, List, Optional

# --- REGIONAL MAPPING ---
ISO_MAP: Dict[str, str] = {
    "US": "United States", "USA": "United States", "UK": "United Kingdom",
    "AU": "Australia", "NZ": "New Zealand", "DE": "Germany", "IE": "Ireland",
    "FR": "France", "LU": "Luxembourg", "NL": "Netherlands", "BE": "Belgium", 
    "ES": "Spain", "PT": "Portugal", "IT": "Italy", "AT": "Austria", 
    "CH": "Switzerland", "DK": "Denmark", "PL": "Poland", "LI": "Liechtenstein",
    "IS": "Iceland", "NO": "Norway", "SE": "Sweden", "FI": "Finland",
    "BY": "Belarus", "RU": "Russia", "KZ": "Kazakhstan", "EE": "Estonia", 
    "LV": "Latvia", "LT": "Lithuania", "GR": "Greece", "RS": "Serbia", 
    "RO": "Romania", "HR": "Croatia", "BG": "Bulgaria", "SI": "Slovenia", 
    "AL": "Albania", "BA": "Bosnia", "JP": "Japan", "KR": "South Korea",
    "ROK": "South Korea", "TW": "Taiwan", "ROC": "Taiwan"
}

# --- MASTER DATABASE ---
LOUNGE_DATA: Dict[str, Dict[str, List[Dict]]] = {
    # --- NORTH AMERICA ---
    "EWR": {"Star Alliance": [{"name": "United Polaris Lounge", "operator": "United", "terminal": "T-C", "features": ["fine-dining", "nap-pods"], "location": "C102-C120"}], "Oneworld / SkyTeam": [{"name": "British Airways Lounge", "operator": "BA", "terminal": "T-B", "features": ["dining"], "location": "Near B50"}], "Premium": [{"name": "Centurion Lounge", "operator": "AMEX", "terminal": "T-A", "features": ["jazz-bar"], "location": "Level 2"}]},
    "JFK": {"SkyTeam": [{"name": "Delta One Lounge", "operator": "Delta", "terminal": "T4", "features": ["spa"], "location": "Gate B27"}]},
    "LAX": {"Oneworld": [{"name": "Qantas First", "operator": "Qantas", "terminal": "TBIT", "features": ["spa"], "location": "Level 5"}]},
    "ORD": {"Star Alliance": [{"name": "United Polaris", "operator": "United", "terminal": "T1", "features": ["dining"], "location": "Gate C18"}]},
    "SLC": {"SkyTeam": [{"name": "Delta Sky Club", "operator": "Delta", "terminal": "A", "features": ["deck"], "location": "Level 2"}]},
    "HNL": {"Oneworld": [{"name": "Plumeria Lounge", "operator": "Hawaiian", "terminal": "T1", "features": ["bar"], "location": "L3"}]},
    "OGG": {"Oneworld": [{"name": "Premier Club", "operator": "Hawaiian", "terminal": "Main", "features": ["wifi"], "location": "Gate 17"}]},
    "ANC": {"Oneworld": [{"name": "Alaska Lounge", "operator": "Alaska", "terminal": "C", "features": ["fireplace"], "location": "Gate C1"}]},
    "FAI": {"Oneworld": [{"name": "Alaska Lounge", "operator": "Alaska", "terminal": "Main", "features": ["wifi"], "location": "Post-Security"}]},

    # --- GERMANY & FRANCE ---
    "FRA": {"Star Alliance": [{"name": "Lufthansa First Class Terminal", "operator": "Lufthansa", "terminal": "FCT", "features": ["valet"], "location": "Stand-alone"}]},
    "MUC": {"Star Alliance": [{"name": "Lufthansa First Lounge", "operator": "Lufthansa", "terminal": "T2", "features": ["limo"], "location": "Satellite K/L"}]},
    "BER": {"Airport": [{"name": "Lounge Tempelhof", "operator": "BER", "terminal": "T1", "features": ["terrace"], "location": "Schengen"}]},
    "DUS": {"Star Alliance": [{"name": "Lufthansa Senator", "operator": "Lufthansa", "terminal": "A", "features": ["work-stalls"], "location": "Gallery"}]},
    "HAM": {"Star Alliance": [{"name": "Lufthansa Business", "operator": "Lufthansa", "terminal": "T2", "features": ["buffet"], "location": "Gate A19"}]},
    "STR": {"Star Alliance": [{"name": "Lufthansa Lounge", "operator": "Lufthansa", "terminal": "T1", "features": ["snacks"], "location": "Gate 173"}]},
    "CGN": {"Star Alliance": [{"name": "Lufthansa Lounge", "operator": "Lufthansa", "terminal": "T1", "features": ["kölsch-on-tap"], "location": "Concourse C"}]},
    "CDG": {"SkyTeam": [{"name": "Air France Lounge", "operator": "Air France", "terminal": "T2F", "features": ["spa"], "location": "Level 2"}]},
    "ORY": {"SkyTeam": [{"name": "Air France Lounge", "operator": "Air France", "terminal": "3", "features": ["showers"], "location": "Airside"}]},
    "NCE": {"Premium": [{"name": "The Infinity", "operator": "NCE", "terminal": "T2", "features": ["buffet"], "location": "2nd Floor"}]},
    "LYS": {"SkyTeam": [{"name": "Air France Lounge", "operator": "Air France", "terminal": "T1", "features": ["hot-meals"], "location": "Level 1"}]},
    "MRS": {"Contract": [{"name": "Cézanne Lounge", "operator": "MRS", "terminal": "T1", "features": ["snacks"], "location": "Hall B"}]},
    "TLS": {"Contract": [{"name": "La Croix du Sud", "operator": "TLS", "terminal": "Main", "features": ["views"], "location": "Hall C"}]},
    "BOD": {"Contract": [{"name": "Hall A Lounge", "operator": "BOD", "terminal": "A", "features": ["wine"], "location": "Level 1"}]},
    "BSL": {"Premium": [{"name": "Skyview Lounge", "operator": "EuroAirport", "terminal": "Main", "features": ["terrace"], "location": "Level 4"}]},
    "NTE": {"Contract": [{"name": "Salon VIP", "operator": "NTE", "terminal": "Main", "features": ["refreshments"], "location": "Airside"}]},
    "MPL": {"Contract": [{"name": "Salon by FDI", "operator": "MPL", "terminal": "Main", "features": ["beer-wine"], "location": "Gate 16"}]},
    "SXB": {"Contract": [{"name": "Salon VIP", "operator": "SXB", "terminal": "Main", "features": ["snacks"], "location": "Airside"}]},

    # --- EUROPE (CENTRAL/SOUTH) ---
    "LUX": {"Contract": [{"name": "The Lounge", "operator": "LUX", "terminal": "A", "features": ["buffet"], "location": "Level 1"}]},
    "AMS": {"SkyTeam": [{"name": "KLM Crown Lounge 52", "operator": "KLM", "terminal": "52", "features": ["sleep-cabins"], "location": "Non-Schengen"}]},
    "BRU": {"Star Alliance": [{"name": "The Loft", "operator": "Brussels Airlines", "terminal": "A", "features": ["massage"], "location": "Gate A42"}]},
    "MAD": {"Oneworld": [{"name": "Iberia Velázquez", "operator": "Iberia", "terminal": "T4S", "features": ["wine"], "location": "Level 1"}]},
    "BCN": {"Premium": [{"name": "Pau Casals", "operator": "Aena", "terminal": "T1", "features": ["billiards"], "location": "Schengen"}]},
    "LIS": {"Star Alliance": [{"name": "TAP Premium", "operator": "TAP", "terminal": "T1", "features": ["pastries"], "location": "Level 2"}]},
    "OPO": {"Contract": [{"name": "ANA Lounge", "operator": "ANA", "terminal": "Main", "features": ["view"], "location": "Airside"}]},
    "FCO": {"SkyTeam": [{"name": "ITA Hangar", "operator": "ITA", "terminal": "T1", "features": ["espresso"], "location": "Pier A"}]},
    "MXP": {"Contract": [{"name": "Montale Lounge", "operator": "SEA", "terminal": "T1", "features": ["wine"], "location": "Non-Schengen"}]},
    "VIE": {"Star Alliance": [{"name": "Austrian Senator", "operator": "Austrian", "terminal": "T3", "features": ["cuisine"], "location": "Level 2"}]},
    "ZRH": {"Star Alliance": [{"name": "SWISS Senator", "operator": "SWISS", "terminal": "E", "features": ["whisky"], "location": "Level 3"}]},
    "GVA": {"Star Alliance": [{"name": "SWISS Business", "operator": "SWISS", "terminal": "T1", "features": ["buffet"], "location": "Mezzanine"}]},
    "CPH": {"Star Alliance": [{"name": "SAS Gold", "operator": "SAS", "terminal": "T3", "features": ["nordic-buffet"], "location": "Pier C"}]},
    "WAW": {"Star Alliance": [{"name": "LOT Polonez", "operator": "LOT", "terminal": "T1", "features": ["polish-dishes"], "location": "Level 2"}]},

    # --- RUSSIA EXPANDED ---
    "SVO": {"SkyTeam": [{"name": "Malevich Lounge", "operator": "SVO", "terminal": "T-C", "features": ["cinema"], "location": "Level 3"}]},
    "DME": {"Premium": [{"name": "Horizon Lounge", "operator": "DME", "terminal": "T2", "features": ["playroom"], "location": "Level 2"}]},
    "LED": {"Contract": [{"name": "Pulkovo Exclusive", "operator": "LED", "terminal": "Main", "features": ["snacks"], "location": "Airside"}]},
    "IKT": {"Contract": [{"name": "Business Lounge", "operator": "IKT", "terminal": "Dom", "features": ["wifi"], "location": "Level 2"}]},
    "VVO": {"Premium": [{"name": "Primorye Lounge", "operator": "VVO", "terminal": "Int", "features": ["showers"], "location": "Gate 5"}]},
    "OVB": {"Contract": [{"name": "Tolmachevo Lounge", "operator": "OVB", "terminal": "C", "features": ["buffet"], "location": "Level 2"}]},
    "SVX": {"Premium": [{"name": "Emerald Lounge", "operator": "SVX", "terminal": "Dom", "features": ["hot-meals"], "location": "Airside"}]},
    "KZN": {"Premium": [{"name": "Gabdulla Tukai", "operator": "KZN", "terminal": "T1A", "features": ["tatar-gastronomy"], "location": "Level 2"}]},

    # --- JAPAN ---
    "HND": {"Star Alliance": [{"name": "ANA Suite Lounge", "operator": "ANA", "terminal": "T3", "features": ["private-suites", "chef-service"], "location": "Gate 110"}], "Oneworld": [{"name": "JAL First Class", "operator": "JAL", "terminal": "T3", "features": ["sushi-bar"], "location": "Level 4"}]},
    "NRT": {"Star Alliance": [{"name": "ANA Lounge", "operator": "ANA", "terminal": "T1", "features": ["noodle-bar"], "location": "Gate 51"}]},
    "KIX": {"Premium": [{"name": "KIX North Lounge", "operator": "Kansai", "terminal": "T1", "features": ["buffet"], "location": "North Wing"}]},
    "ITM": {"Premium": [{"name": "Lounge Osaka", "operator": "Itami", "terminal": "Central", "features": ["work-zones"], "location": "Level 3"}]},

    # --- SOUTH KOREA ---
    "ICN": {"SkyTeam": [{"name": "KAL Lounge", "operator": "Korean Air", "terminal": "T2", "features": ["showers"], "location": "Gate 248"}], "Star Alliance": [{"name": "Asiana Business", "operator": "Asiana", "terminal": "T1", "features": ["grand-piano"], "location": "Gate 11"}]},
    "GMP": {"Premium": [{"name": "Sky Hub Lounge", "operator": "Gimpo", "terminal": "Int", "features": ["massage-chairs"], "location": "Gate 35"}]},
    "PUS": {"SkyTeam": [{"name": "KAL Lounge", "operator": "Korean Air", "terminal": "Int", "features": ["rest-area"], "location": "Level 3"}]},

    # --- TAIWAN ---
    "TPE": {"SkyTeam": [{"name": "Dynasty Lounge", "operator": "CAL", "terminal": "T2", "features": ["noodle-soup"], "location": "Level 4"}], "Star Alliance": [{"name": "The Infinity", "operator": "EVA", "terminal": "T2", "features": ["gelato"], "location": "Level 4"}]},
    "TSA": {"Premium": [{"name": "Taipei International", "operator": "TSA", "terminal": "T1", "features": ["dim-sum"], "location": "Airside"}]},
    "KHH": {"Premium": [{"name": "More Premium Lounge", "operator": "KHH", "terminal": "Int", "features": ["haagen-dazs"], "location": "Gate 21"}]},

    # --- SCANDINAVIA, BALTICS & BALKANS ---
    "KEF": {"Premium": [{"name": "Icelandair Saga", "operator": "Icelandair", "terminal": "Main", "features": ["fireplace"], "location": "Level 2"}]},
    "OSL": {"Contract": [{"name": "OSL Lounge", "operator": "SSP", "terminal": "Main", "features": ["snacks"], "location": "Gate E2"}]},
    "ARN": {"SkyTeam": [{"name": "SAS Gold", "operator": "SAS", "terminal": "T5", "features": ["showers"], "location": "Gate E1"}]},
    "HEL": {"Oneworld": [{"name": "Finnair Business", "operator": "Finnair", "terminal": "Non-Sch", "features": ["sauna"], "location": "Gate 52"}]},
    "TLL": {"Contract": [{"name": "LHV Lounge", "operator": "TLL", "terminal": "Main", "features": ["terrace"], "location": "Gate N1"}]},
    "RIX": {"Contract": [{"name": "Primeclass Riga", "operator": "TAV", "terminal": "Main", "features": ["bar"], "location": "Level 2"}]},
    "VNO": {"Premium": [{"name": "Aspire Lounge", "operator": "Swissport", "terminal": "Main", "features": ["modern"], "location": "Level 3"}]},
    "ATH": {"Star Alliance": [{"name": "Aegean Business", "operator": "Aegean", "terminal": "B", "features": ["greek"], "location": "Schengen"}]},
    "BEG": {"Contract": [{"name": "Business Lounge", "operator": "BEG", "terminal": "Main", "features": ["serbian"], "location": "Gate A4"}]},
    "OTP": {"SkyTeam": [{"name": "TAROM Lounge", "operator": "TAROM", "terminal": "Main", "features": ["snacks"], "location": "Gate 9"}]},
    "ZAG": {"Contract": [{"name": "Primeclass", "operator": "TAV", "terminal": "Main", "features": ["bar"], "location": "Gate 23"}]},
    "SOF": {"Premium": [{"name": "Primeclass Business", "operator": "TAV", "terminal": "T2", "features": ["terrace"], "location": "Level 2"}]},
    "LJU": {"Contract": [{"name": "Business Lounge", "operator": "LJU", "terminal": "Main", "features": ["terrace"], "location": "Gate 1"}]},
    "TIA": {"Contract": [{"name": "Scanderbeg Lounge", "operator": "TIA", "terminal": "Main", "features": ["hospitality"], "location": "Gate 3"}]},
    "SJJ": {"Contract": [{"name": "Business Lounge II", "operator": "SJJ", "terminal": "Main", "features": ["prayer"], "location": "Level 2"}]},
    "MSQ": {"Contract": [{"name": "International Lounge", "operator": "MSQ", "terminal": "Main", "features": ["smoking"], "location": "Gate 3"}]},
    "ALA": {"Premium": [{"name": "The Shanyraq", "operator": "Air Astana", "terminal": "T2", "features": ["cultural"], "location": "Gate 201"}]},
    "NQZ": {"Premium": [{"name": "The Shanyraq", "operator": "Air Astana", "terminal": "Main", "features": ["local"], "location": "Airside"}]},
    "LHR": {"Oneworld": [{"name": "Cathay First", "operator": "Cathay", "terminal": "T3", "features": ["dining"], "location": "Lounge B"}]},
    "SYD": {"Oneworld": [{"name": "Qantas First", "operator": "Qantas", "terminal": "T1", "features": ["spa"], "location": "L4"}]},
    "DUB": {"Airport": [{"name": "Phoenix Lounge", "operator": "daa", "terminal": "T1", "features": ["buffet"], "location": "Terminal 1"}]}
}

# --- COUNTRY MAPPING ---
AIRPORT_TO_COUNTRY: Dict[str, str] = {
    "EWR": "United States", "JFK": "United States", "LAX": "United States", "ORD": "United States", "SLC": "United States", "HNL": "United States", "OGG": "United States", "ANC": "United States", "FAI": "United States",
    "FRA": "Germany", "MUC": "Germany", "BER": "Germany", "DUS": "Germany", "HAM": "Germany", "STR": "Germany", "CGN": "Germany",
    "CDG": "France", "ORY": "France", "NCE": "France", "LYS": "France", "MRS": "France", "TLS": "France", "BOD": "France", "BSL": "France", "NTE": "France", "MPL": "France", "SXB": "France",
    "LUX": "Luxembourg", "AMS": "Netherlands", "BRU": "Belgium", "MAD": "Spain", "BCN": "Spain", "LIS": "Portugal", "OPO": "Portugal", "FCO": "Italy", "MXP": "Italy", "VIE": "Austria", "ZRH": "Switzerland", "GVA": "Switzerland", "CPH": "Denmark", "WAW": "Poland",
    "SVO": "Russia", "DME": "Russia", "LED": "Russia", "IKT": "Russia", "VVO": "Russia", "OVB": "Russia", "SVX": "Russia", "KZN": "Russia",
    "HND": "Japan", "NRT": "Japan", "KIX": "Japan", "ITM": "Japan", "ICN": "South Korea", "GMP": "South Korea", "PUS": "South Korea", "TPE": "Taiwan", "TSA": "Taiwan", "KHH": "Taiwan",
    "KEF": "Iceland", "OSL": "Norway", "ARN": "Sweden", "HEL": "Finland", "TLL": "Estonia", "RIX": "Latvia", "VNO": "Lithuania", "ATH": "Greece", "BEG": "Serbia", "OTP": "Romania", "ZAG": "Croatia", "SOF": "Bulgaria", "LJU": "Slovenia", "TIA": "Albania", "SJJ": "Bosnia", "MSQ": "Belarus", "ALA": "Kazakhstan", "NQZ": "Kazakhstan",
    "LHR": "United Kingdom", "SYD": "Australia", "DUB": "Ireland"
}

def display_lounges(airport_code: str, alliance: Optional[str] = None, features: Optional[List[str]] = None, operator: Optional[str] = None) -> None:
    code = airport_code.upper()
    if code not in LOUNGE_DATA: return
    country = AIRPORT_TO_COUNTRY.get(code, "Unknown")
    print("\n" + "="*75 + f"\n ✈️  HUB: {code} | COUNTRY: {country.upper()}\n" + "="*75)
    for tier, lounges in LOUNGE_DATA[code].items():
        if alliance and alliance.lower() not in tier.lower(): continue
        matched = [l for l in lounges if (not features or all(f.lower() in l['features'] for f in features)) and (not operator or operator.lower() in l['operator'].lower())]
        if matched:
            print(f"\n🔹 {tier}")
            for l in matched: print(f"  - {l['name']} | Operator: {l['operator']}\n    📍 {l['terminal']} | {l['location']}\n    ✨ Features: {', '.join(l['features'])}")

def main():
    parser = argparse.ArgumentParser(description="2026 Global Alliance Lounge Finder")
    parser.add_argument("airport", nargs="?", help="IATA code")
    parser.add_argument("-c", "--country", nargs="+", help="Country/ISO code")
    parser.add_argument("-a", "--alliance", help="Alliance filter")
    parser.add_argument("-o", "--operator", help="Operator filter")
    parser.add_argument("-f", "--features", nargs="+", help="Amenity filter")
    args = parser.parse_args()

    if args.country:
        country_input = " ".join(args.country).strip().upper()
        if country_input.startswith("THE "): country_input = country_input[4:].strip()
        if country_input in ["LI", "LIE", "LIECHTENSTEIN"]:
            print("💡 Liechtenstein is served primarily by Zurich (ZRH).")
            display_lounges("ZRH", args.alliance, args.features, args.operator)
            return
        target_name = ISO_MAP.get(country_input, country_input).lower()
        targets = sorted([code for code, country in AIRPORT_TO_COUNTRY.items() if country.lower() == target_name])
        for code in targets: display_lounges(code, args.alliance, args.features, args.operator)
    elif args.airport: display_lounges(args.airport, args.alliance, args.features, args.operator)

if __name__ == "__main__": main()