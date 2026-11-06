BIHAR FARMER HELP PORTAL
========================

Requirements:
- Python 3.10 or newer recommended
- Internet connection for external government links and the hero background image

Run in Windows / VS Code:
1. Extract this ZIP.
2. Open the extracted folder in VS Code.
3. Open Terminal > New Terminal.
4. Create a virtual environment (recommended):
   py -m venv .venv
5. Activate it in PowerShell:
   .\.venv\Scripts\Activate.ps1
   If PowerShell blocks activation, use:
   .venv\Scripts\python.exe -m pip install Flask
   .venv\Scripts\python.exe app.py
6. Install Flask:
   python -m pip install Flask
7. Start the site:
   python app.py
8. Open this address in your browser:
   http://127.0.0.1:5000

Features:
- Responsive home page
- English, Hindi and Bhojpuri language selection
- Daily Bihar mandi prices from the official Agmarknet data.gov.in feed (requires a data.gov.in API key)
- Mandi filters for crop/district, request time, latest feed arrival date and a chart limited to dates returned by the feed
- Clear mandi-feed errors and retry; no cached or sample prices are presented as live
- Searchable official government links
- Tap-to-call helpline links
- Bihar agriculture/DBT and farm mechanization portals
- PM-KISAN, crop insurance, soil health, e-NAM and IMD links
- Farmer dashboard for district/block/panchayat shortcuts and saved scheme links, stored only in the current browser
- District selector for all 38 Bihar districts and a clearly labeled handoff to the official IMD site (no live forecast integration)
- Scheme finder with official links and review dates
- Guided crop-help prompts with conservative safety guidance and links to official agriculture assistants (no photo diagnosis or pesticide prescription)

Important:
- This is an independent informational demo, not a government website.
- The helpline list is intentionally limited to numbers with reliable official support.
- Confirm current hours, scheme eligibility, deadlines and contact details on official websites.
- The farmer profile is browser-local and is not government registration; avoid shared devices.
- This demo has no account system, admin dashboard or server-side farmer records. Do not collect Aadhaar, bank details, passwords or OTPs here.
- Weather forecasts are not fetched in this demo. Check the linked IMD site for current district forecasts and alerts.
- Crop-help prompts are basic guidance, not AI diagnosis. Do not rely on them for pesticide or fertilizer prescriptions.

Daily market prices setup:
- Register for an API key at https://www.data.gov.in/ and set it as the DATA_GOV_IN_API_KEY environment variable. Keep the key on the server; do not put it in browser JavaScript or commit it to source control.
- For local development, add DATA_GOV_IN_API_KEY=your-key to the root .env file. On Render, set DATA_GOV_IN_API_KEY in the service's Environment settings (the render.yaml entry is intentionally not synced so the secret is never stored in source control), then redeploy the service.
- The portal displays market-reported Bihar rates per quintal from the Agmarknet daily-price dataset. Rates are indicative, can vary by mandi and arrival date, and are not guaranteed sale prices. If the key is not configured or the official feed is unavailable, the portal reports that rates could not be loaded rather than displaying sample values.
