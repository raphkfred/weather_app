from matplotlib.figure import Figure



def create_plot(dates, temperatures_min, temperatures_max):
    """Crée et retourne une Figure Matplotlib avec les courbes de températures min et max sur les dates fournies."""
    figure = Figure(figsize = (3.8, 3.2))
    axes = figure.add_subplot(111)


    x = range(len(dates))
    axes.plot(x, temperatures_max, color = "red", marker = "o", label = "Max")
    axes.plot(x, temperatures_min, color = "blue", marker = "o", label = "Min")
    # Zone grisée entre les deux courbes
    axes.fill_between(x, temperatures_min, temperatures_max, color = "gray", alpha = 0.15)
    axes.set_title("Températures (°C)")
    axes.grid(True)



    # Améliore la lisibilité
    axes.set_xticks(range(len(dates)))
    axes.set_xticklabels([d[5:] for d in dates], rotation = 45)
    figure.tight_layout()

    return figure
