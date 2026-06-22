# Financial-dashboard-lade-stack

> Interactive Streamlit financial analytics dashboard for technology companies

A comprehensive financial analytics dashboard built with Streamlit that turns raw financial CSV data into interactive, publication-grade visualizations. Designed for technology companies that need to track revenue, expenses, profitability, and runway without spreadsheet gymnastics.

🔗 **Live repo:** <https://github.com/girishlade111/Financial-dashboard-lade-stack>

## ✨ Features

- Interactive Plotly & Altair visualizations (revenue, expenses, profitability, runway)
- CSV-driven mock data pipeline for fast iteration
- Multi-page Streamlit layout with sidebar navigation
- PDF report generation via ReportLab
- Reproducible Python environment locked with `uv.lock`
- Replit-native config (`.replit`, `replit.md`) for one-click cloud run

## 🛠️ Tech stack

Python 3.11+ • Streamlit • Pandas • NumPy • Plotly • Altair • Matplotlib • ReportLab • uv

## 🚀 Getting started

```bash
# Option A — uv (recommended)
uv sync
uv run streamlit run app.py

# Option B — pip
python -m venv .venv && source .venv/bin/activate
pip install streamlit pandas numpy plotly altair matplotlib reportlab
streamlit run app.py
```

## 📁 Project structure

```
.
├── app.py                  # Streamlit entrypoint and pages
├── data/
│   └── mock_financial_data.csv
├── .streamlit/config.toml  # Theme & server config
├── pyproject.toml          # uv-managed dependencies
├── uv.lock                 # Locked dependency tree
├── .replit                 # Replit runtime config
└── replit.md               # Replit project notes
```

## 🤝 Contributing

Bug reports and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License

Check the repository for the license file. If none is present, treat as "all rights reserved" by the author.

---

Built by [Girish Lade](https://github.com/girishlade111) · Part of the [LadeStack](https://ladestack.in) open-source collection.
