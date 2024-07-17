import numpy as np
from scipy import optimize as op
import random
# possible imports for 3d graphing
import matplotlib.pyplot as plt
from geopy import distance
from collections import Counter

c = 299792458.0 # speed of light in m/s
chi_square_val = 7.815

def tdoa_solver_3d():

    
    x_min = -100
    x_max = 100
    y_min = -100
    y_max = 100
    z_min = 0
    z_max = 100
    bounds = ([5*x_min, 5*y_min, z_min], [5*x_max, 5*y_max, 5*z_max])
    
    # receivers = [(x_min, y_min, z_min), (x_min, y_max, z_min), (x_max, y_min, z_min), (x_max, y_max, z_min)]
    # emitter = (0, 4, 3*z_max)
    # emitter_lat, emitter_lon, emitter_alt = emitter 

    num_trials = 100
    count = 0
    
        
    r0 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
    r1 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
    r2 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
    r3 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
    #r4 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max), random.uniform(z_min, z_max))
    receivers = [r0, r1, r2, r3]
    receiver_pairs = [
            (0, 1), (0, 2), (0, 3),
            (1, 2), (1, 3),
            (2, 3),
        ]

    emitter = (random.uniform(3*x_min, 3*x_max), random.uniform(3*y_min, 3*y_max), random.uniform(3*z_min, 3*z_max))

    tdoas = generate_true_tdoa_data(emitter, receivers)

    x = np.linspace(3*x_min-1, 3*x_max+1, 300)
    y = np.linspace(3*y_min-1, 3*y_max+1, 300)
    z = np.linspace(3*z_min-1, 3*z_max+1, 300)

    true_diffs = c * tdoas


    def equations(p):
        x, y, z = p

        return [
            hyperboloid_3d(x, y, z, receivers[pair[0]], receivers[pair[1]], true_diffs[pair[0]][pair[1]])
            for pair in receiver_pairs
        ]

    initial_guess = (0, 0, 3*z_max)
    result = op.least_squares(equations, initial_guess, bounds=bounds, ftol=1e-12, xtol=1e-12, gtol=1e-12)

    x_est, y_est, z_est = result.x

    FIM = compute_FIM_3d(receivers, np.array([x_est, y_est, z_est]))
    CRLB = np.linalg.inv(FIM)
    eigenvalues, eigenvectors = np.linalg.eigh(CRLB)
    scaled_eigenvalues = np.sqrt(eigenvalues * chi_square_val)

    # Get the orientation of the ellipse
    width, height, depth = 2 * scaled_eigenvalues

    # Since plotting in 3D requires a different approach, for now, we will print the results
    print("Eigenvalues:", eigenvalues)
    print("Eigenvectors:\n", eigenvectors)
    print("Width:", width)
    print("Height:", height)
    print("Depth:", depth)

    points = []
    initial_guess = [(0, 0, 3*z_max), (3*x_min, 3*y_min, z_max), (3*x_max, 3*y_min, z_max), (3*x_min, 3*y_max, z_max), (3*x_max, 3*y_max, z_max)]
    best_est = []
    for i in range(num_trials):
        curr_points = []
        noisy_tdoas = tdoas + np.random.normal(0, 0.00636, tdoas.shape)
        noisy_tdoas = noisy_tdoas*c
        def noisy_equations(p):
            x, y, z = p
            return [hyperboloid_3d(x, y, z, receivers[pair[0]], receivers[pair[1]], noisy_tdoas[pair[0]][pair[1]]) for pair in receiver_pairs]
        for i in initial_guess:
            noisy_result = op.least_squares(noisy_equations, i, bounds=bounds, ftol=1e-8, xtol=1e-8, gtol=1e-8)
            res_x, res_y, res_z = noisy_result.x
            point = [res_x, res_y, res_z]
            res = np.linalg.norm(noisy_result.x)
            curr_points.append(point)

        points_as_tuples = [tuple(p) for p in curr_points]
        point_counts = Counter(points_as_tuples)
        most_common_point, count = point_counts.most_common(1)[0]
        most_common_point = list(most_common_point)
        best_est.append(most_common_point)
        points.append(curr_points)
    
            # if res < 600:
            #     points.append(point)
            # translated_point = np.array(point) - np.array([x_est, y_est, z_est])
            # transformed_point = np.dot(translated_point, eigenvectors) / scaled_eigenvalues
            # dist = np.linalg.norm(transformed_point)
            # if dist <= 1:
            #     count += 1

    points = np.array(points)
    print(best_est)
    print(len(best_est))
    print(emitter)
    # print("number of points plotted:", len(points))
    # print("Count of points within ellipsoid:", count)


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter([r[0] for r in receivers], [r[1] for r in receivers], [r[2] for r in receivers], c='blue', label='Receivers')
    ax.scatter([e[0] for e in best_est], [e[1] for e in best_est], [e[2] for e in best_est], c='red', marker='o', s=10, label='Best Estimates')
    #ax.scatter(points[:, 0], points[:, 1], points[:, 2], label='Noisy Emitter Locations')
    ax.scatter(*emitter, c='black', marker='s', s=100, label='True Emitter Location')
    ax.scatter(x_est, y_est, z_est, c='green', marker='s', s=60, label='Estimated Emitter Location')
    
    # Plot the error ellipsoid
    plot_error_ellipsoid(ax, np.array([x_est, y_est, z_est]), scaled_eigenvalues, eigenvectors)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D TDOA Visualization')
    ax.legend()
    plt.show()
        
        # errors = np.linalg.norm(result.x - np.array(emitter))
        # values = [
        #     hyperboloid_3d(x, y, z, receivers[pair[0]], receivers[pair[1]], true_diffs[pair[0]][pair[1]])
        #     for pair in receiver_pairs
        # ]

        # if errors[i] > 1 and np.all(values) < 1e-8:
        #     second_soln_count += 1

    # print(f'Mean error: {np.mean(errors)}')
    # print(f'Std error: {np.std(errors)}')
    # print(f"median error: {np.median(errors)}")
    # print(f"Percent correct solutions: {np.sum(errors < 1) / num_trials * 100}")
    # print(f"Percent of choosing wrong from 2 solutions: {second_soln_count / num_trials * 100}")


def compute_FIM_3d(receivers, emitter):
    num_receivers = len(receivers)
    FIM = np.zeros((3, 3))

    for i in range(num_receivers):
        for j in range(i + 1, num_receivers):
            ri = np.array(receivers[i])
            rj = np.array(receivers[j])
            e = np.array(emitter)

            di = np.linalg.norm(ri - e)
            dj = np.linalg.norm(rj - e)

            grad_i = (e - ri) / di
            grad_j = (e - rj) / dj

            grad_diff = grad_i - grad_j
            FIM += np.outer(grad_diff, grad_diff)

    return FIM

def plot_error_ellipsoid(ax, center, radii, rotation):
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = radii[0] * np.outer(np.cos(u), np.sin(v))
    y = radii[1] * np.outer(np.sin(u), np.sin(v))
    z = radii[2] * np.outer(np.ones_like(u), np.cos(v))

    ellipsoid_points = np.array([x.flatten(), y.flatten(), z.flatten()])
    rotated_ellipsoid_points = rotation @ ellipsoid_points

    x = rotated_ellipsoid_points[0, :].reshape(100, 100) + center[0]
    y = rotated_ellipsoid_points[1, :].reshape(100, 100) + center[1]
    z = rotated_ellipsoid_points[2, :].reshape(100, 100) + center[2]

    ax.plot_surface(x, y, z, color='orange', alpha=0.5, rstride=4, cstride=4, linewidth=0)




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