#!/usr/bin/env python3

import re
import sys
from pathlib import Path

# Permette di importare server.py dalla cartella principale
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import search_flights


# =========================
# IMPOSTAZIONI DELLA RICERCA
# =========================

ORIGINS = "LHR,LGW,STN,LTN,LCY"

# Prima prova: 15 destinazioni molto diverse tra loro.
# Poi possiamo portarle a 50, 100+.
DESTINATIONS = {
    "CDG": "Paris",
    "AMS": "Amsterdam",
    "BCN": "Barcelona",
    "MAD": "Madrid",
    "LIS": "Lisbon",
    "FCO": "Rome",
    "MXP": "Milan",
    "ATH": "Athens",
    "IST": "Istanbul",
    "DUB": "Dublin",
    "BER": "Berlin",
    "PRG": "Prague",
    "BUD": "Budapest",
    "VIE": "Vienna",
    "TFS": "Tenerife",
}

DEPARTURE_DATE = "2026-11-14"
RETURN_DATE = "2026-11-22"

ADULTS = 2
RESULTS_PER_ROUTE = 1


def extract_best_prices(text):
    """
    Estrae dal risultato FlightClaw:
    aeroporto di partenza -> destinazione
    prezzo della prima opzione
    """
    found = []

    current_route = None
    current_currency = None

    for line in text.splitlines():
        line = line.strip()

        # Esempio:
        # LHR -> CDG on 2026-11-14 (USD):
        route_match = re.match(
            r"([A-Z]{3}) -> ([A-Z]{3}) on .* \(([A-Z]{3})\):",
            line,
        )

        if route_match:
            current_route = (
                route_match.group(1),
                route_match.group(2),
            )
            current_currency = route_match.group(3)
            continue

        # Esempio:
        # Option 1: $144 total
        price_match = re.match(
            r"Option 1:\s*([^\d]*)([\d,]+)\s+total",
            line,
        )

        if price_match and current_route:
            symbol = price_match.group(1).strip()
            price = float(price_match.group(2).replace(",", ""))

            found.append(
                {
                    "origin": current_route[0],
                    "destination": current_route[1],
                    "currency": current_currency,
                    "symbol": symbol,
                    "price": price,
                }
            )

            current_route = None

    return found


def main():
    print("=" * 70)
    print("✈️  TRAVEL DEAL HUNTER")
    print("=" * 70)
    print(f"Partenza: {ORIGINS}")
    print(f"Date:     {DEPARTURE_DATE} -> {RETURN_DATE}")
    print(f"Passeggeri: {ADULTS} adulti")
    print(f"Destinazioni: {len(DESTINATIONS)}")
    print("=" * 70)
    print()

    all_results = []

    for airport, city in DESTINATIONS.items():
        print(f"🔎 Cerco Londra -> {city} ({airport})...")

        try:
            result = search_flights(
                origin=ORIGINS,
                destination=airport,
                date=DEPARTURE_DATE,
                return_date=RETURN_DATE,
                cabin="ECONOMY",
                stops="ANY",
                results=RESULTS_PER_ROUTE,
                adults=ADULTS,
                children=0,
                infants_in_seat=0,
                infants_on_lap=0,
                show_all_results=False,
            )

            prices = extract_best_prices(result)

            if prices:
                best = min(prices, key=lambda x: x["price"])

                all_results.append(
                    {
                        "city": city,
                        "airport": airport,
                        **best,
                    }
                )

                print(
                    f"   💰 {best['symbol']}{best['price']:,.0f} "
                    f"({best['currency']}) "
                    f"da {best['origin']}"
                )
            else:
                print("   ❌ Nessun risultato")

        except Exception as e:
            print(f"   ⚠️ Errore: {e}")

        print()

    # Ordina dal più economico al più caro
    all_results.sort(key=lambda x: x["price"])

    print()
    print("=" * 70)
    print("🏆 CLASSIFICA DESTINAZIONI")
    print("=" * 70)

    if not all_results:
        print("Nessun volo trovato.")
        return

    for i, result in enumerate(all_results, 1):
        print(
            f"{i:2}. {result['city']:<15} "
            f"{result['airport']}  "
            f"{result['symbol']}{result['price']:,.0f} "
            f"({result['currency']})  "
            f"da {result['origin']}"
        )

    print("=" * 70)
    print(f"Destinazioni trovate: {len(all_results)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
