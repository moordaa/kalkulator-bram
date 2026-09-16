import math
import matplotlib.pyplot as plt
import streamlit as st

# Konfiguracja strony
st.set_page_config(
    page_title="Kalkulator i Pozycjoner Siłowników Bramowych",
    page_icon="🚪",
    layout="centered",
)

st.title("🚪 Pozycjoner Siłowników Bramowych")
st.markdown(
    "Wprowadź geometrię słupka, zawiasu oraz parametry siłownika – program"
    " wyliczy i narysuje punkty mocowania."
)

# Panel boczny: Geometria słupka i zawiasu oraz dane siłownika
st.sidebar.header("1. Geometria słupka i zawiasu")
szer_slupka = st.sidebar.number_input(
    "Szerokość/grubość słupka [mm]",
    min_value=40,
    max_value=500,
    value=100,
    step=10,
)
odl_zawiasu_od_lica = st.sidebar.number_input(
    "Odległość osi zawiasu od lica słupka [mm]",
    min_value=-100,
    max_value=300,
    value=30,
    step=5,
    help="Dodatnia = zawias wystaje w stronę posesji; Ujemna = schowany",
)
odl_zawiasu_od_krawedzi = st.sidebar.number_input(
    "Odległość osi zawiasu od krawędzi (wzdłuż bramy) [mm]",
    min_value=0,
    max_value=300,
    value=50,
    step=5,
)

st.sidebar.header("2. Parametry siłownika")
tryb_sirownika = st.sidebar.radio(
    "Wybór siłownika",
    ["Wpisz parametry ręcznie", "Popularny model (np. skok 400mm)"],
)

if tryb_sirownika == "Wpisz parametry ręcznie":
  L_min = st.sidebar.number_input(
    "Długość min. siłownika (złożony) [mm]", 300, 1500, 750, 10
  )
  L_max = st.sidebar.number_input(
    "Długość max. siłownika (rozłożony) [mm]", 500, 2000, 1150, 10
  )
  skok = L_max - L_min
  st.sidebar.info(f"Wyliczony skok tłoka: {skok} mm")
else:
  # Przykładowy standardowy siłownik liniowy
  skok = st.sidebar.slider("Skok siłownika [mm]", 300, 600, 400, 10)
  L_min = st.sidebar.number_input("Długość min. (złożony) [mm]", 500, 1000, 750, 10)
  L_max = L_min + skok

kat_otwarcia = st.sidebar.slider("Docelowy kąt otwarcia [°]", 80, 130, 90, 1)
szerokosc_skrzydla = 1800  # stała do wizualizatora

# --- MATEMATYCZNE WYZNACZENIE PUNKTÓW A I B ---
# Szukamy takich wartości A (na słupku) oraz B (na skrzydle), które spełniają warunki:
# 1. Odległość mocowań w stanie zamkniętym (0°) równa się L_min (lub mieści się w zakresie)
# 2. Odległość mocowań w stanie otwartym (kat_otwarcia) równa się L_max (lub L_min + skok)

alpha = math.radians(kat_otwarcia)
najlepsze_A = 150
najlepsze_B = 150
min_blad = float("inf")

# Przeszukujemy przestrzenie A i B z krokiem 2 mm
for test_A in range(50, 400, 2):
  for test_B in range(50, 400, 2):
    # Długość w stanie zamkniętym: wektor z (0, test_A) do (test_B, 0)
    d_zamk = math.sqrt(test_B**2 + test_A**2)

    # Długość w stanie otwartym: punkt na skrzydle to (test_B * cos(alpha), test_B * sin(alpha))
    x_skrz_otw = test_B * math.cos(alpha)
    y_skrz_otw = test_B * math.sin(alpha)
    d_otw = math.sqrt((x_skrz_otw - 0) ** 2 + (y_skrz_otw - test_A) ** 2)

    # Sprawdzamy dopasowanie do długości min i max siłownika
    blad = abs(d_zamk - L_min) + abs(d_otw - L_max)
    if blad < min_blad:
      min_blad = blad
      najlepsze_A = test_A
      najlepsze_B = test_B

A = najlepsze_A
B = najlepsze_B

# Dokładne długości dla znalezionych A i B
x_slup_moc, y_slup_moc = 0, A
x_skrz_zamk_moc, y_skrz_zamk_moc = B, 0
rzeczywista_L_min = math.sqrt(
    (x_skrz_zamk_moc - x_slup_moc) ** 2 + (y_skrz_zamk_moc - y_slup_moc) ** 2
)

