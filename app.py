import io
import os
import re
from datetime import datetime
from PIL import Image
import streamlit as st
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

# 1. Muss der allererste Streamlit-Befehl der App sein
st.set_page_config(
    page_title="Probst BKS - ÖNORM F 1053",
    page_icon="🧯",
    layout="centered",
)


def sanitize_text(text: str) -> str:
    """Verhindert FPDF-Abstürze bei Umlauten mit Standard-Schriften (Latin-1)."""
    if not text:
        return ""
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    return text.encode("latin-1", "replace").decode("latin-1")


# --- PASSWORT-SCHUTZ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔐 Login - Probst BKS")
    password = st.text_input("Bitte Passwort eingeben", type="password")

    if st.button("Anmelden"):
        if password == "20Anna16":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Falsches Passwort")
    return False


if check_password():
    st.title("🧯 Prüfbericht Erstellung")
    st.caption("Sachkundiger Nr. 2025 – Probst Brand- und Katastrophenschutz")

    # Session State initialisieren, damit das PDF nach Klicks erhalten bleibt
    if "pdf_data" not in st.session_state:
        st.session_state["pdf_data"] = None
        st.session_state["pdf_filename"] = ""

    # --- EINGABEMASKE ---
    with st.expander("📝 Stammdaten", expanded=True):
        kunde = st.text_input("Kunde", key="input_kunde")
        standort = st.text_input("Standort", key="input_standort")

        col1, col2 = st.columns(2)
        with col1:
            marke = st.text_input("Marke", key="input_marke")
            type_l = st.text_input("Type", key="input_type")
            baujahr = st.text_input("Baujahr", key="input_baujahr")
        with col2:
            letzte = st.text_input("Letzte Überprüfung", key="input_letzte")
            inhalt = st.text_input("Inhalt (z.B. 6kg / 9l)", key="input_inhalt")
            brandklasse = st.text_input("Brandklasse", key="input_brandklasse")

    with st.expander("🧪 Löschmittel & Technik", expanded=True):
        col_lm1, col_lm2 = st.columns(2)
        with col_lm1:
            lm = st.selectbox(
                "Löschmittel", ["Schaum", "Wasser", "Pulver", "CO2"]
            )
        with col_lm2:
            art = st.selectbox(
                "Löscherart", ["Dauerdrucklöscher", "Aufladelöscher"]
            )
        messwert = st.text_input("Messwert (Druck/Gewicht)", value="OK")

    with st.expander("✅ Checkliste ÖNORM F 1053", expanded=True):
        items = [
            "Standortmarkierung vorhanden",
            "Halterung OK",
            "Typenschild lesbar",
            "Behälter OK",
            "Schlauch OK",
            "Armaturen/Sicherung OK",
            "Auslöseeinrichtung OK",
            "Dichtheit geprüft",
            "Gewinde gängig",
            "Schlauch durchgängig",
        ]
        ergebnisse = {}
        for item in items:
            ergebnisse[item] = (
                "OK" if st.checkbox(item, value=True, key=item) else "MANGEL"
            )

        if lm == "Pulver":
            riesel = st.checkbox("Rieselfähigkeit des Pulvers", value=True)
            ergebnisse["Rieselfähigkeit des Pulvers"] = (
                "OK" if riesel else "MANGEL"
            )

    # --- UNTERSCHRIFTENFELD (mit Fix für return_image_data) ---
    st.subheader("✍️ Unterschrift des Sachkundigen")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=140,
        width=380,
        drawing_mode="freedraw",
        update_streamlit=True,
        return_image_data=True,
        key="canvas",
    )

    # --- PDF GENERIERUNG ---
    if st.button("BERICHT ERSTELLEN", type="primary"):
        if not kunde.strip():
            st.error("⚠️ Bitte geben Sie mindestens einen Kundennamen ein!")
        else:
            try:
                pdf = FPDF(orientation="P", unit="mm", format="A4")
                pdf.set_auto_page_break(auto=False)
                pdf.add_page()

                # 1. Kopfbereich & Logo
                if os.path.exists("Logo kopf.png"):
                    pdf.image("Logo kopf.png", x=10, y=10, w=35)

                pdf.set_font("Arial", "B", 15)
                pdf.set_xy(50, 12)
                pdf.cell(
                    0,
                    8,
                    sanitize_text(
                        "Prüfbericht Feuerlöscher nach ÖNORM F 1053"
                    ),
                    ln=True,
                )
                pdf.set_font("Arial", "", 10)
                pdf.set_x(50)
                pdf.cell(
                    0,
                    6,
                    f"Datum: {datetime.now().strftime('%d.%m.%Y')}",
                    ln=True,
                )

                # 2. Stammdaten Tabelle
                pdf.set_y(32)
                pdf.set_fill_color(240, 240, 240)

                daten_liste = [
                    ("Kunde:", kunde),
                    ("Standort:", standort),
                    ("Marke:", marke),
                    ("Type:", type_l),
                    ("Baujahr:", baujahr),
                    ("Letzte Prüfung:", letzte),
                    ("Inhalt:", inhalt),
                    ("Brandklasse:", brandklasse),
                    ("Löschmittel / Art:", f"{lm} / {art}"),
                ]

                for label, wert in daten_liste:
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(45, 6, sanitize_text(label), border=1, fill=True)
                    pdf.set_font("Arial", "", 9)
                    pdf.cell(
                        145,
                        6,
                        sanitize_text(str(wert or "-")),
                        border=1,
                        ln=True,
                    )

                # 3. Checkliste
                pdf.ln(3)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(
                    0, 6, sanitize_text("Prüfergebnisse (Bewertung):"), ln=True
                )

                pdf.set_font("Arial", "", 8.5)
                for punkt, status in ergebnisse.items():
                    pdf.cell(145, 5, sanitize_text(str(punkt)), border=1)
                    if status == "MANGEL":
                        pdf.set_text_color(180, 0, 0)
                        pdf.cell(
                            45,
                            5,
                            status,
                            border=1,
                            ln=True,
                            align="C",
                        )
                        pdf.set_text_color(0, 0, 0)
                    else:
                        pdf.cell(
                            45,
                            5,
                            status,
                            border=1,
                            ln=True,
                            align="C",
                        )

                # Messwertzeile
                pdf.set_font("Arial", "B", 9)
                pdf.cell(
                    145,
                    6,
                    sanitize_text("Spezifischer Messwert (Druck/Gewicht):"),
                    border=1,
                    fill=True,
                )
                pdf.cell(
                    45,
                    6,
                    sanitize_text(str(messwert)),
                    border=1,
                    ln=True,
                    align="C",
                )

                # 4. Footer & Unterschrift
                footer_y = 230
                pdf.set_y(footer_y)
                pdf.set_font("Arial", "", 9)
                pdf.cell(
                    0,
                    5,
                    sanitize_text(
                        "Geprüft durch TÜV-zertifizierten Sachkundigen: Nr. 2025"
                    ),
                    ln=True,
                )
                pdf.set_font("Arial", "B", 9)
                pdf.cell(0, 5, "Probst J.", ln=True)
                pdf.ln(2)
                pdf.set_font("Arial", "", 8)
                pdf.cell(
                    0,
                    4,
                    "Unterschrift: ___________________________",
                    ln=True,
                )

                # Unterschrift einbinden, falls vorhanden
                if canvas_result is not None and canvas_result.image_data is not None:
                    # Prüfen, ob gezeichnet wurde (nicht nur transparenter Hintergrund)
                    if canvas_result.image_data.any():
                        img_data = canvas_result.image_data
                        im = Image.fromarray(img_data.astype("uint8"), "RGBA")
                        with io.BytesIO() as output:
                            im.save(output, format="PNG")
                            pdf.image(output, x=22, y=footer_y + 8, w=48)

                # Firmenlogo unten rechts
                if os.path.exists("Logo_Probst_BKS_querformat.jpg"):
                    pdf.image(
                        "Logo_Probst_BKS_querformat.jpg", x=120, y=235, w=75
                    )

                # 5. Robuster PDF-Export (kompatibel mit fpdf und fpdf2)
                raw_out = pdf.output()
                if isinstance(raw_out, str):
                    pdf_bytes = raw_out.encode("latin-1")
                elif isinstance(raw_out, bytearray):
                    pdf_bytes = bytes(raw_out)
                else:
                    pdf_bytes = raw_out

                # Dateinamen bereinigen
                safe_kunde = (
                    re.sub(r"[^\w\s-]", "", kunde).strip().replace(" ", "_")
                )
                safe_standort = (
                    re.sub(r"[^\w\s-]", "", standort).strip().replace(" ", "_")
                )
                clean_filename = f"Pruefbericht_{safe_kunde or 'Kunde'}_{safe_standort or 'Standort'}.pdf"

                # Im Speicher halten, damit der Download-Button stabil bleibt
                st.session_state["pdf_data"] = pdf_bytes
                st.session_state["pdf_filename"] = clean_filename
                st.success("✅ Prüfbericht erfolgreich generiert!")

            except Exception as e:
                st.error(f"❌ Fehler bei der PDF-Erstellung: {e}")

    # Download-Button bleibt sichtbar, sobald Daten im State liegen
    if st.session_state.get("pdf_data") is not None:
        st.download_button(
            label="📥 PDF JETZT HERUNTERLADEN",
            data=st.session_state["pdf_data"],
            file_name=st.session_state["pdf_filename"],
            mime="application/pdf",
        )
