import math
import matplotlib.pyplot as plt
import streamlit as st
from openai import OpenAI

# Konfiguracja strony
st.set_page_config(
    page_title="Inteligentny Pozycjoner Siłowników Bramowych (AI)",
    page_icon="🚪",
    layout="centered",
)

st.title("🚪 Inteligentny Pozycjoner Siłowników (z AI)")
st.markdown(
    "Wpisz nazwę *dowolnego* siłownika na rynku, a AI pobierze jego parametry w"
    " locie i wyliczy punkty montażowe!"
)

# Panel boczny: Klucz API oraz konfiguracja AI
st.sidebar.header("🔑 Konfiguracja AI")
api_key = st.sidebar.text_input(
    "Klucz API (np. OpenAI / DeepSeek / Gemini)",
    type="password",
    help=(
        "Wprowadź swój klucz API, aby aplikacja mogła odpytywać model o"
        " parametry siłownika."
    ),
)

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

st.sidebar.header("2. Wyszukiwanie siłownika przez AI")
nazwa_modelu = st.sidebar.text_input(
    "Wpisz dokładny model siłownika:", value="Faac 414"
)

# Domyślne wartości na wypadek braku klucza
L_min_domyslne = 855
skok_domyslny = 400

# Przycisk zapytania do AI
if st.sidebar.button("🤖 Pobierz parametry z AI"):
  if not api_key:
    st.sidebar.error("Wprowadź klucz API na górze panelu bocznego!")
  else:
    try:
      client = OpenAI(
          api_key=api_key, base_url="https://api.openai.com/v1"
      )  # Można zmienić base_url pod inne API
      prompt = (
          f"Podaj parametry techniczne siłownika do bram skrzydłowych:"
          f" '{nazwa_modelu}'. Zwróć odpowiedź WYŁĄCZNIE w formacie JSON z"
          ' dwoma kluczami liczbowymi: "L_min" (długość minimalna w stanie'
          ' złożonym w milimetrach) oraz "skok" (skok tłoka w milimetrach).'
          " Żadnego dodatkowego tekstu."
      )

      response = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[{
              "role": "user",
              "content": prompt,
          }],
          temperature=0,
      )
      import json

      odpowiedz_tekst = response.choices[0].message.content.strip()
      # Czyszczenie ewentualnych znaczników markdown
      odpowiedz_tekst = (
          odpowiedz_tekst.replace("```json", "").replace("```", "").strip()
      )
      dane_ai = json.loads(odpowiedz_tekst)

      st.session_state["L_min"] = int(dane_ai["L_min"])
      st.session_state["skok"] = int(dane_ai["skok"])
      st.sidebar.success(
          f"Pomyślnie pobrano dla {nazwa_modelu}:\n- L_min:"
          f" {dane_ai['L_min']}mm\n- Skok: {dane_ai['skok']}mm"
      )
    except Exception as e:
      st.sidebar.error(f"Błąd zapytania do AI: {e}")

# Pobranie wartości ze stanu sesji lub użycie domyślnych
L_min = st.sidebar.number_input(
    "Długość min. ($L_{min}$) [mm]",
    300,
    2000,
    st.session_state.get("L_min", L_min_domyslne),
    10,
)
skok = st.sidebar.number_input(
    "Skok tłoka [mm]", 100, 1000, st.session_state.get("skok", skok_domyslny), 10
)

L_max = L_min + skok
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
    label=f"{nazwa_modelu} (złożony)",
)
ax.plot(
    [x_slup_moc, x_skrz_otw_moc],
    [y_slup_moc, y_skrz_otw_moc],
    color="orange",
    linewidth=2,
    zorder=4,
    label=f"{nazwa_modelu} (rozłożony)",
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
