# Mira 2.0 Release Notes

**Release Date:** November 26, 2025  
**Repository:** https://github.com/cylin-ms/mira

---

## 🎉 Overview

Mira 2.0 is a major release focused on **GPT-5 JJ automated evaluation**, **rich entity card rendering**, and **updated datasets** to help judges efficiently evaluate assertion quality.

---

## 📊 New & Updated Datasets

| Dataset | Size | Description |
|---------|------|-------------|
| **11_25_output.jsonl** | 960 KB | 103 meetings with assertions (justification + sourceID format) |
| **LOD_1121.WithUserUrl.jsonl** | 1.7 MB | Meeting Context with Azure Key Vault URLs for Test Tenant access |
| **LOD_1125.jsonl** | 1.7 MB | Updated context with 99% SourceID recovery |
| **assertion_scores.json** | 2.1 MB | GPT-5 JJ evaluation results for all 1,395 assertions |

**Data Improvements:**
- New assertion format with `justification` and `sourceID` fields (replacing legacy `reasoning`/`source`)
- Azure Key Vault URLs added for easy Test Tenant credential access
- 99% SourceID recovery rate (up from previous versions)

---

## 🤖 GPT-5 JJ Automated Evaluation

- **Full dataset evaluation**: 103 meetings, 1,395 assertions
- **96.2% pass rate** as baseline reference for judges
- **Supporting span extraction** with confidence scores
- **Section attribution** - maps evidence to response sections
- **Visual highlighting** - color-coded spans in the UI
- **Verification checkboxes** - judges can accept/reject GPT-5 findings

---

## 📧 Rich Entity Card Rendering

| Card Type | Features |
|-----------|----------|
| 💬 Chat | Message bubbles with sender, timestamp |
| ✉️ Email | Subject, recipients, body preview |
| 📄 File | Metadata + content with Preview/Raw tabs |
| 👤 User | Avatar with Azure Key Vault link |
| 📢 ChannelMessage | Teams messages with full content |

---

## 🎯 Focus Clarification

- **Primary purpose**: Judges evaluate assertion quality
- **GPT-5 as hints**: Helps judges find evidence faster (not ground truth)
- **Response annotations**: Optional, not mandatory

---

## 🎨 UI/UX Improvements

- Renamed `visualize_output.py` → `mira.py`
- Prominent "Meeting Context" banner with blue gradient
- Purple gradient meeting title styling
- Improved entity type detection from data

---

## 📖 Documentation

- Comprehensive README with detailed walkthroughs
- Contributor acknowledgments (Weiwei Cui, Kening Ren)
- Table of contents with 12 sections
- Command reference for all scripts

---

## 🙏 Acknowledgments

| Contributor | Contribution |
|-------------|--------------|
| **Weiwei Cui** | Meeting Context Data (LOD), assertion methodology documentation |
| **Kening Ren** | Workback Plan response generation, assertions with justification/sourceID |
| **Chin-Yew Lin** | Mira annotation tool, GPT-5 JJ evaluation, documentation |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/cylin-ms/mira.git
cd mira

# Install dependencies
pip install -r requirements.txt

# Launch Mira
streamlit run mira.py
```

---

## 📋 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v2.0** | Nov 26, 2025 | GPT-5 JJ evaluation, entity cards, dataset updates |
| v1.5 | Nov 25, 2025 | Command center UI, response annotations |
| v1.0 | Nov 24, 2025 | Initial release with basic annotation |
