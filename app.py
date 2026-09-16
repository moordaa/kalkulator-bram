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
    "Praktyczny szkic montażowy i kalkulator skoku dla bram skrzydłowych."
)

# Panel boczny z parametrami wejściowymi
st.sidebar.header("Wymiary montażowe")

szer_slupka_x = st.sidebar.slider(
    "Szerokość słupka wzdłuż bramy [mm]", 50, 300, 100, 10
)
szer_slupka_y = st.sidebar.slider(
    "Grubość słupka w głąb posesji [mm]", 50, 300, 100, 10
)

A = st.sidebar.slider(
    "Wymiar A (od zawiasu do mocowania na słupku) [mm]", 50, 300, 150, 5
)
B = st.sidebar.slider(
    "Wymiar B (od zawiasu do mocowania na skrzydle) [mm]", 50, 300, 150, 5
)

szerokosc_skrzydla = st.sidebar.slider(
    "Szerokość skrzydła bramy [mm]", 1000, 3000, 2000, 50
)
kat_otwarcia = st.sidebar.slider("Kąt otwarcia bramy [°]", 80, 130, 90, 1)

skok_sirownika_katalogowy = st.sidebar.number_input(
    "Skok Twojego siłownika (opcja) [mm]", 0, 600, 400, 10
)

# Obliczenia trygonometryczne
alpha = math.radians(kat_otwarcia)

# Geometria: zawias w punkcie (0,0)
# Słupek prostokątny narysujemy w ujemnych X lub odpowiedniej strefie
# Mocowanie na słupku w osi Y (w głąb posesji): (0, A)
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

# --- CZYSTY SZKIC TECHNICZNY (RUT Z GÓRY) ---
st.subheader("📐 Szkic montażowy (Widok z góry)")

fig, ax = plt.subplots(figsize=(8, 8))

# 1. Rysowanie słupka (prostokąt w narożniku)
# Słupek stoi np. od x = -szer_slupka_x do 0, oraz y od -szer_slupka_y/2 do szer_slupka_y/2 + A
slup = plt.Rectangle(
    (-szer_slupka_x, -szer_slupka_y / 2),
    szer_slupka_x,
    szer_slupka_y,
    facecolor="#e0e0e0",
    edgecolor="black",
    linewidth=2,
    zorder=2,
    label="Słupek bramowy",
)
ax.add_patch(slup)

# 2. Skrzydło bramy w pozycji ZAMKNIĘTEJ (szara linia przerywana)
ax.plot(
    [0, szerokosc_skrzydla],
    [0, 0],
    color="gray",
    linestyle="--",
    linewidth=3,
    label="Brama zamknięta",
    zorder=3,
)

# 3. Skrzydło bramy w pozycji OTWARTЕJ (mocna niebieska linia)
ax.plot(
    [0, x_koniec_skrzydla_otw],
    [0, y_koniec_skrzydla_otw],
    color="#0052cc",
    linewidth=4,
    label=f"Brama otwarta ({kat_otwarcia}°)",
    zorder=3,
)

# 4. Siłownik w stanie ZAMKNIĘTYM (pomarańczowa linia)
ax.plot(
    [x_slup_moc, x_skrzydlo_zamk_moc],
    [y_slup_moc, y_skrzydlo_zamk_moc],
    color="#ff8c00",
    linestyle=":",
    linewidth=3,
    label=f"Siłownik zamknięty ({dlugosc_zamkniety:.0f} mm)",
    zorder=4,
)

# 5. Siłownik w stanie OTWARTYM (czerwona linia ciągła)
ax.plot(
    [x_slup_moc, x_skrzydlo_otw_moc],
    [y_slup_moc, y_skrzydlo_otw_moc],
    color="#cc0000",
    linewidth=3,
    label=f"Siłownik otwarty ({dlugosc_otwarty:.0f} mm)",
    zorder=4,
)

# 6. Punkty kluczowe (Zawias, Mocowania)
ax.scatter(
    [0],
    [0],
    color="black",
    s=140,
    zorder=6,
    label="Zawias (Oś obrotu)",
    marker="o",
)
ax.scatter(
    [x_slup_moc],
    [y_slup_moc],
    color="green",
    s=120,
    zorder=6,
    label=f"Mocowanie na słupku (A={A}mm)",
    marker="^",
)
ax.scatter(
    [x_skrzydlo_otw_moc],
    [y_skrzydlo_otw_moc],
    color="purple",
    s=120,
    zorder=6,
    label=f"Mocowanie na skrzydle (B={B}mm)",
    marker="s",
)

# Opisy bezpośrednio na rysunku dla przejrzystości
ax.text(
    -szer_slupka_x / 2,
    0,
    "SŁUPEK",
    color="black",
    fontsize=11,
    weight="bold",
    ha="center",
    va="center",
    zorder=5,
)
ax.text(
    x_slup_moc + 15,
    y_slup_moc,
    f" A = {A} mm",
    color="green",
    fontsize=10,
    weight="bold",
    va="center",
)

# Czyszczenie wyglądu wykresu, żeby przypominał czysty rysunek techniczny (bez siatek i osi)
ax.set_aspect("equal")
ax.axis("off")  # Całkowite wyłączenie osi X i Y, żeby wyglądało jak szkic odręczny/CAD

# Marginesy dopasowane do geometrii
maks_zasięg = max(szerokosc_skrzydla * 0.6, A + 150, B + 150)
ax.set_xlim(-szer_slupka_x - 100, maks_zasięg)
ax.set_ylim(-szer_slupka_y - 100, maks_zasięg)

# Legenda na górze z boku
ax.legend(
    loc="upper right",
    fontsize=10,
    frameon=True,
    facecolor="white",
    edgecolor="none",
)

st.pyplot(fig)
