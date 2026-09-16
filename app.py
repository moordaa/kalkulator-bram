import math
import matplotlib.pyplot as plt
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
    " oraz wizualizacji geometrii bramy skrzydłowej."
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

szerokosc_skrzydla = st.sidebar.slider(
    "Szerokość skrzydła bramy [mm]",
    min_value=1000,
    max_value=3000,
    value=2000,
    step=50,
    help="Całkowita szerokość skrzydła (potrzebna do rysunku)",
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

x_slup_moc, y_slup_moc = 0, A
x_skrzydlo_zamk_moc, y_skrzydlo_zamk_moc = B, 0

dlugosc_zamkniety = math.sqrt(
    (x_skrzydlo_zamk_moc - x_slup_moc) ** 2
    + (y_skrzydlo_zamk_moc - y_slup_moc) ** 2
)

x_koniec_skrzydla_otw = szerokosc_skrzydla * math.cos(alpha)
y_koniec_skrzydla_otw = szerokosc_skrzydla * math.sin(alpha)

x_skrzydlo_otw_moc = B * math.cos(alpha)
y_skrzydlo_otw_moc = B * math.sin(alpha)

dlugosc_otwarty = math.sqrt(
    (x_skrzydlo_otw_moc - x_slup_moc) ** 2
    + (y_skrzydlo_otw_moc - y_slup_moc) ** 2
)

skok_wymagany = abs(dlugosc_otwarty - dlugosc_zamkniety)

# Wyniki tekstowe
st.subheader("📊 Wyniki obliczeń geometrii")

col1, col2, col3 = st.columns(3)
col1.metric("Min. długość (Zamknięta)", f"{dlugosc_zamkniety:.1f} mm")
col2.metric("Maks. długość (Otwarta)", f"{dlugosc_otwarty:.1f} mm")
col3.metric("Wymagany skok tłoka", f"{skok_wymagany:.1f} mm")

if skok_sirownika_katalogowy > 0:
  st.markdown("---")
  if skok_sirownika_katalogowy >= skok_wymagany:
    st.success(
        f"✅ Siłownik o skoku {skok_sirownika_katalogowy} mm da radę"
        f" (wymagane min. {skok_wymagany:.1f} mm)."
    )
  else:
    st.error(
        f"❌ Skok siłownika ({skok_sirownika_katalogowy} mm) jest za mały!"
        f" Potrzebujesz min. {skok_wymagany:.1f} mm."
    )

# --- WIZUALIZACJA GRAFICZNA (WYKRES) ---
st.subheader("📐 Wizualizacja układu (widok z góry)")

fig, ax = plt.subplots(figsize=(6, 6))

ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="gray",
    linestyle="--",
    linewidth=2,
    label="Brama zamknięta",
)
ax.plot(
    [0, x_koniec_skrzydla_otw],
    [0, y_koniec_skrzydla_otw],
    color="blue",
    linewidth=3,
    label=f"Brama otwarta ({kat_otwarcia}°)",
)
ax.plot(
    [x_slup_moc, x_skrzydlo_zamk_moc],
    [y_slup_moc, y_skrzydlo_zamk_moc],
    color="orange",
    linestyle=":",
    linewidth=2,
    label="Siłownik (zamknięty)",
)
ax.plot(
    [x_slup_moc, x_skrzydlo_otw_moc],
    [y_slup_moc, y_skrzydlo_otw_moc],
    color="red",
    linewidth=2,
    label="Siłownik (otwarty)",
)

ax.scatter([0], [0], color="black", s=100, zorder=5, label="Zawias (0,0)")
ax.scatter(
    [x_slup_moc],
    [y_slup_moc],
    color="green",
    s=80,
    zorder=5,
    label="Mocowanie na słupku",
)
ax.scatter(
    [x_skrzydlo_otw_moc],
    [y_skrzydlo_otw_moc],
    color="purple",
    s=80,
    zorder=5,
    label="Mocowanie na skrzydle",
)

ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.6)
ax.axhline(0, color="black", linewidth=1)
ax.axvline(0, color="black", linewidth=1)
ax.set_xlabel("Oś X [mm]")
ax.set_ylabel("Oś Y [mm]")
ax.legend(loc="upper right", fontsize=8)

st.pyplot(fig)
