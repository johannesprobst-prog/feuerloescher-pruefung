import io
import os
import re
from datetime import datetime
import numpy as np
from PIL import Image
import streamlit as st
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

# 1. Muss der allererste Aufruf sein
st.set_page_config(
    page_title="Probst BKS - ÖNORM F 1053",
    page_icon="🧯",
    layout="centered",
)


def fpdf_clean(text: str) -> str:
    """
    Ermöglicht echte deutsche Umlaute (ä, ö, ü, ß, Ä, Ö, Ü) in FPDF
    und fängt nur inkompatible Sonderzeichen (wie Gedankenstriche) ab.
    """
    if not text:
        return ""
    replacements = {
        "–": "-",
        "—": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "•": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
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

    # Session State initialisieren
    if "pdf_data" not in st.session_state:
        st.session_state["pdf_data"] = None
        st.session_state["pdf_filename"] = ""

    # --- EINGABEMASKE ---
    with st.expander("📝 Stammdaten", expanded=True):
        kunde = st.text_input("Kunde", value="Stadtamt Braunau am Inn")
        standort = st.text_input("Standort", value="Labberholzweg 48")

        col1, col2 = st.columns(2)
        with col1:
            marke = st.text_input("Marke", value="Gloria")
            type_l = st.text_input("Type", value="PD 6 GA")
            baujahr = st.text_input("Baujahr", value="2024")
        with col2:
            letzte = st.text_input("Letzte Überprüfung", value="09.2024")
            inhalt = st.text_input("Inhalt (z.B. 6kg / 9l)", value="6kg")
            brandklasse = st.text_input("Brandklasse", value="A, B, C")

    with st.expander("🧪 Löschmittel & Technik", expanded=True):
        col_lm1, col_lm2 = st.columns(2)
        with col_lm1:
            lm = st.selectbox(
                "Löschmittel",
                ["Pulver", "Schaum", "Wasser", "CO2"],
                index=0,
            )
        with col_lm2:
            art = st.selectbox(
                "Löscherart",
                ["Dauerdrucklöscher", "Aufladelöscher"],
                index=0,
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

    # --- UNTERSCHRIFTENFELD ---
    st.subheader("✍️ Unterschrift des Sachkundigen")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=130,
        width=380,
        drawing_mode="freedraw",
        update_streamlit=True,
        return_image_data=True,
        key="sig_canvas",
    )

    # --- PDF GENERIERUNG ---
    if st.button("BERICHT ERSTELLEN", type="primary"):
        if not kunde.strip():
            st.error("⚠️ Bitte geben Sie mindestens einen Kundennamen ein!")
        else:
            try:
                pdf = FPDF(orientation="P", unit="mm", format="A4")
                pdf.set_margins(left=10, top=10, right=10)
                pdf.set_auto_page_break(auto=False)
                pdf.add_page()

                # --- 1. KOPFBEREICH & LOGO ---
                # Logo oben links
                logo_h = 32
                if os.path.exists("Logo kopf.png"):
                    pdf.image("Logo kopf.png", x=10, y=10, w=32)

                # Titel & Metadaten rechts neben dem Logo
                pdf.set_xy(48, 12)
                pdf.set_font("Arial", "B", 13.5)
                pdf.cell(
                    152,
                    7,
                    fpdf_clean("Prüfbericht Feuerlöscher nach ÖNORM F 1053"),
                    ln=True,
                )

                pdf.set_x(48)
                pdf.set_font("Arial", "", 9.5)
                pdf.set_text_color(80, 80, 80)
                pdf.cell(
                    152,
                    5,
                    fpdf_clean(
                        "Sachkundiger Nr. 2025 - Probst Brand- und Katastrophenschutz"
                    ),
                    ln=True,
                )

                pdf.set_x(48)
                pdf.set_font("Arial", "B", 9.5)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(
                    152,
                    6,
                    f"Datum: {datetime.now().strftime('%d.%m.%Y')}",
                    ln=True,
                )

                # --- 2. STAMMDATEN-TABELLE (Start erst unter dem Logo!) ---
                y_start_table = 46  # Garantiert unter dem Logo!
                pdf.set_y(y_start_table)
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

                col_w_label = 48
                col_w_val = 142  # 48 + 142 = 190 mm (exakt DIN A4 Breite abzüglich Ränder)

                for label, wert in daten_liste:
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(
                        col_w_label,
                        5.8,
                        fpdf_clean(label),
                        border=1,
                        fill=True,
                    )
                    pdf.set_font("Arial", "", 9)
                    pdf.cell(
                        col_w_val,
                        5.8,
                        fpdf_clean(str(wert or "-")),
                        border=1,
                        ln=True,
                    )

                # --- 3. PRÜFERGEBNISSE CHECKLISTE ---
                pdf.ln(4)
                pdf.set_font("Arial", "B", 10.5)
                pdf.cell(
                    0, 6, fpdf_clean("Prüfergebnisse (Bewertung):"), ln=True
                )

                pdf.set_font("Arial", "", 8.5)
                col_check_label = 150
                col_check_res = 40

                for punkt, status in ergebnisse.items():
                    pdf.cell(
                        col_check_label, 5.2, fpdf_clean(str(punkt)), border=1
                    )
                    if status == "MANGEL":
                        pdf.set_font("Arial", "B", 8.5)
                        pdf.set_text_color(190, 0, 0)
                        pdf.cell(
                            col_check_res,
                            5.2,
                            status,
                            border=1,
                            ln=True,
                            align="C",
                        )
                        pdf.set_font("Arial", "", 8.5)
                        pdf.set_text_color(0, 0, 0)
                    else:
                        pdf.cell(
                            col_check_res,
                            5.2,
                            status,
                            border=1,
                            ln=True,
                            align="C",
                        )

                # Spezifischer Messwert
                pdf.set_font("Arial", "B", 9)
                pdf.cell(
                    col_check_label,
                    6,
                    fpdf_clean("Spezifischer Messwert (Druck/Gewicht):"),
                    border=1,
                    fill=True,
                )
                pdf.cell(
                    col_check_res,
                    6,
                    fpdf_clean(str(messwert)),
                    border=1,
                    ln=True,
                    align="C",
                )

                # --- 4. FOOTER & UNTERSCHRIFT ---
                footer_y = 230
                pdf.set_y(footer_y)

                # Linke Spalte: Prüferdaten
                pdf.set_font("Arial", "", 9)
                pdf.cell(
                    100,
                    5,
                    fpdf_clean(
                        "Geprüft durch TÜV-zertifizierten Sachkundigen: Nr. 2025"
                    ),
                    ln=True,
                )
                pdf.set_font("Arial", "B", 9.5)
                pdf.cell(100, 5, "Probst J.", ln=True)

                # Unterschriftsfeld
                pdf.set_y(footer_y + 12)
                pdf.set_font("Arial", "", 8.5)
                pdf.cell(
                    100, 4, "Unterschrift: ___________________________", ln=True
                )

                # Unterschrift sauber und transparent einbetten (keine Textüberdeckung)
                if (
                    canvas_result is not None
                    and canvas_result.image_data is not None
                ):
                    raw_data = canvas_result.image_data.astype(np.uint8)
                    # Prüfen, ob wirklich gezeichnet wurde (nicht nur leere weiße/transparente Pixel)
                    has_drawing = (
                        np.any(raw_data[:, :, :3] < 200)
                        if raw_data.shape[-1] >= 3
                        else False
                    )

                    if has_drawing:
                        im = Image.fromarray(raw_data, "RGBA")
                        # Weiß in Transparenz umwandeln, damit nichts überdeckt wird
                        r, g, b, a = im.split()
                        np_im = np.array(im)
                        # Pixel die fast weiß sind transparent machen:
                        white_mask = (
                            (np_im[:, :, 0] > 230)
                            & (np_im[:, :, 1] > 230)
                            & (np_im[:, :, 2] > 230)
                        )
                        np_im[white_mask, 3] = 0
                        clean_sig = Image.fromarray(np_im, "RGBA")

                        with io.BytesIO() as sig_buf:
                            clean_sig.save(sig_buf, format="PNG")
                            # Platziert die Unterschrift exakt AUF der Unterschriftslinie
                            pdf.image(
                                sig_buf, x=26, y=footer_y + 5, w=45, h=16
                            )

                # Rechtes Firmenlogo unten
                if os.path.exists("Logo_Probst_BKS_querformat.jpg"):
                    pdf.image(
                        "Logo_Probst_BKS_querformat.jpg", x=122, y=228, w=78
                    )

                # --- 5. EXPORT ---
                raw_out = pdf.output()
                if isinstance(raw_out, str):
                    pdf_bytes = raw_out.encode("latin-1")
                elif isinstance(raw_out, bytearray):
                    pdf_bytes = bytes(raw_out)
                else:
                    pdf_bytes = raw_out

                safe_kunde = (
                    re.sub(r"[^\w\s-]", "", kunde).strip().replace(" ", "_")
                )
                safe_standort = (
                    re.sub(r"[^\w\s-]", "", standort).strip().replace(" ", "_")
                )
                clean_filename = f"Pruefbericht_{safe_kunde or 'Kunde'}_{safe_standort or 'Standort'}.pdf"

                st.session_state["pdf_data"] = pdf_bytes
                st.session_state["pdf_filename"] = clean_filename
                st.success("✅ Prüfbericht erfolgreich generiert!")

            except Exception as e:
                st.error(f"❌ Fehler bei der PDF-Erstellung: {e}")

    # Stabiler Download-Button
    if st.session_state.get("pdf_data") is not None:
        st.download_button(
            label="📥 PDF JETZT HERUNTERLADEN",
            data=st.session_state["pdf_data"],
            file_name=st.session_state["pdf_filename"],
            mime="application/pdf",
        )
