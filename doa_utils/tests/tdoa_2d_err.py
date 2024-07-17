import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as op
import random


c = 299792458.0  # speed of light in m/s

def tdoa_solver_2d():
    x_min = -100
    x_max = 100
    y_min = -100
    y_max = 100
    bounds = ([3 * x_min, 3 * y_min], [3 * x_max, 3 * y_max])

    num_trials = 1000
    num_variances = 10
    variances = np.logspace(-10, -6, num_variances)
    mean_errors = []

    for noise_variance in variances:
        errors = np.zeros(num_trials)
        for i in range(num_trials):
            r1 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
            r2 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
            r3 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
            receivers = [r1, r2, r3]

            emitter = (random.uniform(3 * x_min, 3 * x_max), random.uniform(3 * y_min, 3 * y_max))
            emitter_lat, emitter_lon = emitter

            tdoas = generate_true_2d_tdoa_data(emitter, receivers)
            noisy_tdoas = tdoas + np.random.normal(scale=noise_variance, size=tdoas.shape)

            true_diff_01 = c * noisy_tdoas[0][1]
            true_diff_02 = c * noisy_tdoas[0][2]
            true_diff_12 = c * noisy_tdoas[1][2]

            def equation(p):
                x, y = p
                eq1 = hyperbola(x, y, receivers[0], receivers[1], true_diff_01)
                eq2 = hyperbola(x, y, receivers[0], receivers[2], true_diff_02)
                eq3 = hyperbola(x, y, receivers[1], receivers[2], true_diff_12)
                return [eq1, eq2, eq3]

            initial_guess = (0, 0)
            result_ls = op.least_squares(equation, initial_guess, bounds=bounds)
            errors[i] = np.linalg.norm(result_ls.x - np.array(emitter))

        mean_errors.append(np.mean(errors))

    plt.plot(variances, mean_errors, marker='o')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Variance of Noise')
    plt.ylabel('Mean Error')
    y_ticks = np.geomspace(min(mean_errors), max(mean_errors), num=10)
    plt.yticks(y_ticks)
    plt.title('Mean Error vs Variance of Noise')
    plt.grid(True)
    plt.show()


def hyperbola(x, y, receiver_1, receiver_2, diff_ab):
    if diff_ab > 0:
        xa, ya = receiver_1
        xb, yb = receiver_2
    else:
        xa, ya = receiver_2
        xb, yb = receiver_1
        diff_ab = -diff_ab
    return np.sqrt((x - xb) ** 2 + (y - yb) ** 2) - np.sqrt((x - xa) ** 2 + (y - ya) ** 2) - diff_ab

def generate_true_2d_tdoa_data(emitter, receivers):
    if emitter:
        assert len(emitter) == 2
    for r in receivers:
        assert len(r) == 2

    emitter_lat, emitter_lon = emitter

    distances = []
    for r_lat, r_lon in receivers:
        d = np.sqrt((r_lat - emitter_lat) ** 2 + (r_lon - emitter_lon) ** 2)
        distances.append(d)

    times = np.array(distances) / c
    min_time = min(times)
    arrival_times = times - min_time
    n = len(arrival_times)

    tdoa = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if i == j:
                continue
            diff = (arrival_times[j] - arrival_times[i])
            tdoa[i, j] = diff
            tdoa[j, i] = diff

    return tdoa

tdoa_solver_2d()
