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
    {"name": "Kisan Call Centre", "name_hi": "किसान कॉल सेंटर", "name_bho": "किसान कॉल सेंटर", "number": "1800-180-1551", "detail": "Agriculture advice in local languages; listed government hours are 6 AM–10 PM daily.", "detail_hi": "स्थानीय भाषाओं में कृषि सलाह; सरकारी जानकारी के अनुसार रोज़ सुबह 6 से रात 10 बजे तक।", "detail_bho": "खेती-बारी के सलाह लोकल भाषा में; सरकारी जानकारी के मुताबिक रोज सबेरे 6 से रात 10 बजे ले सेवा।", "href": "tel:18001801551"},
    {"name": "PMFBY Crop Insurance Helpline", "name_hi": "PMFBY फसल बीमा हेल्पलाइन", "name_bho": "PMFBY फसल बीमा हेल्पलाइन", "number": "14447", "detail": "Crop insurance queries, grievances and crop-loss reporting.", "detail_hi": "फसल बीमा से जुड़े सवाल, शिकायतें और फसल नुकसान की रिपोर्ट।", "detail_bho": "फसल बीमा के सवाल, शिकायत आ फसल के नुकसान के जानकारी दीं।", "href": "tel:14447"},
    {"name": "Emergency Services", "name_hi": "आपातकालीन सेवाएँ", "name_bho": "आपातकालीन सेवा", "number": "112", "detail": "General emergency number in India. Use only for emergencies.", "detail_hi": "भारत का सामान्य आपातकालीन नंबर। केवल आपात स्थिति में उपयोग करें।", "detail_bho": "भारत के आपातकालीन नंबर। खाली आपात स्थिति में इस्तेमाल करीं।", "href": "tel:112"},
]

