import numpy as np
import matplotlib.pyplot as plt
import pymap3d as pm
from scipy import optimize as op
import random
from matplotlib.patches import Ellipse

c = 299792458.0 # speed of light in m/s
confidence_level = 0.95
chi_square_val = 5.991  # Chi-square critical value for 95% confidence in 2D
'''
###################################
test case for 2 possible solutions
receivers = [(-131, -120), (-68, -122), (-72, -68)]
emitter = (5, 40)
emitter_lat, emitter_lon = emitter
'''


'''
# physical distances between receivers and emitters
real_dists = []
for r in receivers:
    receiver_lat, receiver_lon = r
    d = np.sqrt((receiver_lat - emitter_lat)**2 + (receiver_lon - emitter_lon)**2)
    real_dists.append(d)

diff_01 = (real_dists[1] - real_dists[0])
diff_02 = (real_dists[2] - real_dists[0])
diff_12 = (real_dists[2] - real_dists[1])
'''

def tdoa_solver_2d():
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------
    # loop to get generalized error of the solver
    num_trials = 0   # change this value to run the loop or not
    second_soln_count = 0 
    errors = np.zeros(num_trials)
    for i in range (num_trials):

        r1 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        r2 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        r3 = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        receivers = [r1, r2, r3]

        emitter = (random.uniform(3*x_min, 3*x_max), random.uniform(3*y_min, 3*y_max))
        emitter_lat, emitter_lon = emitter

        tdoas = generate_true_2d_tdoa_data(emitter, receivers)
        
        x = np.linspace(3*x_min-1, 3*x_max+1, 300)
        y = np.linspace(3*y_min-1, 3*y_max+1, 300)
        X, Y = np.meshgrid(x, y)
        initial_guess = (0, 0)

        true_diff_01 = c*tdoas[0][1]
        true_diff_02 = c*tdoas[0][2]
        true_diff_12 = c*tdoas[1][2]

        eq0 = hyperbola(X, Y, receivers[0], receivers[1], true_diff_01)
        eq1 = hyperbola(X, Y, receivers[0], receivers[2], true_diff_02)
        eq2 = hyperbola(X, Y, receivers[1], receivers[2], true_diff_12)

        def equation(p):
            x, y = p
            eq1 = hyperbola(x, y, receivers[0], receivers[1], true_diff_01)
            eq2 = hyperbola(x, y, receivers[0], receivers[2], true_diff_02)
            eq3 = hyperbola(x, y, receivers[1], receivers[2], true_diff_12)
            return [eq1, eq2, eq3]

        result_ls = op.least_squares(equation, initial_guess, bounds=bounds, ftol=1e-8, xtol=1e-8, gtol=1e-8)
        errors[i] = np.linalg.norm(result_ls.x - np.array(emitter))

        x_est, y_est = result_ls.x

        val0 = hyperbola(x_est, y_est, receivers[0], receivers[1], true_diff_01)
        val1 = hyperbola(x_est, y_est, receivers[0], receivers[2], true_diff_02)
        val2 = hyperbola(x_est, y_est, receivers[1], receivers[2], true_diff_12)
        
        if errors[i] > 1 and val0 < 1e-8 and val1 < 1e-8 and val2 < 1e-8:
            second_soln_count +=1
            

    # print(f'Mean error: {np.mean(errors)}')
    # print(f'Std error: {np.std(errors)}')
    # print(f"median error: {np.median(errors)}")
    # print(f"Percent correct solutions: {np.sum(errors < 1) / num_trials * 100}")
    # print(f"Percent of choosing wrong from 2 solutions: {second_soln_count / num_trials * 100}")
    # x_true, y_true = result_ls.x
