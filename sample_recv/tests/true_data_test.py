import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib import cm

from doa_utils.caf import fft_caf

def main():

    # load IQ Data:
    iq_data = np.loadtxt('sample_recv/test3.csv', delimiter=',')
    iq_data1 = iq_data[:, 0] + 1j * iq_data[:, 1]

    # iq_data2 = np.roll(iq_data1, 20)

    iq_data = np.loadtxt('sample_recv/test4.csv', delimiter=',')
    iq_data2 = iq_data[:, 0] + 1j * iq_data[:, 1]

    # min_len = min(len(iq_data1), len(iq_data2))
    # iq_data1 = iq_data1[:min_len]
    # iq_data2 = iq_data2[:min_len]

    caf_out, time_shift, freq_shift, max_mag, median_mag = fft_caf(iq_data1, iq_data2, 30)

    print("Time Shift: ", time_shift)
    print("Freq Shift: ", freq_shift)
    print("Max Mag: ", max_mag)
    print("Median Mag: ", median_mag)
    print("Variance: ", max_mag / median_mag)

    # plt.imshow(np.abs(caf_out), aspect='auto')
    # plt.show()

    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    X, Y = np.linspace(-6, 6, caf_out.shape[1]), np.linspace(-800, 800, caf_out.shape[0])
    X, Y = np.meshgrid(X, Y)

    Z = np.abs(caf_out)
    ls = LightSource(270, 45)
    rgb = ls.shade(Z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=rgb,
                       linewidth=0, antialiased=False, shade=False)
    
    plt.imshow(np.abs(caf_out), aspect='auto', extent=[-6, 6, -800, 800])
    plt.show()

if __name__ == "__main__":
    main()