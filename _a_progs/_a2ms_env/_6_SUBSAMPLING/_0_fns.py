import os
from pathlib import Path

import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from tqdm import tqdm


# -----######-----######-----######-----
# MAIN FUNCTION: _drum_0911_breakdown_GET_df_hits
# -----######-----######-----######-----


def _drum_0911__classify_hit(y_slice, sr):
    """
    Very simple heuristic drum type guess:
    - kick: strong low band, low centroid
    - snare: stronger mid band
    - hat/shaker: stronger high band, higher centroid
    """
    if y_slice.size == 0:
        return "other"

    S = np.abs(np.fft.rfft(y_slice))
    freqs = np.fft.rfftfreq(len(y_slice), d=1.0 / sr)

    if S.sum() == 0:
        return "other"

    low_mask = (freqs >= 20) & (freqs < 150)
    mid_mask = (freqs >= 150) & (freqs < 2000)
    high_mask = (freqs >= 2000) & (freqs <= 20000)

    low_energy = S[low_mask].sum()
    mid_energy = S[mid_mask].sum()
    high_energy = S[high_mask].sum()

    centroid = (freqs * S).sum() / (S.sum() + 1e-9)

    energies = np.array([low_energy, mid_energy, high_energy])
    idx_max = int(np.argmax(energies))

    if idx_max == 0 and centroid < 180:
        return "kick"
    elif idx_max == 1:
        return "snare"
    elif idx_max == 2 and centroid > 3000:
        return "hat/shaker"
    else:
        return "other"


