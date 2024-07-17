from typing import List

import numpy as np


class Emitter: 
    def __init__(self, 
                 frequency: int, 
                 position: np.ndarray,
                 velocity: np.ndarray):
        self.frequency = frequency
        self.sample_rate = 20 * self.frequency # 20 samples per cycle for continuous effect when emitting
        self.position = position
        self.velocity = velocity

        self.preamble = '101000010100000'
        self.modulator = {'0' : -1, # exp(2pi * j * freq * (0 + pi))
                          '1' : 1} # exp(2pi * j * freq * 1)

    def generate_signal(self, 
                        bits: str):
        bits = self.preamble + bits
                
        symbols = []

        for i, bit in enumerate(bits):
            symbols.append(self.modulator[bit])

        return symbols
    
class Receiver:
    def __init__(self, 
                 sample_rate: int, # samples / sec
                 bit_duration: int, # sec / bit
                 position: np.ndarray): # cartesian position coords
        # info about emitter to sample accurately
        self.sample_rate = sample_rate 
        self.bit_duration = bit_duration
        self.position = position

    def sample_signal(self, symbols: List[int]):
        samples_per_bit = int(self.sample_rate * self.bit_duration)
        demodded_signal = np.array([])
        # manual flag to switch between pulse position modulation and binary phase shift keying 
        ppm = False 
        if ppm:
            half_samples = int(samples_per_bit / 2)
            for sym in symbols:
                bit = []
                if sym == 1:
                    bit = np.ones(half_samples)
                    bit = np.append(bit, np.zeros(samples_per_bit - half_samples))
                else:
                    bit = np.zeros(half_samples)
                    bit = np.append(bit, np.ones(samples_per_bit - half_samples))
                demodded_signal = np.append(demodded_signal, bit)
        else:
            for sym in symbols:
                sym_samples = np.ones(samples_per_bit) * sym
                demodded_signal = np.append(demodded_signal, sym_samples)
        return demodded_signal
    
    def apply_doppler(self, 
                      signal: np.ndarray, 
                      emitter: Emitter):
        
        c = 299792458.0
        f0 = emitter.frequency
        distance = np.linalg.norm(emitter.position - self.position) # meters
        v = np.dot(emitter.velocity, self.position - emitter.position) / distance # velocity in direction of receiver m/s
        
        f1 = v/c * f0 # must be in Hz

        doppler_shifted_signal = signal * np.exp(2j*np.pi*f1*np.arange(0, len(signal)) / self.sample_rate)  
        return doppler_shifted_signal, f1
    
    def add_time_delay(self, 
                       signal: np.ndarray, 
                       emitter: Emitter):
        
        c = 299792458.0
        distance = np.linalg.norm(emitter.position - self.position)
        time_delay_seconds = distance / c

        time_delay_samples = time_delay_seconds * self.sample_rate
        integer_delay = int(time_delay_samples)
        fractional_delay = time_delay_samples - integer_delay

        N = 100
        n = np.arange(N)
        h = np.sinc(n - (N - 1) / 2 - fractional_delay)
        h *= np.blackman(N)
        h /= np.sum(h)

        time_delayed_signal = np.convolve(signal, h, mode='same')
        integer_delay_signal = np.zeros(integer_delay, dtype=complex)
        time_delayed_signal = np.append(integer_delay_signal, time_delayed_signal)
        time_delayed_signal = time_delayed_signal[:len(signal)]

        return time_delayed_signal, time_delay_seconds
    
    def signal_to_noise_ratio(self, 
                              signal: np.ndarray, 
                              distance: float):
        signal_power = np.sum(np.abs(signal)**2) / len(signal)
        snr_from_distance = lambda x : (1 - 4) / (400000) * x + 4
        snr = snr_from_distance(distance)
        noise_var = signal_power / snr
        return noise_var
    
    def add_noise(self, 
                  signal: np.ndarray, 
                  emitter: Emitter):
        distance = np.linalg.norm(emitter.position - self.position)
        noise_var = self.signal_to_noise_ratio(signal, distance)
        real_noise = np.random.normal(0, noise_var**2/2, len(signal))
        imag_noise = np.random.normal(0, noise_var**2/2, len(signal))
        noise = real_noise + 1j * imag_noise
        return signal + noise
    
    def receive(self, 
                symbols: List[int], 
                emitter: Emitter,
                return_true_values: bool = False):

        signal = self.sample_signal(symbols)
        time_delayed_signal, t = self.add_time_delay(signal, emitter)
        doppler_signal, f = self.apply_doppler(time_delayed_signal, emitter)
        noisy_signal = self.add_noise(doppler_signal, emitter)
        if return_true_values:
            return noisy_signal, t, f
        else:
            return noisy_signal