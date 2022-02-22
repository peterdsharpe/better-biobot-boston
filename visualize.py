import numpy as np
from get_data import (dates, north, south, north_ci, south_ci)
import matplotlib.pyplot as plt
import aerosandbox.tools.pretty_plots as p
import datetime
from scipy import ndimage

north_color = p.palettes['categorical'][0]
south_color = p.palettes['categorical'][1]

zoom_days = 28
zoom_range = (
    datetime.datetime.today() - datetime.timedelta(days=28),
    datetime.datetime.today()
)


def filter(array):
    # not_nan_indices = np.argwhere(~np.isnan(array))
    # first = not_nan_indices[0, 0]
    # last = not_nan_indices[-1, 0] + 1
    isnan = np.isnan(array)

    output = np.empty_like(array)
    output[:] = np.NaN
    output[~isnan] = np.exp(ndimage.gaussian_filter(
        np.log(array)[~isnan],
        sigma=2,
        mode='nearest',
        truncate=4,
    ))
    return output


def zoom(dates, data):
    return dates, data


def make_plot(draw_individual_data=True):
    plt.plot([], [], "-", color=north_color, label="North")
    plt.plot([], [], "-", color=south_color, label="South")
    if draw_individual_data:
        plt.errorbar(
            dates,
            north,
            yerr=north_ci,
            fmt=".",
            color=north_color,
            alpha=0.3
        )
        plt.errorbar(
            dates, south,
            yerr=south_ci,
            fmt=".",
            color=south_color,
            alpha=0.3
        )
    plt.plot(
        *zoom(dates, filter(north)), '-',
        color=north_color,
        alpha=0.8,
        zorder=4,
    )
    plt.plot(
        *zoom(dates, filter(south)), '-',
        color=south_color,
        alpha=0.8,
        zorder=3
    )

    plt.ylabel("RNA copies/mL")
    p.set_ticks(y_major=5000, y_minor=1000)
    plt.ylim(bottom=0, top=12000)
    plt.yscale('log')

fig, ax = plt.subplots(2, 1, figsize=(7, 7))

plt.sca(ax[0])
make_plot(draw_individual_data=False)
plt.title("Overview")
plt.gca().xaxis.set_major_formatter(
    p.mpl.dates.DateFormatter('%b \'%y')
)
plt.gca().xaxis.set_major_locator(
    p.mpl.dates.MonthLocator([1, 4, 7, 10])
)
plt.gca().xaxis.set_minor_locator(
    p.mpl.dates.MonthLocator()
)

plt.sca(ax[1])
make_plot()
plt.title(f"Recent {zoom_days} Days")
plt.gca().xaxis.set_major_formatter(
    p.mpl.dates.DateFormatter('%a.\n%b. %d')
)
plt.gca().xaxis.set_major_locator(
    p.mpl.dates.WeekdayLocator([p.mpl.dates.SU])
)
plt.gca().xaxis.set_minor_locator(
    p.mpl.dates.DayLocator()
)
plt.xlim(zoom_range)

# plt.gcf().autofmt_xdate(rotation=45, ha='center')
p.show_plot(
    "DITP Viral RNA Signal",
)
