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
    "Precyzyjny kalkulator geometrii i punktów montażowych dla bram"
    " skrzydłowych."
)

# Panel boczny: Geometria słupka i zawiasu
st.sidebar.header("1. Geometria słupka i zawiasu")
szer_slupka = st.sidebar.number_input(
    "Szerokość/grubość słupka [mm]", 40, 600, 150, 10
)
odl_zawiasu_od_lica = st.sidebar.number_input(
    "Odległość osi zawiasu od lica słupka [mm]", -100, 400, 40, 5
)
odl_zawiasu_od_krawedzi = st.sidebar.number_input(
    "Odległość osi zawiasu od krawędzi (wzdłuż bramy) [mm]", 0, 400, 50, 5
)

# Panel boczny: Model i parametry siłownika
st.sidebar.header("2. Model i wymiary siłownika")
nazwa_modelu = st.sidebar.text_input(
    "Nazwa / Model siłownika:", value="Mój siłownik liniowy"
)

L_min = st.sidebar.number_input(
    "Całkowita dł. min. ($L_{min}$ - złożony) [mm]", 300, 2000, 750, 10
)
skok = st.sidebar.number_input(
    "Skok tłoka siłownika [mm]", 100, 1000, 400, 10
)
L_max = L_min + skok

kat_otwarcia = st.sidebar.slider("Docelowy kąt otwarcia [°]", 80, 130, 90, 1)
szerokosc_skrzydla = 1800

# --- PRAWIDŁOWY ALGORYTM GEOMETRII ---
alpha = math.radians(kat_otwarcia)
najlepsze_A = 120
najlepsze_B = 120
min_blad = float("inf")

# Szukamy A i B tak, aby długości siłownika pasowały do L_min (zamknięty) i L_max (otwarty)
# Uwzględniamy, że mocowanie na słupku A działa w osi Y (w głąb posesji),
# a mocowanie B na skrzydle w odległości B od zawiasu.
for test_A in range(80, 500, 2):
  for test_B in range(80, 500, 2):
    # Stan zamknięty (brama wzdłuż osi X: od (0,0) do (szerokość, 0))
    # Siłownik łączy punkt (0, test_A) na słupku z punktem (test_B, 0) na skrzydle
    d_zamk = math.sqrt(test_B**2 + test_A**2)

    # Stan otwarty (brama obrócona o kąt alpha)
    # Punkt mocowania na skrzydle po obrocie ma współrzędne:
    # x = test_B * cos(alpha), y = test_B * sin(alpha)
    x_skrz_otw = test_B * math.cos(alpha)
    y_skrz_otw = test_B * math.sin(alpha)

    # Siłownik łączy (0, test_A) z (x_skrz_otw, y_skrz_otw)
    d_otw = math.sqrt((x_skrz_otw - 0) ** 2 + (y_skrz_otw - test_A) ** 2)

    blad = abs(d_zamk - L_min) * 1.5 + abs(d_otw - L_max) * 1.5
    if blad < min_blad:
      min_blad = blad
      najlepsze_A = test_A
      najlepsze_B = test_B

A = najlepsze_A
B = najlepsze_B

# Współrzędne punktów mocowania w układzie ze środkiem w zawiasie (0,0)
# Słupek montowany jest w osi Y na wysokości A
x_slup_moc, y_slup_moc = 0, A
x_skrz_zamk_moc, y_skrz_zamk_moc = B, 0

rzeczywista_L_min = math.sqrt(
    (x_skrz_zamk_moc - x_slup_moc) ** 2 + (y_skrz_zamk_moc - y_slup_moc) ** 2
)

x_skrz_otw_moc = B * math.cos(alpha)
y_skrz_otw_moc = B * math.sin(alpha)
rzeczywista_L_max = math.sqrt(
    (x_skrz_otw_moc - x_slup_moc) ** 2 + (y_skrz_otw_moc - y_slup_moc) ** 2
)

# Wyniki tekstowe
st.subheader(f"📊 Wyniki doboru dla modelu: {nazwa_modelu}")
col1, col2, col3 = st.columns(3)
col1.metric("Wymiar A (Słupek)", f"{A} mm")
col2.metric("Wymiar B (Skrzydło)", f"{B} mm")
col3.metric(
    "Praca siłownika", f"{rzeczywista_L_min:.0f} -> {rzeczywista_L_max:.0f} mm"
)

