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
    "Wybierz model siłownika z bazy (lub podaj własne wymiary) oraz geometrię"
    " słupka – program wyliczy punkty montażowe."
)

# Panel boczny: Geometria słupka i zawiasu
st.sidebar.header("1. Geometria słupka i zawiasu")
szer_slupka = st.sidebar.number_input(
    "Szerokość/grubość słupka [mm]", 40, 600, 100, 10
)
odl_zawiasu_od_lica = st.sidebar.number_input(
    "Odległość osi zawiasu od lica słupka [mm]", -100, 400, 30, 5
)
odl_zawiasu_od_krawedzi = st.sidebar.number_input(
    "Odległość osi zawiasu od krawędzi (wzdłuż bramy) [mm]", 0, 400, 50, 5
)

# Panel boczny: Wybór modelu z bazy lub ręcznie
st.sidebar.header("2. Model siłownika")

baza_modeli = {
    "Nice Wingo 4000 / 4024 (Skok 400)": {"L_min": 740, "skok": 400},
    "Nice Wingo 5000 / 5024 (Skok 510)": {"L_min": 980, "skok": 510},
    "Nice Toona 4016 / 4024 (Skok 400)": {"L_min": 820, "skok": 400},
    "Came Krono 310 / 300 (Skok 340)": {"L_min": 690, "skok": 340},
    "Came Fast (Skok 350)": {"L_min": 600, "skok": 350},
    "Faac 414 (Skok 400)": {"L_min": 855, "skok": 400},
    "Faac 413 (Skok 400)": {"L_min": 770, "skok": 400},
    "Beninca Bill 30 (Skok 380)": {"L_min": 700, "skok": 380},
    "Beninca Bill 40 (Skok 400)": {"L_min": 780, "skok": 400},
    "Somfy Ixengo S (Skok 400)": {"L_min": 700, "skok": 400},
    "Inny model (wpisz wymiary ręcznie)": {"L_min": 750, "skok": 400},
}

wybrany_model = st.sidebar.selectbox("Wybierz model siłownika:", list(baza_modeli.keys()))

if wybrany_model == "Inny model (wpisz wymiary ręcznie)":
  nazwa_modelu = st.sidebar.text_input("Wpisz nazwę swojego modelu:", value="Nietypowy")
  L_min = st.sidebar.number_input(
      "Długość min. siłownika ($L_{min}$ - złożony) [mm]", 300, 2000, 750, 10
  )
  skok = st.sidebar.number_input(
      "Skok tłoka siłownika [mm]", 100, 1000, 400, 10
  )
else:
  nazwa_modelu = wybrany_model
  L_min = baza_modeli[wybrany_model]["L_min"]
  skok = baza_modeli[wybrany_model]["skok"]

L_max = L_min + skok
st.sidebar.info(
    f"Parametry:\n- L min (złożony): **{L_min} mm**\n- Skok: **{skok}"
    f" mm**\n- L max (rozłożony): **{L_max} mm**"
)

kat_otwarcia = st.sidebar.slider("Docelowy kąt otwarcia [°]", 80, 130, 90, 1)
szerokosc_skrzydla = 1800

# --- ALGORYTM OPTYMALIZACJI GEOMETRII (A i B) ---
alpha = math.radians(kat_otwarcia)
najlepsze_A = 150
najlepsze_B = 150
min_blad = float("inf")

for test_A in range(50, 500, 2):
  for test_B in range(50, 500, 2):
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

# Rzeczywiste wartości wyliczone dla wybranej konfiguracji
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
st.subheader(f"📊 Wyniki doboru dla: {nazwa_modelu}")
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
