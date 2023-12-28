from glob import glob
import os


def get_image_list(file_list_txt):
    filelist = []
    with open(file_list_txt) as f:
        for line in f:
            line = line.strip()
            #if ' ' in line:
            #    line = line.split()[0]
            filelist.append(line)
    print(filelist)
    return filelist


class HParams:
        def __init__(self, **kwargs):
            self.data = {}

            for key, value in kwargs.items():
                self.data[key] = value

        def __getattr__(self, key):
            if key not in self.data:
                raise AttributeError(
                    "'HParams' object has no attribute %s" % key)
            return self.data[key]
        
        def set_hparam(self, key, value):
            self.data[key] = value


# Default hyperparameters
hparams = HParams(
    num_mels=80,  # Number of mel-spectrogram channels and local conditioning dimensionality
    #  network
    rescale=True,  # Whether to rescale audio prior to preprocessing
    rescaling_max=0.9,  # Rescaling value

    # Use LWS (https://github.com/Jonathan-LeRoux/lws) for STFT and phase reconstruction
    # It"s preferred to set True to use with https://github.com/r9y9/wavenet_vocoder
    # Does not work if n_ffit is not multiple of hop_size!!
    use_lws=False,

    n_fft=800,  # Extra window size is filled with 0 paddings to match this parameter
    hop_size=200,  # For 16000Hz, 200 = 12.5 ms (0.0125 * sample_rate)
    # For 16000Hz, 800 = 50 ms (If None, win_size = n_fft) (0.05 * sample_rate)
    win_size=800,
    # 16000Hz (corresponding to librispeech) (sox --i <filename>)
    sample_rate=16000,

    # Can replace hop_size parameter. (Recommended: 12.5)
    frame_shift_ms=None,

    # Mel and Linear spectrograms normalization/scaling and clipping
    signal_normalization=True,
    # Whether to normalize mel spectrograms to some predefined range (following below parameters)
    # Only relevant if mel_normalization = True
    allow_clipping_in_normalization=True,
    symmetric_mels=True,
    # Whether to scale the data to be symmetric around 0. (Also multiplies the output range by 2,
    # faster and cleaner convergence)
    max_abs_value=4.,
    # max absolute value of data. If symmetric, data will be [-max, max] else [0, max] (Must not
    # be too big to avoid gradient explosion,
    # not too small for fast convergence)
    # Contribution by @begeekmyfriend
    # Spectrogram Pre-Emphasis (Lfilter: Reduce spectrogram noise and helps model certitude
    # levels. Also allows for better G&L phase reconstruction)
    preemphasize=True,  # whether to apply filter
    preemphasis=0.97,  # filter coefficient.

    # Limits
    min_level_db=-100,
    ref_level_db=20,
    fmin=55,
    # Set this to 55 if your speaker is male! if female, 95 should help taking off noise. (To
    # test depending on dataset. Pitch info: male~[65, 260], female~[100, 525])
    fmax=7600,  # To be increased/reduced depending on data.

    ###################### Our training parameters #################################
    img_size=288,
    fps=25,

    batch_size=16,
    initial_learning_rate=1e-4,
    # ctrl + c, stop whenever eval loss is consistently greater than train loss for ~10 epochs
    nepochs=200000000000000000,
    num_workers=16,
    checkpoint_interval=3000,
    eval_interval=3000,
    save_optimizer_state=True,

    # is initially zero, will be set automatically to 0.03 later. Leads to faster convergence.
    syncnet_wt=0.0,
    syncnet_batch_size=64,
    syncnet_lr=1e-4,
    syncnet_eval_interval=10000,
    syncnet_checkpoint_interval=10000,

    disc_wt=0.07,
    disc_initial_learning_rate=1e-4,
    log_interval=1,
    num_checkpoints=10
)


def hparams_debug_string():
    values = hparams.values()
    hp = ["  %s: %s" % (name, values[name])
          for name in sorted(values) if name != "sentences"]
    return "Hyperparameters:\n" + "\n".join(hp)
