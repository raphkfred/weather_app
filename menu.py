import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import date, timedelta

from constants import *
from weather import *
from weather_queries import *
from plot import *

# ----------------------------------------------------------------------
# Variables globales
# ----------------------------------------------------------------------
# Ville actuelle
city = "Paris"
# city = "Bordeaux"

# Premier jour affiché dans le menu des prévisions
start_day = date.today()

# ImageTk : ces variables globales permettent d'éviter que le garbage collector ne les efface
image_background = None
weather_icon = None
day_icons = []

# Widgets Tkinter (boutons, menu déroulant, graphique) placés sur l'écran courant.
# canvas.delete() n'efface que l'élément du canvas, pas le widget : on les détruit nous-mêmes.
current_widgets = []

# ----------------------------------------------------------------------
# Canvas
# ----------------------------------------------------------------------

def load_background(canvas):
    """Charge "assets/blue_sky.jpg" (jour) ou "assets/night_sky.jpg" (nuit),
    la redimensionne et la place sur le canvas."""
    global image_background

    canvas.delete("fond")
    name = "blue_sky" if time_of_day() == "day" else "night_sky"
    image = Image.open(f"assets/{name}.jpg").convert("RGBA")
    image = image.resize((WIDTH, HEIGHT))
    image_background = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image = image_background, anchor = "nw", tags = "fond")
    canvas.tag_lower("fond")   # le fond reste derrière tout le reste


def load_icon(name, size):
    """Charge une icône de assets/icons et la redimensionne (size x size)."""
    image = Image.open(f"assets/icons/{name}.png").convert("RGBA")
    image = image.resize((size, size))
    return ImageTk.PhotoImage(image)


def erase_screen(canvas):
    """Supprime tout ce qui a le tag 'ecran' (et détruit les widgets associés)."""
    canvas.delete("ecran")
    for widget in current_widgets:
        widget.destroy()
    current_widgets.clear()


def add_button(window, canvas, x, y, text, command):
    """Ajoute un bouton au canvas (avec le tag 'ecran')."""
    button = tk.Button(window, text = text, command = command)
    canvas.create_window(x, y, window = button, tags = "ecran")
    current_widgets.append(button)


# ----------------------------------------------------------------------
# Ecrans
# ----------------------------------------------------------------------

def change_city(window, canvas, new_city):
    """Appelée par le menu déroulant : change de ville et redessine l'accueil."""
    global city
    city = new_city
    draw_welcome_screen(window, canvas)


def draw_welcome_screen(window, canvas):
    """Écran 1 : Icône de la météo, température actuelle, températures min et max du jour."""
    global weather_icon

    erase_screen(canvas)

    # Données météo (avec gestion des erreurs réseau)
    try:
        temperature, code, t_min, t_max = get_current_weather(city)
        error = False
    except Exception as e:
        print("Erreur lors de la requête :", e)
        temperature, code, t_min, t_max = None, None, None, None
        error = True

    # Menu déroulant pour choisir la ville
    selected = tk.StringVar(window, value = city)
    menu = tk.OptionMenu(window, selected, *CITIES.keys(),
                         command = lambda c: change_city(window, canvas, c))
    menu.config(font = ("Helvetica", 18, "bold"), fg = "white", bg = "#3b5d85",
                activebackground = "#3b5d85", activeforeground = "white",
                highlightthickness = 0, bd = 0, width = 11)
    canvas.create_window(WIDTH // 2, 50, window = menu, tags = "ecran")
    current_widgets.append(menu)

    if error:
        canvas.create_text(WIDTH // 2, 250, text = "Données indisponibles\nVérifiez votre connexion",
                           font = ("Helvetica", 16, "bold"), fill = "white",
                           justify = "center", tags = "ecran")
    else:
        # Icône (version nuit s'il fait nuit)
        icon_name = icon_of_code(code, night = (time_of_day() == "night"))
        weather_icon = load_icon(icon_name, 128)
        canvas.create_image(WIDTH // 2, 170, image = weather_icon, tags = "ecran")

        # Température actuelle
        canvas.create_text(WIDTH // 2, 300, text = f"{round(temperature)} °C",
                           font = ("Helvetica", 44, "bold"), fill = "white", tags = "ecran")

        # Min et max du jour
        canvas.create_text(WIDTH // 2, 360,
                           text = f"Min : {round(t_min)} °C     Max : {round(t_max)} °C",
                           font = ("Helvetica", 13), fill = "white", tags = "ecran")

    # Bouton vers les prévisions
    add_button(window, canvas, WIDTH // 2, 440, "Prévisions 7 jours",
               lambda: open_forecast(window, canvas))


def open_forecast(window, canvas):
    """Ouvre le menu des prévisions en partant d'aujourd'hui."""
    global start_day
    start_day = date.today()
    draw_forecast(window, canvas)


def shift_forecast(window, canvas, days):
    """Recule (days < 0) ou avance (days > 0) la période affichée, dans les limites de l'API."""
    global start_day
    new_start = start_day + timedelta(days = days)
    today = date.today()
    if new_start < today - timedelta(days = MAX_DAYS_BACK):
        return
    if new_start > today + timedelta(days = MAX_DAYS_FORWARD):
        return
    start_day = new_start
    draw_forecast(window, canvas)


def draw_forecast(window, canvas):
    """Écran 2 : graphique des températures sur 7 jours"""
    global day_icons

    erase_screen(canvas)
    day_icons = []

    try:
        dates, t_mins, t_maxs, codes = get_forecast_with_codes(city, start_day)
        error = False
    except Exception as e:
        print("Erreur lors de la requête :", e)
        dates, t_mins, t_maxs, codes = [], [], [], []
        error = True

    # Titre, ville et période
    canvas.create_text(WIDTH // 2, 28, text = f"Prévisions sur 7 jours - {city}",
                       font = ("Helvetica", 16, "bold"), fill = "white", tags = "ecran")
    if not error:
        canvas.create_text(WIDTH // 2, 52, text = f"Du  {dates[0]}  au  {dates[-1]}",
                           font = ("Helvetica", 11), fill = "white", tags = "ecran")

        # Graphique Matplotlib intégré dans Tkinter
        figure = create_plot(dates, t_mins, t_maxs)
        zone_graphique = FigureCanvasTkAgg(figure, master = window)
        widget = zone_graphique.get_tk_widget()
        canvas.create_window(WIDTH // 2, 235, window = widget, tags = "ecran")
        current_widgets.append(widget)

        # Une icône par jour (toujours en version "jour")
        for i, code in enumerate(codes):
            icon = load_icon(icon_of_code(code), 34)
            day_icons.append(icon)
            x = 62 + i * 49.7   # aligné sous les dates du graphique
            canvas.create_image(x, 418, image = icon, tags = "ecran")
    else:
        canvas.create_text(WIDTH // 2, 235, text = "Données indisponibles\nVérifiez votre connexion",
                           font = ("Helvetica", 16, "bold"), fill = "white",
                           justify = "center", tags = "ecran")

    # Boutons : reculer, accueil, avancer
    add_button(window, canvas, 110, 465, "◄", lambda: shift_forecast(window, canvas, -7))
    add_button(window, canvas, WIDTH // 2, 465, "Accueil", lambda: draw_welcome_screen(window, canvas))
    add_button(window, canvas, 290, 465, "►", lambda: shift_forecast(window, canvas, 7))
