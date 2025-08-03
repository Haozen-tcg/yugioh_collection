import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO

# ========== Chargement des cartes depuis JSON ==========
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

# ========== Sauvegarde automatique utilisateur ==========
def save_user_collection(df, user_file):
    df_to_save = df[["Nom", "Extension", "Rareté", "Code", "Quantité possédée"]]
    df_to_save.sort_values(by=["Extension", "Nom"], inplace=True)
    df_to_save.to_excel(user_file, index=False, engine='openpyxl')

# ========== Génération export Excel ==========    
def generate_excel_file(df):
    df_export = df[df["Quantité possédée"] > 0][["Nom", "Extension", "Rareté", "Code", "Quantité possédée"]]
    df_export = df_export.sort_values(by=["Extension", "Nom"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Ma Collection")
    output.seek(0)
    return output

# ========== Application principale ==========
def main():
    st.set_page_config(layout="wide")
    st.title("🃏 Gestion de collection Yu-Gi-Oh!")

    user = st.text_input("Entrez votre nom ou pseudo :", "")
    if not user:
        st.warning("Veuillez entrer un nom.")
        st.stop()

    user_file = f"collection_{user.lower().replace(' ', '_')}.xlsx"
    df = load_cards()

    # Charger la collection sauvegardée
    if os.path.exists(user_file):
        try:
            saved_df = pd.read_excel(user_file)
            df = df.merge(saved_df, on=["Nom", "Extension", "Rareté", "Code"], how="left", suffixes=("", "_saved"))
            df["Quantité possédée"] = df["Quantité possédée_saved"].fillna(0).astype(int)
            df.drop(columns=["Quantité possédée_saved"], inplace=True)
        except Exception as e:
            st.error(f"Erreur lors du chargement de la collection : {e}")

    # Sidebar : filtres
    with st.sidebar:
        # Filtre multi-extension
        extensions = sorted(df["Extension"].unique())
        selected_extensions = st.multiselect("📦 Filtrer par extension", extensions, default=extensions)

        recherche = st.text_input("🔍 Rechercher une carte")
        possede = st.checkbox("📦 Afficher uniquement les cartes que je possède")
        if st.button("🔁 Réinitialiser les filtres"):
            recherche = ""
            possede = False
            selected_extensions = extensions

    # Appliquer filtre extension
    df = df[df["Extension"].isin(selected_extensions)]

    # Appliquer les autres filtres
    if recherche:
        df = df[df["Nom"].str.contains(recherche, case=False, na=False)]
    if possede:
        df = df[df["Quantité possédée"] > 0]

    # Pagination
    page_size = 12
    total_pages = max((len(df) - 1) // page_size + 1, 1)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

    start = (page - 1) * page_size
    end = start + page_size
    df_page = df.iloc[start:end]

    # Affichage des cartes
    for i, row in df_page.iterrows():
        cols = st.columns([1, 3, 2])
        with cols[0]:
            st.image(row["Image_URL"], width=100)
        with cols[1]:
            st.markdown(f"**{row['Nom']}**")
            st.markdown(f"`{row['Code']}` — *{row['Extension']}*")
            st.markdown(f"💎 `{row['Rareté']}`")
        with cols[2]:
            qty = st.number_input(f"Quantité ({row['Nom']})", min_value=0, value=int(row["Quantité possédée"]), key=f"qty_{i}")
            df.at[i, "Quantité possédée"] = qty

    # Sauvegarde automatique
    save_user_collection(df, user_file)
    st.success("✅ Collection sauvegardée.")

    # Export Excel
    st.markdown("### 📥 Export Excel")
    excel_data = generate_excel_file(df)
    st.download_button(
        label="Télécharger ma collection",
        data=excel_data,
        file_name=f"yugioh_collection_{user}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()
