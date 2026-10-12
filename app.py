import streamlit as st
import google.generativeai as genai
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, AllChem 
import py3Dmol
from stmol import showmol
import re

st.set_page_config(page_title="De Novo Drug Designer", page_icon=":material/science:", layout="wide")

st.title("De Novo AI Drug Designer (Powered by Gemini)")
st.markdown("""
This app uses **real generative AI** to design new molecules from scratch. 
It includes a cheminformatics validation engine (RDKit) that filters out "chemical hallucinations".
""")

# --- CONFIGURACIÓN DE LA API KEY (SISTEMA DE SECRETOS) ---
st.sidebar.header("AI engine settings")
user_key = st.sidebar.text_input("Enter your own API key (optional):", type="password")

# Lógica inteligente de la clave
if user_key:
    gemini_key = user_key
elif "GEMINI_API_KEY" in st.secrets:
    gemini_key = st.secrets["GEMINI_API_KEY"]
else:
    gemini_key = None

if not gemini_key:
    st.sidebar.warning("No API key detected. Add one to the Streamlit Secrets or enter it above for the app to work.", icon=":material/warning:")
else:
    st.sidebar.success("AI engine ready.", icon=":material/check_circle:")

st.sidebar.markdown("[No key? Get one for free here](https://aistudio.google.com/app/apikey)")

# Configuración del prompt
st.subheader("1. Define the properties of your new drug")
user_prompt = st.text_area(
    "Instructions for the AI:", 
    "You are an expert computational chemist. Generate 5 novel valid SMILES strings for molecules that could act as drugs. They must contain aromatic rings and halogens. Output ONLY the SMILES strings separated by commas. Do not explain anything, do not use markdown, just the SMILES."
)

if st.button("Generate new molecules (de novo)", type="primary"):
    if not gemini_key:
        st.error("No API key available. Please enter one in the sidebar.", icon=":material/error:")
    else:
        with st.spinner("The AI is dreaming up new chemical structures..."):
            try:
                # 1. Configurar la IA de Google
                genai.configure(api_key=gemini_key)
                
                # BÚSQUEDA DINÁMICA DE MODELOS
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if not available_models:
                    st.error("This API key has no access to any generative model.")
                    st.stop()
                
                chosen_model = available_models[0]
                st.toast(f"Connected to {chosen_model}", icon=":material/smart_toy:") 
                
                model = genai.GenerativeModel(chosen_model)
                
                # 2. Generar el contenido
                response = model.generate_content(user_prompt)
                ai_response = response.text
                
                st.subheader("2. Raw AI output")
                st.code(ai_response)
                
                st.subheader("3. RDKit validation engine")
                clean_response = ai_response.replace('`', '').replace('"', '').replace("'", "")
                potential_smiles = re.split(r'[,\n\s]+', clean_response)
                
                valid_molecules = []
                
                for s in potential_smiles:
                    s = s.strip()
                    if len(s) < 3: continue 
                    
                    mol = Chem.MolFromSmiles(s)
                    if mol is not None:
                        valid_molecules.append((s, mol))
                        st.success(f"VALID: {s}", icon=":material/check_circle:")
                    else:
                        if any(char in s for char in ["C", "c", "O", "N", "=", "#", "("]):
                            st.error(f"HALLUCINATION (impossible structure): {s}", icon=":material/cancel:")
                
                # Renderizar las válidas
                if valid_molecules:
                    st.subheader("4. Analysis of the surviving molecules")
                    for smiles, mol in valid_molecules:
                        with st.expander(f"Structure: {smiles}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.image(Draw.MolToImage(mol), caption="2D structure")
                                st.metric("Molecular weight", f"{Descriptors.MolWt(mol):.2f} Da")
                                st.metric("LogP", f"{Descriptors.MolLogP(mol):.2f}")
                            
                            with col2:
                                try:
                                    mol_3d = Chem.AddHs(mol)
                                    params = AllChem.ETKDGv3()
                                    params.randomSeed = 42
                                    res = AllChem.EmbedMolecule(mol_3d, params)
                                    
                                    if res == -1:
                                        res = AllChem.EmbedMolecule(mol_3d, randomSeed=42, useRandomCoords=True)
                                    
                                    if res != -1:
                                        AllChem.MMFFOptimizeMolecule(mol_3d)
                                        mol_block = Chem.MolToMolBlock(mol_3d)
                                        
                                        view = py3Dmol.view(width=400, height=300)
                                        view.addModel(mol_block, "sdf")
                                        view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
                                        view.zoomTo()
                                        showmol(view, height=300, width=400)
                                    else:
                                        st.warning("Geometry too complex for 3D.", icon=":material/warning:")
                                except Exception as e:
                                    st.warning(f"Technical error in the 3D engine: {e}")
                else:
                    st.warning("The AI did not generate any viable molecules.")

            except Exception as e:
                st.error(f"Connection error: {e}", icon=":material/error:")

st.sidebar.info("A project by Marwan El Saabi: bioinformatics and AI.")