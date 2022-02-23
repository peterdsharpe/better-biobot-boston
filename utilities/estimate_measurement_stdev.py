### Workflow:

# Basic idea here: Estimate measurement standard deviation by assuming that measurements taken 1 day apart are drawn
# from the same underlying log-normal distribution.

from get_data import data as all_data
import numpy as np

data = all_data["North"]["values"]
data_ci = all_data["North"]["ci"]
n_bootstrap_samples = 100000
tau = 1

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

estimated_log_stdev = np.log(np.median(
    np.maximum(ratios, 1/ratios)
)) / 2 ** 0.5