import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# --- PASSWORT-SCHUTZ FUNKTION ---
def check_password():
    """Gibt True zurück, wenn das richtige Passwort eingegeben wurde."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Anzeige des Login-Fensters
    st.title("🔐 Login - Probst BKS")
    password = st.text_input("Bitte Passwort eingeben", type="password")
    if st.button("Anmelden"):
        if password == "20Anna16": # 
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Falsches Passwort")
    return False

# --- APP-LOGIK STARTET NUR BEI KORREKTEM LOGIN ---
if check_password():
    st.set_page_config(page_title="Probst BKS - ÖNORM F 1053", page_icon="🧯")
    st.title("🧯 Prüfbericht Erstellung")
    st.write("Gemäß ÖNORM F 1053 - Sachkundiger Nr. 2025")

    # --- EINGABEMASKE ---
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
    if st.button("BERICHT ERSTELLEN & SPEICHERN", type="primary"):
        pdf = FPDF()
        pdf.add_page()
        
        # Logos einbinden
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
        
        # Daten-Tabelle
        daten_liste = [
            ("Kunde:", kunde), ("Standort:", standort),
            ("Baujahr / Letzte Überp.:", f"{baujahr} / {letzte}"),
            ("Marke / Type:", f"{marke} / {type_l}"),
            ("Inhalt / Löschmittel:", f"{inhalt} / {lm}"),
            ("Löscherart:", art),
            ("Brandklasse:", brandklasse)
        ]
        for label, wert in daten_liste:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(50, 7, label, border=1, fill=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(140, 7, str(wert), border=1, ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Prüfergebnisse:", ln=True)
        
        pdf.set_font("Arial", "", 10)
        for p, r in ergebnisse.items():
            pdf.cell(140, 6, p, border=1)
            pdf.cell(50, 6, r, border=1, ln=True, align='C')

        pdf.set_font("Arial", "B", 10)
        pdf.cell(140, 7, "Spezifischer Messwert:", border=1, fill=True)
        pdf.cell(50, 7, messwert, border=1, ln=True, align='C')

        # Footer
        pdf.set_y(225)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, "geprüft durch TÜV zertifizierten Sachkundigen: Nr. 2025", ln=True)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 5, "Probst J.", ln=True)
        pdf.ln(5)
        pdf.cell(0, 5, "Unterschrift: ___________________________", ln=True)

        if os.path.exists("Logo_Probst_BKS_querformat.jpg"):
            pdf.image("Logo_Probst_BKS_querformat.jpg", x=105, y=235, w=95)

        # Download Button
        filename = f"Pruefbericht_{kunde}_{datetime.now().strftime('%Y')}.pdf"
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.success(f"PDF erfolgreich generiert!")
        st.download_button("📥 PDF JETZT HERUNTERLADEN", data=pdf_output, file_name=filename)