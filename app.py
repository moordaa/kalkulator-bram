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
    "Wpisz model siłownika, parametry słupka i zawiasu – program wyliczy"
    " precyzyjne punkty montażowe."
)

# Panel boczny: Geometria słupka i zawiasu
st.sidebar.header("1. Geometria słupka i zawiasu")
szer_slupka = st.sidebar.number_input(
    "Szerokość/grubość słupka [mm]", 40, 500, 100, 10
)
odl_zawiasu_od_lica = st.sidebar.number_input(
    "Odległość osi zawiasu od lica słupka [mm]", -100, 300, 30, 5
)
odl_zawiasu_od_krawedzi = st.sidebar.number_input(
    "Odległość osi zawiasu od krawędzi (wzdłuż bramy) [mm]", 0, 300, 50, 5
)

# Panel boczny: Wyszukiwarka modeli siłowników
st.sidebar.header("2. Wyszukiwanie modelu siłownika")

# Rozbudowana baza katalogowa popularnych modeli
katalog_silownikow = {
    "Nice Wingo 4000 / 4024": {"L_min": 740, "L_max": 1140, "skok": 400},
    "Nice Wingo 5000 / 5024": {"L_min": 980, "L_max": 1490, "skok": 510},
    "Nice Toona 4016 / 4024": {"L_min": 820, "L_max": 1220, "skok": 400},
    "Came Krono 310 / 300": {"L_min": 690, "L_max": 1030, "skok": 340},
    "Came Fast": {"L_min": 600, "L_max": 950, "skok": 350},
    "Faac 414": {"L_min": 855, "L_max": 1255, "skok": 400},
    "Faac 413": {"L_min": 770, "L_max": 1170, "skok": 400},
    "Beninca Bill 30": {"L_min": 700, "L_max": 1080, "skok": 380},
    "Beninca Bill 40": {"L_min": 780, "L_max": 1180, "skok": 400},
    "Somfy Ixengo S": {"L_min": 700, "L_max": 1100, "skok": 400},
}

szukany_model = st.sidebar.text_input(
    "Wpisz nazwę siłownika (np. Faac, Nice, Came):", value="Faac 414"
)

# Dopasowanie na podstawie wpisanej frazy
dopasowany_silownik = None
for nazwa, parametry in katalog_silownikow.items():
  if szukany_model.lower() in nazwa.lower():
    dopasowany_silownik = nazwa
    domyslny_L_min = parametry["L_min"]
    domyslny_L_max = parametry["L_max"]
    break

if dopasowany_silownik:
  st.sidebar.success(
      f"Znaleziono w bazie: **{dopasowany_silownik}**\n- Skok:"
      f" **{katalog_silownikow[dopasowany_silownik]['skok']} mm**"
  )
  L_min = domyslny_L_min
  L_max = domyslny_L_max
else:
  st.sidebar.warning(
      "Nie znaleziono w predefiniowanej bazie. Wprowadź wymiary ręcznie:"
  )
  L_min = st.sidebar.number_input(
      "Długość min. siłownika ($L_{min}$) [mm]", 400, 1500, 800, 10
  )
  L_max = st.sidebar.number_input(
      "Długość max. siłownika ($L_{max}$) [mm]", 600, 2000, 1200, 10
  )

skok = L_max - L_min
kat_otwarcia = st.sidebar.slider("Docelowy kąt otwarcia [°]", 80, 130, 90, 1)
szerokosc_skrzydla = 1800

# --- ALGORYTM OPTYMALIZACJI GEOMETRII (A i B) ---
alpha = math.radians(kat_otwarcia)
najlepsze_A = 150
najlepsze_B = 150
min_blad = float("inf")

for test_A in range(60, 450, 2):
  for test_B in range(60, 450, 2):
    d_zamk = math.sqrt(test_B**2 + test_A**2)
    x_skrz_otw = test_B * math.cos(alpha)
    y_skrz_otw = test_B * math.sin(alpha)
    d_otw = math.sqrt((x_skrz_otw - 0) ** 2 + (y_skrz_otw - test_A) ** 2)

    blad = abs(d_zamk - L_min) * 1.5 + abs(d_otw - L_max) * 1.5
    if blad < min_blad:
      min_blad = blad
      najlepsze_A = test_A
      najlepsze_B = test_B

A = najlepsze_A
B = najlepsze_B

# Rzeczywiste wartości wyliczone
x_slup_moc, y_slup_moc = 0, A
x_skrz_zamk_moc, y_skrz_zamk_moc = B, 0
rzeczywista_L_min = math.sqrt(
    (x_skrz_zamk_moc - x_slup_moc) ** 2 + (y_skrz_zamk_moc - y_slup_moc) ** 2
)

x_skrz_otw_moc = B * math.cos(alpha)
y_skrz_otw_moc = B * math.sin(alpha)
rzeczywista_L_max = math.sqrt(
    (x_skrz_otw_moc - x_slup_moc) ** 2 + (y_skrzydlo_zamk_moc - y_slup_moc) ** 2
)

# Wyniki tekstowe
st.subheader("📊 Wyniki doboru montażowego")
col1, col2, col3 = st.columns(3)
col1.metric("Wymiar A (Słupek)", f"{A} mm")
col2.metric("Wymiar B (Skrzydło)", f"{B} mm")
col3.metric(
    "Praca siłownika", f"{rzeczywista_L_min:.0f} -> {rzeczywista_L_max:.0f} mm"
)

# --- SZKIC TECHNICZNY ---
st.subheader("📐 Szkic montażowy")

fig, ax = plt.subplots(figsize=(8, 8))

# 1. Słupek
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

# 2. Skrzydło zamknięte
ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="#cc0000",
    linewidth=4,
    solid_capstyle="round",
    zorder=3,
)

# 3. Skrzydło otwarte
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

# 4. Linie siłownika
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

# 5. Zawias
zawias = plt.Circle(
    (0, 0), 30, facecolor="white", edgecolor="#800000", linewidth=3, zorder=6
)
ax.add_patch(zawias)

# 6. Zielone punkty mocowania
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

# Opisy wymiarów na rysunku
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
