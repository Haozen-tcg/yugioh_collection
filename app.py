import streamlit as st
import pandas as pd
import json
import os

# ========== Chargement des cartes ==========
def load_cards():
    with open("all_cards.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    data = raw_data.get("data", [])
    cards = []

    for card in data:
        sets = card.get("card_sets", [])
        image_data = card.get("card_images", [{}])[0]

        if sets:
            for set_info in sets:
                cards.append({
                    "Nom": card.get("name", "Inconnu"),
                    "Extension": set_info.get("set_name", "Inconnue"),
                    "Rareté": set_info.get("set_rarity", ""),
                    "Race": card.get("race", ""),
                    "Image_URL": image_data.get("image_url", ""),
                    "Code": set_info.get("set_code", ""),
                    "Quantité possédée": 0
                })
        else:
            cards.append({
                "Nom": card.get("name", "Inconnu"),
                "Extension": "Non spécifiée",
                "Rareté": "",
                "Race": card.get("race", ""),
                "Image_URL": image_data.get("image_url", ""),
                "Code": "",
                "Quantité possédée": 0
            })

    return pd.DataFrame(cards)

# ========== Sauvegarde automatique ==========
def save_user_collection(df, user_file):
    df_to_save = df[["Nom", "Extension", "Quantité possédée"]]
    df_to_save.to_excel(user_file, index=False)

# ========== Interface principale ==========
def main():
    st.set_page_config(layout="wide")
    st.title("🃏 Gestion de collection Yu-Gi-Oh!")

    # --- Choix de l'utilisateur
    user = st.text_input("Entrez votre nom ou pseudo :", "")
    if not user:
        st.warning("Veuillez entrer un nom pour charger votre collection.")
        st.stop()

    user_file = f"collection_{user.lower().replace(' ', '_')}.xlsx"

    # --- Chargement cartes
    df = load_cards()

    # --- Chargement collection existante
    if os.path.exists(user_file):
        try:
            user_df = pd.read_excel(user_file)
            df = df.merge(user_df, on=["Nom", "Extension"], how="left", suffixes=("", "_saved"))
            df["Quantité possédée"] = df["Quantité possédée_saved"].fillna(0).astype(int)
            df.drop(columns=["Quantité possédée_saved"], inplace=True)
        except Exception as e:
            st.error(f"Erreur lors du chargement de la collection : {e}")
    else:
        df["Quantité possédée"] = 0

    # --- Barre de recherche
    with st.sidebar:
        recherche = st.text_input("🔍 Rechercher une carte par nom")
        possede_seulement = st.checkbox("Afficher uniquement les cartes que je possède")
        if st.button("🔄 Réinitialiser les filtres"):
            recherche = ""
            possede_seulement = False

    if recherche:
        df = df[df["Nom"].str.contains(recherche, case=False, na=False)]

    if possede_seulement:
        df = df[df["Quantité possédée"] > 0]

    # --- Pagination
    page_size = 12
    total_pages = (len(df) - 1) // page_size + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

    start = (page - 1) * page_size
    end = start + page_size
    df_page = df.iloc[start:end]

    # --- Affichage des cartes
    for i, row in df_page.iterrows():
        cols = st.columns([1, 3, 2])
        with cols[0]:
            st.image(row["Image_URL"], width=100)
        with cols[1]:
            st.markdown(f"**{row['Nom']}**")
            st.markdown(f"`{row['Code']}` — *{row['Extension']}*")
            st.markdown(f"💎 Rareté : `{row['Rareté']}`")
        with cols[2]:
            qty = st.number_input(f"Quantité ({row['Nom']})", min_value=0, value=int(row["Quantité possédée"]), key=f"qty_{i}")
            df.at[i, "Quantité possédée"] = qty

    # --- Sauvegarde automatique
    save_user_collection(df, user_file)
    st.success("✅ Collection sauvegardée automatiquement.")

# ========== Lancement ==========
if __name__ == "__main__":
    main()
