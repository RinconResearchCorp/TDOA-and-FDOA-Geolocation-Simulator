import numpy as np

def naive_caf(sig1, sig2, max_time_shift, max_freq_shift, num_freqs = 51):
    assert len(sig1) == len(sig2), "Signals must be the same length."
    
    K = len(sig1)

    time_shifts = np.arange(-max_time_shift, max_time_shift + 1)
    freq_shifts = np.linspace(-max_freq_shift, max_freq_shift, num_freqs) / K

    print(time_shifts)
    print(freq_shifts)

    caf_out = np.zeros((len(freq_shifts), len(time_shifts)), dtype = np.complex128)

    for i, tshift in enumerate(time_shifts):
        for j, fshift in enumerate(freq_shifts):
            sig2_shifted = np.roll(sig2, tshift).conj()
            caf = sig1 * sig2_shifted * np.exp(-2j * np.pi * fshift * np.arange(K))
            caf_out[j, i] = np.sum(caf)

    max_ind = np.unravel_index(np.argmax(np.abs(caf_out)), caf_out.shape)
    time_shift  = time_shifts[max_ind[1]]
    freq_shift = freq_shifts[max_ind[0]]

    return caf_out, time_shift, freq_shift

def fft_caf(sig1, sig2, max_time_shift):
    assert len(sig1) == len(sig2), "Signals must be the same length."

    K = len(sig1)
    time_shifts = np.arange(-max_time_shift, max_time_shift + 1)
    
    caf_out = np.zeros((K, len(time_shifts)), dtype = np.complex128)

    for i, tshift in enumerate(time_shifts):
        sig2_shifted = np.roll(sig2, -tshift).conj()
        caf = np.fft.fft(sig1 * sig2_shifted)
        caf_out[:, i] = caf
    
    max_ind = np.unravel_index(np.argmax(np.abs(caf_out)), caf_out.shape)

    time_shift  = time_shifts[max_ind[1]]
    # freq_shift = (K - max_ind[0]) % K / K
    freq_shift = (((max_ind[0] + (K // 2)) % K) - (K // 2)) / K

    max_mag = np.max(np.abs(caf_out))
    median_mag = np.median(np.abs(caf_out))

    return caf_out, time_shift, freq_shift, max_mag, median_mag

def convolution_caf(sig1, sig2, num_freq_shifts = 51):
    assert len(sig1) == len(sig2), "Signals must be the same length."

    K = len(sig1)

    freq_sig1 = np.fft.fft(sig1)
    freq_sig2 = np.fft.fft(sig2)
    freq_sig2_conj = freq_sig2.conj()

    half_shifts = num_freq_shifts // 2
    caf_out = np.zeros((num_freq_shifts, K), dtype = np.complex128)

    for ind in range(num_freq_shifts):
        i = ind - half_shifts  
        # sig1_shifted = np.roll(freq_sig1, i)
        sig1_shifted = freq_sig1
        sig2_shifted = np.roll(freq_sig2_conj, -2*i)
        caf = np.fft.ifft(sig1_shifted * sig2_shifted)
        caf_out[ind, :] = caf

    max_ind = np.unravel_index(np.argmax(np.abs(caf_out)), caf_out.shape)

    time_shift  = (K - max_ind[1]) % K - K
    # time_shift = (max_ind[1] - K // 2) % K if max_ind[1] >= K // 2 else (max_ind[1] + K // 2) % K

    freq_shift = (max_ind[0] - half_shifts) / K * 2  

    max_mag = np.max(np.abs(caf_out))
    median_mag = np.median(np.abs(caf_out))

    return caf_out, time_shift, -freq_shift, max_mag, median_mag