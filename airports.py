#!/usr/bin/env python3
"""
✈  Airport Routing Code Lookup CLI
Supports IATA (e.g. LAX) and ICAO (e.g. KLAX) code lookups.
Returns: name, city, country, timezone, coordinates, and both codes.

Usage:
  python airport_lookup.py LAX
  python airport_lookup.py EGLL
  python airport_lookup.py --search london
  python airport_lookup.py --list-country US
  python airport_lookup.py LAX JFK NRT          # multiple lookups
"""

import sys
import argparse
import json
from math import radians, sin, cos, sqrt, atan2

# ─────────────────────────────────────────────────────────────────────────────
# AIRPORT DATABASE
# Fields: name, city, country, iata, icao, lat, lon, altitude_ft, timezone
# ─────────────────────────────────────────────────────────────────────────────
AIRPORTS = [
    # ── United States (35) ────────────────────────────────────────────────────
    {"name": "Los Angeles International Airport",        "city": "Los Angeles",     "country": "United States", "iata": "LAX", "icao": "KLAX", "lat": 33.9425,  "lon": -118.4081, "alt": 125,  "tz": "America/Los_Angeles"},
    {"name": "John F. Kennedy International Airport",    "city": "New York",        "country": "United States", "iata": "JFK", "icao": "KJFK", "lat": 40.6413,  "lon": -73.7781,  "alt": 13,   "tz": "America/New_York"},
    {"name": "O'Hare International Airport",             "city": "Chicago",         "country": "United States", "iata": "ORD", "icao": "KORD", "lat": 41.9742,  "lon": -87.9073,  "alt": 672,  "tz": "America/Chicago"},
    {"name": "Hartsfield-Jackson Atlanta Intl Airport",  "city": "Atlanta",         "country": "United States", "iata": "ATL", "icao": "KATL", "lat": 33.6407,  "lon": -84.4277,  "alt": 1026, "tz": "America/New_York"},
    {"name": "Dallas/Fort Worth International Airport",  "city": "Dallas",          "country": "United States", "iata": "DFW", "icao": "KDFW", "lat": 32.8998,  "lon": -97.0403,  "alt": 607,  "tz": "America/Chicago"},
    {"name": "Denver International Airport",             "city": "Denver",          "country": "United States", "iata": "DEN", "icao": "KDEN", "lat": 39.8561,  "lon": -104.6737, "alt": 5433, "tz": "America/Denver"},
    {"name": "San Francisco International Airport",      "city": "San Francisco",   "country": "United States", "iata": "SFO", "icao": "KSFO", "lat": 37.6213,  "lon": -122.3790, "alt": 13,   "tz": "America/Los_Angeles"},
    {"name": "Seattle-Tacoma International Airport",     "city": "Seattle",         "country": "United States", "iata": "SEA", "icao": "KSEA", "lat": 47.4502,  "lon": -122.3088, "alt": 433,  "tz": "America/Los_Angeles"},
    {"name": "Miami International Airport",              "city": "Miami",           "country": "United States", "iata": "MIA", "icao": "KMIA", "lat": 25.7959,  "lon": -80.2870,  "alt": 8,    "tz": "America/New_York"},
    {"name": "Newark Liberty International Airport",     "city": "Newark",          "country": "United States", "iata": "EWR", "icao": "KEWR", "lat": 40.6895,  "lon": -74.1745,  "alt": 18,   "tz": "America/New_York"},
    {"name": "Minneapolis–Saint Paul Intl Airport",      "city": "Minneapolis",     "country": "United States", "iata": "MSP", "icao": "KMSP", "lat": 44.8848,  "lon": -93.2223,  "alt": 841,  "tz": "America/Chicago"},
    {"name": "Phoenix Sky Harbor International Airport", "city": "Phoenix",         "country": "United States", "iata": "PHX", "icao": "KPHX", "lat": 33.4373,  "lon": -112.0078, "alt": 1135, "tz": "America/Phoenix"},
    {"name": "Boston Logan International Airport",       "city": "Boston",          "country": "United States", "iata": "BOS", "icao": "KBOS", "lat": 42.3656,  "lon": -71.0096,  "alt": 20,   "tz": "America/New_York"},
    {"name": "Las Vegas Harry Reid Intl Airport",        "city": "Las Vegas",       "country": "United States", "iata": "LAS", "icao": "KLAS", "lat": 36.0840,  "lon": -115.1537, "alt": 2181, "tz": "America/Los_Angeles"},
    {"name": "Charlotte Douglas International Airport",  "city": "Charlotte",       "country": "United States", "iata": "CLT", "icao": "KCLT", "lat": 35.2140,  "lon": -80.9431,  "alt": 748,  "tz": "America/New_York"},
    {"name": "George Bush Intercontinental Airport",     "city": "Houston",         "country": "United States", "iata": "IAH", "icao": "KIAH", "lat": 29.9902,  "lon": -95.3368,  "alt": 97,   "tz": "America/Chicago"},
    {"name": "Orlando International Airport",            "city": "Orlando",         "country": "United States", "iata": "MCO", "icao": "KMCO", "lat": 28.4294,  "lon": -81.3089,  "alt": 96,   "tz": "America/New_York"},
    {"name": "Washington Dulles International Airport",  "city": "Washington D.C.", "country": "United States", "iata": "IAD", "icao": "KIAD", "lat": 38.9531,  "lon": -77.4565,  "alt": 313,  "tz": "America/New_York"},
    {"name": "Ronald Reagan Washington National Airport","city": "Washington D.C.", "country": "United States", "iata": "DCA", "icao": "KDCA", "lat": 38.8512,  "lon": -77.0402,  "alt": 15,   "tz": "America/New_York"},
    {"name": "Honolulu Daniel K. Inouye Intl Airport",   "city": "Honolulu",        "country": "United States", "iata": "HNL", "icao": "PHNL", "lat": 21.3187,  "lon": -157.9225, "alt": 13,   "tz": "Pacific/Honolulu"},
    {"name": "Ted Stevens Anchorage Intl Airport",       "city": "Anchorage",       "country": "United States", "iata": "ANC", "icao": "PANC", "lat": 61.1743,  "lon": -149.9963, "alt": 152,  "tz": "America/Anchorage"},
    {"name": "San Diego International Airport",          "city": "San Diego",       "country": "United States", "iata": "SAN", "icao": "KSAN", "lat": 32.7336,  "lon": -117.1897, "alt": 17,   "tz": "America/Los_Angeles"},
    {"name": "Tampa International Airport",              "city": "Tampa",           "country": "United States", "iata": "TPA", "icao": "KTPA", "lat": 27.9755,  "lon": -82.5332,  "alt": 26,   "tz": "America/New_York"},
    {"name": "Portland International Airport",           "city": "Portland",        "country": "United States", "iata": "PDX", "icao": "KPDX", "lat": 45.5887,  "lon": -122.5975, "alt": 31,   "tz": "America/Los_Angeles"},
    {"name": "Detroit Metropolitan Wayne County Airport","city": "Detroit",         "country": "United States", "iata": "DTW", "icao": "KDTW", "lat": 42.2124,  "lon": -83.3534,  "alt": 645,  "tz": "America/Detroit"},
    {"name": "Philadelphia International Airport",       "city": "Philadelphia",    "country": "United States", "iata": "PHL", "icao": "KPHL", "lat": 39.8719,  "lon": -75.2411,  "alt": 36,   "tz": "America/New_York"},
    {"name": "Salt Lake City International Airport",     "city": "Salt Lake City",  "country": "United States", "iata": "SLC", "icao": "KSLC", "lat": 40.7884,  "lon": -111.9778, "alt": 4227, "tz": "America/Denver"},
    {"name": "Baltimore/Washington Intl Airport",        "city": "Baltimore",       "country": "United States", "iata": "BWI", "icao": "KBWI", "lat": 39.1754,  "lon": -76.6683,  "alt": 146,  "tz": "America/New_York"},
    {"name": "Nashville International Airport",          "city": "Nashville",       "country": "United States", "iata": "BNA", "icao": "KBNA", "lat": 36.1245,  "lon": -86.6782,  "alt": 599,  "tz": "America/Chicago"},
    {"name": "Kansas City International Airport",        "city": "Kansas City",     "country": "United States", "iata": "MCI", "icao": "KMCI", "lat": 39.2976,  "lon": -94.7139,  "alt": 1026, "tz": "America/Chicago"},
    {"name": "Austin-Bergstrom International Airport",   "city": "Austin",          "country": "United States", "iata": "AUS", "icao": "KAUS", "lat": 30.1975,  "lon": -97.6664,  "alt": 542,  "tz": "America/Chicago"},
    {"name": "Raleigh-Durham International Airport",     "city": "Raleigh",         "country": "United States", "iata": "RDU", "icao": "KRDU", "lat": 35.8776,  "lon": -78.7875,  "alt": 435,  "tz": "America/New_York"},
    {"name": "Pittsburgh International Airport",         "city": "Pittsburgh",      "country": "United States", "iata": "PIT", "icao": "KPIT", "lat": 40.4915,  "lon": -80.2329,  "alt": 1203, "tz": "America/New_York"},
    {"name": "Louis Armstrong New Orleans Intl Airport", "city": "New Orleans",     "country": "United States", "iata": "MSY", "icao": "KMSY", "lat": 29.9934,  "lon": -90.2580,  "alt": 4,    "tz": "America/Chicago"},
    {"name": "Indianapolis International Airport",       "city": "Indianapolis",    "country": "United States", "iata": "IND", "icao": "KIND", "lat": 39.7173,  "lon": -86.2944,  "alt": 797,  "tz": "America/Indiana/Indianapolis"},
    # ── Canada (7) ────────────────────────────────────────────────────────────
    {"name": "Toronto Pearson International Airport",    "city": "Toronto",         "country": "Canada",        "iata": "YYZ", "icao": "CYYZ", "lat": 43.6777,  "lon": -79.6248,  "alt": 569,  "tz": "America/Toronto"},
    {"name": "Vancouver International Airport",          "city": "Vancouver",       "country": "Canada",        "iata": "YVR", "icao": "CYVR", "lat": 49.1967,  "lon": -123.1815, "alt": 14,   "tz": "America/Vancouver"},
    {"name": "Montréal-Trudeau International Airport",   "city": "Montreal",        "country": "Canada",        "iata": "YUL", "icao": "CYUL", "lat": 45.4706,  "lon": -73.7408,  "alt": 118,  "tz": "America/Toronto"},
    {"name": "Calgary International Airport",            "city": "Calgary",         "country": "Canada",        "iata": "YYC", "icao": "CYYC", "lat": 51.1315,  "lon": -114.0106, "alt": 3557, "tz": "America/Edmonton"},
    {"name": "Edmonton International Airport",           "city": "Edmonton",        "country": "Canada",        "iata": "YEG", "icao": "CYEG", "lat": 53.3097,  "lon": -113.5800, "alt": 2373, "tz": "America/Edmonton"},
    {"name": "Ottawa Macdonald-Cartier Intl Airport",    "city": "Ottawa",          "country": "Canada",        "iata": "YOW", "icao": "CYOW", "lat": 45.3225,  "lon": -75.6692,  "alt": 374,  "tz": "America/Toronto"},
    {"name": "Winnipeg James Armstrong Richardson Intl", "city": "Winnipeg",        "country": "Canada",        "iata": "YWG", "icao": "CYWG", "lat": 49.9100,  "lon": -97.2399,  "alt": 783,  "tz": "America/Winnipeg"},
    # ── Mexico & Central America (5) ──────────────────────────────────────────
    {"name": "Mexico City Felipe Angeles Intl Airport",  "city": "Mexico City",     "country": "Mexico",        "iata": "NLU", "icao": "MMSM", "lat": 19.7561,  "lon": -99.0150,  "alt": 7316, "tz": "America/Mexico_City"},
    {"name": "Mexico City International Airport",        "city": "Mexico City",     "country": "Mexico",        "iata": "MEX", "icao": "MMMX", "lat": 19.4363,  "lon": -99.0721,  "alt": 7316, "tz": "America/Mexico_City"},
    {"name": "Cancún International Airport",             "city": "Cancún",          "country": "Mexico",        "iata": "CUN", "icao": "MMUN", "lat": 21.0365,  "lon": -86.8770,  "alt": 22,   "tz": "America/Cancun"},
    {"name": "Guadalajara Don Miguel Hidalgo Intl",      "city": "Guadalajara",     "country": "Mexico",        "iata": "GDL", "icao": "MMGL", "lat": 20.5218,  "lon": -103.3107, "alt": 5016, "tz": "America/Mexico_City"},
    {"name": "Juan Santamaría International Airport",    "city": "San José",        "country": "Costa Rica",    "iata": "SJO", "icao": "MROC", "lat": 9.9939,   "lon": -84.2088,  "alt": 3021, "tz": "America/Costa_Rica"},
    # ── Caribbean (2) ─────────────────────────────────────────────────────────
    {"name": "Luis Muñoz Marín International Airport",   "city": "San Juan",        "country": "Puerto Rico",   "iata": "SJU", "icao": "TJSJ", "lat": 18.4394,  "lon": -66.0018,  "alt": 9,    "tz": "America/Puerto_Rico"},
    {"name": "Norman Manley International Airport",      "city": "Kingston",        "country": "Jamaica",       "iata": "KIN", "icao": "MKJP", "lat": 17.9357,  "lon": -76.7875,  "alt": 10,   "tz": "America/Jamaica"},
    # ── South America (10) ────────────────────────────────────────────────────
    {"name": "São Paulo–Guarulhos Intl Airport",         "city": "São Paulo",       "country": "Brazil",        "iata": "GRU", "icao": "SBGR", "lat": -23.4356, "lon": -46.4731,  "alt": 2459, "tz": "America/Sao_Paulo"},
    {"name": "São Paulo Congonhas Airport",               "city": "São Paulo",       "country": "Brazil",        "iata": "CGH", "icao": "SBSP", "lat": -23.6261, "lon": -46.6564,  "alt": 2631, "tz": "America/Sao_Paulo"},
    {"name": "Rio de Janeiro–Galeão Intl Airport",        "city": "Rio de Janeiro",  "country": "Brazil",        "iata": "GIG", "icao": "SBGL", "lat": -22.8099, "lon": -43.2505,  "alt": 28,   "tz": "America/Sao_Paulo"},
    {"name": "El Dorado International Airport",          "city": "Bogotá",          "country": "Colombia",      "iata": "BOG", "icao": "SKBO", "lat": 4.7016,   "lon": -74.1469,  "alt": 8360, "tz": "America/Bogota"},
    {"name": "Jorge Chávez International Airport",       "city": "Lima",            "country": "Peru",          "iata": "LIM", "icao": "SPJC", "lat": -12.0219, "lon": -77.1143,  "alt": 113,  "tz": "America/Lima"},
    {"name": "Ministro Pistarini International Airport", "city": "Buenos Aires",    "country": "Argentina",     "iata": "EZE", "icao": "SAEZ", "lat": -34.8222, "lon": -58.5358,  "alt": 67,   "tz": "America/Argentina/Buenos_Aires"},
    {"name": "Arturo Merino Benítez Intl Airport",       "city": "Santiago",        "country": "Chile",         "iata": "SCL", "icao": "SCEL", "lat": -33.3930, "lon": -70.7858,  "alt": 1555, "tz": "America/Santiago"},
    {"name": "Simon Bolivar International Airport",      "city": "Caracas",         "country": "Venezuela",     "iata": "CCS", "icao": "SVMI", "lat": 10.6031,  "lon": -66.9906,  "alt": 235,  "tz": "America/Caracas"},
    {"name": "Mariscal Sucre International Airport",     "city": "Quito",           "country": "Ecuador",       "iata": "UIO", "icao": "SEQM", "lat": -0.1292,  "lon": -78.3575,  "alt": 7874, "tz": "America/Guayaquil"},
    {"name": "Viru Viru International Airport",          "city": "Santa Cruz",      "country": "Bolivia",       "iata": "VVI", "icao": "SLVR", "lat": -17.6448, "lon": -63.1354,  "alt": 1224, "tz": "America/La_Paz"},
    # ── United Kingdom (4) ────────────────────────────────────────────────────
    {"name": "Heathrow Airport",                         "city": "London",          "country": "United Kingdom","iata": "LHR", "icao": "EGLL", "lat": 51.4775,  "lon": -0.4614,   "alt": 83,   "tz": "Europe/London"},
    {"name": "Gatwick Airport",                          "city": "London",          "country": "United Kingdom","iata": "LGW", "icao": "EGKK", "lat": 51.1481,  "lon": -0.1903,   "alt": 202,  "tz": "Europe/London"},
    {"name": "Manchester Airport",                       "city": "Manchester",      "country": "United Kingdom","iata": "MAN", "icao": "EGCC", "lat": 53.3537,  "lon": -2.2750,   "alt": 257,  "tz": "Europe/London"},
    {"name": "Edinburgh Airport",                        "city": "Edinburgh",       "country": "United Kingdom","iata": "EDI", "icao": "EGPH", "lat": 55.9500,  "lon": -3.3725,   "alt": 135,  "tz": "Europe/London"},
    # ── Western Europe (25) ───────────────────────────────────────────────────
    {"name": "Charles de Gaulle Airport",                "city": "Paris",           "country": "France",        "iata": "CDG", "icao": "LFPG", "lat": 49.0097,  "lon": 2.5479,    "alt": 392,  "tz": "Europe/Paris"},
    {"name": "Paris Orly Airport",                       "city": "Paris",           "country": "France",        "iata": "ORY", "icao": "LFPO", "lat": 48.7253,  "lon": 2.3594,    "alt": 291,  "tz": "Europe/Paris"},
    {"name": "Nice Côte d'Azur Airport",                 "city": "Nice",            "country": "France",        "iata": "NCE", "icao": "LFMN", "lat": 43.6584,  "lon": 7.2159,    "alt": 12,   "tz": "Europe/Paris"},
    {"name": "Frankfurt Airport",                        "city": "Frankfurt",       "country": "Germany",       "iata": "FRA", "icao": "EDDF", "lat": 50.0379,  "lon": 8.5622,    "alt": 364,  "tz": "Europe/Berlin"},
    {"name": "Munich Airport",                           "city": "Munich",          "country": "Germany",       "iata": "MUC", "icao": "EDDM", "lat": 48.3538,  "lon": 11.7861,   "alt": 1487, "tz": "Europe/Berlin"},
    {"name": "Berlin Brandenburg Airport",               "city": "Berlin",          "country": "Germany",       "iata": "BER", "icao": "EDDB", "lat": 52.3667,  "lon": 13.5033,   "alt": 157,  "tz": "Europe/Berlin"},
    {"name": "Amsterdam Airport Schiphol",               "city": "Amsterdam",       "country": "Netherlands",   "iata": "AMS", "icao": "EHAM", "lat": 52.3105,  "lon": 4.7683,    "alt": -11,  "tz": "Europe/Amsterdam"},
    {"name": "Madrid Barajas International Airport",     "city": "Madrid",          "country": "Spain",         "iata": "MAD", "icao": "LEMD", "lat": 40.4719,  "lon": -3.5626,   "alt": 2000, "tz": "Europe/Madrid"},
    {"name": "Barcelona El Prat Airport",                "city": "Barcelona",       "country": "Spain",         "iata": "BCN", "icao": "LEBL", "lat": 41.2971,  "lon": 2.0785,    "alt": 12,   "tz": "Europe/Madrid"},
    {"name": "Palma de Mallorca Airport",                "city": "Palma",           "country": "Spain",         "iata": "PMI", "icao": "LEPA", "lat": 39.5517,  "lon": 2.7388,    "alt": 27,   "tz": "Europe/Madrid"},
    {"name": "Rome Fiumicino Airport",                   "city": "Rome",            "country": "Italy",         "iata": "FCO", "icao": "LIRF", "lat": 41.8003,  "lon": 12.2389,   "alt": 13,   "tz": "Europe/Rome"},
    {"name": "Milan Malpensa Airport",                   "city": "Milan",           "country": "Italy",         "iata": "MXP", "icao": "LIMC", "lat": 45.6306,  "lon": 8.7281,    "alt": 768,  "tz": "Europe/Rome"},
    {"name": "Zurich Airport",                           "city": "Zurich",          "country": "Switzerland",   "iata": "ZRH", "icao": "LSZH", "lat": 47.4647,  "lon": 8.5492,    "alt": 1416, "tz": "Europe/Zurich"},
    {"name": "Geneva Airport",                           "city": "Geneva",          "country": "Switzerland",   "iata": "GVA", "icao": "LSGG", "lat": 46.2381,  "lon": 6.1090,    "alt": 1411, "tz": "Europe/Zurich"},
    {"name": "Copenhagen Airport",                       "city": "Copenhagen",      "country": "Denmark",       "iata": "CPH", "icao": "EKCH", "lat": 55.6180,  "lon": 12.6560,   "alt": 17,   "tz": "Europe/Copenhagen"},
    {"name": "Stockholm Arlanda Airport",                "city": "Stockholm",       "country": "Sweden",        "iata": "ARN", "icao": "ESSA", "lat": 59.6519,  "lon": 17.9186,   "alt": 137,  "tz": "Europe/Stockholm"},
    {"name": "Helsinki-Vantaa Airport",                  "city": "Helsinki",        "country": "Finland",       "iata": "HEL", "icao": "EFHK", "lat": 60.3172,  "lon": 24.9633,   "alt": 179,  "tz": "Europe/Helsinki"},
    {"name": "Oslo Gardermoen Airport",                  "city": "Oslo",            "country": "Norway",        "iata": "OSL", "icao": "ENGM", "lat": 60.1939,  "lon": 11.1004,   "alt": 681,  "tz": "Europe/Oslo"},
    {"name": "Vienna International Airport",             "city": "Vienna",          "country": "Austria",       "iata": "VIE", "icao": "LOWW", "lat": 48.1103,  "lon": 16.5697,   "alt": 600,  "tz": "Europe/Vienna"},
    {"name": "Brussels Airport",                         "city": "Brussels",        "country": "Belgium",       "iata": "BRU", "icao": "EBBR", "lat": 50.9014,  "lon": 4.4844,    "alt": 184,  "tz": "Europe/Brussels"},
    {"name": "Lisbon Humberto Delgado Airport",          "city": "Lisbon",          "country": "Portugal",      "iata": "LIS", "icao": "LPPT", "lat": 38.7813,  "lon": -9.1359,   "alt": 374,  "tz": "Europe/Lisbon"},
    {"name": "Dublin Airport",                           "city": "Dublin",          "country": "Ireland",       "iata": "DUB", "icao": "EIDW", "lat": 53.4213,  "lon": -6.2701,   "alt": 242,  "tz": "Europe/Dublin"},
    {"name": "Athens International Airport",             "city": "Athens",          "country": "Greece",        "iata": "ATH", "icao": "LGAV", "lat": 37.9364,  "lon": 23.9445,   "alt": 308,  "tz": "Europe/Athens"},
    {"name": "Luxembourg Findel Airport",                "city": "Luxembourg City", "country": "Luxembourg",    "iata": "LUX", "icao": "ELLX", "lat": 49.6233,  "lon": 6.2044,    "alt": 1234, "tz": "Europe/Luxembourg"},
    {"name": "Reykjavik Keflavik International Airport", "city": "Reykjavik",       "country": "Iceland",       "iata": "KEF", "icao": "BIKF", "lat": 63.9850,  "lon": -22.6057,  "alt": 171,  "tz": "Atlantic/Reykjavik"},
    # ── Eastern & Central Europe (8) ──────────────────────────────────────────
    {"name": "Warsaw Chopin Airport",                    "city": "Warsaw",          "country": "Poland",        "iata": "WAW", "icao": "EPWA", "lat": 52.1657,  "lon": 20.9671,   "alt": 361,  "tz": "Europe/Warsaw"},
    {"name": "Prague Václav Havel Airport",              "city": "Prague",          "country": "Czech Republic","iata": "PRG", "icao": "LKPR", "lat": 50.1008,  "lon": 14.2600,   "alt": 1247, "tz": "Europe/Prague"},
    {"name": "Budapest Ferenc Liszt Intl Airport",       "city": "Budapest",        "country": "Hungary",       "iata": "BUD", "icao": "LHBP", "lat": 47.4298,  "lon": 19.2610,   "alt": 495,  "tz": "Europe/Budapest"},
    {"name": "Bucharest Henri Coandă Intl Airport",      "city": "Bucharest",       "country": "Romania",       "iata": "OTP", "icao": "LROP", "lat": 44.5711,  "lon": 26.0850,   "alt": 314,  "tz": "Europe/Bucharest"},
    {"name": "Sofia Airport",                            "city": "Sofia",           "country": "Bulgaria",      "iata": "SOF", "icao": "LBSF", "lat": 42.6967,  "lon": 23.4114,   "alt": 1742, "tz": "Europe/Sofia"},
    {"name": "Belgrade Nikola Tesla Airport",            "city": "Belgrade",        "country": "Serbia",        "iata": "BEG", "icao": "LYBE", "lat": 44.8184,  "lon": 20.3091,   "alt": 335,  "tz": "Europe/Belgrade"},
    {"name": "Zagreb Franjo Tuđman Airport",             "city": "Zagreb",          "country": "Croatia",       "iata": "ZAG", "icao": "LDZA", "lat": 45.7429,  "lon": 16.0688,   "alt": 353,  "tz": "Europe/Zagreb"},
    {"name": "Kyiv Boryspil International Airport",      "city": "Kyiv",            "country": "Ukraine",       "iata": "KBP", "icao": "UKBB", "lat": 50.3450,  "lon": 30.8947,   "alt": 427,  "tz": "Europe/Kyiv"},
    # ── Russia & CIS (3) ──────────────────────────────────────────────────────
    {"name": "Sheremetyevo International Airport",       "city": "Moscow",          "country": "Russia",        "iata": "SVO", "icao": "UUEE", "lat": 55.9726,  "lon": 37.4146,   "alt": 630,  "tz": "Europe/Moscow"},
    {"name": "Domodedovo International Airport",         "city": "Moscow",          "country": "Russia",        "iata": "DME", "icao": "UUDD", "lat": 55.4103,  "lon": 37.9026,   "alt": 588,  "tz": "Europe/Moscow"},
    {"name": "Pulkovo Airport",                          "city": "Saint Petersburg","country": "Russia",        "iata": "LED", "icao": "ULLI", "lat": 59.8003,  "lon": 30.2625,   "alt": 78,   "tz": "Europe/Moscow"},
    # ── Turkey (2) ────────────────────────────────────────────────────────────
    {"name": "Istanbul Airport",                         "city": "Istanbul",        "country": "Turkey",        "iata": "IST", "icao": "LTFM", "lat": 41.2753,  "lon": 28.7519,   "alt": 325,  "tz": "Europe/Istanbul"},
    {"name": "Sabiha Gökçen International Airport",      "city": "Istanbul",        "country": "Turkey",        "iata": "SAW", "icao": "LTFJ", "lat": 40.8986,  "lon": 29.3092,   "alt": 312,  "tz": "Europe/Istanbul"},
    # ── Middle East (10) ──────────────────────────────────────────────────────
    {"name": "Dubai International Airport",              "city": "Dubai",           "country": "UAE",           "iata": "DXB", "icao": "OMDB", "lat": 25.2532,  "lon": 55.3657,   "alt": 62,   "tz": "Asia/Dubai"},
    {"name": "Al Maktoum International Airport",         "city": "Dubai",           "country": "UAE",           "iata": "DWC", "icao": "OMDW", "lat": 24.8963,  "lon": 55.1611,   "alt": 171,  "tz": "Asia/Dubai"},
    {"name": "Abu Dhabi International Airport",          "city": "Abu Dhabi",       "country": "UAE",           "iata": "AUH", "icao": "OMAA", "lat": 24.4330,  "lon": 54.6511,   "alt": 88,   "tz": "Asia/Dubai"},
    {"name": "Hamad International Airport",              "city": "Doha",            "country": "Qatar",         "iata": "DOH", "icao": "OTHH", "lat": 25.2731,  "lon": 51.6080,   "alt": 13,   "tz": "Asia/Qatar"},
    {"name": "King Abdulaziz International Airport",     "city": "Jeddah",          "country": "Saudi Arabia",  "iata": "JED", "icao": "OEJN", "lat": 21.6796,  "lon": 39.1565,   "alt": 48,   "tz": "Asia/Riyadh"},
    {"name": "King Khalid International Airport",        "city": "Riyadh",          "country": "Saudi Arabia",  "iata": "RUH", "icao": "OERK", "lat": 24.9576,  "lon": 46.6988,   "alt": 2049, "tz": "Asia/Riyadh"},
    {"name": "Kuwait International Airport",             "city": "Kuwait City",     "country": "Kuwait",        "iata": "KWI", "icao": "OKBK", "lat": 29.2267,  "lon": 47.9689,   "alt": 206,  "tz": "Asia/Kuwait"},
    {"name": "Bahrain International Airport",            "city": "Manama",          "country": "Bahrain",       "iata": "BAH", "icao": "OBBI", "lat": 26.2708,  "lon": 50.6336,   "alt": 6,    "tz": "Asia/Bahrain"},
    {"name": "Muscat International Airport",             "city": "Muscat",          "country": "Oman",          "iata": "MCT", "icao": "OOMS", "lat": 23.5933,  "lon": 58.2844,   "alt": 48,   "tz": "Asia/Muscat"},
    {"name": "Ben Gurion International Airport",         "city": "Tel Aviv",        "country": "Israel",        "iata": "TLV", "icao": "LLBG", "lat": 32.0114,  "lon": 34.8867,   "alt": 135,  "tz": "Asia/Jerusalem"},
    # ── Africa (12) ───────────────────────────────────────────────────────────
    {"name": "Cairo International Airport",              "city": "Cairo",           "country": "Egypt",         "iata": "CAI", "icao": "HECA", "lat": 30.1219,  "lon": 31.4056,   "alt": 382,  "tz": "Africa/Cairo"},
    {"name": "Addis Ababa Bole International Airport",   "city": "Addis Ababa",     "country": "Ethiopia",      "iata": "ADD", "icao": "HAAB", "lat": 8.9779,   "lon": 38.7993,   "alt": 7625, "tz": "Africa/Addis_Ababa"},
    {"name": "OR Tambo International Airport",           "city": "Johannesburg",    "country": "South Africa",  "iata": "JNB", "icao": "FAOR", "lat": -26.1367, "lon": 28.2411,   "alt": 5558, "tz": "Africa/Johannesburg"},
    {"name": "Cape Town International Airport",          "city": "Cape Town",       "country": "South Africa",  "iata": "CPT", "icao": "FACT", "lat": -33.9648, "lon": 18.6017,   "alt": 151,  "tz": "Africa/Johannesburg"},
    {"name": "Murtala Muhammed International Airport",   "city": "Lagos",           "country": "Nigeria",       "iata": "LOS", "icao": "DNMM", "lat": 6.5774,   "lon": 3.3214,    "alt": 135,  "tz": "Africa/Lagos"},
    {"name": "Mohammed V International Airport",         "city": "Casablanca",      "country": "Morocco",       "iata": "CMN", "icao": "GMMN", "lat": 33.3675,  "lon": -7.5900,   "alt": 656,  "tz": "Africa/Casablanca"},
    {"name": "Jomo Kenyatta International Airport",      "city": "Nairobi",         "country": "Kenya",         "iata": "NBO", "icao": "HKJK", "lat": -1.3192,  "lon": 36.9275,   "alt": 5327, "tz": "Africa/Nairobi"},
    {"name": "Kotoka International Airport",             "city": "Accra",           "country": "Ghana",         "iata": "ACC", "icao": "DGAA", "lat": 5.6052,   "lon": -0.1668,   "alt": 205,  "tz": "Africa/Accra"},
    {"name": "Julius Nyerere International Airport",     "city": "Dar es Salaam",   "country": "Tanzania",      "iata": "DAR", "icao": "HTDA", "lat": -6.8780,  "lon": 39.2026,   "alt": 182,  "tz": "Africa/Dar_es_Salaam"},
    {"name": "Houari Boumediene Airport",                "city": "Algiers",         "country": "Algeria",       "iata": "ALG", "icao": "DAAG", "lat": 36.6910,  "lon": 3.2154,    "alt": 827,  "tz": "Africa/Algiers"},
    {"name": "Tunis-Carthage International Airport",     "city": "Tunis",           "country": "Tunisia",       "iata": "TUN", "icao": "DTTA", "lat": 36.8510,  "lon": 10.2272,   "alt": 22,   "tz": "Africa/Tunis"},
    {"name": "Seychelles International Airport",         "city": "Mahé",            "country": "Seychelles",    "iata": "SEZ", "icao": "FSIA", "lat": -4.6743,  "lon": 55.5218,   "alt": 10,   "tz": "Indian/Mahe"},
    # ── South Asia (8) ────────────────────────────────────────────────────────
    {"name": "Indira Gandhi International Airport",      "city": "New Delhi",       "country": "India",         "iata": "DEL", "icao": "VIDP", "lat": 28.5562,  "lon": 77.1000,   "alt": 777,  "tz": "Asia/Kolkata"},
    {"name": "Chhatrapati Shivaji Maharaj Intl Airport", "city": "Mumbai",          "country": "India",         "iata": "BOM", "icao": "VABB", "lat": 19.0896,  "lon": 72.8656,   "alt": 37,   "tz": "Asia/Kolkata"},
    {"name": "Kempegowda International Airport",         "city": "Bangalore",       "country": "India",         "iata": "BLR", "icao": "VOBL", "lat": 13.1979,  "lon": 77.7063,   "alt": 3000, "tz": "Asia/Kolkata"},
    {"name": "Chennai International Airport",            "city": "Chennai",         "country": "India",         "iata": "MAA", "icao": "VOMM", "lat": 12.9900,  "lon": 80.1693,   "alt": 52,   "tz": "Asia/Kolkata"},
    {"name": "Kolkata Netaji Subhas Chandra Bose Intl",  "city": "Kolkata",         "country": "India",         "iata": "CCU", "icao": "VECC", "lat": 22.6547,  "lon": 88.4467,   "alt": 17,   "tz": "Asia/Kolkata"},
    {"name": "Hyderabad Rajiv Gandhi Intl Airport",      "city": "Hyderabad",       "country": "India",         "iata": "HYD", "icao": "VOHS", "lat": 17.2313,  "lon": 78.4298,   "alt": 1741, "tz": "Asia/Kolkata"},
    {"name": "Tribhuvan International Airport",          "city": "Kathmandu",       "country": "Nepal",         "iata": "KTM", "icao": "VNKT", "lat": 27.6966,  "lon": 85.3591,   "alt": 4390, "tz": "Asia/Kathmandu"},
    {"name": "Bandaranaike International Airport",       "city": "Colombo",         "country": "Sri Lanka",     "iata": "CMB", "icao": "VCBI", "lat": 7.1808,   "lon": 79.8841,   "alt": 30,   "tz": "Asia/Colombo"},
    # ── Central & East Asia (14) ──────────────────────────────────────────────
    {"name": "Beijing Capital International Airport",    "city": "Beijing",         "country": "China",         "iata": "PEK", "icao": "ZBAA", "lat": 40.0799,  "lon": 116.6031,  "alt": 116,  "tz": "Asia/Shanghai"},
    {"name": "Beijing Daxing International Airport",     "city": "Beijing",         "country": "China",         "iata": "PKX", "icao": "ZBAD", "lat": 39.5095,  "lon": 116.4105,  "alt": 98,   "tz": "Asia/Shanghai"},
    {"name": "Shanghai Pudong International Airport",    "city": "Shanghai",        "country": "China",         "iata": "PVG", "icao": "ZSPD", "lat": 31.1434,  "lon": 121.8052,  "alt": 13,   "tz": "Asia/Shanghai"},
    {"name": "Shanghai Hongqiao International Airport",  "city": "Shanghai",        "country": "China",         "iata": "SHA", "icao": "ZSSS", "lat": 31.1979,  "lon": 121.3363,  "alt": 10,   "tz": "Asia/Shanghai"},
    {"name": "Guangzhou Baiyun International Airport",   "city": "Guangzhou",       "country": "China",         "iata": "CAN", "icao": "ZGGG", "lat": 23.3924,  "lon": 113.2988,  "alt": 50,   "tz": "Asia/Shanghai"},
    {"name": "Shenzhen Bao'an International Airport",   "city": "Shenzhen",        "country": "China",         "iata": "SZX", "icao": "ZGSZ", "lat": 22.6393,  "lon": 113.8107,  "alt": 13,   "tz": "Asia/Shanghai"},
    {"name": "Chengdu Tianfu International Airport",     "city": "Chengdu",         "country": "China",         "iata": "TFU", "icao": "ZUTF", "lat": 30.3128,  "lon": 104.4441,  "alt": 1587, "tz": "Asia/Shanghai"},
    {"name": "Kunming Changshui International Airport",  "city": "Kunming",         "country": "China",         "iata": "KMG", "icao": "ZPPP", "lat": 24.9920,  "lon": 102.7433,  "alt": 6903, "tz": "Asia/Shanghai"},
    {"name": "Hong Kong International Airport",          "city": "Hong Kong",       "country": "China",         "iata": "HKG", "icao": "VHHH", "lat": 22.3080,  "lon": 113.9185,  "alt": 28,   "tz": "Asia/Hong_Kong"},
    {"name": "Tokyo Narita International Airport",       "city": "Tokyo",           "country": "Japan",         "iata": "NRT", "icao": "RJAA", "lat": 35.7720,  "lon": 140.3929,  "alt": 141,  "tz": "Asia/Tokyo"},
    {"name": "Tokyo Haneda Airport",                     "city": "Tokyo",           "country": "Japan",         "iata": "HND", "icao": "RJTT", "lat": 35.5494,  "lon": 139.7798,  "alt": 35,   "tz": "Asia/Tokyo"},
    {"name": "Osaka Kansai International Airport",       "city": "Osaka",           "country": "Japan",         "iata": "KIX", "icao": "RJBB", "lat": 34.4347,  "lon": 135.2440,  "alt": 26,   "tz": "Asia/Tokyo"},
    {"name": "Nagoya Chubu Centrair Intl Airport",       "city": "Nagoya",          "country": "Japan",         "iata": "NGO", "icao": "RJGG", "lat": 34.8583,  "lon": 136.8050,  "alt": 15,   "tz": "Asia/Tokyo"},
    {"name": "Incheon International Airport",            "city": "Seoul",           "country": "South Korea",   "iata": "ICN", "icao": "RKSI", "lat": 37.4602,  "lon": 126.4407,  "alt": 23,   "tz": "Asia/Seoul"},
    # ── Southeast Asia (10) ───────────────────────────────────────────────────
    {"name": "Singapore Changi Airport",                 "city": "Singapore",       "country": "Singapore",     "iata": "SIN", "icao": "WSSS", "lat": 1.3644,   "lon": 103.9915,  "alt": 22,   "tz": "Asia/Singapore"},
    {"name": "Suvarnabhumi Airport",                     "city": "Bangkok",         "country": "Thailand",      "iata": "BKK", "icao": "VTBS", "lat": 13.6900,  "lon": 100.7501,  "alt": 5,    "tz": "Asia/Bangkok"},
    {"name": "Don Mueang International Airport",         "city": "Bangkok",         "country": "Thailand",      "iata": "DMK", "icao": "VTBD", "lat": 13.9126,  "lon": 100.6067,  "alt": 9,    "tz": "Asia/Bangkok"},
    {"name": "Kuala Lumpur International Airport",       "city": "Kuala Lumpur",    "country": "Malaysia",      "iata": "KUL", "icao": "WMKK", "lat": 2.7456,   "lon": 101.7099,  "alt": 69,   "tz": "Asia/Kuala_Lumpur"},
    {"name": "Ngurah Rai International Airport",         "city": "Bali/Denpasar",   "country": "Indonesia",     "iata": "DPS", "icao": "WADD", "lat": -8.7482,  "lon": 115.1670,  "alt": 14,   "tz": "Asia/Makassar"},
    {"name": "Soekarno-Hatta International Airport",     "city": "Jakarta",         "country": "Indonesia",     "iata": "CGK", "icao": "WIII", "lat": -6.1256,  "lon": 106.6559,  "alt": 34,   "tz": "Asia/Jakarta"},
    {"name": "Ninoy Aquino International Airport",       "city": "Manila",          "country": "Philippines",   "iata": "MNL", "icao": "RPLL", "lat": 14.5086,  "lon": 121.0197,  "alt": 75,   "tz": "Asia/Manila"},
    {"name": "Mactan-Cebu International Airport",        "city": "Cebu",            "country": "Philippines",   "iata": "CEB", "icao": "RPVM", "lat": 10.3075,  "lon": 123.9789,  "alt": 31,   "tz": "Asia/Manila"},
    {"name": "Noi Bai International Airport",            "city": "Hanoi",           "country": "Vietnam",       "iata": "HAN", "icao": "VVNB", "lat": 21.2212,  "lon": 105.8072,  "alt": 39,   "tz": "Asia/Ho_Chi_Minh"},
    {"name": "Tan Son Nhat International Airport",       "city": "Ho Chi Minh City","country": "Vietnam",       "iata": "SGN", "icao": "VVTS", "lat": 10.8188,  "lon": 106.6520,  "alt": 33,   "tz": "Asia/Ho_Chi_Minh"},
    # ── Taiwan, Mongolia, Kazakhstan (3) ──────────────────────────────────────
    {"name": "Taiwan Taoyuan International Airport",     "city": "Taipei",          "country": "Taiwan",        "iata": "TPE", "icao": "RCTP", "lat": 25.0777,  "lon": 121.2328,  "alt": 106,  "tz": "Asia/Taipei"},
    {"name": "Almaty International Airport",             "city": "Almaty",          "country": "Kazakhstan",    "iata": "ALA", "icao": "UAAA", "lat": 43.3521,  "lon": 77.0405,   "alt": 2234, "tz": "Asia/Almaty"},
    {"name": "Nursultan Nazarbayev Intl Airport",        "city": "Astana",          "country": "Kazakhstan",    "iata": "NQZ", "icao": "UACC", "lat": 51.0223,  "lon": 71.4669,   "alt": 1165, "tz": "Asia/Almaty"},
    # ── Australia (26) ────────────────────────────────────────────────────────
    {"name": "Sydney Kingsford Smith Airport",           "city": "Sydney",              "country": "Australia",   "iata": "SYD", "icao": "YSSY", "lat": -33.9399, "lon": 151.1753,  "alt": 21,   "tz": "Australia/Sydney"},
    {"name": "Melbourne Airport",                        "city": "Melbourne",           "country": "Australia",   "iata": "MEL", "icao": "YMML", "lat": -37.6733, "lon": 144.8430,  "alt": 434,  "tz": "Australia/Melbourne"},
    {"name": "Brisbane Airport",                         "city": "Brisbane",            "country": "Australia",   "iata": "BNE", "icao": "YBBN", "lat": -27.3842, "lon": 153.1175,  "alt": 13,   "tz": "Australia/Brisbane"},
    {"name": "Perth Airport",                            "city": "Perth",               "country": "Australia",   "iata": "PER", "icao": "YPPH", "lat": -31.9403, "lon": 115.9670,  "alt": 67,   "tz": "Australia/Perth"},
    {"name": "Adelaide Airport",                         "city": "Adelaide",            "country": "Australia",   "iata": "ADL", "icao": "YPAD", "lat": -34.9450, "lon": 138.5300,  "alt": 20,   "tz": "Australia/Adelaide"},
    {"name": "Gold Coast Airport",                       "city": "Gold Coast",          "country": "Australia",   "iata": "OOL", "icao": "YBCG", "lat": -28.1644, "lon": 153.5047,  "alt": 21,   "tz": "Australia/Brisbane"},
    {"name": "Canberra Airport",                         "city": "Canberra",            "country": "Australia",   "iata": "CBR", "icao": "YSCB", "lat": -35.3069, "lon": 149.1950,  "alt": 1886, "tz": "Australia/Sydney"},
    {"name": "Darwin International Airport",             "city": "Darwin",              "country": "Australia",   "iata": "DRW", "icao": "YPDN", "lat": -12.4147, "lon": 130.8765,  "alt": 103,  "tz": "Australia/Darwin"},
    {"name": "Cairns Airport",                           "city": "Cairns",              "country": "Australia",   "iata": "CNS", "icao": "YBCS", "lat": -16.8858, "lon": 145.7553,  "alt": 10,   "tz": "Australia/Brisbane"},
    {"name": "Hobart International Airport",             "city": "Hobart",              "country": "Australia",   "iata": "HBA", "icao": "YMHB", "lat": -42.8361, "lon": 147.5108,  "alt": 13,   "tz": "Australia/Hobart"},
    {"name": "Launceston Airport",                       "city": "Launceston",          "country": "Australia",   "iata": "LST", "icao": "YMLT", "lat": -41.5453, "lon": 147.2142,  "alt": 562,  "tz": "Australia/Hobart"},
    {"name": "Townsville Airport",                       "city": "Townsville",          "country": "Australia",   "iata": "TSV", "icao": "YBTL", "lat": -19.2525, "lon": 146.7653,  "alt": 18,   "tz": "Australia/Brisbane"},
    {"name": "Sunshine Coast Airport",                   "city": "Sunshine Coast",      "country": "Australia",   "iata": "MCY", "icao": "YBSU", "lat": -26.6033, "lon": 153.0903,  "alt": 15,   "tz": "Australia/Brisbane"},
    {"name": "Newcastle Airport",                        "city": "Newcastle",           "country": "Australia",   "iata": "NTL", "icao": "YWLM", "lat": -32.7950, "lon": 151.8342,  "alt": 9,    "tz": "Australia/Sydney"},
    {"name": "Alice Springs Airport",                    "city": "Alice Springs",       "country": "Australia",   "iata": "ASP", "icao": "YBAS", "lat": -23.8067, "lon": 133.9022,  "alt": 1789, "tz": "Australia/Darwin"},
    {"name": "Ayers Rock (Uluru) Airport",               "city": "Uluru",               "country": "Australia",   "iata": "AYQ", "icao": "YAYE", "lat": -25.1861, "lon": 130.9756,  "alt": 1626, "tz": "Australia/Darwin"},
    {"name": "Whitsunday Coast Airport",                 "city": "Proserpine",          "country": "Australia",   "iata": "PPP", "icao": "YBPN", "lat": -20.4950, "lon": 148.5522,  "alt": 82,   "tz": "Australia/Brisbane"},
    {"name": "Ballina Byron Gateway Airport",            "city": "Ballina",             "country": "Australia",   "iata": "BNK", "icao": "YBNA", "lat": -28.8339, "lon": 153.5622,  "alt": 7,    "tz": "Australia/Sydney"},
    {"name": "Coffs Harbour Airport",                    "city": "Coffs Harbour",       "country": "Australia",   "iata": "CFS", "icao": "YCFS", "lat": -30.3206, "lon": 153.1158,  "alt": 18,   "tz": "Australia/Sydney"},
    {"name": "Albury Airport",                           "city": "Albury",              "country": "Australia",   "iata": "ABX", "icao": "YMAY", "lat": -36.0678, "lon": 146.9578,  "alt": 539,  "tz": "Australia/Sydney"},
    {"name": "Tamworth Regional Airport",                "city": "Tamworth",            "country": "Australia",   "iata": "TMW", "icao": "YSTW", "lat": -31.0839, "lon": 150.8469,  "alt": 1334, "tz": "Australia/Sydney"},
    {"name": "Orange Regional Airport",                  "city": "Orange",              "country": "Australia",   "iata": "OAG", "icao": "YORG", "lat": -33.3817, "lon": 149.1328,  "alt": 3115, "tz": "Australia/Sydney"},
    {"name": "Port Hedland International Airport",       "city": "Port Hedland",        "country": "Australia",   "iata": "PHE", "icao": "YPPD", "lat": -20.3778, "lon": 118.6253,  "alt": 33,   "tz": "Australia/Perth"},
    {"name": "Karratha Airport",                         "city": "Karratha",            "country": "Australia",   "iata": "KTA", "icao": "YPKA", "lat": -20.7122, "lon": 116.7736,  "alt": 29,   "tz": "Australia/Perth"},
    {"name": "Busselton Margaret River Airport",         "city": "Busselton",           "country": "Australia",   "iata": "BQB", "icao": "YBLN", "lat": -33.6886, "lon": 115.4017,  "alt": 55,   "tz": "Australia/Perth"},
    {"name": "Kununurra (East Kimberley) Airport",       "city": "Kununurra",           "country": "Australia",   "iata": "KNX", "icao": "YPKU", "lat": -15.7781, "lon": 128.7075,  "alt": 145,  "tz": "Australia/Perth"},
    # ── New Zealand (15) ──────────────────────────────────────────────────────
    {"name": "Auckland Airport",                         "city": "Auckland",            "country": "New Zealand", "iata": "AKL", "icao": "NZAA", "lat": -37.0082, "lon": 174.7917,  "alt": 23,   "tz": "Pacific/Auckland"},
    {"name": "Wellington International Airport",         "city": "Wellington",          "country": "New Zealand", "iata": "WLG", "icao": "NZWN", "lat": -41.3272, "lon": 174.8050,  "alt": 41,   "tz": "Pacific/Auckland"},
    {"name": "Christchurch Airport",                     "city": "Christchurch",        "country": "New Zealand", "iata": "CHC", "icao": "NZCH", "lat": -43.4894, "lon": 172.5320,  "alt": 123,  "tz": "Pacific/Auckland"},
    {"name": "Queenstown Airport",                       "city": "Queenstown",          "country": "New Zealand", "iata": "ZQN", "icao": "NZQN", "lat": -45.0211, "lon": 168.7392,  "alt": 1171, "tz": "Pacific/Auckland"},
    {"name": "Dunedin Airport",                          "city": "Dunedin",             "country": "New Zealand", "iata": "DUD", "icao": "NZDN", "lat": -45.9281, "lon": 170.1983,  "alt": 4,    "tz": "Pacific/Auckland"},
    {"name": "Hamilton Airport",                         "city": "Hamilton",            "country": "New Zealand", "iata": "HLZ", "icao": "NZHN", "lat": -37.8667, "lon": 175.3322,  "alt": 172,  "tz": "Pacific/Auckland"},
    {"name": "Nelson Airport",                           "city": "Nelson",              "country": "New Zealand", "iata": "NSN", "icao": "NZNS", "lat": -41.2983, "lon": 173.2211,  "alt": 17,   "tz": "Pacific/Auckland"},
    {"name": "Rotorua Airport",                          "city": "Rotorua",             "country": "New Zealand", "iata": "ROT", "icao": "NZRO", "lat": -38.1092, "lon": 176.3172,  "alt": 935,  "tz": "Pacific/Auckland"},
    {"name": "Palmerston North Airport",                 "city": "Palmerston North",    "country": "New Zealand", "iata": "PMR", "icao": "NZPM", "lat": -40.3206, "lon": 175.6167,  "alt": 151,  "tz": "Pacific/Auckland"},
    {"name": "Hawke's Bay Airport",                      "city": "Napier",              "country": "New Zealand", "iata": "NPE", "icao": "NZNR", "lat": -39.4658, "lon": 176.8700,  "alt": 6,    "tz": "Pacific/Auckland"},
    {"name": "New Plymouth Airport",                     "city": "New Plymouth",        "country": "New Zealand", "iata": "NPL", "icao": "NZNP", "lat": -39.0086, "lon": 174.1792,  "alt": 97,   "tz": "Pacific/Auckland"},
    {"name": "Tauranga Airport",                         "city": "Tauranga",            "country": "New Zealand", "iata": "TRG", "icao": "NZTG", "lat": -37.6719, "lon": 176.1961,  "alt": 13,   "tz": "Pacific/Auckland"},
    {"name": "Invercargill Airport",                     "city": "Invercargill",        "country": "New Zealand", "iata": "IVC", "icao": "NZNV", "lat": -46.4124, "lon": 168.3130,  "alt": 5,    "tz": "Pacific/Auckland"},
    {"name": "Whangarei Airport",                        "city": "Whangarei",           "country": "New Zealand", "iata": "WRE", "icao": "NZWR", "lat": -35.7683, "lon": 174.3650,  "alt": 133,  "tz": "Pacific/Auckland"},
    {"name": "Bay of Islands (Kerikeri) Airport",        "city": "Kerikeri",            "country": "New Zealand", "iata": "KKE", "icao": "NZKK", "lat": -35.2628, "lon": 173.9119,  "alt": 492,  "tz": "Pacific/Auckland"},
    # ── Ireland (6) ───────────────────────────────────────────────────────────
    {"name": "Shannon Airport",                          "city": "Shannon",             "country": "Ireland",     "iata": "SNN", "icao": "EINN", "lat": 52.7020,  "lon": -8.9248,   "alt": 46,   "tz": "Europe/Dublin"},
    {"name": "Cork Airport",                             "city": "Cork",                "country": "Ireland",     "iata": "ORK", "icao": "EICK", "lat": 51.8413,  "lon": -8.4911,   "alt": 502,  "tz": "Europe/Dublin"},
    {"name": "Ireland West Airport Knock",               "city": "Knock",               "country": "Ireland",     "iata": "NOC", "icao": "EIKN", "lat": 53.9103,  "lon": -8.8186,   "alt": 665,  "tz": "Europe/Dublin"},
    {"name": "Kerry Airport",                            "city": "Farranfore",          "country": "Ireland",     "iata": "KIR", "icao": "EIKY", "lat": 52.1809,  "lon": -9.5238,   "alt": 112,  "tz": "Europe/Dublin"},
    {"name": "Donegal Airport",                          "city": "Donegal",             "country": "Ireland",     "iata": "CFN", "icao": "EIDL", "lat": 55.0442,  "lon": -8.3408,   "alt": 30,   "tz": "Europe/Dublin"},
    # ── Additional United States (14) ─────────────────────────────────────────
    {"name": "Chicago Midway International Airport",     "city": "Chicago",         "country": "United States", "iata": "MDW", "icao": "KMDW", "lat": 41.7868,  "lon": -87.7522,  "alt": 620,  "tz": "America/Chicago"},
    {"name": "Fort Lauderdale-Hollywood Intl Airport",   "city": "Fort Lauderdale", "country": "United States", "iata": "FLL", "icao": "KFLL", "lat": 26.0726,  "lon": -80.1527,  "alt": 9,    "tz": "America/New_York"},
    {"name": "Sacramento International Airport",         "city": "Sacramento",      "country": "United States", "iata": "SMF", "icao": "KSMF", "lat": 38.6954,  "lon": -121.5908, "alt": 27,   "tz": "America/Los_Angeles"},
    {"name": "Oakland International Airport",            "city": "Oakland",         "country": "United States", "iata": "OAK", "icao": "KOAK", "lat": 37.7213,  "lon": -122.2208, "alt": 9,    "tz": "America/Los_Angeles"},
    {"name": "San Jose International Airport",           "city": "San Jose",        "country": "United States", "iata": "SJC", "icao": "KSJC", "lat": 37.3626,  "lon": -121.9290, "alt": 62,   "tz": "America/Los_Angeles"},
    {"name": "John Wayne Airport",                       "city": "Orange County",   "country": "United States", "iata": "SNA", "icao": "KSNA", "lat": 33.6757,  "lon": -117.8682, "alt": 56,   "tz": "America/Los_Angeles"},
    {"name": "Tucson International Airport",             "city": "Tucson",          "country": "United States", "iata": "TUS", "icao": "KTUS", "lat": 32.1161,  "lon": -110.9410, "alt": 2643, "tz": "America/Phoenix"},
    {"name": "Albuquerque International Sunport",        "city": "Albuquerque",     "country": "United States", "iata": "ABQ", "icao": "KABQ", "lat": 35.0402,  "lon": -106.6091, "alt": 5355, "tz": "America/Denver"},
    {"name": "El Paso International Airport",            "city": "El Paso",         "country": "United States", "iata": "ELP", "icao": "KELP", "lat": 31.8072,  "lon": -106.3779, "alt": 3959, "tz": "America/Denver"},
    {"name": "William P. Hobby Airport",                 "city": "Houston",         "country": "United States", "iata": "HOU", "icao": "KHOU", "lat": 29.6454,  "lon": -95.2789,  "alt": 46,   "tz": "America/Chicago"},
    {"name": "Memphis International Airport",            "city": "Memphis",         "country": "United States", "iata": "MEM", "icao": "KMEM", "lat": 35.0424,  "lon": -89.9767,  "alt": 341,  "tz": "America/Chicago"},
    {"name": "Cincinnati/Northern Kentucky Intl Airport","city": "Cincinnati",      "country": "United States", "iata": "CVG", "icao": "KCVG", "lat": 39.0488,  "lon": -84.6678,  "alt": 896,  "tz": "America/New_York"},
    {"name": "Cleveland Hopkins International Airport",  "city": "Cleveland",       "country": "United States", "iata": "CLE", "icao": "KCLE", "lat": 41.4117,  "lon": -81.8498,  "alt": 791,  "tz": "America/New_York"},
    {"name": "Bradley International Airport",            "city": "Hartford",        "country": "United States", "iata": "BDL", "icao": "KBDL", "lat": 41.9389,  "lon": -72.6832,  "alt": 174,  "tz": "America/New_York"},
    # ── Additional Europe (9) ─────────────────────────────────────────────────
    {"name": "Dusseldorf Airport",                       "city": "Dusseldorf",      "country": "Germany",       "iata": "DUS", "icao": "EDDL", "lat": 51.2895,  "lon": 6.7668,    "alt": 147,  "tz": "Europe/Berlin"},
    {"name": "Hamburg Airport",                          "city": "Hamburg",         "country": "Germany",       "iata": "HAM", "icao": "EDDH", "lat": 53.6304,  "lon": 9.9882,    "alt": 53,   "tz": "Europe/Berlin"},
    {"name": "Lyon Saint-Exupery Airport",               "city": "Lyon",            "country": "France",        "iata": "LYS", "icao": "LFLL", "lat": 45.7256,  "lon": 5.0811,    "alt": 821,  "tz": "Europe/Paris"},
    {"name": "Venice Marco Polo Airport",                "city": "Venice",          "country": "Italy",         "iata": "VCE", "icao": "LIPZ", "lat": 45.5053,  "lon": 12.3519,   "alt": 7,    "tz": "Europe/Rome"},
    {"name": "Naples International Airport",             "city": "Naples",          "country": "Italy",         "iata": "NAP", "icao": "LIRN", "lat": 40.8860,  "lon": 14.2908,   "alt": 294,  "tz": "Europe/Rome"},
    {"name": "Thessaloniki Macedonia Airport",           "city": "Thessaloniki",    "country": "Greece",        "iata": "SKG", "icao": "LGTS", "lat": 40.5197,  "lon": 22.9709,   "alt": 22,   "tz": "Europe/Athens"},
    {"name": "Riga International Airport",               "city": "Riga",            "country": "Latvia",        "iata": "RIX", "icao": "EVRA", "lat": 56.9236,  "lon": 23.9711,   "alt": 36,   "tz": "Europe/Riga"},
    {"name": "Vilnius Airport",                          "city": "Vilnius",         "country": "Lithuania",     "iata": "VNO", "icao": "EYVI", "lat": 54.6341,  "lon": 25.2858,   "alt": 197,  "tz": "Europe/Vilnius"},
    {"name": "Tallinn Airport",                          "city": "Tallinn",         "country": "Estonia",       "iata": "TLL", "icao": "EETN", "lat": 59.4133,  "lon": 24.8328,   "alt": 131,  "tz": "Europe/Tallinn"},
    # ── Additional Asia & Middle East (8) ─────────────────────────────────────
    {"name": "Fukuoka Airport",                          "city": "Fukuoka",         "country": "Japan",         "iata": "FUK", "icao": "RJFF", "lat": 33.5858,  "lon": 130.4511,  "alt": 32,   "tz": "Asia/Tokyo"},
    {"name": "Sapporo New Chitose Airport",              "city": "Sapporo",         "country": "Japan",         "iata": "CTS", "icao": "RJCC", "lat": 42.7752,  "lon": 141.6922,  "alt": 82,   "tz": "Asia/Tokyo"},
    {"name": "Gimpo International Airport",              "city": "Seoul",           "country": "South Korea",   "iata": "GMP", "icao": "RKSS", "lat": 37.5583,  "lon": 126.7906,  "alt": 59,   "tz": "Asia/Seoul"},
    {"name": "Lombok International Airport",             "city": "Lombok",          "country": "Indonesia",     "iata": "LOP", "icao": "WADL", "lat": -8.7573,  "lon": 116.2767,  "alt": 319,  "tz": "Asia/Makassar"},
    {"name": "Yangon International Airport",             "city": "Yangon",          "country": "Myanmar",       "iata": "RGN", "icao": "VYYY", "lat": 16.9073,  "lon": 96.1332,   "alt": 109,  "tz": "Asia/Rangoon"},
    {"name": "Phnom Penh International Airport",         "city": "Phnom Penh",      "country": "Cambodia",      "iata": "PNH", "icao": "VDPP", "lat": 11.5466,  "lon": 104.8440,  "alt": 40,   "tz": "Asia/Phnom_Penh"},
    {"name": "Vientiane Wattay International Airport",   "city": "Vientiane",       "country": "Laos",          "iata": "VTE", "icao": "VLVT", "lat": 17.9883,  "lon": 102.5633,  "alt": 564,  "tz": "Asia/Vientiane"},
    {"name": "Amman Queen Alia International Airport",   "city": "Amman",           "country": "Jordan",        "iata": "AMM", "icao": "OJAI", "lat": 31.7226,  "lon": 35.9932,   "alt": 2395, "tz": "Asia/Amman"},
    # ── Additional Africa (4) ─────────────────────────────────────────────────
    {"name": "Blaise Diagne International Airport",      "city": "Dakar",           "country": "Senegal",       "iata": "DSS", "icao": "GOBD", "lat": 14.6700,  "lon": -17.0730,  "alt": 90,   "tz": "Africa/Dakar"},
    {"name": "Abidjan Felix-Houphouet-Boigny Intl",      "city": "Abidjan",         "country": "Ivory Coast",   "iata": "ABJ", "icao": "DIAP", "lat": 5.2614,   "lon": -3.9263,   "alt": 21,   "tz": "Africa/Abidjan"},
    {"name": "Kigali International Airport",             "city": "Kigali",          "country": "Rwanda",        "iata": "KGL", "icao": "HRYR", "lat": -1.9686,  "lon": 30.1395,   "alt": 4859, "tz": "Africa/Kigali"},
    {"name": "Entebbe International Airport",            "city": "Entebbe",         "country": "Uganda",        "iata": "EBB", "icao": "HUEN", "lat": 0.0424,   "lon": 32.4435,   "alt": 3782, "tz": "Africa/Kampala"},

    # ── United States expanded (49 more) ──────────────────────────────────────
    {"name": "St Louis Lambert International Airport",   "city": "St. Louis",       "country": "United States", "iata": "STL", "icao": "KSTL", "lat": 38.7487,  "lon": -90.3700,  "alt": 618,  "tz": "America/Chicago"},
    {"name": "Milwaukee Mitchell International Airport", "city": "Milwaukee",       "country": "United States", "iata": "MKE", "icao": "KMKE", "lat": 42.9472,  "lon": -87.8966,  "alt": 723,  "tz": "America/Chicago"},
    {"name": "Omaha Eppley Airfield",                    "city": "Omaha",           "country": "United States", "iata": "OMA", "icao": "KOMA", "lat": 41.3032,  "lon": -95.8940,  "alt": 984,  "tz": "America/Chicago"},
    {"name": "Des Moines International Airport",         "city": "Des Moines",      "country": "United States", "iata": "DSM", "icao": "KDSM", "lat": 41.5340,  "lon": -93.6631,  "alt": 958,  "tz": "America/Chicago"},
    {"name": "Louisville Muhammad Ali Intl Airport",     "city": "Louisville",      "country": "United States", "iata": "SDF", "icao": "KSDF", "lat": 38.1744,  "lon": -85.7360,  "alt": 501,  "tz": "America/Kentucky/Louisville"},
    {"name": "Columbus John Glenn International Airport","city": "Columbus",        "country": "United States", "iata": "CMH", "icao": "KCMH", "lat": 39.9980,  "lon": -82.8919,  "alt": 815,  "tz": "America/New_York"},
    {"name": "Richmond International Airport",           "city": "Richmond",        "country": "United States", "iata": "RIC", "icao": "KRIC", "lat": 37.5052,  "lon": -77.3197,  "alt": 167,  "tz": "America/New_York"},
    {"name": "Norfolk International Airport",            "city": "Norfolk",         "country": "United States", "iata": "ORF", "icao": "KORF", "lat": 36.8976,  "lon": -76.0123,  "alt": 26,   "tz": "America/New_York"},
    {"name": "Jacksonville International Airport",       "city": "Jacksonville",    "country": "United States", "iata": "JAX", "icao": "KJAX", "lat": 30.4941,  "lon": -81.6879,  "alt": 30,   "tz": "America/New_York"},
    {"name": "Savannah/Hilton Head International",       "city": "Savannah",        "country": "United States", "iata": "SAV", "icao": "KSAV", "lat": 32.1276,  "lon": -81.2021,  "alt": 50,   "tz": "America/New_York"},
    {"name": "Birmingham-Shuttlesworth Intl Airport",    "city": "Birmingham",      "country": "United States", "iata": "BHM", "icao": "KBHM", "lat": 33.5629,  "lon": -86.7535,  "alt": 644,  "tz": "America/Chicago"},
    {"name": "Little Rock Bill and Hillary Clinton Natl","city": "Little Rock",     "country": "United States", "iata": "LIT", "icao": "KLIT", "lat": 34.7294,  "lon": -92.2243,  "alt": 262,  "tz": "America/Chicago"},
    {"name": "Jackson Medgar Wiley Evers Intl Airport",  "city": "Jackson",         "country": "United States", "iata": "JAN", "icao": "KJAN", "lat": 32.3112,  "lon": -90.0759,  "alt": 346,  "tz": "America/Chicago"},
    {"name": "Baton Rouge Metropolitan Airport",         "city": "Baton Rouge",     "country": "United States", "iata": "BTR", "icao": "KBTR", "lat": 30.5332,  "lon": -91.1496,  "alt": 70,   "tz": "America/Chicago"},
    {"name": "Tulsa International Airport",              "city": "Tulsa",           "country": "United States", "iata": "TUL", "icao": "KTUL", "lat": 36.1984,  "lon": -95.8881,  "alt": 677,  "tz": "America/Chicago"},
    {"name": "Oklahoma City Will Rogers World Airport",  "city": "Oklahoma City",   "country": "United States", "iata": "OKC", "icao": "KOKC", "lat": 35.3931,  "lon": -97.6007,  "alt": 1295, "tz": "America/Chicago"},
    {"name": "Wichita Dwight D. Eisenhower Natl Airport","city": "Wichita",         "country": "United States", "iata": "ICT", "icao": "KICT", "lat": 37.6499,  "lon": -97.4331,  "alt": 1333, "tz": "America/Chicago"},
    {"name": "Colorado Springs Airport",                 "city": "Colorado Springs","country": "United States", "iata": "COS", "icao": "KCOS", "lat": 38.8058,  "lon": -104.7008, "alt": 6187, "tz": "America/Denver"},
    {"name": "Boise Airport",                            "city": "Boise",           "country": "United States", "iata": "BOI", "icao": "KBOI", "lat": 43.5644,  "lon": -116.2228, "alt": 2871, "tz": "America/Boise"},
    {"name": "Spokane International Airport",            "city": "Spokane",         "country": "United States", "iata": "GEG", "icao": "KGEG", "lat": 47.6199,  "lon": -117.5339, "alt": 2376, "tz": "America/Los_Angeles"},
    {"name": "Reno-Tahoe International Airport",         "city": "Reno",            "country": "United States", "iata": "RNO", "icao": "KRNO", "lat": 39.4991,  "lon": -119.7681, "alt": 4415, "tz": "America/Los_Angeles"},
    {"name": "Palm Springs International Airport",       "city": "Palm Springs",    "country": "United States", "iata": "PSP", "icao": "KPSP", "lat": 33.8297,  "lon": -116.5066, "alt": 477,  "tz": "America/Los_Angeles"},
    {"name": "Long Beach Airport",                       "city": "Long Beach",      "country": "United States", "iata": "LGB", "icao": "KLGB", "lat": 33.8177,  "lon": -118.1516, "alt": 60,   "tz": "America/Los_Angeles"},
    {"name": "Burbank Bob Hope Airport",                 "city": "Burbank",         "country": "United States", "iata": "BUR", "icao": "KBUR", "lat": 34.2007,  "lon": -118.3585, "alt": 778,  "tz": "America/Los_Angeles"},
    {"name": "Ontario International Airport",            "city": "Ontario",         "country": "United States", "iata": "ONT", "icao": "KONT", "lat": 34.0560,  "lon": -117.6012, "alt": 944,  "tz": "America/Los_Angeles"},
    {"name": "Fresno Yosemite International Airport",    "city": "Fresno",          "country": "United States", "iata": "FAT", "icao": "KFAT", "lat": 36.7762,  "lon": -119.7182, "alt": 336,  "tz": "America/Los_Angeles"},
    {"name": "Eugene Airport",                           "city": "Eugene",          "country": "United States", "iata": "EUG", "icao": "KEUG", "lat": 44.1246,  "lon": -123.2119, "alt": 374,  "tz": "America/Los_Angeles"},
    {"name": "Fairbanks International Airport",          "city": "Fairbanks",       "country": "United States", "iata": "FAI", "icao": "PAFA", "lat": 64.8151,  "lon": -147.8561, "alt": 434,  "tz": "America/Anchorage"},
    {"name": "Kahului Airport",                          "city": "Maui",            "country": "United States", "iata": "OGG", "icao": "PHOG", "lat": 20.8986,  "lon": -156.4305, "alt": 54,   "tz": "Pacific/Honolulu"},
    {"name": "Kona International Airport",               "city": "Kona",            "country": "United States", "iata": "KOA", "icao": "PHKO", "lat": 19.7388,  "lon": -156.0456, "alt": 47,   "tz": "Pacific/Honolulu"},
    {"name": "Albany International Airport",             "city": "Albany",          "country": "United States", "iata": "ALB", "icao": "KALB", "lat": 42.7483,  "lon": -73.8017,  "alt": 285,  "tz": "America/New_York"},
    {"name": "Buffalo Niagara International Airport",    "city": "Buffalo",         "country": "United States", "iata": "BUF", "icao": "KBUF", "lat": 42.9405,  "lon": -78.7322,  "alt": 724,  "tz": "America/New_York"},
    {"name": "Syracuse Hancock International Airport",   "city": "Syracuse",        "country": "United States", "iata": "SYR", "icao": "KSYR", "lat": 43.1112,  "lon": -76.1063,  "alt": 421,  "tz": "America/New_York"},
    {"name": "Rochester Greater Rochester Intl Airport", "city": "Rochester",       "country": "United States", "iata": "ROC", "icao": "KROC", "lat": 43.1189,  "lon": -77.6724,  "alt": 559,  "tz": "America/New_York"},
    {"name": "Dayton International Airport",             "city": "Dayton",          "country": "United States", "iata": "DAY", "icao": "KDAY", "lat": 39.9024,  "lon": -84.2194,  "alt": 1009, "tz": "America/New_York"},
    {"name": "Grand Rapids Gerald R. Ford Intl Airport", "city": "Grand Rapids",    "country": "United States", "iata": "GRR", "icao": "KGRR", "lat": 42.8808,  "lon": -85.5228,  "alt": 794,  "tz": "America/Detroit"},
    {"name": "Lansing Capital Region International",     "city": "Lansing",         "country": "United States", "iata": "LAN", "icao": "KLAN", "lat": 42.7787,  "lon": -84.5874,  "alt": 861,  "tz": "America/Detroit"},
    {"name": "Flint Bishop International Airport",       "city": "Flint",           "country": "United States", "iata": "FNT", "icao": "KFNT", "lat": 42.9654,  "lon": -83.7436,  "alt": 782,  "tz": "America/Detroit"},
    {"name": "Green Bay Austin Straubel Intl Airport",   "city": "Green Bay",       "country": "United States", "iata": "GRB", "icao": "KGRB", "lat": 44.4851,  "lon": -88.1296,  "alt": 695,  "tz": "America/Chicago"},
    {"name": "Madison Dane County Regional Airport",     "city": "Madison",         "country": "United States", "iata": "MSN", "icao": "KMSN", "lat": 43.1399,  "lon": -89.3375,  "alt": 887,  "tz": "America/Chicago"},
    {"name": "Sioux Falls Regional Airport",             "city": "Sioux Falls",     "country": "United States", "iata": "FSD", "icao": "KFSD", "lat": 43.5820,  "lon": -96.7419,  "alt": 1429, "tz": "America/Chicago"},
    {"name": "Fargo Hector International Airport",       "city": "Fargo",           "country": "United States", "iata": "FAR", "icao": "KFAR", "lat": 46.9207,  "lon": -96.8158,  "alt": 902,  "tz": "America/Chicago"},
    {"name": "Billings Logan International Airport",     "city": "Billings",        "country": "United States", "iata": "BIL", "icao": "KBIL", "lat": 45.8077,  "lon": -108.5428, "alt": 3652, "tz": "America/Denver"},
    {"name": "Great Falls International Airport",        "city": "Great Falls",     "country": "United States", "iata": "GTF", "icao": "KGTF", "lat": 47.4820,  "lon": -111.3709, "alt": 3680, "tz": "America/Denver"},
    {"name": "Missoula Montana Airport",                 "city": "Missoula",        "country": "United States", "iata": "MSO", "icao": "KMSO", "lat": 46.9163,  "lon": -114.0906, "alt": 3206, "tz": "America/Denver"},
    {"name": "Jackson Hole Airport",                     "city": "Jackson Hole",    "country": "United States", "iata": "JAC", "icao": "KJAC", "lat": 43.6073,  "lon": -110.7377, "alt": 6451, "tz": "America/Denver"},
    {"name": "Aspen Pitkin County Airport",              "city": "Aspen",           "country": "United States", "iata": "ASE", "icao": "KASE", "lat": 39.2232,  "lon": -106.8687, "alt": 7820, "tz": "America/Denver"},

    # ── Canada expanded (8 more) ──────────────────────────────────────────────
    {"name": "Quebec City Jean Lesage Intl Airport",     "city": "Quebec City",     "country": "Canada",        "iata": "YQB", "icao": "CYQB", "lat": 46.7911,  "lon": -71.3933,  "alt": 244,  "tz": "America/Toronto"},
    {"name": "Halifax Stanfield International Airport",  "city": "Halifax",         "country": "Canada",        "iata": "YHZ", "icao": "CYHZ", "lat": 44.8808,  "lon": -63.5086,  "alt": 477,  "tz": "America/Halifax"},
    {"name": "Victoria International Airport",           "city": "Victoria",        "country": "Canada",        "iata": "YYJ", "icao": "CYYJ", "lat": 48.6469,  "lon": -123.4258, "alt": 63,   "tz": "America/Vancouver"},
    {"name": "Kelowna International Airport",            "city": "Kelowna",         "country": "Canada",        "iata": "YLW", "icao": "CYLW", "lat": 49.9561,  "lon": -119.3778, "alt": 1421, "tz": "America/Vancouver"},
    {"name": "Saskatoon John G. Diefenbaker Intl",       "city": "Saskatoon",       "country": "Canada",        "iata": "YXE", "icao": "CYXE", "lat": 52.1708,  "lon": -106.6997, "alt": 1653, "tz": "America/Regina"},
    {"name": "Regina International Airport",             "city": "Regina",          "country": "Canada",        "iata": "YQR", "icao": "CYQR", "lat": 50.4319,  "lon": -104.6658, "alt": 1894, "tz": "America/Regina"},
    {"name": "St. Johns International Airport",          "city": "St. Johns",       "country": "Canada",        "iata": "YYT", "icao": "CYYT", "lat": 47.6186,  "lon": -52.7519,  "alt": 461,  "tz": "America/St_Johns"},
    {"name": "Yellowknife Airport",                      "city": "Yellowknife",     "country": "Canada",        "iata": "YZF", "icao": "CYZF", "lat": 62.4628,  "lon": -114.4403, "alt": 674,  "tz": "America/Yellowknife"},

    # ── Central America & Caribbean expanded (6 more) ─────────────────────────
    {"name": "Tocumen International Airport",            "city": "Panama City",     "country": "Panama",        "iata": "PTY", "icao": "MPTO", "lat": 9.0714,   "lon": -79.3835,  "alt": 135,  "tz": "America/Panama"},
    {"name": "La Aurora International Airport",          "city": "Guatemala City",  "country": "Guatemala",     "iata": "GUA", "icao": "MGGT", "lat": 14.5833,  "lon": -90.5275,  "alt": 4952, "tz": "America/Guatemala"},
    {"name": "Toncontin International Airport",          "city": "Tegucigalpa",     "country": "Honduras",      "iata": "TGU", "icao": "MHTG", "lat": 14.0608,  "lon": -87.2172,  "alt": 3294, "tz": "America/Tegucigalpa"},
    {"name": "El Salvador International Airport",        "city": "San Salvador",    "country": "El Salvador",   "iata": "SAL", "icao": "MSSS", "lat": 13.4409,  "lon": -89.0557,  "alt": 101,  "tz": "America/El_Salvador"},
    {"name": "Augusto C. Sandino International Airport", "city": "Managua",         "country": "Nicaragua",     "iata": "MGA", "icao": "MNMG", "lat": 12.1415,  "lon": -86.1682,  "alt": 194,  "tz": "America/Managua"},
    {"name": "Punta Cana International Airport",         "city": "Punta Cana",      "country": "Dominican Rep.","iata": "PUJ", "icao": "MDPC", "lat": 18.5674,  "lon": -68.3634,  "alt": 47,   "tz": "America/Santo_Domingo"},

    # ── South America expanded (10 more) ──────────────────────────────────────
    {"name": "Recife Guararapes International Airport",  "city": "Recife",          "country": "Brazil",        "iata": "REC", "icao": "SBRF", "lat": -8.1265,  "lon": -34.9231,  "alt": 33,   "tz": "America/Recife"},
    {"name": "Salvador Deputado Luis Eduardo Magalhaes", "city": "Salvador",        "country": "Brazil",        "iata": "SSA", "icao": "SBSV", "lat": -12.9086, "lon": -38.3225,  "alt": 64,   "tz": "America/Bahia"},
    {"name": "Belo Horizonte Confins Intl Airport",      "city": "Belo Horizonte",  "country": "Brazil",        "iata": "CNF", "icao": "SBCF", "lat": -19.6244, "lon": -43.9719,  "alt": 2715, "tz": "America/Sao_Paulo"},
    {"name": "Curitiba Afonso Pena International Airport","city": "Curitiba",       "country": "Brazil",        "iata": "CWB", "icao": "SBCT", "lat": -25.5285, "lon": -49.1758,  "alt": 2988, "tz": "America/Sao_Paulo"},
    {"name": "Brasilia President Juscelino Kubitschek",  "city": "Brasilia",        "country": "Brazil",        "iata": "BSB", "icao": "SBBR", "lat": -15.8711, "lon": -47.9186,  "alt": 3497, "tz": "America/Sao_Paulo"},
    {"name": "Medellin Jose Maria Cordova Intl Airport", "city": "Medellin",        "country": "Colombia",      "iata": "MDE", "icao": "SKRG", "lat": 6.1645,   "lon": -75.4231,  "alt": 6955, "tz": "America/Bogota"},
    {"name": "Cali Alfonso Bonilla Aragon Intl Airport", "city": "Cali",            "country": "Colombia",      "iata": "CLO", "icao": "SKCL", "lat": 3.5432,   "lon": -76.3816,  "alt": 3162, "tz": "America/Bogota"},
    {"name": "Guayaquil Jose Joaquin de Olmedo Intl",    "city": "Guayaquil",       "country": "Ecuador",       "iata": "GYE", "icao": "SEGU", "lat": -2.1574,  "lon": -79.8836,  "alt": 19,   "tz": "America/Guayaquil"},
    {"name": "Asuncion Silvio Pettirossi Intl Airport",  "city": "Asuncion",        "country": "Paraguay",      "iata": "ASU", "icao": "SGAS", "lat": -25.2400, "lon": -57.5200,  "alt": 292,  "tz": "America/Asuncion"},
    {"name": "Montevideo Carrasco International Airport","city": "Montevideo",      "country": "Uruguay",       "iata": "MVD", "icao": "SUMU", "lat": -34.8384, "lon": -56.0308,  "alt": 105,  "tz": "America/Montevideo"},

    # ── Europe expanded (55 more) ──────────────────────────────────────────────
    {"name": "Cologne Bonn Airport",                     "city": "Cologne",         "country": "Germany",       "iata": "CGN", "icao": "EDDK", "lat": 50.8659,  "lon": 7.1427,    "alt": 302,  "tz": "Europe/Berlin"},
    {"name": "Stuttgart Airport",                        "city": "Stuttgart",       "country": "Germany",       "iata": "STR", "icao": "EDDS", "lat": 48.6900,  "lon": 9.2216,    "alt": 1300, "tz": "Europe/Berlin"},
    {"name": "Nuremberg Airport",                        "city": "Nuremberg",       "country": "Germany",       "iata": "NUE", "icao": "EDDN", "lat": 49.4987,  "lon": 11.0669,   "alt": 1046, "tz": "Europe/Berlin"},
    {"name": "Hanover Airport",                          "city": "Hanover",         "country": "Germany",       "iata": "HAJ", "icao": "EDDV", "lat": 52.4611,  "lon": 9.6850,    "alt": 183,  "tz": "Europe/Berlin"},
    {"name": "Leipzig Halle Airport",                    "city": "Leipzig",         "country": "Germany",       "iata": "LEJ", "icao": "EDDP", "lat": 51.4232,  "lon": 12.2363,   "alt": 465,  "tz": "Europe/Berlin"},
    {"name": "Dresden Airport",                          "city": "Dresden",         "country": "Germany",       "iata": "DRS", "icao": "EDDC", "lat": 51.1328,  "lon": 13.7672,   "alt": 755,  "tz": "Europe/Berlin"},
    {"name": "Marseille Provence Airport",               "city": "Marseille",       "country": "France",        "iata": "MRS", "icao": "LFML", "lat": 43.4393,  "lon": 5.2214,    "alt": 74,   "tz": "Europe/Paris"},
    {"name": "Toulouse Blagnac Airport",                 "city": "Toulouse",        "country": "France",        "iata": "TLS", "icao": "LFBO", "lat": 43.6293,  "lon": 1.3638,    "alt": 499,  "tz": "Europe/Paris"},
    {"name": "Bordeaux Merignac Airport",                "city": "Bordeaux",        "country": "France",        "iata": "BOD", "icao": "LFBD", "lat": 44.8283,  "lon": -0.7156,   "alt": 162,  "tz": "Europe/Paris"},
    {"name": "Strasbourg Airport",                       "city": "Strasbourg",      "country": "France",        "iata": "SXB", "icao": "LFST", "lat": 48.5383,  "lon": 7.6283,    "alt": 505,  "tz": "Europe/Paris"},
    {"name": "Nantes Atlantique Airport",                "city": "Nantes",          "country": "France",        "iata": "NTE", "icao": "LFRS", "lat": 47.1532,  "lon": -1.6103,   "alt": 90,   "tz": "Europe/Paris"},
    {"name": "Alicante Elche Miguel Hdez Airport",       "city": "Alicante",        "country": "Spain",         "iata": "ALC", "icao": "LEAL", "lat": 38.2822,  "lon": -0.5582,   "alt": 142,  "tz": "Europe/Madrid"},
    {"name": "Malaga Costa del Sol Airport",             "city": "Malaga",          "country": "Spain",         "iata": "AGP", "icao": "LEMG", "lat": 36.6749,  "lon": -4.4991,   "alt": 53,   "tz": "Europe/Madrid"},
    {"name": "Seville San Pablo Airport",                "city": "Seville",         "country": "Spain",         "iata": "SVQ", "icao": "LEZL", "lat": 37.4180,  "lon": -5.8931,   "alt": 112,  "tz": "Europe/Madrid"},
    {"name": "Bilbao Airport",                           "city": "Bilbao",          "country": "Spain",         "iata": "BIO", "icao": "LEBB", "lat": 43.3011,  "lon": -2.9106,   "alt": 138,  "tz": "Europe/Madrid"},
    {"name": "Valencia Airport",                         "city": "Valencia",        "country": "Spain",         "iata": "VLC", "icao": "LEVC", "lat": 39.4893,  "lon": -0.4816,   "alt": 240,  "tz": "Europe/Madrid"},
    {"name": "Lanzarote Airport",                        "city": "Lanzarote",       "country": "Spain",         "iata": "ACE", "icao": "GCRR", "lat": 28.9455,  "lon": -13.6052,  "alt": 46,   "tz": "Atlantic/Canary"},
    {"name": "Gran Canaria Airport",                     "city": "Las Palmas",      "country": "Spain",         "iata": "LPA", "icao": "GCLP", "lat": 27.9319,  "lon": -15.3866,  "alt": 78,   "tz": "Atlantic/Canary"},
    {"name": "Tenerife South Airport",                   "city": "Tenerife",        "country": "Spain",         "iata": "TFS", "icao": "GCTS", "lat": 28.0445,  "lon": -16.5725,  "alt": 209,  "tz": "Atlantic/Canary"},
    {"name": "Porto Francisco Sa Carneiro Airport",      "city": "Porto",           "country": "Portugal",      "iata": "OPO", "icao": "LPPR", "lat": 41.2481,  "lon": -8.6814,   "alt": 228,  "tz": "Europe/Lisbon"},
    {"name": "Faro Airport",                             "city": "Faro",            "country": "Portugal",      "iata": "FAO", "icao": "LPFR", "lat": 37.0144,  "lon": -7.9659,   "alt": 24,   "tz": "Europe/Lisbon"},
    {"name": "Funchal Cristiano Ronaldo Intl Airport",   "city": "Funchal",         "country": "Portugal",      "iata": "FNC", "icao": "LPMA", "lat": 32.6979,  "lon": -16.7745,  "alt": 192,  "tz": "Atlantic/Madeira"},
    {"name": "Turin Caselle Airport",                    "city": "Turin",           "country": "Italy",         "iata": "TRN", "icao": "LIMF", "lat": 45.2008,  "lon": 7.6497,    "alt": 989,  "tz": "Europe/Rome"},
    {"name": "Bologna Guglielmo Marconi Airport",        "city": "Bologna",         "country": "Italy",         "iata": "BLQ", "icao": "LIPE", "lat": 44.5354,  "lon": 11.2887,   "alt": 123,  "tz": "Europe/Rome"},
    {"name": "Florence Amerigo Vespucci Airport",        "city": "Florence",        "country": "Italy",         "iata": "FLR", "icao": "LIRQ", "lat": 43.8100,  "lon": 11.2051,   "alt": 142,  "tz": "Europe/Rome"},
    {"name": "Catania Fontanarossa Airport",             "city": "Catania",         "country": "Italy",         "iata": "CTA", "icao": "LICC", "lat": 37.4668,  "lon": 15.0664,   "alt": 39,   "tz": "Europe/Rome"},
    {"name": "Palermo Falcone Borsellino Airport",       "city": "Palermo",         "country": "Italy",         "iata": "PMO", "icao": "LICJ", "lat": 38.1796,  "lon": 13.0910,   "alt": 65,   "tz": "Europe/Rome"},
    {"name": "Bari Karol Wojtyla Airport",               "city": "Bari",            "country": "Italy",         "iata": "BRI", "icao": "LIBD", "lat": 41.1389,  "lon": 16.7606,   "alt": 177,  "tz": "Europe/Rome"},
    {"name": "Basel Mulhouse Freiburg Airport",          "city": "Basel",           "country": "Switzerland",   "iata": "BSL", "icao": "LFSB", "lat": 47.5896,  "lon": 7.5299,    "alt": 885,  "tz": "Europe/Zurich"},
    {"name": "Gothenburg Landvetter Airport",            "city": "Gothenburg",      "country": "Sweden",        "iata": "GOT", "icao": "ESGG", "lat": 57.6628,  "lon": 12.2798,   "alt": 506,  "tz": "Europe/Stockholm"},
    {"name": "Malmo Airport",                            "city": "Malmo",           "country": "Sweden",        "iata": "MMX", "icao": "ESMS", "lat": 55.5363,  "lon": 13.3762,   "alt": 70,   "tz": "Europe/Stockholm"},
    {"name": "Bergen Flesland Airport",                  "city": "Bergen",          "country": "Norway",        "iata": "BGO", "icao": "ENBR", "lat": 60.2934,  "lon": 5.2181,    "alt": 170,  "tz": "Europe/Oslo"},
    {"name": "Stavanger Sola Airport",                   "city": "Stavanger",       "country": "Norway",        "iata": "SVG", "icao": "ENZV", "lat": 58.8768,  "lon": 5.6378,    "alt": 29,   "tz": "Europe/Oslo"},
    {"name": "Trondheim Vaernes Airport",                "city": "Trondheim",       "country": "Norway",        "iata": "TRD", "icao": "ENVA", "lat": 63.4578,  "lon": 10.9239,   "alt": 56,   "tz": "Europe/Oslo"},
    {"name": "Amsterdam Eindhoven Airport",              "city": "Eindhoven",       "country": "Netherlands",   "iata": "EIN", "icao": "EHEH", "lat": 51.4501,  "lon": 5.3745,    "alt": 74,   "tz": "Europe/Amsterdam"},
    {"name": "Antwerp International Airport",            "city": "Antwerp",         "country": "Belgium",       "iata": "ANR", "icao": "EBAW", "lat": 51.1894,  "lon": 4.4603,    "alt": 39,   "tz": "Europe/Brussels"},
    {"name": "Birmingham Airport",                       "city": "Birmingham",      "country": "United Kingdom","iata": "BHX", "icao": "EGBB", "lat": 52.4539,  "lon": -1.7480,   "alt": 327,  "tz": "Europe/London"},
    {"name": "Bristol Airport",                          "city": "Bristol",         "country": "United Kingdom","iata": "BRS", "icao": "EGGD", "lat": 51.3827,  "lon": -2.7191,   "alt": 622,  "tz": "Europe/London"},
    {"name": "Glasgow Airport",                          "city": "Glasgow",         "country": "United Kingdom","iata": "GLA", "icao": "EGPF", "lat": 55.8642,  "lon": -4.4331,   "alt": 26,   "tz": "Europe/London"},
    {"name": "Belfast International Airport",            "city": "Belfast",         "country": "United Kingdom","iata": "BFS", "icao": "EGAA", "lat": 54.6575,  "lon": -6.2158,   "alt": 268,  "tz": "Europe/London"},
    {"name": "Newcastle Airport",                        "city": "Newcastle",       "country": "United Kingdom","iata": "NCL", "icao": "EGNT", "lat": 54.9875,  "lon": -1.6917,   "alt": 266,  "tz": "Europe/London"},
    {"name": "Leeds Bradford Airport",                   "city": "Leeds",           "country": "United Kingdom","iata": "LBA", "icao": "EGNM", "lat": 53.8659,  "lon": -1.6606,   "alt": 681,  "tz": "Europe/London"},
    {"name": "Luton Airport",                            "city": "London",          "country": "United Kingdom","iata": "LTN", "icao": "EGGW", "lat": 51.8747,  "lon": -0.3683,   "alt": 526,  "tz": "Europe/London"},
    {"name": "Stansted Airport",                         "city": "London",          "country": "United Kingdom","iata": "STN", "icao": "EGSS", "lat": 51.8850,  "lon": 0.2350,    "alt": 348,  "tz": "Europe/London"},
    {"name": "Innsbruck Airport",                        "city": "Innsbruck",       "country": "Austria",       "iata": "INN", "icao": "LOWI", "lat": 47.2602,  "lon": 11.3440,   "alt": 1906, "tz": "Europe/Vienna"},
    {"name": "Salzburg Airport",                         "city": "Salzburg",        "country": "Austria",       "iata": "SZG", "icao": "LOWS", "lat": 47.7933,  "lon": 13.0043,   "alt": 1411, "tz": "Europe/Vienna"},
    {"name": "Krakow John Paul II International Airport","city": "Krakow",          "country": "Poland",        "iata": "KRK", "icao": "EPKK", "lat": 50.0777,  "lon": 19.7848,   "alt": 791,  "tz": "Europe/Warsaw"},
    {"name": "Gdansk Lech Walesa Airport",               "city": "Gdansk",          "country": "Poland",        "iata": "GDN", "icao": "EPGD", "lat": 54.3776,  "lon": 18.4662,   "alt": 489,  "tz": "Europe/Warsaw"},
    {"name": "Wroclaw Copernicus Airport",               "city": "Wroclaw",         "country": "Poland",        "iata": "WRO", "icao": "EPWR", "lat": 51.1027,  "lon": 16.8858,   "alt": 404,  "tz": "Europe/Warsaw"},
    {"name": "Katowice International Airport",           "city": "Katowice",        "country": "Poland",        "iata": "KTW", "icao": "EPKT", "lat": 50.4744,  "lon": 19.0800,   "alt": 995,  "tz": "Europe/Warsaw"},
    {"name": "Bratislava MR Stefanik Airport",           "city": "Bratislava",      "country": "Slovakia",      "iata": "BTS", "icao": "LZIB", "lat": 48.1702,  "lon": 17.2127,   "alt": 436,  "tz": "Europe/Bratislava"},
    {"name": "Ljubljana Joze Pucnik Airport",            "city": "Ljubljana",       "country": "Slovenia",      "iata": "LJU", "icao": "LJLJ", "lat": 46.2237,  "lon": 14.4576,   "alt": 1273, "tz": "Europe/Ljubljana"},
    {"name": "Sarajevo International Airport",           "city": "Sarajevo",        "country": "Bosnia",        "iata": "SJJ", "icao": "LQSA", "lat": 43.8246,  "lon": 18.3315,   "alt": 1708, "tz": "Europe/Sarajevo"},
    {"name": "Skopje Alexander the Great Airport",       "city": "Skopje",          "country": "N. Macedonia",  "iata": "SKP", "icao": "LWSK", "lat": 41.9616,  "lon": 21.6214,   "alt": 781,  "tz": "Europe/Skopje"},
    {"name": "Tirana Nene Tereza International Airport", "city": "Tirana",          "country": "Albania",       "iata": "TIA", "icao": "LATI", "lat": 41.4147,  "lon": 19.7206,   "alt": 126,  "tz": "Europe/Tirane"},
    {"name": "Podgorica Golubovci Airport",              "city": "Podgorica",       "country": "Montenegro",    "iata": "TGD", "icao": "LYPG", "lat": 42.3594,  "lon": 19.2519,   "alt": 141,  "tz": "Europe/Podgorica"},

    # ── Russia expanded (4 more) ──────────────────────────────────────────────
    {"name": "Novosibirsk Tolmachevo Airport",           "city": "Novosibirsk",     "country": "Russia",        "iata": "OVB", "icao": "UNNT", "lat": 55.0126,  "lon": 82.6507,   "alt": 365,  "tz": "Asia/Novosibirsk"},
    {"name": "Yekaterinburg Koltsovo Airport",           "city": "Yekaterinburg",   "country": "Russia",        "iata": "SVX", "icao": "USSS", "lat": 56.7431,  "lon": 60.8027,   "alt": 764,  "tz": "Asia/Yekaterinburg"},
    {"name": "Krasnoyarsk Yemelyanovo Airport",          "city": "Krasnoyarsk",     "country": "Russia",        "iata": "KJA", "icao": "UNKL", "lat": 56.1730,  "lon": 92.4933,   "alt": 942,  "tz": "Asia/Krasnoyarsk"},
    {"name": "Vladivostok International Airport",        "city": "Vladivostok",     "country": "Russia",        "iata": "VVO", "icao": "UHWW", "lat": 43.3990,  "lon": 132.1480,  "alt": 46,   "tz": "Asia/Vladivostok"},

    # ── Middle East expanded (5 more) ─────────────────────────────────────────
    {"name": "Baghdad International Airport",            "city": "Baghdad",         "country": "Iraq",          "iata": "BGW", "icao": "ORBI", "lat": 33.2626,  "lon": 44.2346,   "alt": 114,  "tz": "Asia/Baghdad"},
    {"name": "Beirut Rafic Hariri International Airport","city": "Beirut",          "country": "Lebanon",       "iata": "BEY", "icao": "OLBA", "lat": 33.8209,  "lon": 35.4884,   "alt": 87,   "tz": "Asia/Beirut"},
    {"name": "Tehran Imam Khomeini International Airport","city": "Tehran",         "country": "Iran",          "iata": "IKA", "icao": "OIIE", "lat": 35.4161,  "lon": 51.1522,   "alt": 3305, "tz": "Asia/Tehran"},
    {"name": "Mashhad Shahid Hasheminejad Airport",      "city": "Mashhad",         "country": "Iran",          "iata": "MHD", "icao": "OIMM", "lat": 36.2352,  "lon": 59.6400,   "alt": 3263, "tz": "Asia/Tehran"},

    # ── Africa expanded (15 more) ─────────────────────────────────────────────
    {"name": "Hurghada International Airport",           "city": "Hurghada",        "country": "Egypt",         "iata": "HRG", "icao": "HEGN", "lat": 27.1783,  "lon": 33.7994,   "alt": 52,   "tz": "Africa/Cairo"},
    {"name": "Sharm el-Sheikh International Airport",    "city": "Sharm el-Sheikh", "country": "Egypt",         "iata": "SSH", "icao": "HESH", "lat": 27.9773,  "lon": 34.3950,   "alt": 143,  "tz": "Africa/Cairo"},
    {"name": "Luxor International Airport",              "city": "Luxor",           "country": "Egypt",         "iata": "LXR", "icao": "HELX", "lat": 25.6710,  "lon": 32.7066,   "alt": 294,  "tz": "Africa/Cairo"},
    {"name": "Tripoli Mitiga International Airport",     "city": "Tripoli",         "country": "Libya",         "iata": "MJI", "icao": "HLLM", "lat": 32.8941,  "lon": 13.2760,   "alt": 36,   "tz": "Africa/Tripoli"},
    {"name": "Khartoum Intl Airport",                    "city": "Khartoum",        "country": "Sudan",         "iata": "KRT", "icao": "HSSS", "lat": 15.5895,  "lon": 32.5532,   "alt": 1265, "tz": "Africa/Khartoum"},
    {"name": "Abuja Nnamdi Azikiwe International Airport","city": "Abuja",          "country": "Nigeria",       "iata": "ABV", "icao": "DNAA", "lat": 9.0068,   "lon": 7.2632,    "alt": 1123, "tz": "Africa/Lagos"},
    {"name": "Kano Mallam Aminu Intl Airport",           "city": "Kano",            "country": "Nigeria",       "iata": "KAN", "icao": "DNKN", "lat": 12.0476,  "lon": 8.5246,    "alt": 1562, "tz": "Africa/Lagos"},
    {"name": "Bamako Senou International Airport",       "city": "Bamako",          "country": "Mali",          "iata": "BKO", "icao": "GABS", "lat": 12.5335,  "lon": -7.9499,   "alt": 1247, "tz": "Africa/Bamako"},
    {"name": "Douala International Airport",             "city": "Douala",          "country": "Cameroon",      "iata": "DLA", "icao": "FKKD", "lat": 4.0061,   "lon": 9.7195,    "alt": 33,   "tz": "Africa/Douala"},
    {"name": "Libreville Leon MBA International Airport","city": "Libreville",      "country": "Gabon",         "iata": "LBV", "icao": "FOOL", "lat": 0.4586,   "lon": 9.4123,    "alt": 39,   "tz": "Africa/Libreville"},
    {"name": "Kinshasa N'Djili International Airport",   "city": "Kinshasa",        "country": "DR Congo",      "iata": "FIH", "icao": "FZAA", "lat": -4.3858,  "lon": 15.4446,   "alt": 1027, "tz": "Africa/Kinshasa"},
    {"name": "Luanda Quatro de Fevereiro Airport",       "city": "Luanda",          "country": "Angola",        "iata": "LAD", "icao": "FNLU", "lat": -8.8584,  "lon": 13.2312,   "alt": 243,  "tz": "Africa/Luanda"},
    {"name": "Maputo International Airport",             "city": "Maputo",          "country": "Mozambique",    "iata": "MPM", "icao": "FQMA", "lat": -25.9208, "lon": 32.5726,   "alt": 145,  "tz": "Africa/Maputo"},
    {"name": "Antananarivo Ivato Airport",               "city": "Antananarivo",    "country": "Madagascar",    "iata": "TNR", "icao": "FMMI", "lat": -18.7969, "lon": 47.4788,   "alt": 4198, "tz": "Indian/Antananarivo"},

    # ── South & Central Asia expanded (12 more) ───────────────────────────────
    {"name": "Dhaka Hazrat Shahjalal International",     "city": "Dhaka",           "country": "Bangladesh",    "iata": "DAC", "icao": "VGHS", "lat": 23.8433,  "lon": 90.3979,   "alt": 30,   "tz": "Asia/Dhaka"},
    {"name": "Karachi Jinnah International Airport",     "city": "Karachi",         "country": "Pakistan",      "iata": "KHI", "icao": "OPKC", "lat": 24.9065,  "lon": 67.1608,   "alt": 100,  "tz": "Asia/Karachi"},
    {"name": "Lahore Allama Iqbal International Airport","city": "Lahore",          "country": "Pakistan",      "iata": "LHE", "icao": "OPLA", "lat": 31.5216,  "lon": 74.4036,   "alt": 712,  "tz": "Asia/Karachi"},
    {"name": "Islamabad New International Airport",      "city": "Islamabad",       "country": "Pakistan",      "iata": "ISB", "icao": "OPIS", "lat": 33.5491,  "lon": 72.8558,   "alt": 1668, "tz": "Asia/Karachi"},
    {"name": "Kabul International Airport",              "city": "Kabul",           "country": "Afghanistan",   "iata": "KBL", "icao": "OAKB", "lat": 34.5659,  "lon": 69.2123,   "alt": 5877, "tz": "Asia/Kabul"},
    {"name": "Tashkent Islam Karimov International",     "city": "Tashkent",        "country": "Uzbekistan",    "iata": "TAS", "icao": "UTTT", "lat": 41.2579,  "lon": 69.2811,   "alt": 1417, "tz": "Asia/Tashkent"},
    {"name": "Tbilisi Shota Rustaveli Intl Airport",     "city": "Tbilisi",         "country": "Georgia",       "iata": "TBS", "icao": "UGTB", "lat": 41.6692,  "lon": 44.9547,   "alt": 1467, "tz": "Asia/Tbilisi"},
    {"name": "Yerevan Zvartnots International Airport",  "city": "Yerevan",         "country": "Armenia",       "iata": "EVN", "icao": "UDYZ", "lat": 40.1473,  "lon": 44.3959,   "alt": 2838, "tz": "Asia/Yerevan"},
    {"name": "Baku Heydar Aliyev International Airport", "city": "Baku",            "country": "Azerbaijan",    "iata": "GYD", "icao": "UBBB", "lat": 40.4675,  "lon": 50.0467,   "alt": -3,   "tz": "Asia/Baku"},
    {"name": "Ashgabat International Airport",           "city": "Ashgabat",        "country": "Turkmenistan",  "iata": "ASB", "icao": "UTAA", "lat": 37.9868,  "lon": 58.3610,   "alt": 692,  "tz": "Asia/Ashgabat"},
    {"name": "Bishkek Manas International Airport",      "city": "Bishkek",         "country": "Kyrgyzstan",    "iata": "FRU", "icao": "UAFM", "lat": 43.0613,  "lon": 74.4776,   "alt": 2058, "tz": "Asia/Bishkek"},
    {"name": "Dushanbe International Airport",           "city": "Dushanbe",        "country": "Tajikistan",    "iata": "DYU", "icao": "UTDD", "lat": 38.5433,  "lon": 68.7750,   "alt": 2575, "tz": "Asia/Dushanbe"},

    # ── East & Southeast Asia expanded (20 more) ──────────────────────────────
    {"name": "Wuhan Tianhe International Airport",       "city": "Wuhan",           "country": "China",         "iata": "WUH", "icao": "ZHHH", "lat": 30.7838,  "lon": 114.2081,  "alt": 113,  "tz": "Asia/Shanghai"},
    {"name": "Xian Xianyang International Airport",      "city": "Xian",            "country": "China",         "iata": "XIY", "icao": "ZLXY", "lat": 34.4471,  "lon": 108.7516,  "alt": 1572, "tz": "Asia/Shanghai"},
    {"name": "Chongqing Jiangbei International Airport", "city": "Chongqing",       "country": "China",         "iata": "CKG", "icao": "ZUCK", "lat": 29.7192,  "lon": 106.6417,  "alt": 1365, "tz": "Asia/Shanghai"},
    {"name": "Hangzhou Xiaoshan International Airport",  "city": "Hangzhou",        "country": "China",         "iata": "HGH", "icao": "ZSHC", "lat": 30.2295,  "lon": 120.4344,  "alt": 23,   "tz": "Asia/Shanghai"},
    {"name": "Nanjing Lukou International Airport",      "city": "Nanjing",         "country": "China",         "iata": "NKG", "icao": "ZSNJ", "lat": 31.7420,  "lon": 118.8620,  "alt": 49,   "tz": "Asia/Shanghai"},
    {"name": "Qingdao Jiaodong International Airport",   "city": "Qingdao",         "country": "China",         "iata": "TAO", "icao": "ZSQD", "lat": 36.3621,  "lon": 120.3741,  "alt": 33,   "tz": "Asia/Shanghai"},
    {"name": "Shenyang Taoxian International Airport",   "city": "Shenyang",        "country": "China",         "iata": "SHE", "icao": "ZYTX", "lat": 41.6398,  "lon": 123.4829,  "alt": 198,  "tz": "Asia/Shanghai"},
    {"name": "Urumqi Diwopu International Airport",      "city": "Urumqi",          "country": "China",         "iata": "URC", "icao": "ZWWW", "lat": 43.9071,  "lon": 87.4742,   "alt": 2125, "tz": "Asia/Urumqi"},
    {"name": "Macau International Airport",              "city": "Macau",           "country": "China",         "iata": "MFM", "icao": "VMMC", "lat": 22.1496,  "lon": 113.5916,  "alt": 20,   "tz": "Asia/Macau"},
    {"name": "Jeju International Airport",               "city": "Jeju",            "country": "South Korea",   "iata": "CJU", "icao": "RKPC", "lat": 33.5113,  "lon": 126.4929,  "alt": 118,  "tz": "Asia/Seoul"},
    {"name": "Busan Gimhae International Airport",       "city": "Busan",           "country": "South Korea",   "iata": "PUS", "icao": "RKPK", "lat": 35.1795,  "lon": 128.9382,  "alt": 6,    "tz": "Asia/Seoul"},
    {"name": "Ulaanbaatar Chinggis Khaan Intl Airport",  "city": "Ulaanbaatar",     "country": "Mongolia",      "iata": "ULN", "icao": "ZMUB", "lat": 47.8431,  "lon": 106.7664,  "alt": 4364, "tz": "Asia/Ulaanbaatar"},
    {"name": "Phuket International Airport",             "city": "Phuket",          "country": "Thailand",      "iata": "HKT", "icao": "VTSP", "lat": 8.1132,   "lon": 98.3169,   "alt": 82,   "tz": "Asia/Bangkok"},
    {"name": "Chiang Mai International Airport",         "city": "Chiang Mai",      "country": "Thailand",      "iata": "CNX", "icao": "VTCC", "lat": 18.7668,  "lon": 98.9626,   "alt": 1036, "tz": "Asia/Bangkok"},
    {"name": "Kota Kinabalu International Airport",      "city": "Kota Kinabalu",   "country": "Malaysia",      "iata": "BKI", "icao": "WBKK", "lat": 5.9372,   "lon": 116.0508,  "alt": 10,   "tz": "Asia/Kuala_Lumpur"},
    {"name": "Penang International Airport",             "city": "Penang",          "country": "Malaysia",      "iata": "PEN", "icao": "WMKP", "lat": 5.2977,   "lon": 100.2769,  "alt": 11,   "tz": "Asia/Kuala_Lumpur"},
    {"name": "Surabaya Juanda International Airport",    "city": "Surabaya",        "country": "Indonesia",     "iata": "SUB", "icao": "WARR", "lat": -7.3798,  "lon": 112.7869,  "alt": 9,    "tz": "Asia/Jakarta"},
    {"name": "Medan Kualanamu International Airport",    "city": "Medan",           "country": "Indonesia",     "iata": "KNO", "icao": "WIMM", "lat": 3.6422,   "lon": 98.8853, "alt": 23,   "tz": "Asia/Jakarta"},
    {"name": "Da Nang International Airport",            "city": "Da Nang",         "country": "Vietnam",       "iata": "DAD", "icao": "VVDN", "lat": 16.0439,  "lon": 108.1993,  "alt": 33,   "tz": "Asia/Ho_Chi_Minh"},

    # ── Pacific & Oceania expanded (6 more) ───────────────────────────────────
    {"name": "Nadi International Airport",               "city": "Nadi",            "country": "Fiji",          "iata": "NAN", "icao": "NFFN", "lat": -17.7554, "lon": 177.4431,  "alt": 59,   "tz": "Pacific/Fiji"},
    {"name": "Port Moresby Jacksons International",      "city": "Port Moresby",    "country": "Papua New Guinea","iata": "POM","icao": "AYPY", "lat": -9.4432,  "lon": 147.2200,  "alt": 146,  "tz": "Pacific/Port_Moresby"},
    {"name": "Noumea La Tontouta International Airport", "city": "Noumea",          "country": "New Caledonia",  "iata": "NOU", "icao": "NWWW", "lat": -22.0146, "lon": 166.2130,  "alt": 52,   "tz": "Pacific/Noumea"},
    {"name": "Papeete Tahiti Faaa International Airport","city": "Papeete",         "country": "French Polynesia","iata": "PPT","icao": "NTAA", "lat": -17.5534, "lon": -149.6064, "alt": 5,    "tz": "Pacific/Tahiti"},
    # ── More United States (20) ───────────────────────────────────────────────
    {"name": "Wilmington Airport",                       "city": "Wilmington",      "country": "United States", "iata": "ILM", "icao": "KILM", "lat": 34.2706,  "lon": -77.9026,  "alt": 32,   "tz": "America/New_York"},
    {"name": "Myrtle Beach International Airport",       "city": "Myrtle Beach",    "country": "United States", "iata": "MYR", "icao": "KMYR", "lat": 33.6797,  "lon": -78.9284,  "alt": 25,   "tz": "America/New_York"},
    {"name": "Greenville-Spartanburg Intl Airport",      "city": "Greenville",      "country": "United States", "iata": "GSP", "icao": "KGSP", "lat": 34.8957,  "lon": -82.2189,  "alt": 964,  "tz": "America/New_York"},
    {"name": "Knoxville McGhee Tyson Airport",           "city": "Knoxville",       "country": "United States", "iata": "TYS", "icao": "KTYS", "lat": 35.8110,  "lon": -83.9940,  "alt": 981,  "tz": "America/New_York"},
    {"name": "Lexington Blue Grass Airport",             "city": "Lexington",       "country": "United States", "iata": "LEX", "icao": "KLEX", "lat": 38.0365,  "lon": -84.6059,  "alt": 979,  "tz": "America/New_York"},
    {"name": "Huntsville International Airport",         "city": "Huntsville",      "country": "United States", "iata": "HSV", "icao": "KHSV", "lat": 34.6372,  "lon": -86.7751,  "alt": 629,  "tz": "America/Chicago"},
    {"name": "Pensacola International Airport",          "city": "Pensacola",       "country": "United States", "iata": "PNS", "icao": "KPNS", "lat": 30.4734,  "lon": -87.1866,  "alt": 121,  "tz": "America/Chicago"},
    {"name": "Tallahassee International Airport",        "city": "Tallahassee",     "country": "United States", "iata": "TLH", "icao": "KTLH", "lat": 30.3965,  "lon": -84.3503,  "alt": 81,   "tz": "America/New_York"},
    {"name": "Southwest Florida International Airport",  "city": "Fort Myers",      "country": "United States", "iata": "RSW", "icao": "KRSW", "lat": 26.5362,  "lon": -81.7552,  "alt": 30,   "tz": "America/New_York"},
    {"name": "Sarasota Bradenton International Airport", "city": "Sarasota",        "country": "United States", "iata": "SRQ", "icao": "KSRQ", "lat": 27.3954,  "lon": -82.5544,  "alt": 30,   "tz": "America/New_York"},
    {"name": "Harrisburg International Airport",         "city": "Harrisburg",      "country": "United States", "iata": "MDT", "icao": "KMDT", "lat": 40.1935,  "lon": -76.7634,  "alt": 310,  "tz": "America/New_York"},
    {"name": "Providence T.F. Green International",      "city": "Providence",      "country": "United States", "iata": "PVD", "icao": "KPVD", "lat": 41.7244,  "lon": -71.4282,  "alt": 55,   "tz": "America/New_York"},
    {"name": "Burlington International Airport",         "city": "Burlington",      "country": "United States", "iata": "BTV", "icao": "KBTV", "lat": 44.4720,  "lon": -73.1533,  "alt": 335,  "tz": "America/New_York"},
    {"name": "Portland International Jetport",           "city": "Portland",        "country": "United States", "iata": "PWM", "icao": "KPWM", "lat": 43.6462,  "lon": -70.3093,  "alt": 76,   "tz": "America/New_York"},
    {"name": "Manchester Boston Regional Airport",       "city": "Manchester",      "country": "United States", "iata": "MHT", "icao": "KMHT", "lat": 42.9326,  "lon": -71.4357,  "alt": 266,  "tz": "America/New_York"},
    {"name": "Lubbock Preston Smith International",      "city": "Lubbock",         "country": "United States", "iata": "LBB", "icao": "KLBB", "lat": 33.6636,  "lon": -101.8228, "alt": 3282, "tz": "America/Chicago"},
    {"name": "Amarillo Rick Husband Intl Airport",       "city": "Amarillo",        "country": "United States", "iata": "AMA", "icao": "KAMA", "lat": 35.2194,  "lon": -101.7059, "alt": 3607, "tz": "America/Chicago"},
    {"name": "Midland International Air and Space Port", "city": "Midland",         "country": "United States", "iata": "MAF", "icao": "KMAF", "lat": 31.9425,  "lon": -102.2019, "alt": 2871, "tz": "America/Chicago"},
    {"name": "San Antonio International Airport",        "city": "San Antonio",     "country": "United States", "iata": "SAT", "icao": "KSAT", "lat": 29.5337,  "lon": -98.4698,  "alt": 809,  "tz": "America/Chicago"},
    {"name": "Corpus Christi International Airport",     "city": "Corpus Christi",  "country": "United States", "iata": "CRP", "icao": "KCRP", "lat": 27.7704,  "lon": -97.5012,  "alt": 44,   "tz": "America/Chicago"},
    # ── More Europe (30) ──────────────────────────────────────────────────────
    {"name": "Dusseldorf Weeze Airport",                 "city": "Weeze",           "country": "Germany",       "iata": "NRN", "icao": "EDLV", "lat": 51.6024,  "lon": 6.1422,    "alt": 106,  "tz": "Europe/Berlin"},
    {"name": "Paderborn Lippstadt Airport",              "city": "Paderborn",       "country": "Germany",       "iata": "PAD", "icao": "EDLP", "lat": 51.6141,  "lon": 8.6163,    "alt": 699,  "tz": "Europe/Berlin"},
    {"name": "Erfurt Weimar Airport",                    "city": "Erfurt",          "country": "Germany",       "iata": "ERF", "icao": "EDDE", "lat": 50.9798,  "lon": 10.9581,   "alt": 1036, "tz": "Europe/Berlin"},
    {"name": "Graz Airport",                             "city": "Graz",            "country": "Austria",       "iata": "GRZ", "icao": "LOWG", "lat": 46.9911,  "lon": 15.4396,   "alt": 1115, "tz": "Europe/Vienna"},
    {"name": "Linz Airport",                             "city": "Linz",            "country": "Austria",       "iata": "LNZ", "icao": "LOWL", "lat": 48.2332,  "lon": 14.1875,   "alt": 978,  "tz": "Europe/Vienna"},
    {"name": "Bern Airport",                             "city": "Bern",            "country": "Switzerland",   "iata": "BRN", "icao": "LSZB", "lat": 46.9141,  "lon": 7.4971,    "alt": 1674, "tz": "Europe/Zurich"},
    {"name": "Alghero Fertilia Airport",                 "city": "Alghero",         "country": "Italy",         "iata": "AHO", "icao": "LIEA", "lat": 40.6321,  "lon": 8.2908,    "alt": 87,   "tz": "Europe/Rome"},
    {"name": "Cagliari Elmas Airport",                   "city": "Cagliari",        "country": "Italy",         "iata": "CAG", "icao": "LIEE", "lat": 39.2515,  "lon": 9.0543,    "alt": 13,   "tz": "Europe/Rome"},
    {"name": "Brindisi Papola Casale Airport",           "city": "Brindisi",        "country": "Italy",         "iata": "BDS", "icao": "LIBR", "lat": 40.6576,  "lon": 17.9470,   "alt": 47,   "tz": "Europe/Rome"},
    {"name": "Pisa Galileo Galilei Airport",             "city": "Pisa",            "country": "Italy",         "iata": "PSA", "icao": "LIRP", "lat": 43.6839,  "lon": 10.3927,   "alt": 6,    "tz": "Europe/Rome"},
    {"name": "Verona Villafranca Airport",               "city": "Verona",          "country": "Italy",         "iata": "VRN", "icao": "LIPX", "lat": 45.3957,  "lon": 10.8885,   "alt": 239,  "tz": "Europe/Rome"},
    {"name": "Trieste Ronchi dei Legionari Airport",     "city": "Trieste",         "country": "Italy",         "iata": "TRS", "icao": "LIPQ", "lat": 45.8275,  "lon": 13.4722,   "alt": 39,   "tz": "Europe/Rome"},
    {"name": "Ibiza Airport",                            "city": "Ibiza",           "country": "Spain",         "iata": "IBZ", "icao": "LEIB", "lat": 38.8729,  "lon": 1.3731,    "alt": 24,   "tz": "Europe/Madrid"},
    {"name": "Menorca Airport",                          "city": "Menorca",         "country": "Spain",         "iata": "MAH", "icao": "LEMH", "lat": 39.8626,  "lon": 4.2186,    "alt": 302,  "tz": "Europe/Madrid"},
    {"name": "Santander Airport",                        "city": "Santander",       "country": "Spain",         "iata": "SDR", "icao": "LEXJ", "lat": 43.4271,  "lon": -3.8200,   "alt": 16,   "tz": "Europe/Madrid"},
    {"name": "Zaragoza Airport",                         "city": "Zaragoza",        "country": "Spain",         "iata": "ZAZ", "icao": "LEZG", "lat": 41.6662,  "lon": -1.0415,   "alt": 863,  "tz": "Europe/Madrid"},
    {"name": "Chania International Airport",             "city": "Chania",          "country": "Greece",        "iata": "CHQ", "icao": "LGSA", "lat": 35.5317,  "lon": 24.1497,   "alt": 490,  "tz": "Europe/Athens"},
    {"name": "Rhodes Diagoras Airport",                  "city": "Rhodes",          "country": "Greece",        "iata": "RHO", "icao": "LGRP", "lat": 36.4054,  "lon": 28.0862,   "alt": 17,   "tz": "Europe/Athens"},
    {"name": "Corfu Ioannis Kapodistrias Airport",       "city": "Corfu",           "country": "Greece",        "iata": "CFU", "icao": "LGKR", "lat": 39.6019,  "lon": 19.9117,   "alt": 6,    "tz": "Europe/Athens"},
    {"name": "Heraklion Nikos Kazantzakis Airport",      "city": "Heraklion",       "country": "Greece",        "iata": "HER", "icao": "LGIR", "lat": 35.3397,  "lon": 25.1803,   "alt": 115,  "tz": "Europe/Athens"},
    {"name": "Minsk National Airport",                   "city": "Minsk",           "country": "Belarus",       "iata": "MSQ", "icao": "UMMS", "lat": 53.8825,  "lon": 28.0325,   "alt": 670,  "tz": "Europe/Minsk"},
    {"name": "Chisinau International Airport",           "city": "Chisinau",        "country": "Moldova",       "iata": "KIV", "icao": "LUKK", "lat": 46.9277,  "lon": 28.9310,   "alt": 399,  "tz": "Europe/Chisinau"},
    {"name": "Palanga International Airport",            "city": "Palanga",         "country": "Lithuania",     "iata": "PLQ", "icao": "EYPA", "lat": 55.9733,  "lon": 21.0939,   "alt": 33,   "tz": "Europe/Vilnius"},
    {"name": "Paphos International Airport",             "city": "Paphos",          "country": "Cyprus",        "iata": "PFO", "icao": "LCPH", "lat": 34.7180,  "lon": 32.4857,   "alt": 41,   "tz": "Asia/Nicosia"},
    {"name": "Larnaca International Airport",            "city": "Larnaca",         "country": "Cyprus",        "iata": "LCA", "icao": "LCLK", "lat": 34.8751,  "lon": 33.6249,   "alt": 8,    "tz": "Asia/Nicosia"},
    {"name": "Valletta Malta International Airport",     "city": "Valletta",        "country": "Malta",         "iata": "MLA", "icao": "LMML", "lat": 35.8575,  "lon": 14.4775,   "alt": 300,  "tz": "Europe/Malta"},
    {"name": "Antalya Airport",                          "city": "Antalya",         "country": "Turkey",        "iata": "AYT", "icao": "LTAI", "lat": 36.8987,  "lon": 30.8005,   "alt": 177,  "tz": "Europe/Istanbul"},
    # ── More Africa (10) ──────────────────────────────────────────────────────
    {"name": "Nairobi Wilson Airport",                   "city": "Nairobi",         "country": "Kenya",         "iata": "WIL", "icao": "HKNW", "lat": -1.3217,  "lon": 36.8148,   "alt": 5536, "tz": "Africa/Nairobi"},
    {"name": "Mombasa Moi International Airport",        "city": "Mombasa",         "country": "Kenya",         "iata": "MBA", "icao": "HKMO", "lat": -4.0348,  "lon": 39.5942,   "alt": 200,  "tz": "Africa/Nairobi"},
    {"name": "Zanzibar Abeid Amani Karume Airport",      "city": "Zanzibar",        "country": "Tanzania",      "iata": "ZNZ", "icao": "HTZA", "lat": -6.2220,  "lon": 39.2249,   "alt": 54,   "tz": "Africa/Dar_es_Salaam"},
    {"name": "Lusaka Kenneth Kaunda Intl Airport",       "city": "Lusaka",          "country": "Zambia",        "iata": "LUN", "icao": "FLKK", "lat": -15.3308, "lon": 28.4526,   "alt": 3779, "tz": "Africa/Lusaka"},
    {"name": "Harare International Airport",             "city": "Harare",          "country": "Zimbabwe",      "iata": "HRE", "icao": "FVHA", "lat": -17.9318, "lon": 31.0928,   "alt": 4887, "tz": "Africa/Harare"},
    {"name": "Windhoek Hosea Kutako Intl Airport",       "city": "Windhoek",        "country": "Namibia",       "iata": "WDH", "icao": "FYWH", "lat": -22.4799, "lon": 17.4709,   "alt": 5640, "tz": "Africa/Windhoek"},
    {"name": "Gaborone Sir Seretse Khama Intl Airport",  "city": "Gaborone",        "country": "Botswana",      "iata": "GBE", "icao": "FBSK", "lat": -24.5552, "lon": 25.9182,   "alt": 3299, "tz": "Africa/Gaborone"},
    {"name": "Conakry Gbessia International Airport",    "city": "Conakry",         "country": "Guinea",        "iata": "CKY", "icao": "GUCY", "lat": 9.5769,   "lon": -13.6120,  "alt": 72,   "tz": "Africa/Conakry"},
    {"name": "Lome Gnassingbe Eyadema Intl Airport",     "city": "Lome",            "country": "Togo",          "iata": "LFW", "icao": "DXXX", "lat": 6.1656,   "lon": 1.2545,    "alt": 72,   "tz": "Africa/Lome"},
    # ── More Asia & Pacific (32) ──────────────────────────────────────────────
    {"name": "Harbin Taiping International Airport",     "city": "Harbin",          "country": "China",         "iata": "HRB", "icao": "ZYHB", "lat": 45.6235,  "lon": 126.2502,  "alt": 457,  "tz": "Asia/Shanghai"},
    {"name": "Tianjin Binhai International Airport",     "city": "Tianjin",         "country": "China",         "iata": "TSN", "icao": "ZBTJ", "lat": 39.1244,  "lon": 117.3463,  "alt": 10,   "tz": "Asia/Shanghai"},
    {"name": "Dalian Zhoushuizi International Airport",  "city": "Dalian",          "country": "China",         "iata": "DLC", "icao": "ZYTL", "lat": 38.9657,  "lon": 121.5386,  "alt": 107,  "tz": "Asia/Shanghai"},
    {"name": "Xiamen Gaoqi International Airport",       "city": "Xiamen",          "country": "China",         "iata": "XMN", "icao": "ZSAM", "lat": 24.5440,  "lon": 118.1277,  "alt": 59,   "tz": "Asia/Shanghai"},
    {"name": "Zhengzhou Xinzheng International Airport", "city": "Zhengzhou",       "country": "China",         "iata": "CGO", "icao": "ZHCC", "lat": 34.5197,  "lon": 113.8408,  "alt": 495,  "tz": "Asia/Shanghai"},
    {"name": "Changsha Huanghua International Airport",  "city": "Changsha",        "country": "China",         "iata": "CSX", "icao": "ZGHA", "lat": 28.1892,  "lon": 113.2196,  "alt": 217,  "tz": "Asia/Shanghai"},
    {"name": "Nanning Wuxu International Airport",       "city": "Nanning",         "country": "China",         "iata": "NNG", "icao": "ZGNN", "lat": 22.6083,  "lon": 108.1722,  "alt": 421,  "tz": "Asia/Shanghai"},
    {"name": "Haikou Meilan International Airport",      "city": "Haikou",          "country": "China",         "iata": "HAK", "icao": "ZJHK", "lat": 19.9349,  "lon": 110.4590,  "alt": 75,   "tz": "Asia/Shanghai"},
    {"name": "Sanya Phoenix International Airport",      "city": "Sanya",           "country": "China",         "iata": "SYX", "icao": "ZJSY", "lat": 18.3029,  "lon": 109.4122,  "alt": 92,   "tz": "Asia/Shanghai"},
    {"name": "Lhasa Gonggar Airport",                    "city": "Lhasa",           "country": "China",         "iata": "LXA", "icao": "ZULS", "lat": 29.2978,  "lon": 90.9119,   "alt": 11713,"tz": "Asia/Shanghai"},
    {"name": "Sendai Airport",                           "city": "Sendai",          "country": "Japan",         "iata": "SDJ", "icao": "RJSS", "lat": 38.1397,  "lon": 140.9170,  "alt": 15,   "tz": "Asia/Tokyo"},
    {"name": "Okinawa Naha Airport",                     "city": "Okinawa",         "country": "Japan",         "iata": "OKA", "icao": "ROAH", "lat": 26.1958,  "lon": 127.6461,  "alt": 12,   "tz": "Asia/Tokyo"},
    {"name": "Hiroshima Airport",                        "city": "Hiroshima",       "country": "Japan",         "iata": "HIJ", "icao": "RJOA", "lat": 34.4361,  "lon": 132.9194,  "alt": 1088, "tz": "Asia/Tokyo"},
    {"name": "Kagoshima Airport",                        "city": "Kagoshima",       "country": "Japan",         "iata": "KOJ", "icao": "RJFK", "lat": 31.8034,  "lon": 130.7191,  "alt": 906,  "tz": "Asia/Tokyo"},
    {"name": "Taichung Ching Chuang Kang Airport",       "city": "Taichung",        "country": "Taiwan",        "iata": "RMQ", "icao": "RCMQ", "lat": 24.2648,  "lon": 120.6203,  "alt": 663,  "tz": "Asia/Taipei"},
    {"name": "Kaohsiung International Airport",          "city": "Kaohsiung",       "country": "Taiwan",        "iata": "KHH", "icao": "RCKH", "lat": 22.5771,  "lon": 120.3498,  "alt": 31,   "tz": "Asia/Taipei"},
    {"name": "Langkawi International Airport",           "city": "Langkawi",        "country": "Malaysia",      "iata": "LGK", "icao": "WMKL", "lat": 6.3296,   "lon": 99.7287,   "alt": 29,   "tz": "Asia/Kuala_Lumpur"},
    {"name": "Johor Bahru Senai International Airport",  "city": "Johor Bahru",     "country": "Malaysia",      "iata": "JHB", "icao": "WMKJ", "lat": 1.6413,   "lon": 103.6698,  "alt": 135,  "tz": "Asia/Kuala_Lumpur"},
    {"name": "Kochi International Airport",              "city": "Kochi",           "country": "India",         "iata": "COK", "icao": "VOCI", "lat": 10.1520,  "lon": 76.3919,   "alt": 30,   "tz": "Asia/Kolkata"},
    {"name": "Pune Airport",                             "city": "Pune",            "country": "India",         "iata": "PNQ", "icao": "VAPO", "lat": 18.5822,  "lon": 73.9197,   "alt": 1942, "tz": "Asia/Kolkata"},
    {"name": "Ahmedabad Sardar Vallabhbhai Patel Intl",  "city": "Ahmedabad",       "country": "India",         "iata": "AMD", "icao": "VAAH", "lat": 23.0772,  "lon": 72.6347,   "alt": 189,  "tz": "Asia/Kolkata"},
    {"name": "Goa Dabolim International Airport",        "city": "Goa",             "country": "India",         "iata": "GOI", "icao": "VAGO", "lat": 15.3808,  "lon": 73.8314,   "alt": 150,  "tz": "Asia/Kolkata"},
    {"name": "Thiruvananthapuram International Airport", "city": "Thiruvananthapuram","country": "India",        "iata": "TRV", "icao": "VOTV", "lat": 8.4821,   "lon": 76.9201,   "alt": 30,   "tz": "Asia/Kolkata"},
    {"name": "Coimbatore International Airport",         "city": "Coimbatore",      "country": "India",         "iata": "CJB", "icao": "VOCB", "lat": 11.0300,  "lon": 77.0434,   "alt": 1321, "tz": "Asia/Kolkata"},
    {"name": "Colombo Ratmalana Airport",                "city": "Colombo",         "country": "Sri Lanka",     "iata": "RML", "icao": "VCCC", "lat": 6.8219,   "lon": 79.8862,   "alt": 22,   "tz": "Asia/Colombo"},
    {"name": "Male Velana International Airport",        "city": "Male",            "country": "Maldives",      "iata": "MLE", "icao": "VRMM", "lat": 4.1918,   "lon": 73.5290,   "alt": 6,    "tz": "Indian/Maldives"},
    {"name": "Siem Reap Angkor International Airport",   "city": "Siem Reap",       "country": "Cambodia",      "iata": "REP", "icao": "VDSR", "lat": 13.4107,  "lon": 103.8132,  "alt": 60,   "tz": "Asia/Phnom_Penh"},
    # ── Final batch to reach 500 ──────────────────────────────────────────────
    {"name": "Osaka Itami Airport",                      "city": "Osaka",           "country": "Japan",         "iata": "ITM", "icao": "RJOO", "lat": 34.7855,  "lon": 135.4380,  "alt": 40,   "tz": "Asia/Tokyo"},
    {"name": "Kobe Airport",                             "city": "Kobe",            "country": "Japan",         "iata": "UKB", "icao": "RJBE", "lat": 34.6328,  "lon": 135.2239,  "alt": 22,   "tz": "Asia/Tokyo"},
    {"name": "Srinagar Sheikh ul Alam Airport",          "city": "Srinagar",        "country": "India",         "iata": "SXR", "icao": "VISR", "lat": 33.9871,  "lon": 74.7742,   "alt": 5429, "tz": "Asia/Kolkata"},
    {"name": "Varanasi Lal Bahadur Shastri Airport",     "city": "Varanasi",        "country": "India",         "iata": "VNS", "icao": "VIBN", "lat": 25.4524,  "lon": 82.8593,   "alt": 266,  "tz": "Asia/Kolkata"},
    {"name": "Jaipur Sanganer Airport",                  "city": "Jaipur",          "country": "India",         "iata": "JAI", "icao": "VIJP", "lat": 26.8242,  "lon": 75.8122,   "alt": 1263, "tz": "Asia/Kolkata"},
    {"name": "Lucknow Chaudhary Charan Singh Airport",   "city": "Lucknow",         "country": "India",         "iata": "LKO", "icao": "VILK", "lat": 26.7606,  "lon": 80.8893,   "alt": 410,  "tz": "Asia/Kolkata"},
    {"name": "Nagpur Dr. Babasaheb Ambedkar Intl",       "city": "Nagpur",          "country": "India",         "iata": "NAG", "icao": "VANP", "lat": 21.0922,  "lon": 79.0472,   "alt": 1033, "tz": "Asia/Kolkata"},
    {"name": "Brunei International Airport",             "city": "Bandar Seri Begawan","country": "Brunei",     "iata": "BWN", "icao": "WBSB", "lat": 4.9442,   "lon": 114.9283,  "alt": 73,   "tz": "Asia/Brunei"},
    {"name": "Dili Presidente Nicolau Lobato Intl",      "city": "Dili",            "country": "Timor-Leste",   "iata": "DIL", "icao": "WPDL", "lat": -8.5493,  "lon": 125.5247,  "alt": 154,  "tz": "Asia/Dili"},
    {"name": "Honiara Henderson International Airport",  "city": "Honiara",         "country": "Solomon Islands","iata": "HIR","icao": "AGGH", "lat": -9.4280,  "lon": 160.0548,  "alt": 28,   "tz": "Pacific/Guadalcanal"},
    {"name": "Vanuatu Bauerfield International Airport", "city": "Port Vila",       "country": "Vanuatu",       "iata": "VLI", "icao": "NVVV", "lat": -17.6993, "lon": 168.3200,  "alt": 70,   "tz": "Pacific/Efate"},
    {"name": "Apia Faleolo International Airport",       "city": "Apia",            "country": "Samoa",         "iata": "APW", "icao": "NSFA", "lat": -13.8300, "lon": -172.0083, "alt": 58,   "tz": "Pacific/Apia"},
    {"name": "Tonga Fua'amotu International Airport",    "city": "Nukualofa",       "country": "Tonga",         "iata": "TBU", "icao": "NFTF", "lat": -21.2412, "lon": -175.1497, "alt": 126,  "tz": "Pacific/Tongatapu"},
    {"name": "Tarawa Bonriki International Airport",     "city": "South Tarawa",    "country": "Kiribati",      "iata": "TRW", "icao": "NGTA", "lat": 1.3816,   "lon": 173.1422,  "alt": 9,    "tz": "Pacific/Tarawa"},
    {"name": "Ankara Esenboga International Airport",    "city": "Ankara",          "country": "Turkey",        "iata": "ESB", "icao": "LTAC", "lat": 40.1281,  "lon": 32.9951,   "alt": 3125, "tz": "Europe/Istanbul"},
    {"name": "Izmir Adnan Menderes International",       "city": "Izmir",           "country": "Turkey",        "iata": "ADB", "icao": "LTBJ", "lat": 38.2924,  "lon": 27.1570,   "alt": 412,  "tz": "Europe/Istanbul"},
    {"name": "Bodrum Milas International Airport",       "city": "Bodrum",          "country": "Turkey",        "iata": "BJV", "icao": "LTFE", "lat": 37.2506,  "lon": 27.6643,   "alt": 21,   "tz": "Europe/Istanbul"},
    {"name": "Trabzon Airport",                          "city": "Trabzon",         "country": "Turkey",        "iata": "TZX", "icao": "LTCG", "lat": 40.9952,  "lon": 39.7897,   "alt": 104,  "tz": "Europe/Istanbul"},
    {"name": "Astana Nursultan Nazarbayev Intl",         "city": "Astana",          "country": "Kazakhstan",    "iata": "TSE", "icao": "UACC", "lat": 51.0223,  "lon": 71.4669,   "alt": 1165, "tz": "Asia/Almaty"},
    {"name": "Sanaa International Airport",              "city": "Sanaa",           "country": "Yemen",         "iata": "SAH", "icao": "OYSN", "lat": 15.4763,  "lon": 44.2197,   "alt": 7216, "tz": "Asia/Aden"},
    {"name": "Mogadishu Aden Adde International",        "city": "Mogadishu",       "country": "Somalia",       "iata": "MGQ", "icao": "HCMM", "lat": 2.0144,   "lon": 45.3047,   "alt": 29,   "tz": "Africa/Mogadishu"},
    {"name": "Djibouti Ambouli International Airport",   "city": "Djibouti City",   "country": "Djibouti",      "iata": "JIB", "icao": "HDAM", "lat": 11.5473,  "lon": 43.1595,   "alt": 49,   "tz": "Africa/Djibouti"},

    {"name": "Chiang Rai Mae Fah Luang Airport",         "city": "Chiang Rai",      "country": "Thailand",      "iata": "CEI", "icao": "VTCT", "lat": 19.9523,  "lon": 99.8829,   "alt": 1280, "tz": "Asia/Bangkok"},
    {"name": "Hat Yai International Airport",            "city": "Hat Yai",         "country": "Thailand",      "iata": "HDY", "icao": "VTSS", "lat": 6.9332,   "lon": 100.3930,  "alt": 90,   "tz": "Asia/Bangkok"},
    {"name": "Medan Polonia International Airport",      "city": "Medan",           "country": "Indonesia",     "iata": "MES", "icao": "WIMK", "lat": 3.5587,   "lon": 98.6713,   "alt": 114,  "tz": "Asia/Jakarta"},
    {"name": "Palawan Puerto Princesa Airport",          "city": "Puerto Princesa",  "country": "Philippines",  "iata": "PPS", "icao": "RPVP", "lat": 9.7421,   "lon": 118.7590,  "alt": 71,   "tz": "Asia/Manila"},


    {"name": "Groningen Airport Eelde", "city": "Groningen", "country": "Netherlands", "iata": "GRQ", "icao": "EHGG", "lat": 53.1197, "lon": 6.5797, "alt": 17, "tz": "Europe/Amsterdam"},
    {"name": "Kyiv Zhuliany International Airport", "city": "Kyiv", "country": "Ukraine", "iata": "IEV", "icao": "UKKK", "lat": 50.4016, "lon": 30.4497, "alt": 587, "tz": "Europe/Kyiv"},

    {"name": "Juneau International Airport", "city": "Juneau", "country": "United States", "iata": "JNU", "icao": "PAJN", "lat": 58.355, "lon": -134.5763, "alt": 21, "tz": "America/Anchorage"},
    {"name": "Sitka Rocky Gutierrez Airport", "city": "Sitka", "country": "United States", "iata": "SIT", "icao": "PASI", "lat": 57.0471, "lon": -135.3616, "alt": 21, "tz": "America/Anchorage"},
    {"name": "Kodiak Airport", "city": "Kodiak", "country": "United States", "iata": "ADQ", "icao": "PADQ", "lat": 57.75, "lon": -152.4938, "alt": 73, "tz": "America/Anchorage"},
    {"name": "Guam Antonio B. Won Pat Intl Airport", "city": "Hagatna", "country": "United States", "iata": "GUM", "icao": "PGUM", "lat": 13.4834, "lon": 144.7961, "alt": 298, "tz": "Pacific/Guam"},
    {"name": "Saipan International Airport", "city": "Saipan", "country": "United States", "iata": "SPN", "icao": "PGSN", "lat": 15.119, "lon": 145.729, "alt": 215, "tz": "Pacific/Guam"},
    {"name": "Lihue Airport", "city": "Kauai", "country": "United States", "iata": "LIH", "icao": "PHLI", "lat": 21.976, "lon": -159.339, "alt": 153, "tz": "Pacific/Honolulu"},
    {"name": "Hilo International Airport", "city": "Hilo", "country": "United States", "iata": "ITO", "icao": "PHTO", "lat": 19.7214, "lon": -155.0484, "alt": 38, "tz": "Pacific/Honolulu"},
    {"name": "Wichita Falls Municipal Airport", "city": "Wichita Falls", "country": "United States", "iata": "SPS", "icao": "KSPS", "lat": 33.9888, "lon": -98.4919, "alt": 1019, "tz": "America/Chicago"},
    {"name": "Abilene Regional Airport", "city": "Abilene", "country": "United States", "iata": "ABI", "icao": "KABI", "lat": 32.4113, "lon": -99.6819, "alt": 1791, "tz": "America/Chicago"},
    {"name": "Tyler Pounds Regional Airport", "city": "Tyler", "country": "United States", "iata": "TYR", "icao": "KTYR", "lat": 32.3541, "lon": -95.4024, "alt": 544, "tz": "America/Chicago"},
    {"name": "Shreveport Regional Airport", "city": "Shreveport", "country": "United States", "iata": "SHV", "icao": "KSHV", "lat": 32.4466, "lon": -93.8256, "alt": 258, "tz": "America/Chicago"},
    {"name": "Laredo International Airport", "city": "Laredo", "country": "United States", "iata": "LRD", "icao": "KLRD", "lat": 27.5438, "lon": -99.4615, "alt": 508, "tz": "America/Chicago"},
    {"name": "McAllen Miller International Airport", "city": "McAllen", "country": "United States", "iata": "MFE", "icao": "KMFE", "lat": 26.1758, "lon": -98.2385, "alt": 107, "tz": "America/Chicago"},
    {"name": "Brownsville South Padre Island Airport", "city": "Brownsville", "country": "United States", "iata": "BRO", "icao": "KBRO", "lat": 25.9068, "lon": -97.4259, "alt": 22, "tz": "America/Chicago"},
    {"name": "Harlingen Valley International Airport", "city": "Harlingen", "country": "United States", "iata": "HRL", "icao": "KHRL", "lat": 26.2285, "lon": -97.6544, "alt": 36, "tz": "America/Chicago"},
    {"name": "Chattanooga Metropolitan Airport", "city": "Chattanooga", "country": "United States", "iata": "CHA", "icao": "KCHA", "lat": 35.0353, "lon": -85.2038, "alt": 683, "tz": "America/New_York"},
    {"name": "Tri-Cities Regional Airport", "city": "Johnson City", "country": "United States", "iata": "TRI", "icao": "KTRI", "lat": 36.4752, "lon": -82.4074, "alt": 1519, "tz": "America/New_York"},
    {"name": "Asheville Regional Airport", "city": "Asheville", "country": "United States", "iata": "AVL", "icao": "KAVL", "lat": 35.4362, "lon": -82.5418, "alt": 2165, "tz": "America/New_York"},
    {"name": "Fayetteville Regional Airport", "city": "Fayetteville", "country": "United States", "iata": "FAY", "icao": "KFAY", "lat": 34.9912, "lon": -78.8803, "alt": 189, "tz": "America/New_York"},
    {"name": "Florence Regional Airport", "city": "Florence", "country": "United States", "iata": "FLO", "icao": "KFLO", "lat": 34.1853, "lon": -79.7239, "alt": 146, "tz": "America/New_York"},
    {"name": "Columbia Metropolitan Airport", "city": "Columbia", "country": "United States", "iata": "CAE", "icao": "KCAE", "lat": 33.9388, "lon": -81.1195, "alt": 236, "tz": "America/New_York"},
    {"name": "Augusta Regional Airport", "city": "Augusta", "country": "United States", "iata": "AGS", "icao": "KAGS", "lat": 33.3699, "lon": -81.9645, "alt": 144, "tz": "America/New_York"},
    {"name": "Gulfport Biloxi International Airport", "city": "Gulfport", "country": "United States", "iata": "GPT", "icao": "KGPT", "lat": 30.4073, "lon": -89.0701, "alt": 28, "tz": "America/Chicago"},
    {"name": "Mobile Regional Airport", "city": "Mobile", "country": "United States", "iata": "MOB", "icao": "KMOB", "lat": 30.6913, "lon": -88.2428, "alt": 219, "tz": "America/Chicago"},
    {"name": "Gainesville Regional Airport", "city": "Gainesville", "country": "United States", "iata": "GNV", "icao": "KGNV", "lat": 29.69, "lon": -82.2717, "alt": 152, "tz": "America/New_York"},
    {"name": "Daytona Beach International Airport", "city": "Daytona Beach", "country": "United States", "iata": "DAB", "icao": "KDAB", "lat": 29.1799, "lon": -81.0581, "alt": 34, "tz": "America/New_York"},
    {"name": "Palm Beach International Airport", "city": "West Palm Beach", "country": "United States", "iata": "PBI", "icao": "KPBI", "lat": 26.6832, "lon": -80.0956, "alt": 19, "tz": "America/New_York"},
    {"name": "Key West International Airport", "city": "Key West", "country": "United States", "iata": "EYW", "icao": "KEYW", "lat": 24.5561, "lon": -81.7596, "alt": 3, "tz": "America/New_York"},
    {"name": "St. Thomas Cyril E. King Airport", "city": "Charlotte Amalie", "country": "United States", "iata": "STT", "icao": "TIST", "lat": 18.3373, "lon": -64.9733, "alt": 23, "tz": "America/St_Thomas"},
    {"name": "Rapid City Regional Airport", "city": "Rapid City", "country": "United States", "iata": "RAP", "icao": "KRAP", "lat": 44.0453, "lon": -103.0574, "alt": 3204, "tz": "America/Denver"},
    {"name": "Grand Junction Regional Airport", "city": "Grand Junction", "country": "United States", "iata": "GJT", "icao": "KGJT", "lat": 39.1224, "lon": -108.5267, "alt": 4858, "tz": "America/Denver"},
    {"name": "Durango La Plata County Airport", "city": "Durango", "country": "United States", "iata": "DRO", "icao": "KDRO", "lat": 37.1515, "lon": -107.7538, "alt": 6685, "tz": "America/Denver"},
    {"name": "Santa Fe Municipal Airport", "city": "Santa Fe", "country": "United States", "iata": "SAF", "icao": "KSAF", "lat": 35.6171, "lon": -106.0885, "alt": 6348, "tz": "America/Denver"},
    {"name": "Redding Municipal Airport", "city": "Redding", "country": "United States", "iata": "RDD", "icao": "KRDD", "lat": 40.509, "lon": -122.2931, "alt": 505, "tz": "America/Los_Angeles"},
    {"name": "Ponce Mercedita Airport", "city": "Ponce", "country": "Puerto Rico", "iata": "PSE", "icao": "TJPS", "lat": 18.0083, "lon": -66.563, "alt": 29, "tz": "America/Puerto_Rico"},
    {"name": "Monterrey General Mariano Escobedo Intl", "city": "Monterrey", "country": "Mexico", "iata": "MTY", "icao": "MMMY", "lat": 25.7785, "lon": -100.1072, "alt": 1278, "tz": "America/Monterrey"},
    {"name": "Tijuana General Abelardo L Rodriguez Intl", "city": "Tijuana", "country": "Mexico", "iata": "TIJ", "icao": "MMTJ", "lat": 32.5411, "lon": -116.97, "alt": 489, "tz": "America/Tijuana"},
    {"name": "Thunder Bay Airport", "city": "Thunder Bay", "country": "Canada", "iata": "YQT", "icao": "CYQT", "lat": 48.3719, "lon": -89.3239, "alt": 653, "tz": "America/Toronto"},
    {"name": "London Airport Canada", "city": "London", "country": "Canada", "iata": "YXU", "icao": "CYXU", "lat": 43.0356, "lon": -81.1526, "alt": 912, "tz": "America/Toronto"},
    {"name": "Windsor Airport", "city": "Windsor", "country": "Canada", "iata": "YQG", "icao": "CYQG", "lat": 42.2756, "lon": -82.9556, "alt": 622, "tz": "America/Toronto"},
    {"name": "Prince George Airport", "city": "Prince George", "country": "Canada", "iata": "YXS", "icao": "CYXS", "lat": 53.8894, "lon": -122.6791, "alt": 2267, "tz": "America/Vancouver"},
    {"name": "Kamloops Airport", "city": "Kamloops", "country": "Canada", "iata": "YKA", "icao": "CYKA", "lat": 50.7022, "lon": -120.4444, "alt": 1133, "tz": "America/Vancouver"},
    {"name": "Abbotsford International Airport", "city": "Abbotsford", "country": "Canada", "iata": "YXX", "icao": "CYXX", "lat": 49.0253, "lon": -122.3611, "alt": 195, "tz": "America/Vancouver"},
    {"name": "Fort McMurray Airport", "city": "Fort McMurray", "country": "Canada", "iata": "YMM", "icao": "CYMM", "lat": 56.6533, "lon": -111.222, "alt": 1211, "tz": "America/Edmonton"},
    {"name": "Lethbridge Airport", "city": "Lethbridge", "country": "Canada", "iata": "YQL", "icao": "CYQL", "lat": 49.6298, "lon": -112.7998, "alt": 3048, "tz": "America/Edmonton"},
    {"name": "Puerto Vallarta Licenciado Ordaz Intl", "city": "Puerto Vallarta", "country": "Mexico", "iata": "PVR", "icao": "MMPR", "lat": 20.6801, "lon": -105.2544, "alt": 23, "tz": "America/Mexico_City"},
    {"name": "Los Cabos International Airport", "city": "San Jose del Cabo", "country": "Mexico", "iata": "SJD", "icao": "MMSD", "lat": 23.1518, "lon": -109.7211, "alt": 374, "tz": "America/Mazatlan"},
    {"name": "Acapulco International Airport", "city": "Acapulco", "country": "Mexico", "iata": "ACA", "icao": "MMAA", "lat": 16.7571, "lon": -99.754, "alt": 16, "tz": "America/Mexico_City"},
    {"name": "Manaus Eduardo Gomes International Airport", "city": "Manaus", "country": "Brazil", "iata": "MAO", "icao": "SBEG", "lat": -3.0386, "lon": -60.0497, "alt": 264, "tz": "America/Manaus"},
    {"name": "Fortaleza Pinto Martins International", "city": "Fortaleza", "country": "Brazil", "iata": "FOR", "icao": "SBFZ", "lat": -3.7763, "lon": -38.5326, "alt": 82, "tz": "America/Fortaleza"},
    {"name": "Belem Val de Cans International Airport", "city": "Belem", "country": "Brazil", "iata": "BEL", "icao": "SBBE", "lat": -1.3793, "lon": -48.4763, "alt": 54, "tz": "America/Belem"},
    {"name": "Natal Governador Aluizio Alves Intl", "city": "Natal", "country": "Brazil", "iata": "NAT", "icao": "SBSG", "lat": -5.9112, "lon": -35.2497, "alt": 168, "tz": "America/Fortaleza"},
    {"name": "Cartagena Rafael Nunez International", "city": "Cartagena", "country": "Colombia", "iata": "CTG", "icao": "SKCG", "lat": 10.4424, "lon": -75.513, "alt": 4, "tz": "America/Bogota"},
    {"name": "Karlsruhe Baden Airport", "city": "Karlsruhe", "country": "Germany", "iata": "FKB", "icao": "EDSB", "lat": 48.7794, "lon": 8.0805, "alt": 407, "tz": "Europe/Berlin"},
    {"name": "Rostock Laage Airport", "city": "Rostock", "country": "Germany", "iata": "RLG", "icao": "ETNL", "lat": 53.9182, "lon": 12.2783, "alt": 138, "tz": "Europe/Berlin"},
    {"name": "Saarbrucken Airport", "city": "Saarbrucken", "country": "Germany", "iata": "SCN", "icao": "EDDR", "lat": 49.2146, "lon": 7.1095, "alt": 1058, "tz": "Europe/Berlin"},
    {"name": "Friedrichshafen Airport", "city": "Friedrichshafen", "country": "Germany", "iata": "FDH", "icao": "EDNY", "lat": 47.6713, "lon": 9.5115, "alt": 1367, "tz": "Europe/Berlin"},
    {"name": "Klagenfurt Airport", "city": "Klagenfurt", "country": "Austria", "iata": "KLU", "icao": "LOWK", "lat": 46.6425, "lon": 14.3377, "alt": 1470, "tz": "Europe/Vienna"},
    {"name": "Brest Guipavas Airport", "city": "Brest", "country": "France", "iata": "BES", "icao": "LFRB", "lat": 48.4479, "lon": -4.4185, "alt": 325, "tz": "Europe/Paris"},
    {"name": "Montpellier Mediterranee Airport", "city": "Montpellier", "country": "France", "iata": "MPL", "icao": "LFMT", "lat": 43.5763, "lon": 3.963, "alt": 17, "tz": "Europe/Paris"},
    {"name": "Perpignan Rivesaltes Airport", "city": "Perpignan", "country": "France", "iata": "PGF", "icao": "LFMP", "lat": 42.7402, "lon": 2.8707, "alt": 144, "tz": "Europe/Paris"},
    {"name": "Pau Pyrenees Airport", "city": "Pau", "country": "France", "iata": "PUF", "icao": "LFBP", "lat": 43.38, "lon": -0.4186, "alt": 616, "tz": "Europe/Paris"},
    {"name": "Limoges Bellegarde Airport", "city": "Limoges", "country": "France", "iata": "LIG", "icao": "LFBL", "lat": 45.8628, "lon": 1.1794, "alt": 1300, "tz": "Europe/Paris"},
    {"name": "Clermont-Ferrand Auvergne Airport", "city": "Clermont-Ferrand", "country": "France", "iata": "CFE", "icao": "LFLC", "lat": 45.7867, "lon": 3.1692, "alt": 1090, "tz": "Europe/Paris"},
    {"name": "Rennes Saint-Jacques Airport", "city": "Rennes", "country": "France", "iata": "RNS", "icao": "LFRN", "lat": 48.0695, "lon": -1.7348, "alt": 124, "tz": "Europe/Paris"},
    {"name": "Caen Carpiquet Airport", "city": "Caen", "country": "France", "iata": "CFR", "icao": "LFRK", "lat": 49.1733, "lon": -0.45, "alt": 256, "tz": "Europe/Paris"},
    {"name": "Valladolid Airport", "city": "Valladolid", "country": "Spain", "iata": "VLL", "icao": "LEVD", "lat": 41.7061, "lon": -4.8519, "alt": 2776, "tz": "Europe/Madrid"},
    {"name": "Asturias Airport", "city": "Oviedo", "country": "Spain", "iata": "OVD", "icao": "LEAS", "lat": 43.5636, "lon": -6.0346, "alt": 416, "tz": "Europe/Madrid"},
    {"name": "San Sebastian Airport", "city": "San Sebastian", "country": "Spain", "iata": "EAS", "icao": "LESO", "lat": 43.3565, "lon": -1.7906, "alt": 16, "tz": "Europe/Madrid"},
    {"name": "Jerez Airport", "city": "Jerez de la Frontera", "country": "Spain", "iata": "XRY", "icao": "LEJR", "lat": 36.7446, "lon": -6.06, "alt": 93, "tz": "Europe/Madrid"},
    {"name": "Almeria Airport", "city": "Almeria", "country": "Spain", "iata": "LEI", "icao": "LEAM", "lat": 36.8439, "lon": -2.3701, "alt": 70, "tz": "Europe/Madrid"},
    {"name": "Murcia Corvera Airport", "city": "Murcia", "country": "Spain", "iata": "RMU", "icao": "LEMI", "lat": 37.8033, "lon": -1.1253, "alt": 633, "tz": "Europe/Madrid"},
    {"name": "Girona Costa Brava Airport", "city": "Girona", "country": "Spain", "iata": "GRO", "icao": "LEGE", "lat": 41.901, "lon": 2.7605, "alt": 468, "tz": "Europe/Madrid"},
    {"name": "Reus Airport", "city": "Reus", "country": "Spain", "iata": "REU", "icao": "LERS", "lat": 41.1474, "lon": 1.1672, "alt": 233, "tz": "Europe/Madrid"},
    {"name": "Tenerife North Airport", "city": "Tenerife", "country": "Spain", "iata": "TFN", "icao": "GCXO", "lat": 28.4827, "lon": -16.3415, "alt": 2076, "tz": "Atlantic/Canary"},
    {"name": "Fuerteventura Airport", "city": "Fuerteventura", "country": "Spain", "iata": "FUE", "icao": "GCFV", "lat": 28.4527, "lon": -13.8638, "alt": 85, "tz": "Atlantic/Canary"},
    {"name": "Azores Ponta Delgada Airport", "city": "Ponta Delgada", "country": "Portugal", "iata": "PDL", "icao": "LPPD", "lat": 37.7412, "lon": -25.6979, "alt": 259, "tz": "Atlantic/Azores"},
    {"name": "Genoa Cristoforo Colombo Airport", "city": "Genoa", "country": "Italy", "iata": "GOA", "icao": "LIMJ", "lat": 44.4133, "lon": 8.8375, "alt": 13, "tz": "Europe/Rome"},
    {"name": "Pescara International Airport", "city": "Pescara", "country": "Italy", "iata": "PSR", "icao": "LIBP", "lat": 42.4317, "lon": 14.1811, "alt": 48, "tz": "Europe/Rome"},
    {"name": "Lamezia Terme International Airport", "city": "Lamezia Terme", "country": "Italy", "iata": "SUF", "icao": "LICA", "lat": 38.9054, "lon": 16.2423, "alt": 39, "tz": "Europe/Rome"},
    {"name": "Reggio Calabria Airport", "city": "Reggio Calabria", "country": "Italy", "iata": "REG", "icao": "LICR", "lat": 38.0712, "lon": 15.6516, "alt": 96, "tz": "Europe/Rome"},
    {"name": "Ostrava Leos Janacek Airport", "city": "Ostrava", "country": "Czech Republic", "iata": "OSR", "icao": "LKMT", "lat": 49.6963, "lon": 18.1111, "alt": 844, "tz": "Europe/Prague"},
    {"name": "Brno Turany Airport", "city": "Brno", "country": "Czech Republic", "iata": "BRQ", "icao": "LKTB", "lat": 49.1513, "lon": 16.6944, "alt": 778, "tz": "Europe/Prague"},
    {"name": "Debrecen International Airport", "city": "Debrecen", "country": "Hungary", "iata": "DEB", "icao": "LHDC", "lat": 47.4889, "lon": 21.6153, "alt": 359, "tz": "Europe/Budapest"},
    {"name": "Cluj-Napoca International Airport", "city": "Cluj-Napoca", "country": "Romania", "iata": "CLJ", "icao": "LRCL", "lat": 46.7852, "lon": 23.6862, "alt": 1048, "tz": "Europe/Bucharest"},
    {"name": "Timisoara Traian Vuia International Airport", "city": "Timisoara", "country": "Romania", "iata": "TSR", "icao": "LRTR", "lat": 45.8099, "lon": 21.3379, "alt": 348, "tz": "Europe/Bucharest"},
    {"name": "Iasi International Airport", "city": "Iasi", "country": "Romania", "iata": "IAS", "icao": "LRIA", "lat": 47.1785, "lon": 27.6206, "alt": 397, "tz": "Europe/Bucharest"},
    {"name": "Plovdiv International Airport", "city": "Plovdiv", "country": "Bulgaria", "iata": "PDV", "icao": "LBPD", "lat": 42.0678, "lon": 24.8508, "alt": 597, "tz": "Europe/Sofia"},
    {"name": "Varna Airport", "city": "Varna", "country": "Bulgaria", "iata": "VAR", "icao": "LBWN", "lat": 43.2321, "lon": 27.8251, "alt": 230, "tz": "Europe/Sofia"},
    {"name": "Burgas Airport", "city": "Burgas", "country": "Bulgaria", "iata": "BOJ", "icao": "LBBG", "lat": 42.5696, "lon": 27.5152, "alt": 135, "tz": "Europe/Sofia"},
    {"name": "Prishtina Adem Jashari International", "city": "Prishtina", "country": "Kosovo", "iata": "PRN", "icao": "BKPR", "lat": 42.5728, "lon": 21.0358, "alt": 1789, "tz": "Europe/Belgrade"},
    {"name": "Tivat Airport", "city": "Tivat", "country": "Montenegro", "iata": "TIV", "icao": "LYTV", "lat": 42.4047, "lon": 18.7233, "alt": 20, "tz": "Europe/Podgorica"},
    {"name": "Dubrovnik Airport", "city": "Dubrovnik", "country": "Croatia", "iata": "DBV", "icao": "LDDU", "lat": 42.5614, "lon": 18.2682, "alt": 527, "tz": "Europe/Zagreb"},
    {"name": "Split Airport", "city": "Split", "country": "Croatia", "iata": "SPU", "icao": "LDSP", "lat": 43.5389, "lon": 16.298, "alt": 79, "tz": "Europe/Zagreb"},
    {"name": "Zadar Airport", "city": "Zadar", "country": "Croatia", "iata": "ZAD", "icao": "LDZD", "lat": 44.1083, "lon": 15.3467, "alt": 289, "tz": "Europe/Zagreb"},
    {"name": "Ohrid St Paul the Apostle Airport", "city": "Ohrid", "country": "N. Macedonia", "iata": "OHD", "icao": "LWOH", "lat": 41.18, "lon": 20.7423, "alt": 2313, "tz": "Europe/Skopje"},
    {"name": "Torshavn Vagar Airport", "city": "Torshavn", "country": "Faroe Islands", "iata": "FAE", "icao": "EKVG", "lat": 62.0636, "lon": -7.2772, "alt": 280, "tz": "Atlantic/Faroe"},
    {"name": "Reykjavik Domestic Airport", "city": "Reykjavik", "country": "Iceland", "iata": "RKV", "icao": "BIRK", "lat": 64.13, "lon": -21.9406, "alt": 48, "tz": "Atlantic/Reykjavik"},
    {"name": "Akureyri Airport", "city": "Akureyri", "country": "Iceland", "iata": "AEY", "icao": "BIAR", "lat": 65.66, "lon": -18.0727, "alt": 6, "tz": "Atlantic/Reykjavik"},
    {"name": "Marrakech Menara Airport", "city": "Marrakech", "country": "Morocco", "iata": "RAK", "icao": "GMMX", "lat": 31.6069, "lon": -8.0363, "alt": 1545, "tz": "Africa/Casablanca"},
    {"name": "Agadir Al Massira Airport", "city": "Agadir", "country": "Morocco", "iata": "AGA", "icao": "GMAD", "lat": 30.325, "lon": -9.413, "alt": 276, "tz": "Africa/Casablanca"},
    {"name": "Fez Sais Airport", "city": "Fez", "country": "Morocco", "iata": "FEZ", "icao": "GMFF", "lat": 33.9273, "lon": -4.9779, "alt": 1900, "tz": "Africa/Casablanca"},
    {"name": "Rabat Sale Airport", "city": "Rabat", "country": "Morocco", "iata": "RBA", "icao": "GMME", "lat": 34.0515, "lon": -6.7515, "alt": 276, "tz": "Africa/Casablanca"},
    {"name": "Tangier Ibn Battouta Airport", "city": "Tangier", "country": "Morocco", "iata": "TNG", "icao": "GMTT", "lat": 35.7269, "lon": -5.9168, "alt": 62, "tz": "Africa/Casablanca"},
    {"name": "Ouagadougou Airport", "city": "Ouagadougou", "country": "Burkina Faso", "iata": "OUA", "icao": "DFFD", "lat": 12.3532, "lon": -1.5124, "alt": 1037, "tz": "Africa/Ouagadougou"},
    {"name": "Niamey Diori Hamani International", "city": "Niamey", "country": "Niger", "iata": "NIM", "icao": "DRRN", "lat": 13.4815, "lon": 2.1836, "alt": 732, "tz": "Africa/Niamey"},
    {"name": "Ndjamena Hassan Djamous International", "city": "N'Djamena", "country": "Chad", "iata": "NDJ", "icao": "FTTJ", "lat": 12.1337, "lon": 15.034, "alt": 968, "tz": "Africa/Ndjamena"},
    {"name": "Kilimanjaro International Airport", "city": "Arusha", "country": "Tanzania", "iata": "JRO", "icao": "HTKJ", "lat": -3.4294, "lon": 37.0745, "alt": 2932, "tz": "Africa/Dar_es_Salaam"},
    {"name": "Lilongwe Kamuzu International Airport", "city": "Lilongwe", "country": "Malawi", "iata": "LLW", "icao": "FWKI", "lat": -13.7894, "lon": 33.781, "alt": 4035, "tz": "Africa/Blantyre"},
    {"name": "Mauritius Sir Seewoosagur Ramgoolam Intl", "city": "Port Louis", "country": "Mauritius", "iata": "MRU", "icao": "FIMP", "lat": -20.4302, "lon": 57.6836, "alt": 186, "tz": "Indian/Mauritius"},
    {"name": "Reunion Roland Garros Airport", "city": "Saint-Denis", "country": "Reunion", "iata": "RUN", "icao": "FMEE", "lat": -20.8871, "lon": 55.5103, "alt": 66, "tz": "Indian/Reunion"},
    {"name": "Asmara International Airport", "city": "Asmara", "country": "Eritrea", "iata": "ASM", "icao": "HHAS", "lat": 15.2919, "lon": 38.9107, "alt": 7661, "tz": "Africa/Asmara"},
    {"name": "Oujda Angads Airport", "city": "Oujda", "country": "Morocco", "iata": "OUD", "icao": "GMFO", "lat": 34.7872, "lon": -1.924, "alt": 1535, "tz": "Africa/Casablanca"},
    {"name": "Dakar Leopold Sedar Senghor Airport", "city": "Dakar", "country": "Senegal", "iata": "DKR", "icao": "GOOY", "lat": 14.7397, "lon": -17.4902, "alt": 85, "tz": "Africa/Dakar"},
    {"name": "Basra International Airport", "city": "Basra", "country": "Iraq", "iata": "BSR", "icao": "ORMM", "lat": 30.5491, "lon": 47.6621, "alt": 11, "tz": "Asia/Baghdad"},
    {"name": "Erbil International Airport", "city": "Erbil", "country": "Iraq", "iata": "EBL", "icao": "ORER", "lat": 36.2376, "lon": 43.9632, "alt": 1341, "tz": "Asia/Baghdad"},
    {"name": "Damascus International Airport", "city": "Damascus", "country": "Syria", "iata": "DAM", "icao": "OSDI", "lat": 33.4115, "lon": 36.5156, "alt": 2020, "tz": "Asia/Damascus"},
    {"name": "Aden Airport", "city": "Aden", "country": "Yemen", "iata": "ADE", "icao": "OYAA", "lat": 12.8295, "lon": 45.0288, "alt": 7, "tz": "Asia/Aden"},
    {"name": "Samarkand International Airport", "city": "Samarkand", "country": "Uzbekistan", "iata": "SKD", "icao": "UTSS", "lat": 39.7005, "lon": 66.9838, "alt": 2224, "tz": "Asia/Tashkent"},
    {"name": "Fergana International Airport", "city": "Fergana", "country": "Uzbekistan", "iata": "FEG", "icao": "UTKF", "lat": 40.3588, "lon": 71.745, "alt": 1980, "tz": "Asia/Tashkent"},
    {"name": "Osh Airport", "city": "Osh", "country": "Kyrgyzstan", "iata": "OSS", "icao": "UAFO", "lat": 40.609, "lon": 72.7932, "alt": 2927, "tz": "Asia/Bishkek"},
    {"name": "Chittagong Shah Amanat Intl Airport", "city": "Chittagong", "country": "Bangladesh", "iata": "CGP", "icao": "VGEG", "lat": 22.2496, "lon": 91.8133, "alt": 12, "tz": "Asia/Dhaka"},
    {"name": "Mandalay International Airport", "city": "Mandalay", "country": "Myanmar", "iata": "MDL", "icao": "VYMD", "lat": 21.7022, "lon": 95.9779, "alt": 298, "tz": "Asia/Rangoon"},
    {"name": "Salalah Airport", "city": "Salalah", "country": "Oman", "iata": "SLL", "icao": "OOSA", "lat": 17.0387, "lon": 54.0913, "alt": 73, "tz": "Asia/Muscat"},
    {"name": "Ningbo Lishe International Airport", "city": "Ningbo", "country": "China", "iata": "NGB", "icao": "ZSNB", "lat": 29.8267, "lon": 121.4616, "alt": 13, "tz": "Asia/Shanghai"},
    {"name": "Fuzhou Changle International Airport", "city": "Fuzhou", "country": "China", "iata": "FOC", "icao": "ZSFZ", "lat": 25.9351, "lon": 119.6631, "alt": 46, "tz": "Asia/Shanghai"},
    {"name": "Wenzhou Longwan International Airport", "city": "Wenzhou", "country": "China", "iata": "WNZ", "icao": "ZSWZ", "lat": 27.9122, "lon": 120.8522, "alt": 23, "tz": "Asia/Shanghai"},
    {"name": "Jinan Yaoqiang International Airport", "city": "Jinan", "country": "China", "iata": "TNA", "icao": "ZSJN", "lat": 36.8572, "lon": 117.216, "alt": 76, "tz": "Asia/Shanghai"},
    {"name": "Hefei Xinqiao International Airport", "city": "Hefei", "country": "China", "iata": "HFE", "icao": "ZSOF", "lat": 31.78, "lon": 116.9897, "alt": 108, "tz": "Asia/Shanghai"},
    {"name": "Taiyuan Wusu Airport", "city": "Taiyuan", "country": "China", "iata": "TYN", "icao": "ZBYN", "lat": 37.7469, "lon": 112.6283, "alt": 2569, "tz": "Asia/Shanghai"},
    {"name": "Lanzhou Zhongchuan International Airport", "city": "Lanzhou", "country": "China", "iata": "LHW", "icao": "ZLLL", "lat": 36.5152, "lon": 103.6204, "alt": 6388, "tz": "Asia/Shanghai"},
    {"name": "Guiyang Longdongbao International Airport", "city": "Guiyang", "country": "China", "iata": "KWE", "icao": "ZUGY", "lat": 26.5385, "lon": 106.8012, "alt": 3736, "tz": "Asia/Shanghai"},
    {"name": "Nanchang Changbei International Airport", "city": "Nanchang", "country": "China", "iata": "KHN", "icao": "ZSCN", "lat": 28.865, "lon": 115.9, "alt": 144, "tz": "Asia/Shanghai"},
    {"name": "Changchun Longjia International Airport", "city": "Changchun", "country": "China", "iata": "CGQ", "icao": "ZYCC", "lat": 43.9962, "lon": 125.6845, "alt": 761, "tz": "Asia/Shanghai"},
    {"name": "Hohhot Baita International Airport", "city": "Hohhot", "country": "China", "iata": "HET", "icao": "ZBHH", "lat": 40.8514, "lon": 111.824, "alt": 3556, "tz": "Asia/Shanghai"},
    {"name": "Yinchuan Hedong International Airport", "city": "Yinchuan", "country": "China", "iata": "INC", "icao": "ZLIC", "lat": 38.3219, "lon": 106.393, "alt": 3701, "tz": "Asia/Shanghai"},
    {"name": "Matsuyama Airport", "city": "Matsuyama", "country": "Japan", "iata": "MYJ", "icao": "RJOM", "lat": 33.8272, "lon": 132.6997, "alt": 25, "tz": "Asia/Tokyo"},
    {"name": "Kumamoto Airport", "city": "Kumamoto", "country": "Japan", "iata": "KMJ", "icao": "RJFT", "lat": 32.8373, "lon": 130.8554, "alt": 642, "tz": "Asia/Tokyo"},
    {"name": "Nagasaki Airport", "city": "Nagasaki", "country": "Japan", "iata": "NGS", "icao": "RJFU", "lat": 32.9169, "lon": 129.9141, "alt": 15, "tz": "Asia/Tokyo"},
    {"name": "Oita Airport", "city": "Oita", "country": "Japan", "iata": "OIT", "icao": "RJFO", "lat": 33.4794, "lon": 131.7369, "alt": 18, "tz": "Asia/Tokyo"},
    {"name": "Okayama Airport", "city": "Okayama", "country": "Japan", "iata": "OKJ", "icao": "RJOB", "lat": 34.7569, "lon": 133.8552, "alt": 806, "tz": "Asia/Tokyo"},
    {"name": "Asahikawa Airport", "city": "Asahikawa", "country": "Japan", "iata": "AKJ", "icao": "RJEC", "lat": 43.6708, "lon": 142.4475, "alt": 721, "tz": "Asia/Tokyo"},
    {"name": "Daegu International Airport", "city": "Daegu", "country": "South Korea", "iata": "TAE", "icao": "RKTN", "lat": 35.8941, "lon": 128.6589, "alt": 116, "tz": "Asia/Seoul"},
    {"name": "Cheongju International Airport", "city": "Cheongju", "country": "South Korea", "iata": "CJJ", "icao": "RKTU", "lat": 36.7166, "lon": 127.4991, "alt": 191, "tz": "Asia/Seoul"},
    {"name": "Phu Quoc International Airport", "city": "Phu Quoc", "country": "Vietnam", "iata": "PQC", "icao": "VVPQ", "lat": 10.227, "lon": 103.9674, "alt": 37, "tz": "Asia/Ho_Chi_Minh"},
    {"name": "Nha Trang Cam Ranh Airport", "city": "Nha Trang", "country": "Vietnam", "iata": "CXR", "icao": "VVCR", "lat": 11.9982, "lon": 109.2192, "alt": 40, "tz": "Asia/Ho_Chi_Minh"},
    {"name": "Kuching International Airport", "city": "Kuching", "country": "Malaysia", "iata": "KCH", "icao": "WBGG", "lat": 1.4847, "lon": 110.3469, "alt": 89, "tz": "Asia/Kuala_Lumpur"},
    {"name": "Miri Airport", "city": "Miri", "country": "Malaysia", "iata": "MYY", "icao": "WBGR", "lat": 4.322, "lon": 113.9869, "alt": 59, "tz": "Asia/Kuala_Lumpur"},
    {"name": "Christmas Island Airport", "city": "Flying Fish Cove", "country": "Australia", "iata": "CXI", "icao": "YCXI", "lat": -10.4507, "lon": 105.6927, "alt": 916, "tz": "Indian/Christmas"},
    {"name": "Cocos Keeling Islands Airport", "city": "West Island", "country": "Australia", "iata": "CCK", "icao": "YPCC", "lat": -12.1883, "lon": 96.8339, "alt": 10, "tz": "Indian/Cocos"},
    {"name": "Norfolk Island Airport", "city": "Kingston", "country": "Australia", "iata": "NLK", "icao": "YSNF", "lat": -29.0415, "lon": 167.9388, "alt": 371, "tz": "Pacific/Norfolk"},
    {"name": "Broome International Airport", "city": "Broome", "country": "Australia", "iata": "BME", "icao": "YBRM", "lat": -17.9447, "lon": 122.2323, "alt": 56, "tz": "Australia/Perth"},
    {"name": "Suva Nausori International Airport", "city": "Suva", "country": "Fiji", "iata": "SUV", "icao": "NFNA", "lat": -18.0433, "lon": 178.5594, "alt": 17, "tz": "Pacific/Fiji"},
    {"name": "Pago Pago International Airport", "city": "Pago Pago", "country": "American Samoa", "iata": "PPG", "icao": "NSTU", "lat": -14.331, "lon": -170.7104, "alt": 32, "tz": "Pacific/Pago_Pago"},
    {"name": "Rarotonga International Airport", "city": "Avarua", "country": "Cook Islands", "iata": "RAR", "icao": "NCRG", "lat": -21.2027, "lon": -159.8059, "alt": 26, "tz": "Pacific/Rarotonga"},
    {"name": "Majuro Marshall Islands Airport", "city": "Majuro", "country": "Marshall Islands", "iata": "MAJ", "icao": "PKMJ", "lat": 7.0648, "lon": 171.2722, "alt": 6, "tz": "Pacific/Majuro"},
    {"name": "Pohnpei International Airport", "city": "Palikir", "country": "Micronesia", "iata": "PNI", "icao": "PTPN", "lat": 6.9851, "lon": 158.209, "alt": 10, "tz": "Pacific/Pohnpei"},
    {"name": "Koror Babeldaob Airport", "city": "Koror", "country": "Palau", "iata": "ROR", "icao": "PTRO", "lat": 7.3673, "lon": 134.5443, "alt": 176, "tz": "Pacific/Palau"},
    {"name": "Funafuti International Airport", "city": "Funafuti", "country": "Tuvalu", "iata": "FUN", "icao": "NGFU", "lat": -8.525, "lon": 179.196, "alt": 9, "tz": "Pacific/Funafuti"},

    {"name": "Bozeman Yellowstone International Airport", "city": "Bozeman", "country": "United States", "iata": "BZN", "icao": "KBZN", "lat": 45.7777, "lon": -111.1528, "alt": 4473, "tz": "America/Denver"},
    {"name": "Helena Regional Airport", "city": "Helena", "country": "United States", "iata": "HLN", "icao": "KHLN", "lat": 46.6068, "lon": -111.9833, "alt": 3877, "tz": "America/Denver"},
    {"name": "Twin Falls Magic Valley Regional Airport", "city": "Twin Falls", "country": "United States", "iata": "TWF", "icao": "KTWF", "lat": 42.4818, "lon": -114.4878, "alt": 4154, "tz": "America/Boise"},
    {"name": "Medford Rogue Valley International Airport", "city": "Medford", "country": "United States", "iata": "MFR", "icao": "KMFR", "lat": 42.3742, "lon": -122.8731, "alt": 1335, "tz": "America/Los_Angeles"},
    {"name": "Bellingham International Airport", "city": "Bellingham", "country": "United States", "iata": "BLI", "icao": "KBLI", "lat": 48.7928, "lon": -122.5375, "alt": 170, "tz": "America/Los_Angeles"},
    {"name": "Yakima Air Terminal", "city": "Yakima", "country": "United States", "iata": "YKM", "icao": "KYKM", "lat": 46.5682, "lon": -120.5444, "alt": 1099, "tz": "America/Los_Angeles"},
    {"name": "Wenatchee Pangborn Memorial Airport", "city": "Wenatchee", "country": "United States", "iata": "EAT", "icao": "KEAT", "lat": 47.3988, "lon": -120.2074, "alt": 1245, "tz": "America/Los_Angeles"},
    {"name": "Pullman-Moscow Regional Airport", "city": "Pullman", "country": "United States", "iata": "PUW", "icao": "KPUW", "lat": 46.7439, "lon": -117.11, "alt": 2556, "tz": "America/Los_Angeles"},
    {"name": "Kalispell Glacier Park International", "city": "Kalispell", "country": "United States", "iata": "FCA", "icao": "KGPI", "lat": 48.3105, "lon": -114.2556, "alt": 2977, "tz": "America/Denver"},
    {"name": "Provo Municipal Airport", "city": "Provo", "country": "United States", "iata": "PVU", "icao": "KPVU", "lat": 40.2192, "lon": -111.7234, "alt": 4497, "tz": "America/Denver"},
    {"name": "Flagstaff Pulliam Airport", "city": "Flagstaff", "country": "United States", "iata": "FLG", "icao": "KFLG", "lat": 35.1385, "lon": -111.6715, "alt": 7014, "tz": "America/Phoenix"},
    {"name": "Yuma International Airport", "city": "Yuma", "country": "United States", "iata": "YUM", "icao": "KNYL", "lat": 32.6566, "lon": -114.606, "alt": 213, "tz": "America/Phoenix"},
    {"name": "Monterey Regional Airport", "city": "Monterey", "country": "United States", "iata": "MRY", "icao": "KMRY", "lat": 36.587, "lon": -121.843, "alt": 257, "tz": "America/Los_Angeles"},
    {"name": "Santa Barbara Municipal Airport", "city": "Santa Barbara", "country": "United States", "iata": "SBA", "icao": "KSBA", "lat": 34.4262, "lon": -119.8404, "alt": 10, "tz": "America/Los_Angeles"},
    {"name": "San Luis Obispo Regional Airport", "city": "San Luis Obispo", "country": "United States", "iata": "SBP", "icao": "KSBP", "lat": 35.2368, "lon": -120.6414, "alt": 212, "tz": "America/Los_Angeles"},
    {"name": "Stockton Metropolitan Airport", "city": "Stockton", "country": "United States", "iata": "SCK", "icao": "KSCK", "lat": 37.8942, "lon": -121.2375, "alt": 33, "tz": "America/Los_Angeles"},
    {"name": "Eureka California Redwood Coast Airport", "city": "Eureka", "country": "United States", "iata": "ACV", "icao": "KACV", "lat": 40.9781, "lon": -124.1086, "alt": 221, "tz": "America/Los_Angeles"},
    {"name": "Crescent City Del Norte County Airport", "city": "Crescent City", "country": "United States", "iata": "CEC", "icao": "KCEC", "lat": 41.7802, "lon": -124.2367, "alt": 61, "tz": "America/Los_Angeles"},
    {"name": "Atlantic City International Airport", "city": "Atlantic City", "country": "United States", "iata": "ACY", "icao": "KACY", "lat": 39.4576, "lon": -74.5772, "alt": 75, "tz": "America/New_York"},
    {"name": "Poznan Lawica Airport", "city": "Poznan", "country": "Poland", "iata": "POZ", "icao": "EPPO", "lat": 52.421, "lon": 16.8263, "alt": 308, "tz": "Europe/Warsaw"},
    {"name": "Lodz Wladyslaw Reymont Airport", "city": "Lodz", "country": "Poland", "iata": "LCJ", "icao": "EPLL", "lat": 51.7219, "lon": 19.3981, "alt": 604, "tz": "Europe/Warsaw"},
    {"name": "Constanta Mihail Kogalniceanu Airport", "city": "Constanta", "country": "Romania", "iata": "CND", "icao": "LRCK", "lat": 44.3622, "lon": 28.4883, "alt": 353, "tz": "Europe/Bucharest"},
    {"name": "Maastricht Aachen Airport", "city": "Maastricht", "country": "Netherlands", "iata": "MST", "icao": "EHBK", "lat": 50.9117, "lon": 5.7701, "alt": 375, "tz": "Europe/Amsterdam"},
    {"name": "Liege Airport", "city": "Liege", "country": "Belgium", "iata": "LGG", "icao": "EBLG", "lat": 50.6374, "lon": 5.4432, "alt": 659, "tz": "Europe/Brussels"},
    {"name": "Ostend Bruges International Airport", "city": "Ostend", "country": "Belgium", "iata": "OST", "icao": "EBOS", "lat": 51.1989, "lon": 2.8622, "alt": 13, "tz": "Europe/Brussels"},
    {"name": "Gwangju Airport", "city": "Gwangju", "country": "South Korea", "iata": "KWJ", "icao": "RKJJ", "lat": 35.1264, "lon": 126.8089, "alt": 39, "tz": "Asia/Seoul"},
    {"name": "Takamatsu Airport", "city": "Takamatsu", "country": "Japan", "iata": "TAK", "icao": "RJOT", "lat": 34.2141, "lon": 134.0161, "alt": 607, "tz": "Asia/Tokyo"},

    {"name": "Laramie Regional Airport", "city": "Laramie", "country": "United States", "iata": "LAR", "icao": "KLAR", "lat": 41.3121, "lon": -105.675, "alt": 7284, "tz": "America/Denver"},
    {"name": "Gillette Campbell County Airport", "city": "Gillette", "country": "United States", "iata": "GCC", "icao": "KGCC", "lat": 44.3489, "lon": -105.5393, "alt": 4365, "tz": "America/Denver"},
    {"name": "Casper Natrona County Airport", "city": "Casper", "country": "United States", "iata": "CPR", "icao": "KCPR", "lat": 42.908, "lon": -106.4644, "alt": 5350, "tz": "America/Denver"},
    {"name": "Idaho Falls Regional Airport", "city": "Idaho Falls", "country": "United States", "iata": "IDA", "icao": "KIDA", "lat": 43.5146, "lon": -112.07, "alt": 4744, "tz": "America/Boise"},
    {"name": "Pocatello Regional Airport", "city": "Pocatello", "country": "United States", "iata": "PIH", "icao": "KPIH", "lat": 42.9098, "lon": -112.596, "alt": 4452, "tz": "America/Boise"},
    {"name": "Lewiston Nez Perce County Airport", "city": "Lewiston", "country": "United States", "iata": "LWS", "icao": "KLWS", "lat": 46.3745, "lon": -117.0153, "alt": 1442, "tz": "America/Los_Angeles"},
    {"name": "Hagerstown Regional Airport", "city": "Hagerstown", "country": "United States", "iata": "HGR", "icao": "KHGR", "lat": 39.7079, "lon": -77.7295, "alt": 703, "tz": "America/New_York"},
    {"name": "Charlottesville Albemarle Airport", "city": "Charlottesville", "country": "United States", "iata": "CHO", "icao": "KCHO", "lat": 38.1386, "lon": -78.4529, "alt": 639, "tz": "America/New_York"},
    {"name": "Roanoke Blacksburg Regional Airport", "city": "Roanoke", "country": "United States", "iata": "ROA", "icao": "KROA", "lat": 37.3255, "lon": -79.9754, "alt": 1175, "tz": "America/New_York"},
    {"name": "Lynchburg Regional Airport", "city": "Lynchburg", "country": "United States", "iata": "LYH", "icao": "KLYH", "lat": 37.3267, "lon": -79.2004, "alt": 938, "tz": "America/New_York"},
    {"name": "New Bern Coastal Carolina Regional Airport", "city": "New Bern", "country": "United States", "iata": "EWN", "icao": "KEWN", "lat": 35.073, "lon": -77.043, "alt": 18, "tz": "America/New_York"},
    {"name": "Burlington Regional Airport", "city": "Burlington", "country": "United States", "iata": "BRL", "icao": "KBRL", "lat": 40.7832, "lon": -91.1255, "alt": 698, "tz": "America/Chicago"},
    {"name": "Quad Cities International Airport", "city": "Moline", "country": "United States", "iata": "MLI", "icao": "KMLI", "lat": 41.4485, "lon": -90.5075, "alt": 590, "tz": "America/Chicago"},
    {"name": "Peoria General Downing Airport", "city": "Peoria", "country": "United States", "iata": "PIA", "icao": "KPIA", "lat": 40.6642, "lon": -89.6933, "alt": 660, "tz": "America/Chicago"},
    {"name": "Bloomington Normal Airport", "city": "Bloomington", "country": "United States", "iata": "BMI", "icao": "KBMI", "lat": 40.4771, "lon": -88.9159, "alt": 871, "tz": "America/Chicago"},
    {"name": "Springfield Capital Airport", "city": "Springfield", "country": "United States", "iata": "SPI", "icao": "KSPI", "lat": 39.8441, "lon": -89.6779, "alt": 598, "tz": "America/Chicago"},
    {"name": "Rockford Chicago Rockford International", "city": "Rockford", "country": "United States", "iata": "RFD", "icao": "KRFD", "lat": 42.1954, "lon": -89.0972, "alt": 742, "tz": "America/Chicago"},
    {"name": "South Bend Regional Airport", "city": "South Bend", "country": "United States", "iata": "SBN", "icao": "KSBN", "lat": 41.7087, "lon": -86.3173, "alt": 799, "tz": "America/Indiana/Indianapolis"},
    {"name": "Fort Wayne International Airport", "city": "Fort Wayne", "country": "United States", "iata": "FWA", "icao": "KFWA", "lat": 40.9785, "lon": -85.1951, "alt": 815, "tz": "America/Indiana/Indianapolis"},
    {"name": "Evansville Regional Airport", "city": "Evansville", "country": "United States", "iata": "EVV", "icao": "KEVV", "lat": 38.037, "lon": -87.5323, "alt": 418, "tz": "America/Chicago"},
    {"name": "Moncton Greater Moncton Airport", "city": "Moncton", "country": "Canada", "iata": "YQM", "icao": "CYQM", "lat": 46.1122, "lon": -64.6789, "alt": 232, "tz": "America/Moncton"},
    {"name": "Fredericton International Airport", "city": "Fredericton", "country": "Canada", "iata": "YFC", "icao": "CYFC", "lat": 45.8689, "lon": -66.5372, "alt": 68, "tz": "America/Moncton"},
    {"name": "Charlottetown Airport", "city": "Charlottetown", "country": "Canada", "iata": "YYG", "icao": "CYYG", "lat": 46.29, "lon": -63.1211, "alt": 160, "tz": "America/Halifax"},
    {"name": "Sydney Cape Breton Airport", "city": "Sydney", "country": "Canada", "iata": "YQY", "icao": "CYQY", "lat": 46.1614, "lon": -60.0478, "alt": 203, "tz": "America/Halifax"},
    {"name": "Buenos Aires Jorge Newbery Airport", "city": "Buenos Aires", "country": "Argentina", "iata": "AEP", "icao": "SABE", "lat": -34.5592, "lon": -58.4158, "alt": 18, "tz": "America/Argentina/Buenos_Aires"},
    {"name": "Cordoba Ingeniero Taravella Airport", "city": "Cordoba", "country": "Argentina", "iata": "COR", "icao": "SACO", "lat": -31.3236, "lon": -64.208, "alt": 1604, "tz": "America/Argentina/Cordoba"},
    {"name": "Mendoza El Plumerillo Airport", "city": "Mendoza", "country": "Argentina", "iata": "MDZ", "icao": "SAME", "lat": -32.8317, "lon": -68.7929, "alt": 2310, "tz": "America/Argentina/Mendoza"},
    {"name": "Bariloche International Airport", "city": "Bariloche", "country": "Argentina", "iata": "BRC", "icao": "SAZS", "lat": -41.1512, "lon": -71.1575, "alt": 2774, "tz": "America/Argentina/Salta"},
    {"name": "Miyazaki Airport", "city": "Miyazaki", "country": "Japan", "iata": "KMI", "icao": "RJFM", "lat": 31.8772, "lon": 131.449, "alt": 20, "tz": "Asia/Tokyo"},
    {"name": "Obihiro Airport", "city": "Obihiro", "country": "Japan", "iata": "OBO", "icao": "RJCB", "lat": 42.7333, "lon": 143.2167, "alt": 506, "tz": "Asia/Tokyo"},
    {"name": "Hakodate Airport", "city": "Hakodate", "country": "Japan", "iata": "HKD", "icao": "RJCH", "lat": 41.77, "lon": 140.822, "alt": 151, "tz": "Asia/Tokyo"},
    {"name": "Lord Howe Island Airport", "city": "Lord Howe Island", "country": "Australia", "iata": "LDH", "icao": "YLHI", "lat": -31.5383, "lon": 159.0775, "alt": 5, "tz": "Australia/Lord_Howe"},
    {"name": "Noumea Magenta Airport", "city": "Noumea", "country": "New Caledonia", "iata": "GEA", "icao": "NWWM", "lat": -22.2583, "lon": 166.4729, "alt": 10, "tz": "Pacific/Noumea"},

    {"name": "Milan Bergamo Orio Al Serio Airport", "city": "Bergamo", "country": "Italy", "iata": "BGY", "icao": "LIME", "lat": 45.6739, "lon": 9.7042, "alt": 782, "tz": "Europe/Rome"},
    {"name": "Olbia Costa Smeralda Airport", "city": "Olbia", "country": "Italy", "iata": "OLB", "icao": "LIEO", "lat": 40.8987, "lon": 9.5178, "alt": 37, "tz": "Europe/Rome"},

    {"name": "Tehran Mehrabad International Airport", "city": "Tehran", "country": "Iran", "iata": "THR", "icao": "OIII", "lat": 35.6892, "lon": 51.3136, "alt": 3962, "tz": "Asia/Tehran"},
    {"name": "Isfahan International Airport", "city": "Isfahan", "country": "Iran", "iata": "IFN", "icao": "OIFM", "lat": 32.7508, "lon": 51.8613, "alt": 5059, "tz": "Asia/Tehran"},
    {"name": "Shiraz International Airport", "city": "Shiraz", "country": "Iran", "iata": "SYZ", "icao": "OISS", "lat": 29.5392, "lon": 52.5898, "alt": 4920, "tz": "Asia/Tehran"},
    {"name": "Tabriz International Airport", "city": "Tabriz", "country": "Iran", "iata": "TBZ", "icao": "OITT", "lat": 38.1339, "lon": 46.235, "alt": 4459, "tz": "Asia/Tehran"},
    {"name": "Ahvaz International Airport", "city": "Ahvaz", "country": "Iran", "iata": "AWZ", "icao": "OIAW", "lat": 31.3374, "lon": 48.762, "alt": 66, "tz": "Asia/Tehran"},
    {"name": "Volgograd International Airport", "city": "Volgograd", "country": "Russia", "iata": "VOG", "icao": "URWW", "lat": 48.7825, "lon": 44.3455, "alt": 279, "tz": "Europe/Moscow"},
    {"name": "Kazan International Airport", "city": "Kazan", "country": "Russia", "iata": "KZN", "icao": "UWKD", "lat": 55.6063, "lon": 49.2787, "alt": 410, "tz": "Europe/Moscow"},
    {"name": "Ufa International Airport", "city": "Ufa", "country": "Russia", "iata": "UFA", "icao": "UWUU", "lat": 54.5575, "lon": 55.8744, "alt": 449, "tz": "Asia/Yekaterinburg"},
    {"name": "Samara Kurumoch International Airport", "city": "Samara", "country": "Russia", "iata": "KUF", "icao": "UWWW", "lat": 53.505, "lon": 50.1644, "alt": 477, "tz": "Europe/Samara"},
    {"name": "Mineralnye Vody Airport", "city": "Mineralnye Vody", "country": "Russia", "iata": "MRV", "icao": "URMM", "lat": 44.2251, "lon": 43.0819, "alt": 1054, "tz": "Europe/Moscow"},

    {"name": "Norilsk Alykel Airport", "city": "Norilsk", "country": "Russia", "iata": "NSK", "icao": "UOOO", "lat": 69.3111, "lon": 87.3322, "alt": 574, "tz": "Asia/Krasnoyarsk"},
    {"name": "Murmansk Airport", "city": "Murmansk", "country": "Russia", "iata": "MMK", "icao": "ULMM", "lat": 68.7817, "lon": 32.7508, "alt": 243, "tz": "Europe/Moscow"},
    {"name": "Arkhangelsk Talagi Airport", "city": "Arkhangelsk", "country": "Russia", "iata": "ARH", "icao": "ULAA", "lat": 64.6003, "lon": 40.7167, "alt": 36, "tz": "Europe/Moscow"},
    {"name": "Perm Bolshoye Savino Airport", "city": "Perm", "country": "Russia", "iata": "PEE", "icao": "USPP", "lat": 57.9145, "lon": 56.0212, "alt": 404, "tz": "Asia/Yekaterinburg"},
    {"name": "Tyumen Roschino Airport", "city": "Tyumen", "country": "Russia", "iata": "TJM", "icao": "USTR", "lat": 57.1896, "lon": 68.9933, "alt": 378, "tz": "Asia/Yekaterinburg"},
    {"name": "Omsk Tsentralny Airport", "city": "Omsk", "country": "Russia", "iata": "OMS", "icao": "UNOO", "lat": 54.967, "lon": 73.3105, "alt": 312, "tz": "Asia/Omsk"},
    {"name": "Irkutsk Airport", "city": "Irkutsk", "country": "Russia", "iata": "IKT", "icao": "UIII", "lat": 52.268, "lon": 104.3889, "alt": 1675, "tz": "Asia/Irkutsk"},
    {"name": "Khabarovsk Novyi Airport", "city": "Khabarovsk", "country": "Russia", "iata": "KHV", "icao": "UHHH", "lat": 48.528, "lon": 135.1883, "alt": 244, "tz": "Asia/Vladivostok"},
    {"name": "Yakutsk Airport", "city": "Yakutsk", "country": "Russia", "iata": "YKS", "icao": "UEEE", "lat": 62.0933, "lon": 129.7706, "alt": 325, "tz": "Asia/Yakutsk"},
    {"name": "Magadan Sokol Airport", "city": "Magadan", "country": "Russia", "iata": "GDX", "icao": "UHMM", "lat": 59.91, "lon": 150.7203, "alt": 574, "tz": "Asia/Magadan"},
    {"name": "Salta Martin Miguel de Guemes Airport", "city": "Salta", "country": "Argentina", "iata": "SLA", "icao": "SASA", "lat": -24.856, "lon": -65.4862, "alt": 4088, "tz": "America/Argentina/Salta"},
    {"name": "Tucuman Benjamin Matienzo Airport", "city": "Tucuman", "country": "Argentina", "iata": "TUC", "icao": "SANT", "lat": -26.8409, "lon": -65.1049, "alt": 1509, "tz": "America/Argentina/Tucuman"},
    {"name": "Mar del Plata Airport", "city": "Mar del Plata", "country": "Argentina", "iata": "MDQ", "icao": "SAZM", "lat": -37.9342, "lon": -57.5733, "alt": 72, "tz": "America/Argentina/Buenos_Aires"},

]

