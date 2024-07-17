import numpy as np
import matplotlib.pyplot as plt
from signal_generator import Emitter, Receiver

import random
import matplotlib.pyplot as plt
from matplotlib import cm

from caf import fft_caf, convolution_caf

def main():
    emitter = Emitter(1090e6, np.array([0, 0, 0]), np.array([1000, 0, 0]))
    receiver1 = Receiver(21.80e6, 1e-6, np.array([1000, 9000, 7000]))
    receiver2 = Receiver(21.80e6, 1e-6, np.array([-500, 0, 0]))
    
    message = ''.join([random.choice('01') for _ in range(10000)])
   
    symbols = emitter.generate_signal(message)
 
    signal1 = receiver1.sample_signal(symbols)
    signal2 = receiver2.sample_signal(symbols)

    tsignal1, t1 = receiver1.add_time_delay(signal1, emitter)
    tsignal2, t2 = receiver2.add_time_delay(signal2, emitter)
    tshift_samples = int((t1 - t2) * receiver1.sample_rate) 
    dsignal1, f1 = receiver1.apply_doppler(tsignal1, emitter)
    dsignal2, f2 = receiver2.apply_doppler(tsignal2, emitter)

    print(f"True TDOA (seconds): {(t1 - t2) / receiver1.sample_rate}")
    print(f"True TDOA (samples): {tshift_samples}")
    print(f"True FDOA (Hz): {(f1) - (f2)}")
    print(f"Signal length: {len(dsignal1)}")
        
    caf, tshift, fshift, max_caf, med_caf = fft_caf(dsignal1, dsignal2, 1000)
    # caf, tshift, fshift, max_caf, med_caf = convolution_caf(dsignal1, dsignal2, 1001)

    print(f"Estimated TDOA (samples): {tshift}")
    print(f"Estimated TDOA (seconds): {tshift / receiver1.sample_rate}")
    print(f"Estimated FDOA (Hz): {fshift * receiver1.sample_rate}")
    print(f"Max CAF: {max_caf}")
    print(f"Median CAF: {med_caf}")

    max_idx = np.argmax(np.abs(caf))  # Flatten index
    max_freq_idx, max_time_idx = np.unravel_index(max_idx, caf.shape)

    # Define the size of the neighborhood around the peak to visualize
    half_window_size = 25  # Adjust this based on your specific needs

    # Calculate the bounds, ensuring they stay within the array limits
    start_freq_idx = max(max_freq_idx - half_window_size, 0)
    end_freq_idx = min(max_freq_idx + half_window_size, caf.shape[0])
    start_time_idx = max(max_time_idx - half_window_size, 0)
    end_time_idx = min(max_time_idx + half_window_size, caf.shape[1])

    # Extract the subset of the data around the peak
    subset_caf = np.abs(caf[start_freq_idx:end_freq_idx, start_time_idx:end_time_idx])

    # Create meshgrid for plotting
    time_ax = np.arange(start_time_idx, end_time_idx)
    freq_ax = np.arange(start_freq_idx, end_freq_idx)
    T, F = np.meshgrid(time_ax, freq_ax)

    # Create a 3D plot
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    surf = ax.plot_surface(T, F, subset_caf, cmap=cm.coolwarm, linewidth=0, antialiased=True)

    # Customize the axes.
    ax.set_xlabel('Time Shifts')
    ax.set_ylabel('Frequency Shifts')
    ax.set_zlabel('CAF Magnitude')

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()


if __name__ == '__main__':
    main()


# def main():
#     # Constants:
#     c = 299792458.0 # Speed of light [m/s]
#     f0 = 1090e6 # Carrier frequency [Hz]
#     fs = 2 * f0 # Sampling frequency [Hz]
#     bit_duration = 1e-6 # [s]

#     flag = 'test_caf'

#     starting_message = 'Hello!'
#     binary_message = ''.join(format(ord(i), '08b') for i in starting_message)

#     if flag == "test_caf":
#         emitter_pos = np.array([0, 0])
#         emitter_vel = np.array([50, 50])
#         emitter = Emitter(f0, emitter_pos, emitter_vel)

#         receiver1_pos = np.array([10, 10])
#         receiver1 = Receiver(fs, bit_duration, receiver1_pos)

#         receiver2_pos = np.array([-15, -15])
#         receiver2 = Receiver(fs, bit_duration, receiver2_pos)
    
#         symbols = emitter.generate_signal(binary_message)

#         signal1, tshift1 = receiver1.receive(symbols, emitter)
#         signal2, tshift2 = receiver2.receive(symbols, emitter)

#         signal2 = signal2 * np.exp(2j*np.pi * 100000 * np.arange(len(signal2)) / fs)

#         # print(f"True TDOA (seconds): {tshift1 - tshift2}")
#         print(f"True TDOA (seconds): {(tshift1 - tshift2)}")

#         caf1, t1, f1, mag1, med1 = convolution_caf(signal1, signal2, 150)

#         print(f"Estimated TDOA (seconds): {t1 / fs}")
#         print(f"Estimated FDOA: {f1}")
#         print (f"Caf peak magnitude: {mag1} - Median: {med1}")