x_skrz_otw_moc = B * math.cos(alpha)
y_skrz_otw_moc = B * math.sin(alpha)
rzeczywista_L_max = math.sqrt(
    (x_skrz_otw_moc - x_slup_moc) ** 2 + (y_skrzydlo_zamk_moc - y_slup_moc) ** 2
)  # poprawka na współrzędne

# Wyniki tekstowe
st.subheader("📊 Wyniki dobowe montażu")
col1, col2, col3 = st.columns(3)
col1.metric("Wyliczony Wymiar A (Słupek)", f"{A} mm")
col2.metric("Wyliczony Wymiar B (Skrzydło)", f"{B} mm")
col3.metric(
    "Praca siłownika", f"{rzeczywista_L_min:.0f} -> {rzeczywista_L_max:.0f} mm"
)

# --- SZKIC TECHNICZNY W UKŁADZIE TWOJEGO RYSUNKU ---
st.subheader("📐 Szkic montażowy")

fig, ax = plt.subplots(figsize=(8, 8))

# 1. Słupek (czarny prostokąt uwzględniający położenie zawiasu)
slup_x = -odl_zawiasu_od_lica - szer_slupka
slup_y = -odl_zawiasu_od_krawedzi
slup = plt.Rectangle(
    (slup_x, slup_y),
    szer_slupka,
    szer_slupka,
    facecolor="white",
    edgecolor="black",
    linewidth=3,
    zorder=2,
)
ax.add_patch(slup)

# 2. Skrzydło zamknięte (poziomo w prawo - czerwone)
ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="#cc0000",
    linewidth=4,
    solid_capstyle="round",
    zorder=3,
)

# 3. Skrzydło otwarte (pod kątem - czerwone)
x_koniec_skrzydla_otw = szerokosc_skrzydla * math.cos(alpha)
y_koniec_skrzydla_otw = szerokosc_skrzydla * math.sin(alpha)
ax.plot(
    [0, x_koniec_skrzydla_otw],
    [0, y_koniec_skrzydla_otw],
    color="#cc0000",
    linewidth=4,
    solid_capstyle="round",
    zorder=3,
)

# 4. Linie siłownika (złożony / rozłożony)
ax.plot(
    [x_slup_moc, B],
    [y_slup_moc, 0],
    color="orange",
    linestyle=":",
    linewidth=2,
    zorder=4,
    label="Siłownik złożony",
)
ax.plot(
    [x_slup_moc, x_skrz_otw_moc],
    [y_slup_moc, y_skrz_otw_moc],
    color="orange",
    linewidth=2,
    zorder=4,
    label="Siłownik rozłożony",
)

# 5. Kółko zawiasu w (0,0)
zawias = plt.Circle(
    (0, 0), 30, facecolor="white", edgecolor="#800000", linewidth=3, zorder=6
)
ax.add_patch(zawias)

# 6. Zielone kwadraty (punkty mocowania)
moc_slup = plt.Rectangle(
    (x_slup_moc - 18, y_slup_moc - 18),
    36,
    36,
    facecolor="white",
    edgecolor="green",
    linewidth=3,
    zorder=7,
)
ax.add_patch(moc_slup)

moc_skrzydlo = plt.Rectangle(
    (x_skrz_otw_moc - 18, y_skrz_otw_moc - 18),
    36,
    36,
    facecolor="white",
    edgecolor="green",
    linewidth=3,
    zorder=7,
)
ax.add_patch(moc_skrzydlo)

# Opisy wymiarów
ax.annotate(
    f"A = {A} mm",
    xy=(0, A),
    xytext=(-140, A / 2),
    arrowprops=dict(arrowstyle="->", color="green", lw=1.5),
    color="green",
    fontsize=11,
    weight="bold",
)
ax.annotate(
    f"B = {B} mm",
    xy=(x_skrz_otw_moc / 2, y_skrz_otw_moc / 2),
    xytext=(-140, (y_skrz_otw_moc / 2) + 40),
    arrowprops=dict(arrowstyle="->", color="green", lw=1.5),
    color="green",
    fontsize=11,
    weight="bold",
)

ax.set_aspect("equal")
ax.axis("off")

maks_zasięg = max(szerokosc_skrzydla * 0.5, A + 100, B + 100)
ax.set_xlim(slup_x - 100, maks_zasięg)
ax.set_ylim(slup_y - 100, maks_zasięg)

st.pyplot(fig)