# end of loop for error tests -----------------------------------------------------------------------------------------------------------------------------------
#-------------------------start of loop to add noise-------------------------------------------------------------------------------------------------------------
    x_min, x_max = -100, 100
    y_min, y_max = -10, 100
    bounds = ([5*x_min, 5*y_min], [5*x_max, 5*y_max])

    x = np.linspace(3 * x_min - 10, 3 * x_max + 10, 300)
    y = np.linspace(3 * y_min - 10, 3 * y_max + 10, 300)
    X, Y = np.meshgrid(x, y)
    

    receivers = [(random.uniform(x_min, x_max), random.uniform(y_min, y_max)) for _ in range(3)]
    emitter = (random.uniform(3*x_min, 3*x_max), random.uniform(3*y_min, 3*y_max))
    emitter_lat, emitter_lon = emitter

    initial_guess = (emitter_lat, emitter_lon) + np.random.random(2)*5

    tdoas = generate_true_2d_tdoa_data(emitter, receivers)

    num_samples = 200 # change here to run loop or not
    equations = []
    results_x = []
    results_y = []
    
    
# end of loop -----------------------------------------------------------------------------------------------------------------------------------------------       

    # r1 = (x_min, y_min)
    # r2 = (x_min, y_max)
    # r3 = (x_max, y_min)
    # receivers = [r1, r2, r3]

    # emitter = (3*x_max, 3*y_max)
    # emitter_lat, emitter_lon = emitter


    diff_01 = c*tdoas[0][1]
    diff_02 = c*tdoas[0][2]
    diff_12 = c*tdoas[1][2]

    eqA = hyperbola(X, Y, receivers[0], receivers[1], diff_01)
    eqB = hyperbola(X, Y, receivers[0], receivers[2], diff_02)
    eqC = hyperbola(X, Y, receivers[1], receivers[2], diff_12)
        
    def equations(p):
        x, y = p
        eq1 = hyperbola(x, y, receivers[0], receivers[1], diff_01)
        eq2 = hyperbola(x, y, receivers[0], receivers[2], diff_02)
        eq3 = hyperbola(x, y, receivers[1], receivers[2], diff_12)
        return [eq1, eq2, eq3]

    # Find estimated emitter location (no noise)
    result = op.least_squares(equations, initial_guess, bounds=bounds, ftol=1e-12, xtol=1e-12, gtol=1e-12)
    x_est, y_est = result.x

    FIM = compute_FIM(receivers, np.array([x_est, y_est]))
    CRLB = np.linalg.inv(FIM)
    eigenvalues, eigenvectors = np.linalg.eigh(CRLB)

    
    # Get the orientation of the ellipse
    angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))
    width = 2 * np.sqrt(eigenvalues[0] * chi_square_val)
    height = 2 * np.sqrt(eigenvalues[1] * chi_square_val)

    # print("Eigenvalues:", eigenvalues)
    # print("Eigenvectors:", eigenvectors)
    # print(width, height)

    for sample in range(num_samples):       
        tdoas = generate_true_2d_tdoa_data(emitter, receivers)
        # Add noise to the TDOA data (assuming Gaussian noise)
        noisy_tdoas = tdoas + np.random.normal(0, 10e-9)
        
        diff_01 = c*noisy_tdoas[0][1]
        diff_02 = c*noisy_tdoas[0][2]
        diff_12 = c*noisy_tdoas[1][2]

        def equations(p):
            x, y = p
            eq1 = hyperbola(x, y, receivers[0], receivers[1], diff_01)
            eq2 = hyperbola(x, y, receivers[0], receivers[2], diff_02)
            eq3 = hyperbola(x, y, receivers[1], receivers[2], diff_12)
            return [eq1, eq2, eq3]

        # Find estimated emitter location
        result_ls = op.least_squares(equations, initial_guess, bounds=bounds)
        res_x, res_y = result_ls.x

        curr_err = np.linalg.norm(result_ls.x - emitter)

        if curr_err < max(0.5*width, 0.5*height):
            results_x.append(res_x)
            results_y.append(res_y)
        
    fig, ax = plt.subplots()
    ellipse = Ellipse(xy=(x_est, y_est), width=width, height=height, angle=angle, edgecolor='orange', facecolor='orange', alpha=0.5)    
    ax.plot([r[0] for r in receivers], [r[1] for r in receivers], 'bo', label='Receivers')
    ax.add_patch(ellipse)
    
    plt.scatter([r for r in results_x], [r for r in results_y], s=3, label='noise results')
    plt.contour(X, Y, eqA, levels=[0], colors='r')
    plt.contour(X, Y, eqB, levels=[0], colors='g')
    plt.contour(X, Y, eqC, levels=[0], colors='b')
    plt.scatter(emitter_lat, emitter_lon, c='black', marker='s', s=100, label='True Emitter Location')
    plt.scatter(x_est, y_est, c='green', marker='s', s=60, label='Estimated Emitter Location')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('TDOA Visualization')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

    # for A in hyperbolaA:
    #     plt.contour(X, Y, A, levels=[0], colors='r', alpha=0.2)
    # for B in hyperbolaB:
    #     plt.contour(X, Y, B, levels=[0], colors='g', alpha=0.2)
    # for C in hyperbolaC:
    #     plt.contour(X, Y, C, levels=[0], colors='b', alpha=0.2)
    # error = np.sqrt((x_est - emitter_lat)**2 + (y_est - emitter_lon)**2)

    # plt.contour(X, Y, eq0, levels=[0], colors='r')
    # plt.contour(X, Y, eq1, levels=[0], colors='g')
    # plt.contour(X, Y, eq2, levels=[0], colors='b')
    # plt.scatter(emitter_lat, emitter_lon, c='black', marker='s', s=100,  label='True Emitter Location')
    # plt.scatter(x_est, y_est, c='green', marker='s', s=60, label='Estimated Emitter Location')
    # plt.scatter([r[0] for r in receivers], [r[1] for r in receivers], c='blue', label='Receivers')
    # #plt.scatter([r.x[0] for r in results], [r.x[1] for r in results], c='red', label='estimated emitters')
    # #plt.annotate(f'Error: {error:.2f}', xy=(x_est, y_est), xytext=(x_est + 1, y_est + 1),
    # #            arrowprops=dict(facecolor='black', shrink=.05))
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.title('TDOA Visualization')
    # plt.legend()
    # plt.grid(True)
    # plt.axis('equal')
    # plt.show()