# ─────────────────────────────────────────────────────────────────────────────
# Indexes
# ─────────────────────────────────────────────────────────────────────────────
IATA_INDEX = {a["iata"].upper(): a for a in AIRPORTS}
ICAO_INDEX = {a["icao"].upper(): a for a in AIRPORTS}

# ─────────────────────────────────────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
RED    = "\033[31m"
DIM    = "\033[2m"

def c(color, text):
    return f"{color}{text}{RESET}"

def fmt_airport(a, verbose=False):
    lines = []
    lines.append(c(BOLD + CYAN, f"\n  ✈  {a['name']}"))
    lines.append(f"  {'─' * 52}")
    lines.append(f"  {c(YELLOW, 'IATA:')}  {c(BOLD, a['iata'])}    {c(YELLOW, 'ICAO:')}  {c(BOLD, a['icao'])}")
    lines.append(f"  {c(YELLOW, 'City:')}  {a['city']},  {a['country']}")
    lines.append(f"  {c(YELLOW, 'Timezone:')}  {a['tz']}")
    lines.append(f"  {c(YELLOW, 'Coordinates:')}  {a['lat']:+.4f}°,  {a['lon']:+.4f}°")
    lines.append(f"  {c(YELLOW, 'Elevation:')}  {a['alt']:,} ft  ({int(a['alt'] * 0.3048):,} m)")
    lines.append("")
    return "\n".join(lines)

