import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as op
import random
from geopy import distance


c = 299792458.0  # speed of light in m/s

def tdoa_solver_3d():
    x_min = -100
    x_max = 100
    y_min = -100
    y_max = 100
    z_min = 0
    z_max = 100
    bounds = ([3*x_min, 3*y_min, 3*z_min], [3*x_max, 3*y_max, 3*z_max])
    num_trials = 1000

    noise_variances = np.logspace(-10, -5, 30)
    mean_errors = []

    for noise_variance in noise_variances:
        errors = np.zeros(num_trials)

        for i in range(num_trials):
            r0 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
            r1 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
            r2 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
            r3 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
            receivers = [r0, r1, r2, r3]

            emitter = (random.uniform(3*x_min, 3*x_max), random.uniform(3*y_min, 3*y_max), random.uniform(3*z_min, 3*z_max))

            tdoas = generate_true_tdoa_data(emitter, receivers)
            noise = np.random.normal(0, noise_variance, tdoas.shape)
            noisy_tdoas = tdoas + noise

            true_diffs = c * noisy_tdoas[np.triu_indices(len(receivers), 1)]

            def equations(p):
                x, y, z = p
                eq1 = hyperboloid_3d(x, y, z, receivers[0], receivers[1], true_diffs[0])
                eq2 = hyperboloid_3d(x, y, z, receivers[0], receivers[2], true_diffs[1])
                eq3 = hyperboloid_3d(x, y, z, receivers[0], receivers[3], true_diffs[2])
                eq4 = hyperboloid_3d(x, y, z, receivers[1], receivers[2], true_diffs[3])
                eq5 = hyperboloid_3d(x, y, z, receivers[1], receivers[3], true_diffs[4])
                eq6 = hyperboloid_3d(x, y, z, receivers[2], receivers[3], true_diffs[5])
                return [eq1, eq2, eq3, eq4, eq5, eq6]

            initial_guess = (0, 0, 3*z_max)
            result = op.least_squares(equations, initial_guess, bounds=bounds, ftol=1e-12, xtol=1e-12, gtol=1e-12)
            errors[i] = np.linalg.norm(result.x - np.array(emitter))


        mean_errors.append(np.mean(errors))

    plt.figure()
    plt.plot(noise_variances, mean_errors)
    plt.xscale("log")
    plt.xlabel('Noise Variance')
    plt.ylabel('Mean Error')
    plt.title('Mean Error vs Noise Variance for 3D TDOA Solver')
    plt.grid(True, which="both", ls="--")
    plt.show()

def hyperboloid_3d(x, y, z, receiver_1, receiver_2, diff_ab):
    if diff_ab > 0:
        xa, ya, za = receiver_1
        xb, yb, zb = receiver_2
    else:
        xa, ya, za = receiver_2
        xb, yb, zb = receiver_1
        diff_ab = -diff_ab
    return np.sqrt((x - xb) ** 2 + (y - yb) ** 2 + (z - zb) ** 2) - np.sqrt((x - xa) ** 2 + (y - ya) ** 2 + (z - za) ** 2) - diff_ab

def generate_true_tdoa_data(emitter, receivers, coord_sys='cartesian'):
    distance_func = get_distance_func(len(emitter), coord_sys)

    # physical distances between receivers and emitters
    distances = []
    for r in receivers:
        d = distance_func(emitter, r)
        distances.append(d)

    times = np.array(distances)/c
    min_time = min(times)
    arrival_times = times - min_time
    n = len(arrival_times)
    
    tdoa = np.zeros( (n, n))

    for i in range(n):
        for j in range(i + 1, n):
            if i == j:
                continue
            diff = arrival_times[j] - arrival_times[i]
            tdoa[i,j] = diff
            tdoa[j,i] = diff
    
    return tdoa

def get_distance_func(dim, coord_sys):
    if coord_sys == 'cartesian':
        if dim == 2:
            return lambda x,y: np.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)
        if dim == 3:
            return lambda x,y: np.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2 + (x[2] - y[2])**2)
        
    if coord_sys == 'latlon':
        if dim == 2:
            return lambda x,y: distance.distance(x,y).m
        if dim == 3:
            return lambda x,y: np.sqrt( (distance.distance((x[0], x[1]), (y[0], y[1])).m)**2 + (x[2] - y[2])**2)

tdoa_solver_3d()
