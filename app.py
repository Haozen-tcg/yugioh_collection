import streamlit as st
import pandas as pd
import json
import os

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

def main():
    st.set_page_config(layout="wide")
    st.title("🃏 Gestion de ta collection Yu-Gi-Oh!")

    df = load_cards()
    if df.empty:
        st.stop()

    # 🔍 Barre de recherche avec loupe
    st.markdown("### 🔍 Rechercher une carte")
    search_col1, search_col2 = st.columns([8, 1])
    with search_col1:
        search_query = st.text_input("Nom de la carte", "", label_visibility="collapsed").strip().lower()
    with search_col2:
        st.write("")  # espace vertical
        st.button("🔍", key="search_button")

    # 📂 Filtre par extension
    extensions = sorted(df["Extension"].unique())
    selected_ext = st.selectbox("📂 Filtrer par extension :", ["Toutes"] + extensions)

    # 🧹 Filtrage combiné
    filtered_df = df.copy()
    if selected_ext != "Toutes":
        filtered_df = filtered_df[filtered_df["Extension"] == selected_ext]
    if search_query:
        filtered_df = filtered_df[filtered_df["Nom"].str.lower().str.contains(search_query)]

    if filtered_df.empty:
        st.warning("Aucune carte trouvée avec les filtres appliqués.")
        return

    # 🔽 Tri
    sort_by = st.selectbox("Trier les cartes par :", ["Extension", "Nom", "Rareté"])
    filtered_df = filtered_df.sort_values(by=[sort_by, "Nom"]).reset_index(drop=True)

    # 📄 Pagination
    st.markdown("## 📋 Liste des cartes")
    cards_per_page = 50
    total_cards = len(filtered_df)
    total_pages = (total_cards // cards_per_page) + (1 if total_cards % cards_per_page else 0)

    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    start_idx = (page - 1) * cards_per_page
    end_idx = start_idx + cards_per_page
    subset_df = filtered_df.iloc[start_idx:end_idx]

    for index, row in subset_df.iterrows():
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
                key=f"qty_{start_idx + index}"
            )
            filtered_df.at[start_idx + index, "Quantité possédée"] = qty

    # 💾 Export
    if st.button("💾 Sauvegarder ma collection"):
        filename = "ma_collection_yugioh.xlsx"
        filtered_df.to_excel(filename, index=False)
        st.success(f"Collection sauvegardée dans **{filename}**")

if __name__ == "__main__":
    main()
