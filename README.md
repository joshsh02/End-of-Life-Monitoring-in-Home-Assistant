# Home Assistant End-of-Life (EOL) Tracker

A custom [Home Assistant](https://www.home-assistant.io/) integration that monitors end-of-life (EOL) status for software and hardware products using data from [endoflife.date](https://endoflife.date). This helps users manage device sustainability and security by staying informed about support lifecycles.

---

## ✨ Features

- **EOL Status Monitoring:** Automatically checks product support and lifecycle status.
- **Vendor Mapping:** Uses product-specific URIs to fetch data from `endoflife.date`.
- **Multiple Sensors:** Generates entities for key support attributes like EOL, LTS, Discontinued, and Maintained.
- **Notifications:** Optionally triggers persistent notifications for unreachable or invalid URIs.

---

## 📦 Installation

1. Copy the `eol_tracker/` folder into your Home Assistant `custom_components/` directory.
2. Restart Home Assistant.
3. In Home Assistant, go to **Settings > Devices & Services > Integrations**, then click **Add Integration** and search for **EOL Tracker**.

---

## ⚙️ Configuration

Once added via the UI, provide the full product URI from [endoflife.date's API](https://endoflife.date/docs/api).

### Example Input:
https://endoflife.date/api/v1/products/iPad/releases/11
