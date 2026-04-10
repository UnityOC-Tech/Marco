import argparse

# Comprehensive 2026 Lounge Database (Updated with Tokyo)
LOUNGE_DATA = {
    "HND": {
        "Star Alliance Gold": ["ANA Suite Lounge (T2 & T3)", "ANA Lounge (T2 & T3)"],
        "Oneworld Emerald": ["JAL First Class Lounge (T3)"],
        "Oneworld Sapphire": ["JAL Sakura Lounge (T3)", "Cathay Pacific Lounge (T3 - Level 6)"],
        "SkyTeam Elite Plus": ["Delta Sky Club (T3 - Flagship with Noodle Bar)", "TIAT Lounge (Contract for other SkyTeam)"]
    },
    "NRT": {
        "Star Alliance Gold": ["ANA Suite Lounge (T1 Satellite 5)", "ANA Lounge (T1 Satellite 2 & 5)", "United Club (T1 Satellite 3)"],
        "Oneworld Emerald": ["JAL First Class Lounge (T2)"],
        "Oneworld Sapphire": ["JAL Sakura Lounge (T2)", "Cathay Pacific First & Business Class Lounge (T2)"],
        "SkyTeam Elite Plus": ["Korean Air KAL Lounge (T1)", "China Airlines Dynasty Lounge (T2)"]
    },
    "LHR": {
        "Star Alliance Gold": ["United Club (T2)", "Lufthansa Senator Lounge (T2)", "Singapore SilverKris (T2)", "Air Canada Maple Leaf Lounge (T2)"],
        "Oneworld Emerald": ["Cathay Pacific First Class Lounge (T3)", "British Airways First Lounge (T5/T3)", "American Airlines First Class Lounge (T3)"],
        "Oneworld Sapphire": ["Cathay Pacific Business Lounge (T3)", "Qantas London Lounge (T3)", "BA Galleries Club (T5/T3)", "American Admirals Club (T3)"],
        "SkyTeam Elite Plus": ["Virgin Atlantic Clubhouse (T3 - Access for DL/VS/AF/KL)", "SkyTeam Lounge (T4)"]
    },
    "SIN": {
        "Star Alliance Gold": ["KrisFlyer Gold Lounge (T2/T3)", "SilverKris Lounge (Business Class section)"],
        "Oneworld Emerald": ["Qantas First Lounge (T1)", "Cathay Pacific Lounge (T4)"],
        "Oneworld Sapphire": ["Qantas Business Lounge (T1)", "British Airways Lounge (T1)"],
        "SkyTeam Elite Plus": ["Marhaba Lounge (T1/T3)", "SATS Premier Lounge (T2)"]
    },
    "JFK": {
        "Star Alliance Gold": ["Lufthansa Senator Lounge (T1)", "Turkish Airlines Lounge (T1)", "Air India Maharaja Lounge (T4)"],
        "Oneworld Emerald": ["Soho Lounge (T8)", "Chelsea Lounge (T8)"],
        "Oneworld Sapphire": ["Greenwich Lounge (T8)", "British Airways Galleries (T8)"],
        "SkyTeam Elite Plus": ["Delta Sky Club (T4)", "Virgin Atlantic Clubhouse (T4)", "Air France Lounge (T1)"]
    },
    "FRA": {
        "Star Alliance Gold": ["Lufthansa Senator Lounges (T1 - A, B, Z)", "Air Canada Maple Leaf Lounge (T1B)"],
        "Oneworld Emerald": ["JAL First Class Lounge (T2)", "Cathay Pacific Lounge (T2)"],
        "SkyTeam Elite Plus": ["New SkyTeam Flagship Lounge (T3 - Opening April 2026!)", "Air France/KLM Lounge (T2)"]
    },
    "HKG": {
        "Star Alliance Gold": ["Singapore SilverKris Lounge (T1)", "United Club (T1)"],
        "Oneworld Emerald": ["The Pier, First (Near Gate 63)", "The Deck (Interim Emerald Lounge)"],
        "Oneworld Sapphire": ["The Pier, Business", "The Qantas Hong Kong Lounge", "The Bridge"],
        "SkyTeam Elite Plus": ["SkyTeam Exclusive Lounge (Gate 15)"]
    },
    "SYD": {
        "Star Alliance Gold": ["Air New Zealand Lounge (T1)", "Singapore SilverKris (T1)"],
        "Oneworld Emerald": ["Qantas International First Lounge (T1)"],
        "Oneworld Sapphire": ["Qantas Business (Temp space near G24 during 2026 reno)"],
        "SkyTeam Elite Plus": ["SkyTeam Exclusive Lounge (T1 Pier B)"]
    },
    "DOH": {
        "Oneworld Emerald": ["Qatar Airways Platinum Lounge South", "Al Safwa First (Ticketed First Only)"],
        "Oneworld Sapphire": ["Qatar Airways Gold Lounge South", "Al Mourjan Business (Ticketed J Only)"],
        "Star Alliance Gold": ["Al Maha Lounge (Contract)"]
    },
    "ICN": {
        "SkyTeam Elite Plus": ["Korean Air Prestige Lounge (T2)", "Korean Air First Lounge (T2)"],
        "Oneworld Emerald/Sapphire": ["oneworld Branded Lounge (T1 Gate 28)"],
        "Star Alliance Gold": ["Asiana Business Lounge (T1 - Check merger status for T2 move)"]
    }
}

# 2026 Operational Alerts
ALERTS = {
    "HND": "ℹ️ ANA (Star Alliance) updated its shower reservation system (Jan 2026). Use the ANA App to book.",
    "FRA": "⚠️ Terminal 3 opens April 2026. SkyTeam operations moving from T2 to T3.",
    "ICN": "⚠️ Asiana (Star Alliance) merger into Korean Air (SkyTeam) is nearing completion; expect T1 gate changes.",
    "SYD": "⚠️ Qantas Business Lounge reno continues. Follow signs for 'Temporary Lounge' near Gate 24.",
    "HKG": "⚠️ 'The Wing' First Class remains closed for renovation. Use 'The Deck' for Emerald access."
}

def display_lounges(airport_code, alliance_filter=None):
    code = airport_code.upper()
    if code not in LOUNGE_DATA:
        print(f"\n❌ Error: {code} data missing.")
        return

    print(f"\n--- ✈️ 2026 LOUNGE ACCESS: {code} ---")
    if code in ALERTS: print(f"\n{ALERTS[code]}")

    found_any = False
    for tier, lounges in LOUNGE_DATA[code].items():
        if alliance_filter and alliance_filter.lower() not in tier.lower():
            continue
        found_any = True
        print(f"\n🔹 {tier}")
        for lounge in lounges:
            print(f"  - {lounge}")

def main():
    parser = argparse.ArgumentParser(description="2026 Global Alliance Lounge Finder")
    parser.add_argument("airport", help="3-letter IATA code (e.g. HND, NRT, LHR)")
    parser.add_argument("-a", "--alliance", help="Filter by alliance (Star, Oneworld, SkyTeam)")
    args = parser.parse_args()
    display_lounges(args.airport, args.alliance)

if __name__ == "__main__":
    main()