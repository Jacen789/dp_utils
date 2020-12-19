import os
import glob
import librosa
import pysptk
import pyworld
import numpy as np

from tqdm import tqdm
from nnmnkwii import preprocessing as P


order = 59
sampling_rate = 16000
frame_period = 5
hop_length = int(sampling_rate * (frame_period * 0.001))  # 80
n_fft = win_length = 1024
f0_floor = 71.0
f0_ceil = 700
use_harvest = True  # If False, use dio and stonemask
windows = [
    (0, 0, np.array([1.0])),
    (1, 1, np.array([-0.5, 0.0, 0.5])),
    (1, 1, np.array([1.0, -2.0, 1.0])),
]
f0_interpolation_kind = "quadratic"
mod_spec_smoothing = True
mod_spec_smoothing_cutoff = 50  # Hz


def collect_features(wav_path):
    x, fs = librosa.load(wav_path, sr=sampling_rate)
    x = x.astype(np.float64)
    if use_harvest:
        f0, timeaxis = pyworld.harvest(
            x, fs, frame_period=frame_period,
            f0_floor=f0_floor, f0_ceil=f0_ceil)
    else:
        f0, timeaxis = pyworld.dio(
            x, fs, frame_period=frame_period,
            f0_floor=f0_floor, f0_ceil=f0_ceil)
        f0 = pyworld.stonemask(x, f0, timeaxis, fs)

    spectrogram = pyworld.cheaptrick(x, f0, timeaxis, fs)
    aperiodicity = pyworld.d4c(x, f0, timeaxis, fs)
    # print("f0.shape: ", f0.shape)
    # print("spectrogram.shape: ", spectrogram.shape)
    # print("aperiodicity.shape: ", aperiodicity.shape)

    bap = pyworld.code_aperiodicity(aperiodicity, fs)
    alpha = pysptk.util.mcepalpha(fs)
    mgc = pysptk.sp2mc(spectrogram, order=order, alpha=alpha)
    f0 = f0[:, None]
    lf0 = f0.copy()
    nonzero_indices = np.nonzero(f0)
    lf0[nonzero_indices] = np.log(f0[nonzero_indices])
    if use_harvest:
        # https://github.com/mmorise/World/issues/35#issuecomment-306521887
        vuv = (aperiodicity[:, 0] < 0.5).astype(np.float32)[:, None]
    else:
        vuv = (lf0 != 0).astype(np.float32)
    lf0 = P.interp1d(lf0, kind=f0_interpolation_kind)
    # print("bap.shape: ", bap.shape)
    # print("mgc.shape: ", mgc.shape)
    # print("lf0.shape: ", lf0.shape)
    # print("vuv.shape: ", vuv.shape)

    # Parameter trajectory smoothing
    if mod_spec_smoothing:
        modfs = fs / hop_length
        mgc = P.modspec_smoothing(
            mgc, modfs, cutoff=mod_spec_smoothing_cutoff)

    # draw("img.jpg", x, lf0, vuv, mgc, bap)

    mgc = P.delta_features(mgc, windows)
    lf0 = P.delta_features(lf0, windows)
    bap = P.delta_features(bap, windows)

    # print("-1 mgc.shape: ", mgc.shape)
    # print("-1 lf0.shape: ", lf0.shape)
    # print("-1 vuv.shape: ", vuv.shape)
    # print("-1 bap.shape: ", bap.shape)

    features = np.hstack((mgc, lf0, vuv, bap))

    return features.astype(np.float32)


def draw(path, wav, lf0, vuv, mgc, bap):
    import matplotlib
    import matplotlib.pyplot as plt
    import librosa.display

    D = librosa.amplitude_to_db(np.abs(librosa.stft(
        wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length)), ref=np.max)
    # print("D.shape: ", D.shape)
    mgc = librosa.amplitude_to_db(mgc)
    fig, ax = plt.subplots()

    # img = librosa.display.specshow(D, x_axis='time', y_axis='log', sr=sampling_rate, hop_length=hop_length, ax=ax)
    # # img = librosa.display.specshow(D, x_axis='time', y_axis='hz', sr=sampling_rate, hop_length=hop_length, ax=ax)
    # fig.colorbar(img, ax=ax, format="%+2.f dB")
    # times = librosa.times_like(lf0.squeeze(), sr=sampling_rate, hop_length=hop_length)
    # ax.plot(times, vuv.squeeze() * f0_ceil, "g--", label='vuv', linewidth=1)
    # ax.plot(times, np.exp(lf0.squeeze()), "r--", label='f0', linewidth=1)
    # ax.legend(loc='upper right')

    hz_to_y_scale = (n_fft // 2 + 1) / (sampling_rate / 2)
    plt.imshow(np.vstack((D, mgc.transpose(1, 0))), origin="lower")
    ax.plot(vuv.squeeze() * f0_ceil * hz_to_y_scale,
            "g--", label='vuv', linewidth=1)
    ax.plot(np.exp(lf0.squeeze()) * hz_to_y_scale,
            "r--", label='f0', linewidth=1)
    ax.plot(bap.squeeze(), "y--", label='bap', linewidth=1)

    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def main():
    data_dir = r"D:\datasets\BZNSYP\Wave"
    file_paths = glob.glob(os.path.join(data_dir, "*.wav"))
    file_paths.sort()

    for i, file_path in enumerate(tqdm(file_paths)):
        if i >= 10:
            break
        features = collect_features(file_path)
        print("features.shape: ", features.shape)


if __name__ == "__main__":
    main()
