import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io

# --- PASSWORT-SCHUTZ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🔐 Login - Probst BKS")
    password = st.text_input("Bitte Passwort eingeben", type="password")
    if st.button("Anmelden"):
        # HIER DEIN PASSWORT EINTRAGEN
        if password == "20Anna16": 
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Falsches Passwort")
    return False

if check_password():
    st.set_page_config(page_title="Probst BKS - ÖNORM F 1053", page_icon="🧯")
    st.title("🧯 Prüfbericht Erstellung")
    st.write("Sachkundiger Nr. 2025 - Probst Brand- und Katastrophenschutz")

    # --- EINGABEMASKE ---
    with st.expander("📝 Stammdaten", expanded=True):
        kunde = st.text_input("Kunde")
        standort = st.text_input("Standort")
        
        col1, col2 = st.columns(2)
        with col1:
            marke = st.text_input("Marke")
            type_l = st.text_input("Type")
            baujahr = st.text_input("Baujahr")
        with col2:
            letzte = st.text_input("Letzte Überprüfung")
            inhalt = st.text_input("Inhalt (z.B. 6kg / 9l)")
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

    # --- UNTERSCHRIFTENFELD ---
    st.subheader("✍️ Unterschrift des Sachkundigen")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="canvas",
    )

    # --- PDF GENERIERUNG ---
    if st.button("BERICHT ERSTELLEN", type="primary"):
        if not kunde:
            st.error("Bitte geben Sie einen Kunden ein!")
        else:
            try:
                pdf = FPDF()
                pdf.add_page()
                
                # Logo oben links
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
                
                # Stammdaten Tabelle (Deine gewünschte Reihenfolge)
                daten_liste = [
                    ("Kunde:", kunde), ("Standort:", standort),
                    ("Marke:", marke), ("Type:", type_l),
                    ("Baujahr:", baujahr), ("Letzte Prüfung:", letzte),
                    ("Inhalt:", inhalt), ("Brandklasse:", brandklasse),
                    ("Löschmittel / Art:", f"{lm} / {art}")
                ]
                
                for label, wert in daten_liste:
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(50, 7, label, border=1, fill=True)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(140, 7, str(wert), border=1, ln=True)

                pdf.ln(5)
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, "Pruefergebnisse (Bewertung):", ln=True)
                
                pdf.set_font("Arial", "", 10)
                for p, r in ergebnisse.items():
                    pdf.cell(140, 6, str(p), border=1)
                    pdf.cell(50, 6, str(r), border=1, ln=True, align='C')

                pdf.set_font("Arial", "B", 10)
                pdf.cell(140, 7, "Spezifischer Messwert (Druck/Gewicht):", border=1, fill=True)
                pdf.cell(50, 7, str(messwert), border=1, ln=True, align='C')

                # Unterschrift einbetten
                if canvas_result.image_data is not None:
                    # Bilddaten von Canvas verarbeiten
                    img_data = canvas_result.image_data
                    im = Image.fromarray(img_data.astype('uint8'), 'RGBA')
                    # In PNG umwandeln für das PDF
                    with io.BytesIO() as output:
                        im.save(output, format="PNG")
                        pdf.image(output, x=25, y=230, w=50)

                # Footer Bereich
                pdf.set_y(225)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 5, "geprüft durch TÜV zertifizierten Sachkundigen: Nr. 2025", ln=True)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 5, "Probst J.", ln=True)
                pdf.ln(5)
                pdf.cell(0, 5, "Unterschrift: ___________________________", ln=True)

                # Logo unten rechts
                if os.path.exists("Logo_Probst_BKS_querformat.jpg"):
                    pdf.image("Logo_Probst_BKS_querformat.jpg", x=105, y=235, w=95)

                # PDF Download Vorbereitung
                pdf_bytes = pdf.output()
                
                # Dateiname generieren: "Pruefbericht_Kunde_Standort.pdf"
                # Wir entfernen Sonderzeichen, damit der Download sicher klappt
                safe_kunde = "".join(x for x in kunde if x.isalnum() or x in "._- ")
                safe_standort = "".join(x for x in standort if x.isalnum() or x in "._- ")
                clean_filename = f"Pruefbericht_{safe_kunde}_{safe_standort}.pdf".replace(" ", "_")

                st.success(f"PDF für {kunde} am Standort {standort} erfolgreich generiert!")
                st.download_button(
                    label="📥 PDF JETZT HERUNTERLADEN",
                    data=bytes(pdf_bytes),
                    file_name=clean_filename,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Fehler bei der PDF-Erstellung: {e}")