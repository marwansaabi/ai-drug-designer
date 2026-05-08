import streamlit as st
import google.generativeai as genai
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, AllChem 
import py3Dmol
from stmol import showmol
import re

st.set_page_config(page_title="De Novo Drug Designer", page_icon="🧬", layout="wide")

st.title("🧠 De Novo AI Drug Designer (Powered by Gemini)")
st.markdown("""
Esta aplicación utiliza **Inteligencia Artificial Generativa Real** para inventar nuevas moléculas desde cero. 
Incluye un motor de validación quimioinformática (RDKit) para filtrar "alucinaciones químicas".
""")

# --- CONFIGURACIÓN DE LA API KEY (SISTEMA DE SECRETOS) ---
st.sidebar.header("Configuración del Motor de IA")
user_key = st.sidebar.text_input("Introduce tu propia API Key (opcional):", type="password")

# Lógica inteligente de la clave
if user_key:
    gemini_key = user_key
elif "GEMINI_API_KEY" in st.secrets:
    gemini_key = st.secrets["GEMINI_API_KEY"]
else:
    gemini_key = None

if not gemini_key:
    st.sidebar.warning("⚠️ No se ha detectado ninguna clave. Para que la app funcione, añade una clave en los Secrets de Streamlit o escríbela arriba.")
else:
    st.sidebar.success("✅ Motor de IA listo para usar.")

st.sidebar.markdown("[¿No tienes clave? Consíguelo gratis aquí](https://aistudio.google.com/app/apikey)")

# Configuración del prompt
st.subheader("1. Define las propiedades de tu nuevo fármaco")
user_prompt = st.text_area(
    "Instrucciones para la IA:", 
    "You are an expert computational chemist. Generate 5 novel valid SMILES strings for molecules that could act as drugs. They must contain aromatic rings and halogens. Output ONLY the SMILES strings separated by commas. Do not explain anything, do not use markdown, just the SMILES."
)

if st.button("🚀 Generar Nuevas Moléculas (De Novo)"):
    if not gemini_key:
        st.error("⚠️ Error: No hay una API Key disponible. Por favor, introdúcela en la barra lateral.")
    else:
        with st.spinner("El cerebro de IA está 'soñando' nuevas estructuras químicas..."):
            try:
                # 1. Configurar la IA de Google
                genai.configure(api_key=gemini_key)
                
                # BÚSQUEDA DINÁMICA DE MODELOS
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if not available_models:
                    st.error("La API Key no tiene acceso a ningún modelo generativo.")
                    st.stop()
                
                chosen_model = available_models[0]
                st.toast(f"🤖 Conectado a: {chosen_model}") 
                
                model = genai.GenerativeModel(chosen_model)
                
                # 2. Generar el contenido
                response = model.generate_content(user_prompt)
                ai_response = response.text
                
                st.subheader("2. Resultados Crudos de la IA (Raw Output)")
                st.code(ai_response)
                
                st.subheader("3. Motor de Validación RDKit")
                clean_response = ai_response.replace('`', '').replace('"', '').replace("'", "")
                potential_smiles = re.split(r'[,\n\s]+', clean_response)
                
                valid_molecules = []
                
                for s in potential_smiles:
                    s = s.strip()
                    if len(s) < 3: continue 
                    
                    mol = Chem.MolFromSmiles(s)
                    if mol is not None:
                        valid_molecules.append((s, mol))
                        st.success(f"✅ VÁLIDA: {s}")
                    else:
                        if any(char in s for char in ["C", "c", "O", "N", "=", "#", "("]):
                            st.error(f"❌ ALUCINACIÓN (Estructura imposible): {s}")
                
                # Renderizar las válidas
                if valid_molecules:
                    st.subheader("4. Análisis de las Moléculas Sobrevivientes")
                    for smiles, mol in valid_molecules:
                        with st.expander(f"Estructura: {smiles}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.image(Draw.MolToImage(mol), caption="Estructura 2D")
                                st.metric("Peso Molecular", f"{Descriptors.MolWt(mol):.2f} Da")
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
                                        st.warning("⚠️ Geometría demasiado compleja para 3D.")
                                except Exception as e:
                                    st.warning(f"Error técnico en el motor 3D: {e}")
                else:
                    st.warning("La IA no generó ninguna molécula viable.")

            except Exception as e:
                st.error(f"⚠️ Error de conexión: {e}")

st.sidebar.info("Proyecto de Marwan Saabi: Bioinformática + IA.")