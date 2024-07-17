import random
import numpy as np
import matplotlib.pyplot as plt

from signal_generator import Emitter, Receiver
from caf import fft_caf, convolution_caf

c = 3e8

def main():
    fs = 1090e6
    sr = 21.80e6
    br = 1e-6
    
    message = ''.join([random.choice(['0', '1']) for _ in range(112)])

    emitter_pos = np.array([0, 75])
    emitter_vel = np.array([0, 270]) # a little more than 600 mph
    receiver_poss = [np.array([0, 0]), np.array([0, 100])]
    emitter = Emitter(fs, emitter_pos, emitter_vel)
    receivers = [Receiver(sr, br, receiver_pos) for receiver_pos in receiver_poss]

    symbols = emitter.generate_signal(message)

    signals = []
    tshifts = []
    fshifts = []

    for receiver in receivers:
        signal, tshift, fshift = receiver.receive(symbols, emitter, return_true_values=True)
        signals.append(signal)
        tshifts.append(tshift)
        fshifts.append(fshift)
    
    tdoa = tshifts[1] - tshifts[0]
    fdoa = fshifts[1] - fshifts[0]

    fft_cafvals, fft_tshift, fft_fshift, _, _ = fft_caf(signals[0], signals[1], int(2 * tdoa))
    conv_cafvals, conv_tshift, conv_fshift, _, _ = convolution_caf(signals[0], signals[1], int(2 * fdoa))

    print(f"True TDOA: {tdoa} - True FDOA: {fdoa}")
    print(f"FFT TDOA: {fft_tshift / sr} - FFT FDOA: {fft_fshift * sr}")
    print(f"Convolution TDOA: {conv_tshift / sr} - Convolution FDOA: {conv_fshift * sr}")

    plt.imshow(np.abs(fft_cafvals), origin='lower', aspect = 'auto')
    plt.title("FFT CAF")
    plt.show()
    plt.imshow(np.abs(conv_cafvals), origin='lower', aspect = 'auto')
    plt.title("Convolution CAF")
    plt.show()

if __name__ == '__main__':  
    main()