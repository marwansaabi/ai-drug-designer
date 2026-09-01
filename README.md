# 🧬 De Novo Drug Designer (Gemini + RDKit)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://marwan-drug-discovery.streamlit.app/)

A Streamlit app that uses an LLM to propose novel molecular structures and then validates
them with cheminformatics tooling before showing anything to the user. The interesting part
isn't the generation — it's the filter: LLMs routinely emit SMILES strings that look
plausible but violate basic valence rules, so every candidate is parsed by RDKit and
discarded if it doesn't describe a chemically real molecule.

## How it works

1. **Generation** — Google Gemini is prompted for SMILES strings under user-defined
   constraints (e.g. "must contain aromatic rings and halogens"). The model is selected
   dynamically from those the API key has access to, so the app doesn't break when a
   specific model version is deprecated.
2. **Validation** — each candidate is parsed with `Chem.MolFromSmiles()`. Anything RDKit
   can't parse is rejected and shown separately, so you can see the model's failure rate.
3. **3D conformers** — surviving molecules get hydrogens added, coordinates embedded via
   ETKDGv3, and geometry relaxed with MMFF94. Molecules that fail to embed fall back to
   random-coordinate embedding before being reported as too complex.
4. **Profiling** — molecular weight and LogP are computed with RDKit descriptors.

## Features

- Dynamic model discovery (no hardcoded Gemini version)
- Explicit reporting of invalid generations rather than silently dropping them
- Interactive 3D rendering with py3Dmol
- Bring-your-own API key via the sidebar, or `st.secrets` when self-hosting

## Limitations

This is a demonstration of a generate-then-validate pipeline, not a drug discovery tool.
Passing RDKit parsing means a structure is chemically valid — it says nothing about
synthesizability, binding affinity, toxicity, or novelty. There is no docking, no ADMET
prediction, and no check against known compound databases.

## Setup

```bash
git clone https://github.com/marwansaabi/ai-drug-designer.git
cd ai-drug-designer
pip install -r requirements.txt
streamlit run app.py
```

You'll need a Google AI Studio API key ([free tier available](https://aistudio.google.com/app/apikey)).
Paste it in the sidebar, or add it to `.streamlit/secrets.toml` as `GEMINI_API_KEY`.

On Debian/Ubuntu, the system packages in `packages.txt` are required for RDKit's 2D
rendering to work.

## Tech stack

Python · Streamlit · Google Generative AI · RDKit · py3Dmol / stmol

## Author

**Marwan El Saabi** — MSc Bioinformatics student
[Portfolio](https://marwansaabi.github.io) · [GitHub](https://github.com/marwansaabi) · [LinkedIn](https://www.linkedin.com/in/marwansaabi/)