def compute_FIM(receivers, emitter):
    num_receivers = len(receivers)
    FIM = np.zeros((2, 2))  # 2x2 matrix for 2D localization
    
    for i in range(num_receivers):
        for j in range(i + 1, num_receivers):
            ri = np.array(receivers[i])
            rj = np.array(receivers[j])
            e = np.array(emitter)
            
            # Distances from the emitter to receivers
            di = np.linalg.norm(ri - e)
            dj = np.linalg.norm(rj - e)
            
            # Gradients
            grad_i = (e - ri) / di
            grad_j = (e - rj) / dj
            
            # Gradient difference
            grad_diff = grad_i - grad_j
            
            # Update FIM
            FIM += np.outer(grad_diff, grad_diff)
    
    return FIM

    
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
    '''
        Generates precide time difference of arrival provided with emitter and receiver locations
        Does not consider altitude - hence 2d data

        emitter: (lat, lon), position for emitter if known
        receivers: [(lat, lon), (lat, lon), ...] = coords for [receiver0, receiver1, ...]
        returns: matrix of tdoa values with shape (num_receivers, num_receivers)  
                 tdoa[i,j] == tdoa[j,i] is the time difference between receiver i and j  
    '''

    if emitter:
        assert len(emitter) == 2 
    for r in receivers:
        assert len(r) == 2  

    emitter_lat, emitter_lon = emitter

    # physical distances between receivers and emitters
    distances = []
    for r_lat, r_lon in receivers:
        d = np.sqrt((r_lat - emitter_lat)**2 + (r_lon - emitter_lon)**2)
        
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
            diff = (arrival_times[j] - arrival_times[i])
            tdoa[i,j] = diff
            tdoa[j,i] = diff
    
    return tdoa
    
tdoa_solver_2d()