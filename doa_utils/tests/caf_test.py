import numpy as np
import matplotlib.pyplot as plt
from caf import naive_caf, fft_caf, convolution_caf

def test_caf():
    sig1 = np.random.randn(256) + 1j * np.random.randn(256)

    fft_caf_out1, tshift1, fshift1, max_mag, median_mag = fft_caf(sig1, sig1, 51)
    print(tshift1, fshift1, max_mag, median_mag)

    conv_caf_out1, tshift1, fshift1, max_mag, median_mag = convolution_caf(sig1, sig1, 100)
    print(tshift1, fshift1, max_mag, median_mag)

    sig2 = np.roll(sig1, 2)

    fft_caf_out2, tshift1, fshift1, max_mag, median_mag = fft_caf(sig1, sig2, 51)
    print(tshift1, fshift1, max_mag, median_mag)
    
    conv_caf_out2, tshift2, fshift2, max_mag, median_mag = convolution_caf(sig1, sig2)
    print(tshift2, fshift2, max_mag, median_mag)

    sig3 = sig1 *  np.exp(1j * 2 * np.pi * .1 * np.arange(len(sig1)))

    fft_caf_out3, tshift3, fshift3, max_mag, median_mag = fft_caf(sig1, sig3, 100)
    print(tshift3, fshift3, max_mag, median_mag)

    conv_caf_out3, tshift3, fshift3, max_mag, median_mag = convolution_caf(sig1, sig3, 1000)
    print(tshift3, fshift3, max_mag, median_mag)

    sig4 = np.roll(sig3, 2)
    
    fft_caf_out4, tshift4, fshift4, max_mag, median_mag = fft_caf(sig1, sig4, 100)
    print(tshift4, fshift4, max_mag, median_mag)

    conv_caf_out4, tshift4, fshift4, max_mag, median_mag = convolution_caf(sig1, sig4, 1000)
    print(tshift4, fshift4, max_mag, median_mag)

    # cafs = [fft_caf_out1, fft_caf_out2, fft_caf_out3, fft_caf_out4, conv_caf_out1, conv_caf_out2, conv_caf_out3, conv_caf_out4]
    # titles = ["No shift fft", "2 sample shift fft", ".1 freq shift fft", "2 sample, .1 freq shift fft", "No shift conv", "2 sample shift conv", ".1 freq shift conv", "2 sample, .1 freq shift conv"]

    # fig, ax = plt.subplots(2, 4)
    # # let ax be indexed by one value instead of tuple
    # ax = ax.ravel()

    # for i, caf in enumerate(cafs):
    #     ax[i].imshow(np.abs(caf), origin='lower', aspect = 'auto')
    #     ax[i].set_title(titles[i])
    #     ax[i].set_xlabel("time")
    #     ax[i].set_ylabel("frequency")

    # plt.show()

if __name__ == '__main__':
    test_caf()