import numpy as np
from get_data import data
import matplotlib.pyplot as plt
import aerosandbox.tools.pretty_plots as p
import datetime
from aerosandbox.tools.pretty_plots.utilities.natural_univariate_spline import NaturalUnivariateSpline as Spline
from tqdm import tqdm
from utilities.estimate_measurement_stdev import estimated_log_stdev

np.random.seed(0)

data["North"]["color"] = p.palettes['categorical'][0]
data["South"]["color"] = p.palettes['categorical'][1]
data["North"]["zorder"] = 6
data["South"]["zorder"] = 5

today = datetime.datetime.today()

zoom_days = 28
zoom_range = (
    today - datetime.timedelta(days=28),
    today
)


def make_plot(zoomed=False):
    for region_name, region_data in data.items():
        plt.plot([], [], "-",
                 color=region_data["color"],
                 label=f"{region_name} Region"
                 )

        plt.plot(
            region_data["dates"],
            region_data["values"] / 1e3,
            ".",
            color=region_data["color"],
            markeredgewidth=0,
            markersize=4 if zoomed else 2.5,
            alpha=0.8,
            zorder=region_data["zorder"]
        )

        x=region_data["dates"].astype(float)
        y=np.log(region_data["values"] / 1e3)
        y_stdev=estimated_log_stdev
        n_bootstraps=2000
        n_fit_points=1800
        spline_degree=3

        ### Discard any NaN points
        isnan = np.logical_or(
            np.isnan(x),
            np.isnan(y),
        )
        x = x[~isnan]
        y = y[~isnan]

        ### Prepare for the bootstrap
        x_fit = np.linspace(x.min(), np.datetime64(today).astype('datetime64[s]').astype(float) / 86400, n_fit_points)

        y_bootstrap_fits = np.empty((n_bootstraps, len(x_fit)))

        for i in tqdm(range(n_bootstraps), desc="Bootstrapping", unit=" samples"):

            ### Obtain a bootstrap resample
            ### Here, instead of truly resampling, we just pick weights that effectively mimic a resample.
            ### A computationally-efficient way to pick weights is the following clever trick with uniform sampling:
            splits = np.random.rand(len(x) + 1) * len(x)  # "limit" bootstrapping
            splits[0] = 0
            splits[-1] = len(x)

            weights = np.diff(np.sort(splits))

            y_bootstrap_fits[i, :] = Spline(
                x=x,
                y=y,
                w=weights,
                s=len(x) * y_stdev,
                k=spline_degree,
                ext='extrapolate'
            )(x_fit)

        xb = x_fit
        yb = y_bootstrap_fits

        xb = (xb * 86400).astype('datetime64[s]')
        yb = np.exp(yb)

        plt.plot(
            xb,
            np.nanquantile(yb, q=0.5, axis=0),
            color=region_data["color"],
            linewidth=1,
            zorder=region_data["zorder"] + 0.2
        )
        plt.fill_between(
            xb,
            *np.nanquantile(
                yb,
                q=[
                    (1 - 0.75) / 2,
                    1 - (1 - 0.75) / 2,
                ],
                axis=0
            ),
            color=region_data["color"],
            alpha=0.3,
            linewidth=0,
            zorder=region_data["zorder"] + 0.1
        )

        # plt.plot(
        #     region_data["dates"],
        #     filter(region_data["values"]),
        #     '-',
        #     color=region_data["color"],
        #     alpha=0.8,
        #     zorder=4,
        # )

    plt.ylabel("RNA copies/μL")
    p.set_ticks(y_major=2, y_minor=0.5)

    plt.plot([], [], ".k",
             markeredgewidth=0,
             markersize=4,
             alpha=0.8,
             label="Data"
             )
    plt.fill_between(
        [],
        [],
        [],
        color="k",
        alpha=0.3,
        label="75% CI"
    )


fig, ax = plt.subplots(2, 1, figsize=(7, 7))

plt.sca(ax[0])
make_plot()
plt.title("Overview")
plt.gca().xaxis.set_major_formatter(
    p.mpl.dates.DateFormatter('%b. 1\n\'%y')
)
plt.gca().xaxis.set_major_locator(
    p.mpl.dates.MonthLocator([1, 7])
)
plt.gca().xaxis.set_minor_locator(
    p.mpl.dates.MonthLocator()
)
plt.xlim(right=datetime.datetime.today())
plt.ylim(bottom=0)
plt.legend(
    ncol=2,
    framealpha=0
)

plt.sca(ax[1])
make_plot(zoomed=True)
plt.title(f"Zoom-in of Recent {zoom_days} Days")
plt.gca().xaxis.set_major_formatter(
    p.mpl.dates.DateFormatter('%a.\n%b. %#d')
)
plt.gca().xaxis.set_major_locator(
    p.mpl.dates.WeekdayLocator([p.mpl.dates.SU])
)
plt.gca().xaxis.set_minor_locator(
    p.mpl.dates.DayLocator()
)
plt.xlim(zoom_range)
plt.ylim(bottom=0)

# plt.gcf().autofmt_xdate(rotation=45, ha='center')
p.show_plot(
    "Boston COVID-19 Wastewater Data\nBiobot Analytics",
    legend=False,
    show=False,
    set_ticks=False,
)

plt.savefig("assets/after.svg")

for a in ax:
    a.set_yscale('log')
    a.set_ylim(
        bottom=np.array([
            np.nanmin(dataset["values"])
            for dataset in data.values()
        ]).min() / 1e3,
        top=np.array([
            np.nanmax(dataset["values"])
            for dataset in data.values()
        ]).max() / 1e3,
    )

plt.savefig("assets/after-log.svg")

plt.show()