def _drum_0911__apply_fade(y_slice, sr, fade_in_ms, fade_out_ms):
    """
    Apply linear fade-in / fade-out to avoid clicks at the boundaries.
    """
    y = y_slice.copy()
    n = len(y)
    if n == 0:
        return y

    fade_in_samples = int(sr * fade_in_ms / 1000.0)
    fade_out_samples = int(sr * fade_out_ms / 1000.0)

    # Avoid fades longer than half the sample
    fade_in_samples = max(0, min(fade_in_samples, n // 2))
    fade_out_samples = max(0, min(fade_out_samples, n // 2))

    if fade_in_samples > 0:
        fade_in = np.linspace(0.0, 1.0, fade_in_samples, endpoint=True)
        y[:fade_in_samples] *= fade_in

    if fade_out_samples > 0:
        fade_out = np.linspace(1.0, 0.0, fade_out_samples, endpoint=True)
        y[-fade_out_samples:] *= fade_out

    return y


def _drum_0911__bitdepth_to_subtype(bit_depth):
    """
    Map bit-depth preference to a soundfile subtype.
    """
    if bit_depth == 16:
        return "PCM_16"
    if bit_depth == 24:
        return "PCM_24"
    if bit_depth == 32:
        return "PCM_32"
    if str(bit_depth).lower() in ["float", "float32", "32f", "f32"]:
        return "FLOAT"
    return "PCM_24"


def _drum_0911__process_one_file(
    path_audio,
    out_root,
    segment_start,
    segment_end,
    sr_target,
    pre_hit_ms,
    post_hit_max_ms,
    min_hit_ms,
    fade_in_ms,
    fade_out_ms,
    bit_depth,
):
    """
    Process a single loop:
    - load audio (mono)
    - optional segment crop (e.g. 32–60s for 16 bars)
    - detect onsets
    - slice hits
    - smooth front & tail (fades)
    - save as sample_1.wav, sample_2.wav, ...
    - return rows for df_hits
    """
    path_audio = Path(path_audio)
    if not path_audio.is_file():
        return []

    # Load mono audio
    # sr_target = None => keep original sample rate (max quality)
    if sr_target is None:
        y, sr = librosa.load(path_audio.as_posix(), sr=None, mono=True)
    else:
        y, sr = librosa.load(path_audio.as_posix(), sr=sr_target, mono=True)

    dur_total = len(y) / float(sr)

    # Segment selection (seconds) – for your 16-bar zone
    if segment_start is not None or segment_end is not None:
        start_sec = max(segment_start if segment_start is not None else 0.0, 0.0)
        end_sec = segment_end if segment_end is not None else dur_total
        end_sec = min(end_sec, dur_total)

        if end_sec <= start_sec:
            return []

        start_sample = int(start_sec * sr)
        end_sample = int(end_sec * sr)
        y = y[start_sample:end_sample]
        seg_offset_sec = start_sec
    else:
        seg_offset_sec = 0.0

    if y.size == 0:
        return []

    # Onset detection
    onset_frames = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        backtrack=True,
        units="frames",
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    if len(onset_times) == 0:
        return []

    # Output folder: <out_root>/<loop_name>
    loop_name = path_audio.stem
    loop_folder = Path(out_root) / loop_name
    loop_folder.mkdir(parents=True, exist_ok=True)

    # Hit slicing params
    pre_hit_sec = pre_hit_ms / 1000.0
    post_hit_max_sec = post_hit_max_ms / 1000.0
    min_hit_sec = min_hit_ms / 1000.0

    subtype = _drum_0911__bitdepth_to_subtype(bit_depth)

    rows = []
    sample_counter = 1  # sample_1, sample_2, ...

    for i, onset_t in enumerate(onset_times):
        # Start slightly before onset
        start_t = max(onset_t - pre_hit_sec, 0.0)

        if i < len(onset_times) - 1:
            next_onset = onset_times[i + 1]
            end_t = min(onset_t + post_hit_max_sec, next_onset)
        else:
            end_t = min(onset_t + post_hit_max_sec, len(y) / float(sr))

        if end_t <= start_t:
            continue

        # Enforce minimum duration
        if (end_t - start_t) < min_hit_sec:
            end_t = min(start_t + min_hit_sec, len(y) / float(sr))
            if end_t <= start_t:
                continue

        start_sample = int(start_t * sr)
        end_sample = int(end_t * sr)
        y_slice = y[start_sample:end_sample]

        if y_slice.size == 0:
            continue

        # Smooth edges
        y_slice = _drum_0911__apply_fade(
            y_slice,
            sr,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
        )

        # Anti-clipping normalization (keep a bit of headroom)
        max_abs = np.max(np.abs(y_slice))
        if max_abs > 0.99:
            y_slice = y_slice / max_abs * 0.99

        # Basic features
        peak = float(np.max(np.abs(y_slice)))
        rms = float(np.sqrt(np.mean(y_slice**2)))

        # Drum type guess – just for the table
        drum_type = _drum_0911__classify_hit(y_slice, sr)

        # Save slice as sample_#.wav
        slice_name = f"sample_{sample_counter}.wav"
        sample_counter += 1

        path_slice = loop_folder / slice_name
        sf.write(path_slice.as_posix(), y_slice, sr, subtype=subtype)

        onset_abs = float(onset_t + seg_offset_sec)
        offset_abs = float(end_t + seg_offset_sec)

        row = {
            "parent_path": path_audio.as_posix(),
            "loop_name": loop_name,
            "slice_index": i,
            "sample_name": slice_name,
            "drum_type_guess": drum_type,
            "slice_path": path_slice.as_posix(),
            "onset_sec_segment": float(onset_t),
            "offset_sec_segment": float(end_t),
            "onset_sec_abs": onset_abs,
            "offset_sec_abs": offset_abs,
            "duration_sec": float(end_t - onset_t),
            "peak_amp": peak,
            "rms": rms,
            "sr": sr,
            "bit_depth": bit_depth,
        }
        rows.append(row)

    return rows


def _drum_0911_breakdown_GET_df_hits(
    paths_or_folder,
    out_root="./_DRUM_HITS_OUT",
    segment_start=32.0,
    segment_end=60.0,
    sr_target=None,
    pre_hit_ms=10.0,
    post_hit_max_ms=300.0,
    min_hit_ms=40.0,
    fade_in_ms=3.0,
    fade_out_ms=8.0,
    bit_depth=24,
    exts=None,
):
    """
    DRUM LOOP BREAKDOWN – SMOOTHED 16-BAR HIT EXTRACTOR (NO PKL)

    INPUT:
        paths_or_folder:
            - list/iterable of audio file paths
            - OR a folder path (string/Path); all audio files in it will be processed
        out_root:
            - output folder you choose.
              Each loop -> <out_root>/<loop_name>/sample_1.wav, sample_2.wav, ...
        segment_start / segment_end:
            - time window in seconds to analyze (e.g. 32–60s for 16 bars)
            - use None / None to process full file
        sr_target:
            - None => keep original sample rate (best quality)
            - or e.g. 44100 to force a specific SR
        pre_hit_ms:
            - ms BEFORE onset to include in slice
        post_hit_max_ms:
            - max ms AFTER onset before cutting (or reaching next onset)
        min_hit_ms:
            - minimum hit duration
        fade_in_ms / fade_out_ms:
            - how much to smooth front and tail of each hit (ms)
        bit_depth:
            - 16, 24, 32, or "float" – WAV subtype
        exts:
            - list of audio extensions to include if paths_or_folder is a folder.
              default: [".wav", ".aiff", ".aif", ".flac", ".mp3"]

    OUTPUT:
        df_hits: one row per detected hit:
            - parent_path, loop_name, slice_index, sample_name, drum_type_guess
            - slice_path, onset_sec_segment, offset_sec_segment
            - onset_sec_abs, offset_sec_abs, duration_sec
            - peak_amp, rms, sr, bit_depth
    """
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    # Resolve file paths
    if isinstance(paths_or_folder, (str, Path)):
        folder = Path(paths_or_folder)
        if not folder.is_dir():
            raise ValueError("paths_or_folder is a string/Path but not a folder.")
        if exts is None:
            exts = [".wav", ".aiff", ".aif", ".flac", ".mp3"]
        exts_lower = {e.lower() for e in exts}
        paths = [
            p.as_posix()
            for p in sorted(folder.iterdir())
            if p.is_file() and p.suffix.lower() in exts_lower
        ]
    else:
        # Assume iterable/list of paths
        paths = [Path(p).as_posix() for p in paths_or_folder]

    all_rows = []

    # TQM progress bar
    for path_audio in tqdm(paths, desc="TQM – DRUM LOOP BREAKDOWN", ncols=80):
        rows = _drum_0911__process_one_file(
            path_audio=path_audio,
            out_root=out_root,
            segment_start=segment_start,
            segment_end=segment_end,
            sr_target=sr_target,
            pre_hit_ms=pre_hit_ms,
            post_hit_max_ms=post_hit_max_ms,
            min_hit_ms=min_hit_ms,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            bit_depth=bit_depth,
        )
        if rows:
            all_rows.extend(rows)

    if len(all_rows) == 0:
        return pd.DataFrame()

    df_hits = pd.DataFrame(all_rows)
    df_hits = df_hits.sort_values(
        by=["parent_path", "slice_index"], ascending=[True, True]
    ).reset_index(drop=True)

    return df_hits
