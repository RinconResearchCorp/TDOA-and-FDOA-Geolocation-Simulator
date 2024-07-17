import numpy as np
from geopy import distance
import string
import random

from signal_generator import ADSBEncoder

c = 299792458.0 # speed of light in m/s


def main():
    emitter = (1,1,10000)
    receivers = [(0,1,0), (1,0,0), (-1,0,0)]
    tdoa = generate_tdoa_data(emitter, receivers, random_emitter=True, mode='from_signals', coord_sys='cartesian')
    print(tdoa)

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

def generate_tdoa_data(emitter, receivers, random_emitter = False, mode='from_distance', coord_sys = 'cartesian'):
    
    if random_emitter:
        dims = len(receivers[0])
        
        max_idxs = []
        
        for i in range(dims):
            max_idxs.append(max(receivers, key=lambda x: np.abs(x[i]))[i])

        emitter =  np.random.random(dims) - 0.5 * 3 * np.array(max_idxs)

    if mode == 'from_signals':
        return generate_tdoa_from_signals(emitter, receivers, coord_sys=coord_sys)

    if mode == 'from_distance':
        return generate_true_tdoa_data(emitter, receivers, coord_sys=coord_sys)

def generate_tdoa_from_signals(emitter, receivers, coord_sys = 'cartesian'):

    distance_func = get_distance_func(len(emitter), coord_sys)
    distances = [distance_func(emitter, r) for r in receivers]
    
    times = np.array(distances)/c

    encoder = ADSBEncoder()

    message_length = random.randint(5, 25)
    message = ''.join(random.choice(string.ascii_letters) for _ in range(message_length))
    binary_message = ''.join(format(ord(i), '08b') for i in message)

    # "Transmit signal", takes times[i] to go distance[i]
    signals = [encoder.modulate(binary_message, noisy=True, time_delay = t) for t in times]

    # find (index of) start of signal via cross-correlation conver to seconds using sampling rate
    signal_start_times = []
    for signal in signals:
        start_time, _ = encoder.find_signal_start(signal)
        signal_start_times.append(start_time)
    
    signal_start_times = np.array(signal_start_times) / encoder.sample_rate

    n = len(signal_start_times)

    tdoa = np.zeros( (n, n))

    for i in range(n):
        for j in range(i + 1, n):
            if i == j:
                continue
            diff = signal_start_times[j] - signal_start_times[i]
            tdoa[i,j] = diff
            tdoa[j,i] = diff

    return tdoa


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


if __name__ == "__main__":
    main()