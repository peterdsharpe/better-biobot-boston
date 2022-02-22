# Make a variogram of the northern and southern data
from get_data import (dates, north, south, north_ci, south_ci)
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import aerosandbox.tools.pretty_plots as p

data = north
data_ci = north_ci
n_bootstrap_samples = 100000
tau = 10

valid_indices = np.argwhere(
    ~np.isnan(data[:-tau]) & ~np.isnan(data[tau:])
)[:, 0]

indices = np.random.choice(valid_indices, size=n_bootstrap_samples, replace=True)

pairs = np.array([
    np.random.triangular(
        data[indices] - data_ci[0][indices],
        data[indices],
        data[indices] + data_ci[1][indices],
    ),
    np.random.triangular(
        data[indices + tau] - data_ci[0][indices + tau],
        data[indices + tau],
        data[indices + tau] + data_ci[1][indices + tau]
    )
]).T
pairs = np.concatenate([
    pairs,
    pairs[:, ::-1]
], axis=0)
differences = pairs[:, 0] - pairs[:, 1]
# ratios = np.concatenate([
#     differences / (pairs[:, 0] + pairs[:, 1]) * 2,
#     # differences / pairs[:, 1],
# ])
ratios = pairs[:, 1] / pairs[:, 0]
log_ratios = np.log10(ratios)

fig, ax = plt.subplots()
plt.scatter(
    pairs[:, 0],
    pairs[:, 1],
    alpha=0.05
)
plt.xscale('log')
plt.yscale('log')
p.show_plot(
    None,
    "Viral Signal at Day $X$",
    f"Viral Signal at Day $X+{tau}$"
)

fig, ax = plt.subplots()
p.sns.histplot(log_ratios,
               stat='density',
               kde=True,
               kde_kws=dict(
                   gridsize=200
               )
               )
plt.yscale('log')
y_data = plt.gca().containers[0].datavalues
y_data = y_data[y_data != 0]
plt.ylim(bottom=0.1 * y_data.min(), top=10 * y_data.max())

std = np.std(log_ratios)
distribution = stats.norm
parameters = distribution.fit(log_ratios)
x = np.linspace(log_ratios.min(), log_ratios.max(), 500)
plt.plot(
    x,
    distribution.pdf(x, *parameters),
    color='red'
)
p.show_plot()
