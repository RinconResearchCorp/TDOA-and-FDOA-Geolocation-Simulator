import numpy as np

from signal_generator import Emitter, Receiver
from solver import estimate_emitter

def main():
    chi_square_val_2d = 5.991  # Chi-square critical value for 95% confidence in 2D

    flag = "tdoa + fdoa"
    dim = 2

    num_receivers_map = {
        "tdoa + fdoa" : dim + 1,
        "tdoa" : dim + 1,
        "fdoa no velocity" : 2*dim + 1,
        "fdoa" : dim + 1,
    }

    num_receivers = num_receivers_map[flag]

    emitter_pos = (np.random.random(dim) - 0.5) * 10000
    emitter_vel = (np.random.random(dim) - 0.5) * 100
    emitter = Emitter(1090e6, emitter_pos, emitter_vel)

    message = "1010"

    receivers = [Receiver(20.90e6, 1e-6, (np.random.random(dim) - 0.5) * 10000) for i in range(num_receivers)]
    
    symbols = emitter.generate_signal(message)

    signals = [receiver.sample_signal(symbols) for receiver in receivers]
    doppler_info = [receivers[i].apply_doppler(signals[i], emitter) for i in range(num_receivers)]
    signals, doppler_freqs = zip(*doppler_info)
    times_info = [receivers[i].add_time_delay(signals[i], emitter) for i in range(num_receivers)]
    time_signal, times = zip(*times_info)

    num_trials = 500
    positions = []
    velocities = []
    for i in range(num_trials):
        times_noise = np.array(times) + np.random.normal(0, 20e-9, len(times))
        times = times_noise.tolist()
        doppler_freqs_noise = np.array(doppler_freqs) + np.random.normal(0, 10, len(doppler_freqs))
        doppler_freqs = doppler_freqs_noise.tolist()
        if flag == "tdoa + fdoa":
            solution = estimate_emitter(receivers, fdoa_data=doppler_freqs, toa_data=times)
            position = solution[:dim]
            velocity = solution[dim:]
            positions.append(position)
            velocities.append(velocity)


        if flag == "tdoa":
            solution = estimate_emitter(receivers, toa_data=times)
            position = solution
            positions.append(position)

        if flag == "fdoa no velocity":
            solution = estimate_emitter(receivers, fdoa_data=doppler_freqs)
            position = solution[:dim]
            velocity = solution[dim:]

        if flag == "fdoa":
            solution = estimate_emitter(receivers, fdoa_data=doppler_freqs, emitter_velocity=emitter_vel)
            position = solution

    errors_pos = [np.linalg.norm(pos - emitter_pos) for pos in positions]
    errors_vel = [np.linalg.norm(vel - emitter_vel) for vel in velocities]
    print(f'Mean error: {np.mean(errors_pos)}')
    print(f'Std error: {np.std(errors_pos)}')
    print(f"median error: {np.median(errors_pos)}")
    print(f"True Emitter Position: {emitter_pos}")
    
    # print(f"Estimated Emitter Position: {position}")
    # print(f"Error in Position: {np.linalg.norm(emitter_pos - position)}")
    
    if flag == "tdoa + fdoa" or flag == "fdoa no velocity":

        print(f"True Emitter Velocity: {emitter_vel}")
        print(f'Mean velocity: {np.mean(velocities)}')
        print(f'Std velocity: {np.std(velocities)}')
        # print(f"Estimated Emitter Velocity: {velocity}")
    
    if flag == "tdoa + fdoa" or flag == "fdoa no velocity":
        print(f"Mean Error in Velocity: {np.mean(errors_vel)}")
        print(f"Median error: {np.median(errors_vel)}")
        print(f"Std Error in Velocity: {np.std(errors_vel)}")



if __name__ == "__main__":
    main()