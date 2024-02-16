from scipy import signal
from scipy.io import wavfile
import numpy as np
import sys

def filter_bitstream(data, center_freq, width):
    filter = signal.butter(
        4,
        [center_freq - width, center_freq + width],
        'bandpass', 
        fs=44100, 
        output='sos' # second order sections for more stability
    )
    filtered = signal.sosfilt(filter, data)

    # abs and lowpass via moving average (https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-moving-average-using-python-numpy-scipy)
    return np.convolve(abs(filtered), np.ones(10))

def amplitude_to_bit(amplitude):
    return int(amplitude > 0)

def parse_byte(data, current_sample, bit_length_samples):

    # parse byte
    byte = 0
    for bit_num in range(7, -1, -1):
        amplitude = data[round(current_sample)]
        byte |= amplitude_to_bit(amplitude) << bit_num
        current_sample += bit_length_samples

    # check sync bits
    sync_bits_ok = True
    for sync_bit in [0, 1, 0]:
        sync_bits_ok &= amplitude_to_bit(data[round(current_sample)]) == sync_bit
        current_sample += bit_length_samples  
    
    # use sync bits to synchronize
    next_bit_center = current_sample
    if sync_bits_ok:
        sync_bits_center = round(current_sample - (bit_length_samples*2))

        right, left = sync_bits_center, sync_bits_center    
        while data[right] > 0:
            right += 1
        while data[left] > 0:
            left -= 1

        bit_duration = right - left
        sync_bits_center = left + (bit_duration / 2)
        next_bit_center = sync_bits_center + (bit_length_samples * 2)

    return (byte, next_bit_center, sync_bits_ok)

if __name__ == "__main__":
    zero_center_freq = 5041
    one_center_freq = 7281
    filter_width = 1500
    bit_length_seconds = 1/(4194304 / 4096)
    bit_length_samples = bit_length_seconds/(1/44100)

    sample_rate, data = wavfile.read(sys.argv[1])

    # convert to mono
    if len(data.shape) != 1:
        data = data[:,0]

    bits = filter_bitstream(data, one_center_freq, filter_width) - filter_bitstream(data, zero_center_freq, filter_width)

    # find preamble
    current_sample = 0
    while True:
        byte, next_byte_start, sync_bits_ok = parse_byte(bits, current_sample, bit_length_samples)
        if sync_bits_ok and (byte == 0b10101010):
            byte, data_start, sync_bits_ok = parse_byte(bits, next_byte_start, bit_length_samples)
            if sync_bits_ok and (byte == 0b10101010):
                print(f"preamble found at: {current_sample}")
                current_sample = data_start
                print(f"data begins at: {current_sample}")
                break
        current_sample += 3

    # decode data
    all_bytes = []
    while len(all_bytes) < (0x2000*4):
        byte, current_sample, sync_bits_ok = parse_byte(bits, current_sample, bit_length_samples)

        if not sync_bits_ok:
            print("SYNC BIT ERROR")
            print(f"{current_sample=}")
            exit()

        all_bytes.append(byte)

    with open('recovered_save.sav', 'wb') as f:
        f.write(bytes(all_bytes))

    print("done")