def fmt_airport_short(a):
    return (
        f"  {c(BOLD, a['iata'])} / {c(BOLD, a['icao'])}  "
        f"{a['name'][:42]:<42}  "
        f"{a['city']}, {a['country']}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Lookup logic
# ─────────────────────────────────────────────────────────────────────────────
def lookup(code):
    code = code.strip().upper()
    if code in IATA_INDEX:
        return IATA_INDEX[code], "IATA"
    if code in ICAO_INDEX:
        return ICAO_INDEX[code], "ICAO"
    return None, None

def search(query):
    q = query.lower()
    results = []
    for a in AIRPORTS:
        if (q in a["name"].lower()
                or q in a["city"].lower()
                or q in a["country"].lower()
                or q in a["iata"].lower()
                or q in a["icao"].lower()):
            results.append(a)
    return results

def list_country(country_query):
    q = country_query.lower()
    return [a for a in AIRPORTS if q in a["country"].lower()]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def nearest(lat, lon, n=5):
    scored = sorted(AIRPORTS, key=lambda a: haversine_km(lat, lon, a["lat"], a["lon"]))
    return [(a, haversine_km(lat, lon, a["lat"], a["lon"])) for a in scored[:n]]

# ─────────────────────────────────────────────────────────────────────────────
# JSON export
# ─────────────────────────────────────────────────────────────────────────────
def to_dict(a):
    return {
        "name": a["name"],
        "city": a["city"],
        "country": a["country"],
        "iata": a["iata"],
        "icao": a["icao"],
        "latitude": a["lat"],
        "longitude": a["lon"],
        "elevation_ft": a["alt"],
        "timezone": a["tz"],
    }

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def build_parser():
    p = argparse.ArgumentParser(
        prog="airport_lookup",
        description=(
            "✈  Airport Routing Code Lookup\n"
            "Supports IATA (e.g. LAX) and ICAO (e.g. KLAX) codes.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  airport_lookup LAX
  airport_lookup KLAX
  airport_lookup LAX JFK NRT
  airport_lookup --search london
  airport_lookup --list-country Japan
  airport_lookup --nearest 51.5 -0.12
  airport_lookup LAX --json
  airport_lookup --stats
        """,
    )
    p.add_argument(
        "codes",
        nargs="*",
        metavar="CODE",
        help="IATA or ICAO code(s) to look up",
    )
    p.add_argument(
        "--search", "-s",
        metavar="QUERY",
        help="Search airports by name, city, or country",
    )
    p.add_argument(
        "--list-country", "-l",
        metavar="COUNTRY",
        help="List all airports in a given country",
    )
    p.add_argument(
        "--nearest", "-n",
        nargs=2,
        metavar=("LAT", "LON"),
        type=float,
        help="Find the 5 nearest airports to given coordinates",
    )
    p.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON",
    )
    p.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics",
    )
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── stats ─────────────────────────────────────────────────────────────────
    if args.stats:
        countries = sorted(set(a["country"] for a in AIRPORTS))
        print(c(BOLD + CYAN, f"\n  ✈  Airport Database Statistics"))
        print(f"  {'─' * 40}")
        print(f"  Total airports : {c(BOLD, str(len(AIRPORTS)))}")
        print(f"  Countries      : {c(BOLD, str(len(countries)))}")
        print(f"\n  Countries covered:")
        for co in countries:
            count = sum(1 for a in AIRPORTS if a["country"] == co)
            print(f"    {co:<30} {count} airport{'s' if count > 1 else ''}")
        print()
        return

    # ── nearest ───────────────────────────────────────────────────────────────
    if args.nearest:
        lat, lon = args.nearest
        results = nearest(lat, lon)
        if args.json:
            print(json.dumps([{**to_dict(a), "distance_km": round(d, 1)} for a, d in results], indent=2))
            return
        print(c(BOLD + CYAN, f"\n  ✈  5 Nearest Airports to ({lat:+.4f}, {lon:+.4f})"))
        print(f"  {'─' * 60}")
        for a, dist in results:
            print(f"  {c(BOLD, a['iata'])} / {c(BOLD, a['icao'])}  {c(GREEN, f'{dist:,.0f} km')}  "
                  f"{a['name'][:36]} — {a['city']}, {a['country']}")
        print()
        return

    # ── search ────────────────────────────────────────────────────────────────
    if args.search:
        results = search(args.search)
        if not results:
            print(c(RED, f"\n  No airports found matching '{args.search}'\n"))
            sys.exit(1)
        if args.json:
            print(json.dumps([to_dict(a) for a in results], indent=2))
            return
        print(c(BOLD + CYAN, f"\n  ✈  Search results for '{args.search}'  ({len(results)} found)"))
        print(f"  {'─' * 70}")
        for a in results:
            print(fmt_airport_short(a))
        print()
        return

    # ── list-country ──────────────────────────────────────────────────────────
    if args.list_country:
        results = list_country(args.list_country)
        if not results:
            print(c(RED, f"\n  No airports found for country '{args.list_country}'\n"))
            sys.exit(1)
        if args.json:
            print(json.dumps([to_dict(a) for a in results], indent=2))
            return
        label = results[0]["country"] if results else args.list_country
        print(c(BOLD + CYAN, f"\n  ✈  Airports in {label}  ({len(results)} found)"))
        print(f"  {'─' * 70}")
        for a in results:
            print(fmt_airport_short(a))
        print()
        return

    # ── code lookup ───────────────────────────────────────────────────────────
    if not args.codes:
        parser.print_help()
        return

    found, not_found = [], []
    for code in args.codes:
        a, kind = lookup(code)
        if a:
            found.append((a, kind))
        else:
            not_found.append(code)

    if args.json:
        print(json.dumps([to_dict(a) for a, _ in found], indent=2))
        if not_found:
            for code in not_found:
                sys.stderr.write(f"Not found: {code}\n")
        return

    for a, kind in found:
        print(fmt_airport(a))

    for code in not_found:
        print(c(RED, f"\n  ✗  '{code}' — code not found in database."))
        # suggest close IATA matches
        suggestions = [k for k in list(IATA_INDEX) + list(ICAO_INDEX)
                       if k.startswith(code[:2].upper())][:4]
        if suggestions:
            print(c(DIM, f"     Did you mean: {', '.join(suggestions)}?"))
        print()

    if not_found:
        sys.exit(1)


if __name__ == "__main__":
    main()
