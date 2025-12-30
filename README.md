# 📡 SimDatabase - VerifyPK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/E4crypt3d/SimDatabase/graphs/commit-activity)

A professional command-line utility designed for validating and retrieving informational data associated with Pakistani Phone Numbers and CNICs. `VerifyPK` provides detailed analysis of CNICs, including provincial and regional insights.

---

## 🚀 Key Features

- **🔍 Advanced Verification**: Validate Pakistan-specific phone formats (`92...`, `03...`) and CNIC standards.
- **📊 Detailed CNIC Analysis**: Decodes CNIC numbers to provide:
  - Province / Territory identification.
  - Division and District insights.
  - Family Number correlation.
  - Gender identification.
- **🔄 Robust Request Handling**: Built-in retry mechanism for stable network communication.
- **🎨 Rich Terminal Interface**: Beautifully formatted tables and color-coded output for enhanced readability.
- **🛡️ Data Integrity**: Normalizes and validates input before processing.

---

## 🛠️ Technology Stack

- **Core Logic**: [Python 3.8+](https://www.python.org/)
- **Networking**: [Requests](https://requests.readthedocs.io/)
- **Parsing**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- **UI/Styling**: [Stringcolor](https://github.com/skat97/stringcolor)
- **Data Handling**: Standard typing & Regex

---

## 📥 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/E4crypt3d/SimDatabase.git
   cd SimDatabase
   ```

2. **Environment Setup** (Optional but Recommended)
   ```bash
   python -m venv env
   source env/bin/scripts/activate  # On Windows: .\env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💡 Usage

Run the script directly from your terminal using the following arguments:

### 📱 Phone Number Verification
```bash
python VerifyPK.py -n 03XXXXXXXXX
```

### 🪪 CNIC Verification & Analysis
```bash
python VerifyPK.py -c XXXXX-XXXXXXX-X
```

### ⚙️ Example Output
For CNIC verification:
```text
VerifyPK - Sim Database Tool

CNIC DETAILED ANALYSIS:
+----------------------+----------------------+
| Input CNIC           | 42101-XXXXXXX-1      |
| Normalized CNIC      | 42101XXXXXXX1        |
| Province / Territory | Sindh                |
| Division             | Karachi              |
| Family Number        | XXXXXX               |
| Gender               | Male                 |
+----------------------+----------------------+
```

---

## 📂 Project Structure

```text
SimDatabase/
├── VerifyPK.py       # Main entry point & CLI logic
├── utils.py          # Helper functions & data processing
├── requirements.txt  # Project dependencies
├── VerifyPK.exe      # Compiled binary for Windows
└── README.md         # Comprehensive documentation
```

---

## 🔧 Troubleshooting

If you encounter connection timeouts or issues reaching the database:
- Ensure you have an active internet connection.
- **Pro Tip**: Use Cloudflare DNS (`1.1.1.1` / `1.0.0.1`) for faster and more reliable lookup requests.

---

## ⚖️ Disclaimer

> [!WARNING]
> **Educational and Informational Purposes Only.**
> This tool is provided for educational purposes and for verifying personal information. Any misuse of this tool for illegal activities or unauthorized data access is strictly prohibited. The developers are not responsible for how this tool is used. By using this software, you agree to comply with all local and international privacy laws. Information retrieved is sourced from public endpoints and may not always be up-to-date or accurate.

---

<p align="center">Made with ❤️ for the Developer Community</p>
