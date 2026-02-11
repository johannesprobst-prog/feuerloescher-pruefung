import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# --- PASSWORT-SCHUTZ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🔐 Login - Probst BKS")
    password = st.text_input("Bitte Passwort eingeben", type="password")
    if st.button("Anmelden"):
        if password == "DeinSicheresPasswort123": # <--- ÄNDERE DIESES PASSWORT!
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Falsches Passwort")
    return False

if check_password():
    st.set_page_config(page_title="Probst BKS - ÖNORM F 1053", page_icon="🧯")
    st.title("🧯 Prüfbericht Erstellung")
    st.write("Gemäß ÖNORM F 1053 - Sachkundiger Nr. 2025")

    # --- EINGABEMASKE (REIHENFOLGE ANGEPASST) ---
    with st.expander("📝 Stammdaten", expanded=True):
        kunde = st.text_input("Kunde")
        standort = st.text_input("Standort")
        
        col1, col2 = st.columns(2)
        with col1:
            marke = st.text_input("Marke")
            baujahr = st.text_input("Baujahr")
            inhalt = st.text_input("Inhalt (z.B. 6kg / 9l)")
        with col2:
            type_l = st.text_input("Type")
            letzte = st.text_input("Letzte Überprüfung")
            brandklasse = st.text_input("Brandklasse")

    with st.expander("🧪 Löschmittel & Technik", expanded=True):
        lm = st.selectbox("Löschmittel", ["Schaum", "Wasser", "Pulver", "CO2"])
        art = st.selectbox("Löscherart", ["Dauerdrucklöscher", "Aufladelöscher"])
        messwert = st.text_input("Messwert (Druck/Gewicht)", value="OK")

    with st.expander("✅ Checkliste ÖNORM F 1053", expanded=True):
        items = ["Standortmarkierung vorhanden", "Halterung OK", "Typenschild lesbar", 
                 "Behälter OK", "Schlauch OK", "Armaturen/Sicherung OK", 
                 "Auslöseeinrichtung OK", "Dichtheit geprüft", "Gewinde gängig", "Schlauch durchgängig"]
        ergebnisse = {}
        for item in items:
            ergebnisse[item] = "OK" if st.checkbox(item, value=True, key=item) else "MANGEL"
        
        if lm == "Pulver":
            riesel = st.checkbox("Rieselfähigkeit des Pulvers", value=True)
            ergebnisse["Rieselfähigkeit des Pulvers"] = "OK" if riesel else "MANGEL"

    # --- PDF GENERIERUNG ---
    if st.button("BERICHT ERSTELLEN", type="primary"):
        pdf = FPDF()
        pdf.add_page()
        
        # Logos (Bilddateien müssen im GitHub Ordner liegen)
        if os.path.exists("Logo kopf.png"):
            pdf.image("Logo kopf.png", x=10, y=10, w=35)
        
        pdf.set_font("Arial", "B", 16)
        pdf.set_xy(50, 15)
        pdf.cell(0, 10, "Prüfbericht Feuerlöscher nach ÖNORM F 1053", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_x(50)
        pdf.cell(0, 5, f"Datum: {datetime.now().strftime('%d.%m.%Y')}", ln=True)

        pdf.ln(20)
        pdf.set_fill_color(240, 240, 240)
        
        # Daten-Tabelle REIHENFOLGE IM PDF ANGEPASST
        daten_liste = [
            ("Kunde:", kunde), 
            ("Standort:", standort),
            ("Marke:", marke),
            ("Type:", type_l),
            ("Baujahr:", baujahr),
            ("Letzte Überprüfung:", letzte),
            ("Inhalt:", inhalt),
            ("Brandklasse:", brandklasse),
            ("Löschmittel / Art:", f"{lm} / {art}")
        ]
        
        for label, wert in daten_liste:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(50, 7, label, border=1, fill=True)
            pdf.