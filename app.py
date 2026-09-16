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
    "Precyzyjny szkic montażowy z pełnym wymiarowaniem dla bram skrzydłowych."
)

# Panel boczny zgodnie z wytycznymi
st.sidebar.header("Parametry montażowe")

A = st.sidebar.slider("Wymiar A (Słupek) [mm]", 50, 500, 150, 5)
B = st.sidebar.slider("Wymiar B (Skrzydło) [mm]", 50, 400, 150, 5)
skok_sirownika_katalogowy = st.sidebar.number_input(
    "Skok siłownika [mm]", 100, 800, 400, 10
)

odleglosc_zawiasu_krawedz = st.sidebar.slider(
    "Odległość zawiasu od krawędzi w stronę otwierania [mm]", 0, 200, 50, 5
)
odleglosc_zawiasu_slup = st.sidebar.slider(
    "Odległość osi zawiasu od lica słupka [mm]", -50, 200, 30, 5
)

# Stałe parametry do wizualizacji szkicu
szerokosc_slupka_x = 100
grubosc_slupka_y = 100
szerokosc_skrzydla = 2000
kat_otwarcia = 90  # domyślny kąt na rysunku szkicu, obliczenia dla 90°

# Obliczenia trygonometryczne
alpha = math.radians(kat_otwarcia)

# Geometria w układzie: zawias w (0,0)
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
st.subheader("📊 Wyniki obliczeń")
col1, col2, col3 = st.columns(3)
col1.metric("Min. długość (Zamknięta)", f"{dlugosc_zamkniety:.1f} mm")
col2.metric("Maks. długość (Otwarta)", f"{dlugosc_otwarty:.1f} mm")
col3.metric("Wymagany skok tłoka", f"{skok_wymagany:.1f} mm")

if skok_sirownika_katalogowy > 0:
  st.markdown("---")
  if skok_sirownika_katalogowy >= skok_wymagany:
    st.success(
        f"✅ Siłownik o skoku {skok_sirownika_katalogowy} mm jest odpowiedni"
        f" (wymagane min. {skok_wymagany:.1f} mm)."
    )
  else:
    st.error(
        f"❌ Za mały skok siłownika! Masz {skok_sirownika_katalogowy} mm, a"
        f" potrzebujesz min. {skok_wymagany:.1f} mm."
    )

# --- SZKIC TECHNICZNY Z WYMIAROWANIEM ---
st.subheader("📐 Szkic montażowy z wymiarowaniem (Widok z góry)")

fig, ax = plt.subplots(figsize=(9, 9))

# 1. Rysowanie słupka
slup_x = -odleglosc_zawiasu_slup - szerokosc_slupka_x
slup_y = -odleglosc_zawiasu_krawedz
slup = plt.Rectangle(
    (slup_x, slup_y),
    szerokosc_slupka_x,
    grubosc_slupka_y,
    facecolor="#e8e8e8",
    edgecolor="black",
    linewidth=2,
    zorder=2,
)
ax.add_patch(slup)

# 2. Skrzydło zamknięte (szara linia)
ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="gray",
    linestyle="--",
    linewidth=2.5,
    label="Brama zamknięta",
    zorder=3,
)

# 3. Skrzydło otwarte (niebieska linia)
ax.plot(
    [0, x_koniec_skrzydla_otw],
    [0, y_koniec_skrzydla_otw],
    color="#0052cc",
    linewidth=3.5,
    label="Brama otwarta (90°)",
    zorder=3,
)

# 4. Siłownik zamknięty (pomarańczowa linia)
ax.plot(
    [x_slup_moc, x_skrzydlo_zamk_moc],
    [y_slup_moc, y_skrzydlo_zamk_moc],
    color="#ff8c00",
    linestyle=":",
    linewidth=2.5,
    label=f"Siłownik zamknięty ({dlugosc_zamkniety:.0f} mm)",
    zorder=4,
)

# 5. Siłownik otwarty (czerwona linia)
ax.plot(
    [x_slup_moc, x_skrzydlo_otw_moc],
    [y_slup_moc, y_skrzydlo_otw_moc],
    color="#cc0000",
    linewidth=2.5,
    label=f"Siłownik otwarty ({dlugosc_otwarty:.0f} mm)",
    zorder=4,
)

# 6. Punkty kluczowe (Zawias i mocowania)
ax.scatter(
    [0],
    [0],
    color="black",
    s=130,
    zorder=6,
    label="Oś zawiasu (0,0)",
    marker="o",
)
ax.scatter(
    [x_slup_moc],
    [y_slup_moc],
    color="green",
    s=110,
    zorder=6,
    label=f"Mocowanie słupka (A={A}mm)",
    marker="^",
)
ax.scatter(
    [x_skrzydlo_otw_moc],
    [y_skrzydlo_otw_moc],
    color="purple",
    s=110,
    zorder=6,
    label=f"Mocowanie skrzydła (B={B}mm)",
    marker="s",
)

# --- NANIESIONE WYMIARY I OPISY TECHNICZNE NA RYSUNKU ---
# Opis słupka
ax.text(
    slup_x + szerokosc_slupka_x / 2,
    slup_y + grubosc_slupka_y / 2,
    "SŁUPEK",
    color="black",
    fontsize=10,
    weight="bold",
    ha="center",
    va="center",
    zorder=5,
)

# Wymiar A (linia pomocnicza i opis)
ax.annotate(
    f"Wymiar A = {A} mm",
    xy=(0, A),
    xytext=(-120, A / 2),
    arrowprops=dict(arrowstyle="->", color="green", lw=1.5),
    color="green",
    fontsize=11,
    weight="bold",
)

# Wymiar B (linia pomocnicza i opis)
ax.annotate(
    f"Wymiar B = {B} mm",
    xy=(B / 2, 0),
    xytext=(B / 2, -70),
    arrowprops=dict(arrowstyle="->", color="purple", lw=1.5),
    color="purple",
    fontsize=11,
    weight="bold",
    ha="center",
)

# Opis osi zawiasu
ax.text(
    15,
    -15,
    "Zawias",
    color="black",
    fontsize=9,
    weight="bold",
    ha="left",
    va="top",
)

# Czysty styl CAD / szkic techniczny (brak osi matematycznych)
ax.set_aspect("equal")
ax.axis("off")

maks_zasięg = max(szerokosc_skrzydla * 0.5, A + 100, B + 100)
ax.set_xlim(slup_x - 80, maks_zasięg)
ax.set_ylim(slup_y - 100, maks_zasięg)

ax.legend(
    loc="upper right",
    fontsize=9,
    frameon=True,
    facecolor="white",
    edgecolor="none",
)

st.pyplot(fig)
