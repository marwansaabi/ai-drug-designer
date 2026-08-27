# 🧬 AI-Powered De Novo Drug Designer (Gemini + RDKit)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://marwan-drug-discovery.streamlit.app/)

This application represents a cutting-edge **De Novo Drug Discovery pipeline**. It combines the generative power of Large Language Models (LLMs) with the scientific rigor of Cheminformatics.

## 🚀 The Architecture
Unlike simple generative apps, this tool implements a **validation-first approach**:
1. **Generative Layer:** Uses Google Gemini to "dream" novel molecular structures based on specific chemical constraints.
2. **Cheminformatics Filter:** Every molecule is parsed by **RDKit**. If the LLM hallucinates a structure that violates the laws of physics/valence, it is instantly discarded.
3. **3D Conformer Generation:** Valid molecules are converted into 3D structures using the **ETKDGv3 algorithm** and energy-optimized via **MMFF (Merck Molecular Force Field)**.

## ✨ Key Features
- **Real-time AI Generation:** Direct integration with Google Gemini Pro/Flash.
- **Dynamic Model Discovery:** Automatic failover to available LLM versions.
- **Interactive Visualization:** 3D molecular rendering with atomic-level detail.
- **Physicochemical Profiling:** Automated calculation of MW and LogP.

## 🛠️ Installation & Setup
```bash
git clone https://github.com/marwansaabi/ai-drug-designer.git
cd ai-drug-designer
pip install -r requirements.txt
streamlit run app.py
