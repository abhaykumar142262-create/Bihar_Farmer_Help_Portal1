(() => {
  const status = document.getElementById("market-price-status");
  const refreshButton = document.getElementById("market-price-refresh");
  const rows = document.getElementById("market-price-rows");
  if (!status || !refreshButton || !rows) return;

  const supportedLanguages = ["en", "hi", "bho"];
  const savedLanguage = localStorage.getItem("farmer-help-language");
  let language = supportedLanguages.includes(savedLanguage) ? savedLanguage : "en";
  let tableState;
  const messages = {
    loading: ["Loading official market rates...", "आधिकारिक मंडी भाव लोड हो रहे हैं...", "सरकारी मंडी भाव लोड हो रहल बा..."],
    loaded: [
      (count) => `${count} market rate${count === 1 ? "" : "s"} loaded from the official feed.`,
      (count) => `आधिकारिक फ़ीड से ${count} मंडी भाव मिले।`,
      (count) => `सरकारी फीड से ${count} मंडी भाव मिलल।`,
    ],
    empty: [
      "No Bihar market rates are currently available from the official feed.",
      "आधिकारिक फ़ीड में अभी बिहार के मंडी भाव उपलब्ध नहीं हैं।",
      "सरकारी फीड में अभी बिहार के मंडी भाव नइखे मिलत।",
    ],
    error: [
      (detail) => detail || "Unable to load market rates. Please try again or open the official source.",
      (detail) => detail || "मंडी भाव लोड नहीं हो सके। फिर कोशिश करें या आधिकारिक स्रोत खोलें।",
      (detail) => detail || "मंडी के भाव ना लोड भइल। फेर कोशिश करीं चाहे सरकारी स्रोत देखीं।",
    ],
  };
  const tableMessages = {
    loading: [
      "Loading daily market rates...",
      "दैनिक मंडी भाव लोड हो रहे हैं...",
      "रोज के मंडी भाव लोड हो रहल बा...",
    ],
    empty: [
      "No Bihar rates are currently available from the official feed.",
      "आधिकारिक फ़ीड में अभी बिहार के भाव उपलब्ध नहीं हैं।",
      "सरकारी फीड में अभी बिहार के भाव नइखे मिलत।",
    ],
    error: [
      "Live rates could not be loaded. Check the message above and try again.",
      "लाइव भाव लोड नहीं हो सके। ऊपर दिया संदेश देखें और फिर कोशिश करें।",
      "लाइव भाव ना लोड भइल। ऊपर के संदेश देखीं आ फेर कोशिश करीं।",
    ],
  };
  const errorMessages = {
    "Daily market rates are not configured yet. Please try again later.": [
      "Daily market rates are not configured. Set DATA_GOV_IN_API_KEY on the server.",
      "दैनिक मंडी भाव सेट नहीं हैं। सर्वर पर DATA_GOV_IN_API_KEY सेट करें।",
      "दैनिक मंडी भाव के सेटिंग नइखे। सर्वर पर DATA_GOV_IN_API_KEY सेट करीं।",
    ],
    "The official market-rate service is temporarily unavailable.": [
      "The official market-rate service is temporarily unavailable. Please try again later.",
      "आधिकारिक मंडी भाव सेवा अभी उपलब्ध नहीं है। कृपया बाद में फिर कोशिश करें।",
      "सरकारी मंडी भाव सेवा अभी उपलब्ध नइखे। कुछ देर बाद फेर कोशिश करीं।",
    ],
    "Could not reach the official market-rate service. Please try again.": [
      "Could not reach the official market-rate service. Check the server connection and try again.",
      "आधिकारिक मंडी भाव सेवा से संपर्क नहीं हो सका। सर्वर कनेक्शन जाँचें और फिर कोशिश करें।",
      "सरकारी मंडी भाव सेवा से संपर्क ना हो सकल। सर्वर कनेक्शन जाँचीं आ फेर कोशिश करीं।",
    ],
    "Could not load official market rates. Please try again.": [
      "Could not load official market rates. Please try again.",
      "आधिकारिक मंडी भाव लोड नहीं हो सके। फिर कोशिश करें।",
      "सरकारी मंडी भाव ना लोड भइल। फेर कोशिश करीं।",
    ],
    "The official market-rate service returned unexpected data.": [
      "The official market-rate service returned unexpected data. Please try again later.",
      "आधिकारिक मंडी भाव सेवा से गलत डेटा मिला। कृपया बाद में फिर कोशिश करें।",
      "सरकारी मंडी भाव सेवा से अनजान डेटा मिलल। कुछ देर बाद फेर कोशिश करीं।",
    ],
    "The official market-rate service returned unusable data.": [
      "The official market-rate service returned unusable data. Please try again later.",
      "आधिकारिक मंडी भाव सेवा से उपयोग योग्य डेटा नहीं मिला। कृपया बाद में फिर कोशिश करें।",
      "सरकारी मंडी भाव सेवा से काम के डेटा ना मिलल। कुछ देर बाद फेर कोशिश करीं।",
    ],
  };

  function setStatus(message, count) {
    status.dataset.statusMessage = message;
    status.dataset.count = count === undefined ? "" : String(count);
    const languageIndex = supportedLanguages.indexOf(language);
    const text = messages[message][languageIndex];
    const detail = message === "error" && errorMessages[count]
      ? errorMessages[count][languageIndex]
      : count;
    status.textContent = typeof text === "function" ? text(detail) : text;
  }

  function setTableState(state) {
    tableState = state;
    const [english, hindi] = tableMessages[state];
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 6;
    cell.dataset.en = english;
    cell.dataset.hi = hindi;
    cell.dataset.bho = tableMessages[state][2];
    cell.textContent = tableMessages[state][supportedLanguages.indexOf(language)];
    row.append(cell);
    rows.replaceChildren(row);
  }

  function formatPrice(value) {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(value);
  }

  function addCell(row, english, hindi, bhojpuri, value) {
    const cell = document.createElement("td");
    cell.dataset.en = english;
    cell.dataset.hi = hindi;
    cell.dataset.bho = bhojpuri;
    cell.textContent = value;
    row.append(cell);
  }

  async function loadPrices() {
    refreshButton.disabled = true;
    setStatus("loading");
    setTableState("loading");
    try {
      const response = await fetch("/api/daily-prices", { cache: "no-store" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Market rates request failed");
      if (!Array.isArray(data.prices)) throw new Error("Market rates response was invalid");

      rows.replaceChildren();
      for (const price of data.prices) {
        const row = document.createElement("tr");
        addCell(row, price.commodity, price.commodity, price.commodity, price.commodity);
        addCell(row, price.market, price.market, price.market, price.market);
        addCell(row, price.arrival_date, price.arrival_date, price.arrival_date, price.arrival_date);
        addCell(row, formatPrice(price.min_price), formatPrice(price.min_price), formatPrice(price.min_price), formatPrice(price.min_price));
        addCell(row, formatPrice(price.modal_price), formatPrice(price.modal_price), formatPrice(price.modal_price), formatPrice(price.modal_price));
        addCell(row, formatPrice(price.max_price), formatPrice(price.max_price), formatPrice(price.max_price), formatPrice(price.max_price));
        rows.append(row);
      }
      if (!data.prices.length) setTableState("empty");
      setStatus(data.prices.length ? "loaded" : "empty", data.prices.length);
    } catch (error) {
      console.error("Could not load official market rates:", error);
      setTableState("error");
      setStatus("error", error.message);
    } finally {
      refreshButton.disabled = false;
    }
  }

  refreshButton.addEventListener("click", loadPrices);
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.addEventListener("click", () => {
      language = supportedLanguages.includes(button.dataset.language) ? button.dataset.language : "en";
      if (status.dataset.statusMessage) {
        setStatus(status.dataset.statusMessage, status.dataset.count);
      }
      if (tableState) setTableState(tableState);
    });
  });

  loadPrices();
})();