# --- SZKIC TECHNICZNY ---
st.subheader("📐 Szkic montażowy")

fig, ax = plt.subplots(figsize=(8, 8))

# 1. Pozycjonowanie słupka względem zawiasu (0,0)
# Słupek ma szerokość w osi X i grubość w osi Y
slup_x_min = -odl_zawiasu_od_lica
slup_x_max = slup_x_min + szer_slupka
slup_y_min = -odl_zawiasu_od_krawedzi
slup_y_max = slup_y_min + szer_slupka

slup = plt.Rectangle(
    (slup_x_min, slup_y_min),
    szer_slupka,
    szer_slupka,
    facecolor="#f0f0f0",
    edgecolor="black",
    linewidth=2.5,
    zorder=2,
    label="Słupek",
)
ax.add_patch(slup)

# 2. Skrzydło zamknięte (poziomo)
ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="gray",
    linestyle="--",
    linewidth=3,
    label="Brama zamknięta",
    zorder=3,
)

# 3. Skrzydło otwarte (pod kątem)
x_koniec_skrzydla_otw = szerokosc_skrzydla * math.cos(alpha)
y_koniec_skrzydla_otw = szerokosc_skrzydla * math.sin(alpha)
ax.plot(
    [0, x_koniec_skrzydla_otw],
    [0, y_koniec_skrzydla_otw],
    color="#0052cc",
    linewidth=4,
    label=f"Brama otwarta ({kat_otwarcia}°)",
    zorder=3,
)

# 4. Siłownik w stanie zamkniętym (przerywana linia pomarańczowa)
ax.plot(
    [x_slup_moc, x_skrz_zamk_moc],
    [y_slup_moc, y_skrz_zamk_moc],
    color="#ff8c00",
    linestyle=":",
    linewidth=2.5,
    label=f"Złożony ({rzeczywista_L_min:.0f} mm)",
    zorder=4,
)

# 5. Siłownik w stanie otwartym (ciągła linia czerwona)
ax.plot(
    [x_slup_moc, x_skrz_otw_moc],
    [y_slup_moc, y_skrz_otw_moc],
    color="#cc0000",
    linewidth=2.5,
    label=f"Rozłożony ({rzeczywista_L_max:.0f} mm)",
    zorder=4,
)

# 6. Oś zawiasu w (0,0)
zawias = plt.Circle(
    (0, 0), 25, facecolor="white", edgecolor="black", linewidth=3, zorder=6
)
ax.add_patch(zawias)
ax.text(
    15,
    -25,
    "Oś zawiasu",
    fontsize=9,
    weight="bold",
    color="black",
    ha="left",
    zorder=7,
)

# 7. Punkty mocowania (widoczne na ścianie słupka i skrzydła)
ax.scatter(
    [x_slup_moc],
    [y_slup_moc],
    color="green",
    s=120,
    marker="^",
    zorder=6,
    label=f"Mocowanie słupka (A={A}mm)",
)
ax.scatter(
    [x_skrz_otw_moc],
    [y_skrz_otw_moc],
    color="purple",
    s=120,
    marker="s",
    zorder=6,
    label=f"Mocowanie skrzydła (B={B}mm)",
)

# Opisy na rysunku
ax.text(
    slup_x_min + szer_slupka / 2,
    slup_y_min + szer_slupka / 2,
    "SŁUPEK",
    color="black",
    fontsize=10,
    weight="bold",
    ha="center",
    va="center",
    zorder=5,
)

ax.annotate(
    f"Wymiar A = {A} mm",
    xy=(0, A),
    xytext=(-140, A / 2),
    arrowprops=dict(arrowstyle="->", color="green", lw=1.5),
    color="green",
    fontsize=10,
    weight="bold",
)

ax.set_aspect("equal")
ax.axis("off")

maks_zasięg = max(szerokosc_skrzydla * 0.5, A + 100, B + 100)
ax.set_xlim(slup_x_min - 80, maks_zasięg)
ax.set_ylim(slup_y_min - 80, maks_zasięg)

ax.legend(
    loc="upper right",
    fontsize=9,
    frameon=True,
    facecolor="white",
    edgecolor="none",
)
st.pyplot(fig)
