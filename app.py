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
    "Narzędzie do precyzyjnego wyznaczania punktów montażowych ($A$ i $B$),"
    " skoku oraz wizualizacji geometrii bramy skrzydłowej."
)

# Panel boczny z parametrami wejściowymi
st.sidebar.header("Parametry montażowe")

szerokosc_slupka = st.sidebar.slider(
    "Szerokość słupka (profilu) [mm]",
    min_value=60,
    max_value=200,
    value=100,
    step=10,
    help="Grubość/szerokość słupka w osi bramy",
)

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
    help="Całkowita szerokość skrzydła",
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

# Współrzędne: zawias w (0,0)
# Słupek rośnie w ujemne X lub dodatnie Y w zależności od montażu.
# Przyjmijmy: słupek prostokątny od x = -szerokosc_slupka do 0, y od -szerokosc_slupka do A + 20
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

# --- CZYTELNA WIZUALIZACJA GRAFICZNA ---
st.subheader("📐 Szkic montażowy (widok z góry)")

fig, ax = plt.subplots(figsize=(8, 8))

# Rysowanie słupka jako prostokąta (np. profil stalowy)
# Zakładamy słupek kwadratowy o szerokości 'szerokosc_slupka', postawiony w narożniku
slup_rect = plt.Rectangle(
    (-szerokosc_slupka, -szerokosc_slupka / 2),
    szerokosc_slupka,
    szerokosc_slupka + A,
    facecolor="#d3d3d3",
    edgecolor="black",
    linewidth=1.5,
    alpha=0.6,
    label="Słupek bramowy",
)
ax.add_patch(slup_rect)

# Skrzydło zamknięte (szara linia przerywana)
ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="gray",
    linestyle="--",
    linewidth=3,
    label="Brama zamknięta",
)

# Skrzydło otwarte (niebieska linia gruba)
ax.plot(
    [0, x_koniec_skrzydla_otw],
    [0, y_koniec_skrzydla_otw],
    color="#1f77b4",
    linewidth=4,
    label=f"Brama otwarta ({kat_otwarcia}°)",
)

# Siłownik w stanie zamkniętym (pomarańczowa linia przerywana)
ax.plot(
    [x_slup_moc, x_skrzydlo_zamk_moc],
    [y_slup_moc, y_skrzydlo_zamk_moc],
    color="orange",
    linestyle=":",
    linewidth=2.5,
    label=f"Siłownik zamknięty ({dlugosc_zamkniety:.1f} mm)",
)

# Siłownik w stanie otwartym (czerwona linia ciągła)
ax.plot(
    [x_slup_moc, x_skrzydlo_otw_moc],
    [y_slup_moc, y_skrzydlo_otw_moc],
    color="red",
    linewidth=2.5,
    label=f"Siłownik otwarty ({dlugosc_otwarty:.1f} mm)",
)

# Oznaczenia punktów
ax.scatter([0], [0], color="black", s=120, zorder=5, label="Oś zawiasu (0,0)")
ax.scatter(
    [x_slup_moc],
    [y_slup_moc],
    color="green",
    s=100,
    zorder=5,
    label=f"Mocowanie słupka (A={A}mm)",
)
ax.scatter(
    [x_skrzydlo_otw_moc],
    [y_skrzydlo_otw_moc],
    color="purple",
    s=100,
    zorder=5,
    label=f"Mocowanie skrzydła (B={B}mm)",
)

# Dodanie opisów tekstowych bezpośrednio na wykresie dla jasności
ax.text(
    10,
    A + 10,
    f"Słupek\n(A = {A} mm)",
    color="green",
    fontsize=10,
    weight="bold",
)
ax.text(
    B / 2,
    -150,
    f"Skrzydło\n(B = {B} mm)",
    color="purple",
    fontsize=10,
    weight="bold",
)

ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.6)
ax.axhline(0, color="black", linewidth=0.8, alpha=0.5)
ax.axvline(0, color="black", linewidth=0.8, alpha=0.5)

# Dopasowanie marginesów wykresu, żeby wszystko było widoczne
maks_zasięg = max(szerokosc_skrzydla * 0.7, A + 100, B + 100)
ax.set_xlim(-szerokosc_slupka - 50, maks_zasięg)
ax.set_ylim(-szerokosc_slupka - 100, maks_zasięg)

ax.set_xlabel("Oś X [mm]", fontsize=11)
ax.set_ylabel("Oś Y (w głąb posesji) [mm]", fontsize=11)
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)

st.pyplot(fig)
