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
Incluye un motor de validación quimioinformática (RDKit) para filtrar "alucinaciones químicas" e invalidar estructuras físicamente imposibles.
""")

# Sidebar para la API Key
st.sidebar.header("Configuración del Motor de IA")
gemini_key = st.sidebar.text_input("Introduce tu Google Gemini API Key (AIza...):", type="password")
st.sidebar.markdown("[¿No tienes clave? Consíguela gratis aquí](https://aistudio.google.com/app/apikey)")

# Configuración del prompt
st.subheader("1. Define las propiedades de tu nuevo fármaco")
user_prompt = st.text_area(
    "Instrucciones para la IA:", 
    "You are an expert computational chemist. Generate 5 novel valid SMILES strings for molecules that could act as drugs. They must contain aromatic rings and halogens. Output ONLY the SMILES strings separated by commas. Do not explain anything, do not use markdown, just the SMILES."
)

if st.button("🚀 Generar Nuevas Moléculas (De Novo)"):
    if not gemini_key:
        st.error("⚠️ Por favor, introduce tu Gemini API Key en la barra lateral.")
    else:
        with st.spinner("El cerebro de IA está 'soñando' nuevas estructuras químicas. Esto es IA real..."):
            try:
                # 1. Configurar la IA de Google
                genai.configure(api_key=gemini_key)
                
                # BÚSQUEDA DINÁMICA DE MODELOS
                # Le pedimos a Google su lista actual de modelos que soporten generación de texto
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if not available_models:
                    st.error("Tu API Key no tiene acceso a ningún modelo generativo en este momento.")
                    st.stop()
                
                # Elegimos automáticamente el primer modelo válido que encontremos
                chosen_model = available_models[0]
                st.toast(f"🤖 Conectado exitosamente al modelo: {chosen_model}") # Mensaje flotante chulo
                
                model = genai.GenerativeModel(chosen_model)
                
                # 2. Generar el contenido
                response = model.generate_content(user_prompt)
                ai_response = response.text
                
                st.subheader("2. Resultados Crudos de la IA (Raw Output)")
                st.code(ai_response)
                
                st.subheader("3. Motor de Validación RDKit (Filtro de Alucinaciones)")
                # Limpieza agresiva por si la IA añade comillas o saltos de línea
                clean_response = ai_response.replace('`', '').replace('"', '').replace("'", "")
                potential_smiles = re.split(r'[,\n\s]+', clean_response)
                
                valid_molecules = []
                
                for s in potential_smiles:
                    s = s.strip()
                    if len(s) < 3: continue 
                    
                    # Intentamos construir la molécula físicamente
                    mol = Chem.MolFromSmiles(s)
                    if mol is not None:
                        valid_molecules.append((s, mol))
                        st.success(f"✅ VÁLIDA: {s}")
                    else:
                        if any(char in s for char in ["C", "c", "O", "N", "=", "#", "("]):
                            st.error(f"❌ ALUCINACIÓN (Estructura físicamente imposible): {s}")
                
                # Renderizar las válidas
                if valid_molecules:
                    st.subheader("4. Análisis de las Moléculas Sobrevivientes")
                    for smiles, mol in valid_molecules:
                        with st.expander(f"Estructura: {smiles}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.image(Draw.MolToImage(mol), caption="Estructura 2D")
                                st.metric("Peso Molecular", f"{Descriptors.MolWt(mol):.2f} Da")
                                st.metric("LogP (Lipofilicidad)", f"{Descriptors.MolLogP(mol):.2f}")
                            
                            with col2:
                                try:
                                    # 1. Añadimos Hidrógenos
                                    mol_3d = Chem.AddHs(mol)
                                    
                                    # 2. INTENTO 1: Método estándar de distancias
                                    params = AllChem.ETKDGv3() # Usamos una versión más moderna de los parámetros
                                    params.randomSeed = 42
                                    
                                    res = AllChem.EmbedMolecule(mol_3d, params)
                                    
                                    # 3. INTENTO 2: Si el 1 falla, forzamos coordenadas aleatorias (el "brute force")
                                    if res == -1:
                                        res = AllChem.EmbedMolecule(mol_3d, randomSeed=42, useRandomCoords=True)
                                    
                                    # 4. Optimización de energía (solo si logramos darle forma 3D)
                                    if res != -1:
                                        AllChem.MMFFOptimizeMolecule(mol_3d)
                                        mol_block = Chem.MolToMolBlock(mol_3d)
                                        
                                        view = py3Dmol.view(width=400, height=300)
                                        view.addModel(mol_block, "sdf")
                                        view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
                                        view.zoomTo()
                                        showmol(view, height=300, width=400)
                                    else:
                                        st.warning("⚠️ Geometría demasiado compleja para renderizar en 3D.")
                                except Exception as e:
                                    st.warning(f"Error técnico en el motor 3D: {e}")
                else:
                    st.warning("La IA no generó ninguna molécula químicamente viable. ¡Prueba dándole otras instrucciones!")

            except Exception as e:
                st.error(f"⚠️ Error de conexión con Google Gemini: {e}")

st.sidebar.info("Este proyecto combina Modelos Fundacionales (Gemini) con Validación Quimioinformática (RDKit).")