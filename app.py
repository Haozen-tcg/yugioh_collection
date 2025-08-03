import streamlit as st
import pandas as pd
import json
import os

# 📥 Charger les cartes depuis un fichier JSON
@st.cache_data
def load_cards(json_file="all_cards.json"):
    if not os.path.exists(json_file):
        st.error(f"Fichier {json_file} introuvable. Télécharge-le d'abord depuis l'API.")
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

# 🖼️ Interface Streamlit
def main():
    st.set_page_config(layout="wide")
    st.title("🃏 Gestion de ta collection Yu-Gi-Oh!")

    df = load_cards()
    if df.empty:
        st.stop()

    # 📌 Sélection d'extension
    extensions = sorted(df["Extension"].unique())
    selected_ext = st.selectbox("Choisis une extension :", ["Toutes"] + extensions)

    if selected_ext != "Toutes":
        filtered_df = df[df["Extension"] == selected_ext].reset_index(drop=True)
    else:
        filtered_df = df.copy()

    # 🔽 Tri dynamique
    sort_by = st.selectbox("Trier les cartes par :", ["Extension", "Nom", "Rareté"])
    filtered_df = filtered_df.sort_values(by=[sort_by, "Nom"]).reset_index(drop=True)

    st.markdown("## 📋 Liste des cartes")

    for index, row in filtered_df.iterrows():
        cols = st.columns([1, 3])
        with cols[0]:
            if row["Image_URL"]:
                st.image(row["Image_URL"], width=140)
        with cols[1]:
            st.markdown(f"### {row['Nom']}")
            st.markdown(f"- **Extension** : {row['Extension']}")
            st.markdown(f"- **Rareté** : {row['Rareté']}")
            st.markdown(f"- **Race** : {row['Race']}")
            qty = st.number_input(
                "Quantité possédée",
                min_value=0,
                value=int(row["Quantité possédée"]),
                key=f"qty_{index}"
            )
            filtered_df.at[index, "Quantité possédée"] = qty

    # 💾 Sauvegarde
    if st.button("💾 Sauvegarder ma collection"):
        filename = "ma_collection_yugioh.xlsx"
        filtered_df.to_excel(filename, index=False)
        st.success(f"Collection sauvegardée dans **{filename}**")

if __name__ == "__main__":
    main()
