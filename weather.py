from datetime import datetime

from constants import SUNRISE_HOUR, SUNSET_HOUR

# Météo


def icon_of_code(code, night = False):

    if code == 0:
        name = "night" if night else "sunny"
    elif code in (1, 2):
        name = "partly_cloudy_night" if night else "partly_cloudy_day"
    elif code == 3:
        name = "cloudy"
    elif code in (45, 48):
        name = "fog"
    elif code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        name = "rain"
    elif code in (71, 73, 75, 77, 85, 86):
        name = "snow"
    elif code in (95, 96, 99):
        name = "storm"
    else:
        name = "cloudy"   # code inconnu : on affiche un nuage par défaut
    return name

def time_of_day():
    hour = datetime.now().hour
    if SUNRISE_HOUR <= hour < SUNSET_HOUR:
        return "day"
    return "night"
