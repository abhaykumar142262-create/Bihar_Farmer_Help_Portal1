import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

HELPLINES = [
    {"name": "Kisan Call Centre", "name_hi": "किसान कॉल सेंटर", "name_bho": "किसान कॉल सेंटर", "number": "1800-180-1551", "detail": "Agriculture advice in local languages; listed government hours are 6 AM–10 PM daily.", "detail_hi": "स्थानीय भाषाओं में कृषि सलाह; सरकारी जानकारी के अनुसार रोज़ सुबह 6 से रात 10 बजे तक।", "detail_bho": "खेती-बारी के सलाह लोकल भाषा में; सरकारी जानकारी के मुताबिक रोज सबेरे 6 से रात 10 बजे ले सेवा।", "href": "tel:18001801551", "source_url": "https://www.dackkms.gov.in/Account/aboutus.aspx", "verified_on": "06 Nov 2026"},
    {"name": "PMFBY Crop Insurance Helpline", "name_hi": "PMFBY फसल बीमा हेल्पलाइन", "name_bho": "PMFBY फसल बीमा हेल्पलाइन", "number": "14447", "detail": "Crop insurance queries, grievances and crop-loss reporting.", "detail_hi": "फसल बीमा से जुड़े सवाल, शिकायतें और फसल नुकसान की रिपोर्ट।", "detail_bho": "फसल बीमा के सवाल, शिकायत आ फसल के नुकसान के जानकारी दीं।", "href": "tel:14447"},
    {"name": "Emergency Services", "name_hi": "आपातकालीन सेवाएँ", "name_bho": "आपातकालीन सेवा", "number": "112", "detail": "General emergency number in India. Use only for emergencies.", "detail_hi": "भारत का सामान्य आपातकालीन नंबर। केवल आपात स्थिति में उपयोग करें।", "detail_bho": "भारत के आपातकालीन नंबर। खाली आपात स्थिति में इस्तेमाल करीं।", "href": "tel:112"},
]

GOVERNMENT_LINKS = [
    {"title": "Bihar Agriculture Department", "title_hi": "बिहार कृषि विभाग", "title_bho": "बिहार कृषि विभाग", "detail": "Department news, services and official contact directory.", "detail_hi": "विभाग की खबरें, सेवाएँ और आधिकारिक संपर्क निर्देशिका।", "detail_bho": "विभाग के खबर, सेवा आ सरकारी संपर्क सूची।", "url": "https://state.bihar.gov.in/krishi/CitizenHome.html"},
    {"title": "Bihar Agriculture Schemes (DBT)", "title_hi": "बिहार कृषि योजनाएँ (DBT)", "title_bho": "बिहार खेती-बारी के योजना (DBT)", "detail": "Department-listed Bihar agriculture schemes and farmer services.", "detail_hi": "विभाग द्वारा सूचीबद्ध बिहार कृषि योजनाएँ और किसान सेवाएँ।", "detail_bho": "विभाग के बतावल बिहार के खेती-बारी योजना आ किसान सेवा।", "url": "https://dbtagriculture.bihar.gov.in/Krishimis/WebPortal/Scheme.aspx"},
    {"title": "Soil Health Card", "title_hi": "मृदा स्वास्थ्य कार्ड", "title_bho": "माटी के सेहत कार्ड", "detail": "Soil testing and nutrient recommendations.", "detail_hi": "मिट्टी की जाँच और पोषक तत्वों की सिफारिशें।", "detail_bho": "माटी के जाँच आ पोषक तत्व के सलाह।", "url": "https://soilhealth.dac.gov.in/"},
    {"title": "e-NAM National Agriculture Market", "title_hi": "e-NAM राष्ट्रीय कृषि बाज़ार", "title_bho": "e-NAM राष्ट्रीय कृषि बाजार", "detail": "Online agricultural market information and services.", "detail_hi": "ऑनलाइन कृषि बाज़ार की जानकारी और सेवाएँ।", "detail_bho": "ऑनलाइन कृषि बाजार के जानकारी आ सेवा।", "url": "https://www.enam.gov.in/"},
    {"title": "India Meteorological Department", "title_hi": "भारत मौसम विज्ञान विभाग", "title_bho": "भारत मौसम विज्ञान विभाग", "detail": "Official weather forecasts and warnings.", "detail_hi": "आधिकारिक मौसम पूर्वानुमान और चेतावनियाँ।", "detail_bho": "सरकारी मौसम के पूर्वानुमान आ चेतावनी।", "url": "https://mausam.imd.gov.in/"},
]

MARKET_PRICE_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"


@app.route("/api/daily-prices", methods=["GET"])
def daily_prices():
    api_key = os.getenv("DATA_GOV_IN_API_KEY")
    if not api_key:
        return jsonify(error="Daily market rates are not configured yet. Please try again later."), 503

    page_size = 1000
    records = []
    offset = 0
    try:
        while True:
            response = requests.get(
                MARKET_PRICE_API,
                params={
                    "api-key": api_key,
                    "format": "json",
                    "filters[state]": "Bihar",
                    "limit": page_size,
                    "offset": offset,
                },
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            page_records = payload["records"]
            if not isinstance(page_records, list):
                raise ValueError("The market price feed records field is not a list")
            records.extend(page_records)

            total = payload.get("total")
            if not page_records or len(page_records) < page_size:
                break
            if total is not None and len(records) >= int(total):
                break
            offset += len(page_records)
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        app.logger.warning("Daily market price feed returned HTTP %s", status)
        return jsonify(error="The official market-rate service is temporarily unavailable."), 502
    except (requests.Timeout, requests.ConnectionError):
        app.logger.exception("Daily market price feed request failed")
        return jsonify(error="Could not reach the official market-rate service. Please try again."), 502
    except requests.RequestException:
        app.logger.exception("Daily market price feed request failed")
        return jsonify(error="Could not load official market rates. Please try again."), 502

    except (ValueError, KeyError, TypeError):
        app.logger.error("Daily market price feed returned an unexpected response")
        return jsonify(error="The official market-rate service returned unexpected data."), 502

    prices = []
    for record in records:
        if not isinstance(record, dict):
            continue
        try:
            commodity = record["commodity"]
            market = record["market"]
            arrival_date = record["arrival_date"]
            district = record.get("district", "")
            if not all(isinstance(value, str) and value.strip() for value in (commodity, market, arrival_date)):
                continue
            if not isinstance(district, str):
                continue
            price_values = [
                float(Decimal(str(record[field]).replace(",", "")))
                for field in ("min_price", "modal_price", "max_price")
            ]
            if any(not Decimal(str(value)).is_finite() for value in price_values):
                continue
        except (KeyError, InvalidOperation, OverflowError, TypeError, ValueError):
            continue

        prices.append({
            "commodity": commodity.strip(),
            "market": market.strip(),
            "district": district.strip(),
            "arrival_date": arrival_date.strip(),
            "min_price": price_values[0],
            "modal_price": price_values[1],
            "max_price": price_values[2],
        })

    if records and not prices:
        app.logger.error("Daily market price feed contained no usable records")
        return jsonify(error="The official market-rate service returned unusable data."), 502

    def arrival_date_key(item):
        for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(item["arrival_date"], date_format)
            except ValueError:
                continue
        return datetime.min

    prices.sort(key=arrival_date_key, reverse=True)
    return jsonify(prices=prices, source="data.gov.in / Agmarknet")


@app.route("/", methods=["GET"])
def home():
    links = GOVERNMENT_LINKS
    return render_template("index.html", helplines=HELPLINES, links=links, query=request.args.get("q", ""))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
