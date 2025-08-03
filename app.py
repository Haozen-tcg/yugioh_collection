import streamlit as st
import pandas as pd
import json
import os

# Charger les données (supposons fichier JSON déjà téléchargé)
@st.cache_data
def load_cards(json_file="all_cards.json"):
    if not os.path.exists(json_file):
        st.error(f"Le fichier {json_file} est introuvable.")
        return pd.DataFrame()
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    cards = data.get("data", [])
    rows = []
    for card in cards:
        sets = card.get("card_sets", [])
        for s in sets:
            rows.append({
                "Nom": card.get("name"),
                "Extension": s.get("set_name"),
                "Rareté": s.get("set_rarity"),
                "Race": card.get("race"),
                "Quantité possédée": 0,
                "Image_URL": card.get("card_images")[0].get("image_url") if card.get("card_images") else ""
            })
    return pd.DataFrame(rows)

# Interface
def main():
    st.title("Gestion de ta collection Yu-Gi-Oh!")
    
    df = load_cards()
    if df.empty:
        st.stop()

    # Filtre extension
    extensions = sorted(df["Extension"].unique())
    selected_ext = st.selectbox("Choisis une extension :", ["Toutes"] + extensions)

    if selected_ext != "Toutes":
        df = df[df["Extension"] == selected_ext]

    # Affichage tableau avec possibilité d’édition de la quantité
    edited_df = st.data_editor(df, num_rows="dynamic")

    # Sauvegarder la collection
    if st.button("Sauvegarder ma collection"):
        edited_df.to_excel("collection_modifiee.xlsx", index=False)
        st.success("Collection sauvegardée dans collection_modifiee.xlsx")

if __name__ == "__main__":
    main()