GOVERNMENT_LINKS = [
    {"title": "Bihar Agriculture Department / DBT Portal", "title_hi": "बिहार कृषि विभाग / DBT पोर्टल", "title_bho": "बिहार कृषि विभाग / DBT पोर्टल", "detail": "Bihar farmer registration, agriculture schemes and DBT services.", "detail_hi": "बिहार किसान पंजीकरण, कृषि योजनाएँ और DBT सेवाएँ।", "detail_bho": "बिहार में किसान रजिस्ट्रेशन, खेती के योजना आ DBT सेवा।", "url": "https://dbtagriculture.bihar.gov.in/"},
    {"title": "Bihar Agriculture Schemes", "title_hi": "बिहार कृषि योजनाएँ", "title_bho": "बिहार खेती-बारी के योजना", "detail": "View agriculture schemes listed by the Bihar Agriculture Department.", "detail_hi": "बिहार कृषि विभाग द्वारा सूचीबद्ध कृषि योजनाएँ देखें।", "detail_bho": "बिहार कृषि विभाग के बतावल खेती-बारी के योजना देखीं।", "url": "https://dbtagriculture.bihar.gov.in/Krishimis/WebPortal/Scheme.aspx"},
    {"title": "Bihar Farm Mechanization (OFMAS)", "title_hi": "बिहार कृषि यंत्रीकरण (OFMAS)", "title_bho": "बिहार खेती के मशीनीकरण (OFMAS)", "detail": "Farmer login and application status for farm mechanization subsidy.", "detail_hi": "कृषि यंत्रीकरण सब्सिडी के लिए किसान लॉगिन और आवेदन की स्थिति।", "detail_bho": "खेती के मशीन पर मिलए वाला सहायता खातिर किसान लॉगिन आ आवेदन के स्थिति।", "url": "https://farmech.bihar.gov.in/Group_Farmer_Login.aspx"},
    {"title": "PM-KISAN", "title_hi": "PM-KISAN", "title_bho": "PM-KISAN", "detail": "Check scheme information, status and e-KYC options.", "detail_hi": "योजना की जानकारी, स्थिति और e-KYC विकल्प देखें।", "detail_bho": "योजना के जानकारी, स्थिति आ e-KYC के विकल्प देखीं।", "url": "https://pmkisan.gov.in/"},
    {"title": "Pradhan Mantri Fasal Bima Yojana", "title_hi": "प्रधानमंत्री फसल बीमा योजना", "title_bho": "प्रधानमंत्री फसल बीमा योजना", "detail": "Crop insurance application, policy status and claim information.", "detail_hi": "फसल बीमा आवेदन, पॉलिसी की स्थिति और दावा जानकारी।", "detail_bho": "फसल बीमा के आवेदन, पॉलिसी के स्थिति आ दावा के जानकारी।", "url": "https://pmfby.gov.in/"},
    {"title": "Soil Health Card", "title_hi": "मृदा स्वास्थ्य कार्ड", "title_bho": "माटी के सेहत कार्ड", "detail": "Soil testing and nutrient recommendations.", "detail_hi": "मिट्टी की जाँच और पोषक तत्वों की सिफारिशें।", "detail_bho": "माटी के जाँच आ पोषक तत्व के सलाह।", "url": "https://soilhealth.dac.gov.in/"},
    {"title": "e-NAM National Agriculture Market", "title_hi": "e-NAM राष्ट्रीय कृषि बाज़ार", "title_bho": "e-NAM राष्ट्रीय कृषि बाजार", "detail": "Online agricultural market information and services.", "detail_hi": "ऑनलाइन कृषि बाज़ार की जानकारी और सेवाएँ।", "detail_bho": "ऑनलाइन कृषि बाजार के जानकारी आ सेवा।", "url": "https://www.enam.gov.in/"},
    {"title": "India Meteorological Department", "title_hi": "भारत मौसम विज्ञान विभाग", "title_bho": "भारत मौसम विज्ञान विभाग", "detail": "Official weather forecasts and warnings.", "detail_hi": "आधिकारिक मौसम पूर्वानुमान और चेतावनियाँ।", "detail_bho": "सरकारी मौसम के पूर्वानुमान आ चेतावनी।", "url": "https://mausam.imd.gov.in/"},
    {"title": "Agricultural Skill / Kisan Call Centre information", "title_hi": "कृषि कौशल / किसान कॉल सेंटर जानकारी", "title_bho": "खेती के जानकारी / किसान कॉल सेंटर", "detail": "Official information about Kisan Call Centre services.", "detail_hi": "किसान कॉल सेंटर सेवाओं के बारे में आधिकारिक जानकारी।", "detail_bho": "किसान कॉल सेंटर के सेवा के सरकारी जानकारी।", "url": "https://www.manage.gov.in/kcc/kcc.asp"},
]

MARKET_PRICE_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"


@app.route("/api/daily-prices", methods=["GET"])
def daily_prices():
    api_key = os.getenv("DATA_GOV_IN_API_KEY")
    if not api_key:
        return jsonify(error="Daily market rates are not configured yet. Please try again later."), 503

    try:
        response = requests.get(
            MARKET_PRICE_API,
            params={
                "api-key": api_key,
                "format": "json",
                "filters[state]": "Bihar",
                "limit": 100,
            },
            timeout=15,
        )
        response.raise_for_status()
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

    try:
        payload = response.json()
        records = payload["records"]
        if not isinstance(records, list):
            raise ValueError("The market price feed records field is not a list")
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
            if not all(isinstance(value, str) and value.strip() for value in (commodity, market, arrival_date)):
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
    q = request.args.get("q", "").strip().lower()
    links = GOVERNMENT_LINKS
    if q:
        links = [
            x for x in GOVERNMENT_LINKS
            if q in " ".join(x[key] for key in ("title", "title_hi", "title_bho", "detail", "detail_hi", "detail_bho")).lower()
        ]
    return render_template("index.html", helplines=HELPLINES, links=links, query=request.args.get("q", ""))

if __name__ == "__main__":
    app.run()
