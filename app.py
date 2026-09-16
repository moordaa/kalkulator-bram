import math
import streamlit as st

# Konfiguracja strony
st.set_page_config(
    page_title="Kalkulator Geometrii Siłowników Bramowych",
    page_icon="🚪",
    layout="centered",
)

st.title("🚪 Kalkulator Geometrii Siłowników Bramowych")
st.markdown(
    "Narzędzie do obliczania wymiarów montażowych ($A$ i $B$), skoku siłownika"
    " oraz sprawdzania geometrii dla bram skrzydłowych."
)

# Panel boczny z parametrami wejściowymi
st.sidebar.header("Parametry montażowe")

A = st.sidebar.slider(
    "Wymiar A (Słupek) [mm]",
    min_value=50,
    max_value=300,
    value=150,
    step=5,
    help=(
        "Odległość osi zawiasu od punktu mocowania na słupku (w osi"
        " prostopadłej do zamkniętej bramy)"
    ),
)

B = st.sidebar.slider(
    "Wymiar B (Skrzydło) [mm]",
    min_value=50,
    max_value=300,
    value=150,
    step=5,
    help="Odległość osi zawiasu od punktu mocowania na skrzydle bramy",
)

kat_otwarcia = st.sidebar.slider(
    "Kąt otwarcia bramy [°]",
    min_value=80,
    max_value=130,
    value=90,
    step=1,
    help="Docelowy kąt otwarcia skrzydła",
)

skok_sirownika_katalogowy = st.sidebar.number_input(
    "Skok Twojego siłownika (opcjonalnie) [mm]",
    min_value=0,
    max_value=600,
    value=400,
    step=10,
    help=(
        "Wpisz skok, aby sprawdzić czy siłownik fizycznie obsłuży ten kąt"
        " (0 = pomiń)"
    ),
)

# Obliczenia trygonometryczne
alpha = math.radians(kat_otwarcia)

x_slup, y_slup = 0, A
x_skrzydlo_zamk, y_skrzydlo_zamk = B, 0
dlugosc_zamkniety = math.sqrt(
    (x_skrzydlo_zamk - x_slup) ** 2 + (y_skrzydlo_zamk - y_slup) ** 2
)

x_skrzydlo_otw = B * math.cos(alpha)
y_skrzydlo_otw = B * math.sin(alpha)
dlugosc_otwarty = math.sqrt(
    (x_skrzydlo_otw - x_slup) ** 2 + (y_skrzydlo_otw - y_slup) ** 2
)

skok_wymagany = abs(dlugosc_otwarty - dlugosc_zamkniety)

# Wyniki
st.subheader("📊 Wyniki obliczeń geometrii")

col1, col2, col3 = st.columns(3)
col1.metric("Min. długość (Zamknięta)", f"{dlugosc_zamkniety:.1f} mm")
col2.metric("Maks. długość (Otwarta)", f"{dlugosc_otwarty:.1f} mm")
col3.metric("Wymagany skok tłoka", f"{skok_wymagany:.1f} mm")

if skok_sirownika_katalogowy > 0:
  st.markdown("---")
  st.subheader("🔍 Weryfikacja wybranego siłownika")
  if skok_sirownika_katalogowy >= skok_wymagany:
    st.success(
        f"✅ Twój siłownik o skoku {skok_sirownika_katalogowy} mm **poradzi"
        f" sobie** z tymi wymiarami (wymagane minimum to"
        f" {skok_wymagany:.1f} mm)."
    )
  else:
    st.error(
        f"❌ Uwaga! Skok Twojego siłownika ({skok_sirownika_katalogowy} mm)"
        f" jest **za mały** dla tych wymiarów i kąta! Potrzebujesz co"
        f" najmniej {skok_wymagany:.1f} mm skoku."
    )
