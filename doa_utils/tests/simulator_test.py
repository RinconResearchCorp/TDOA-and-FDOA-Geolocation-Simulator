import numpy as np

from simulator import simulate_doa
import matplotlib.pyplot as plt

def main():
    emitter_position = np.array([100, 100, 100])
    emitter_velocity = np.array([0, -70, 0])
    receiver_positions = [np.array([0, 0, 0]), np.array([100, 0, 0]), np.array([0, 100, 0]), np.array([0, 0, 100])]
    fft_pos, fft_vel, conv_pos, conv_vel = simulate_doa(emitter_position, emitter_velocity, receiver_positions, None)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(*emitter_position, marker='o', c='b', label='Emitter')
    ax.quiver(*emitter_position, *emitter_velocity, color='b')
    ax.scatter(*fft_pos, marker='o', c='g', label='FFT-CAF')
    ax.quiver(*fft_pos, *fft_vel, color='g')
    ax.scatter(*conv_pos, marker='x', c='r', label='Conv-CAF')
    ax.quiver(*conv_pos, *conv_vel, color='r')
    ax.scatter(*receiver_positions[0], c='k', label=f'Receiver')

    for i, receiver in enumerate(receiver_positions[1:]):
        ax.scatter(*receiver, c='k') 

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    plt.show()

if __name__ == "__main__":
    main()