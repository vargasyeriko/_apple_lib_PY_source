# ===================== 0_FNS =====================
import os
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from datetime import datetime


# -----######-----###### CORE FUNCTION 1: KICK LOCATOR -----######-----######
def _kick_1011_where_GET_df_kicks(
    df,
    col_path='Path',
    max_kicks=5,
    low_max_hz=180,
    hop_length=512,
    win_length=2048,
    min_kick_distance_ms=40,
    tqm_bar=True
):
    """
    KICK LOCATOR:
    Find where the kick "lives" for each audio file in df[col_path].

    For each row:
      - Loads audio (mono, native sr).
      - Computes STFT.
      - Focuses on low-band (<= low_max_hz).
      - Uses spectral centroid to prefer low-heavy frames.
      - Builds a kick score and clusters nearby frames into single hits.
      - Selects up to `max_kicks` strongest kicks (<= 5) per file.

    New columns appended:
      - 'kick_detected'        : bool
      - 'kick_frames'          : list of frame indices
      - 'kick_times_sec'       : list of times (float seconds)
      - 'kick_strengths'       : list of normalized strengths (0–1)
      - 'kick_main_time_sec'   : float or NaN (strongest kick)
      - 'kick_main_strength'   : float or NaN
      - 'kick_error'           : error message or None
    """

    df = df.copy()
    n_rows = len(df)

    # Prepare output columns
    df['kick_detected'] = False
    df['kick_frames'] = [[] for _ in range(n_rows)]
    df['kick_times_sec'] = [[] for _ in range(n_rows)]
    df['kick_strengths'] = [[] for _ in range(n_rows)]
    df['kick_main_time_sec'] = np.nan
    df['kick_main_strength'] = np.nan
    df['kick_error'] = None

    # Small helper: text-based TQM bar
    def _tqm_update(idx, total):
        if not tqm_bar or total == 0:
            return
        pct = int((idx + 1) * 100 / total)
        bar_len = 30
        done = int(bar_len * pct / 100)
        bar = '█' * done + '-' * (bar_len - done)
        print(f"\r[KICK_TQM] |{bar}| {idx + 1}/{total} ({pct}%)", end='')

    for i, (idx, row) in enumerate(df.iterrows()):
        path = row.get(col_path, None)

        # TQM progress update
        _tqm_update(i, n_rows)

        if not isinstance(path, str) or not os.path.isfile(path):
            df.at[idx, 'kick_error'] = 'missing_or_invalid_path'
            continue

        try:
            # 1) LOAD AUDIO
            y, sr = librosa.load(path, sr=None, mono=True)
            if y is None or len(y) == 0:
                df.at[idx, 'kick_error'] = 'empty_audio'
                continue

            # 2) STFT
            S = np.abs(librosa.stft(
                y,
                n_fft=win_length,
                hop_length=hop_length,
                win_length=win_length
            ))
            freqs = librosa.fft_frequencies(sr=sr, n_fft=win_length)

            if S.shape[1] == 0:
                df.at[idx, 'kick_error'] = 'no_frames'
                continue

            # 3) LOW-BAND ENERGY (where kick usually lives)
            low_mask = freqs <= low_max_hz
            if not np.any(low_mask):
                low_mask = freqs <= (sr / 4.0)  # fallback

            low_band_energy = S[low_mask, :].sum(axis=0)  # shape: (frames,)
            if low_band_energy.max() > 0:
                low_band_norm = low_band_energy / low_band_energy.max()
            else:
                df.at[idx, 'kick_error'] = 'low_band_zero'
                continue

            # 4) SPECTRAL CENTROID (to push toward low-heavy frames)
            total_energy = S.sum(axis=0)
            centroid = (freqs[:, None] * S).sum(axis=0) / (total_energy + 1e-9)
            centroid_norm = np.clip(centroid / (sr / 2.0), 0.0, 1.0)
            lowness = 1.0 - centroid_norm  # 1 when centroid is low

            # 5) KICK SCORE = low-band energy * lowness
            kick_score_raw = low_band_norm * lowness

            # Light smoothing (3-frame moving average)
            if len(kick_score_raw) >= 3:
                kernel = np.array([0.25, 0.5, 0.25])
                kick_score = np.convolve(kick_score_raw, kernel, mode='same')
            else:
                kick_score = kick_score_raw

            # 6) THRESHOLDING (dynamic)
            max_score = kick_score.max()
            if max_score <= 0:
                df.at[idx, 'kick_error'] = 'zero_kick_score'
                continue

            threshold = 0.35 * max_score
            candidate_frames = np.where(kick_score >= threshold)[0]
            if len(candidate_frames) == 0:
                df.at[idx, 'kick_error'] = 'no_frames_above_threshold'
                continue

            # 7) CLUSTER NEARBY FRAMES INTO SINGLE HITS
            frame_duration = hop_length / float(sr)
            min_dist_frames = max(
                1,
                int((min_kick_distance_ms / 1000.0) / frame_duration)
            )

            candidate_frames = np.sort(candidate_frames)
            clusters = []
            current_cluster = [candidate_frames[0]]

            for f in candidate_frames[1:]:
                if f - current_cluster[-1] <= min_dist_frames:
                    current_cluster.append(f)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [f]
            clusters.append(current_cluster)

            # For each cluster, keep the frame with highest kick_score
            peak_frames = []
            peak_strengths = []
            for cluster in clusters:
                cluster = np.array(cluster, dtype=int)
                cluster_scores = kick_score[cluster]
                best_idx = cluster[np.argmax(cluster_scores)]
                peak_frames.append(int(best_idx))
                peak_strengths.append(float(kick_score[best_idx]))

            if len(peak_frames) == 0:
                df.at[idx, 'kick_error'] = 'no_cluster_peaks'
                continue

            # 8) SELECT TOP-N (max_kicks) BY STRENGTH, THEN SORT BY TIME
            peak_frames = np.array(peak_frames, dtype=int)
            peak_strengths = np.array(peak_strengths, dtype=float)

            if peak_strengths.max() > 0:
                peak_strengths_norm = peak_strengths / peak_strengths.max()
            else:
                peak_strengths_norm = peak_strengths

            order_by_strength = np.argsort(-peak_strengths_norm)
            top_n = min(max_kicks, len(order_by_strength))
            top_idx = order_by_strength[:top_n]

            top_frames = peak_frames[top_idx]
            top_strengths = peak_strengths_norm[top_idx]

            # Sort selected kicks by time
            order_by_time = np.argsort(top_frames)
            top_frames = top_frames[order_by_time]
            top_strengths = top_strengths[order_by_time]

            # 9) FRAMES -> TIMES
            kick_times = librosa.frames_to_time(
                top_frames,
                sr=sr,
                hop_length=hop_length
            )
            kick_times = kick_times.tolist()
            top_frames = top_frames.tolist()
            top_strengths = top_strengths.tolist()

            # 10) SAVE RESULTS INTO DF
            df.at[idx, 'kick_detected'] = True
            df.at[idx, 'kick_frames'] = top_frames
            df.at[idx, 'kick_times_sec'] = kick_times
            df.at[idx, 'kick_strengths'] = top_strengths

            if len(kick_times) > 0:
                strongest_idx = int(np.argmax(top_strengths))
                df.at[idx, 'kick_main_time_sec'] = float(kick_times[strongest_idx])
                df.at[idx, 'kick_main_strength'] = float(top_strengths[strongest_idx])

        except Exception as e:
            df.at[idx, 'kick_error'] = f'exception: {type(e).__name__}: {e}'

    if tqm_bar and n_rows > 0:
        print()  # newline after TQM bar

    return df


# -----######-----###### CORE FUNCTION 2: KICK PROCESSOR -----######-----######
def _kick_1011_proc_GET_kick_slices(
    df,
    col_path='Path',
    col_kick_times='kick_times_sec',
    sr_target=44100,
    pre_ms=10.0,
    post_ms=220.0,
    fade_ms=5.0,
    noise_floor_ratio=0.02,
    tail_extra_ms=10.0,
    norm_target_peak=0.99,
    tqm_bar=True
):
    """
    KICK PROCESSOR:
    Turn detected kick times into clean, normalized, de-noised slices in memory.

    For each row where `kick_detected` is True:
      - Loads audio at sr_target, mono.
      - For each kick time:
          * Takes a window [t - pre_ms, t + post_ms].
          * Applies small fade in/out (avoid clicks).
          * Trims extra noise by cutting leading/trailing
            samples below (noise_floor_ratio * peak).
          * Leaves a tiny tail (tail_extra_ms) after last strong sample.
          * Re-normalizes to `norm_target_peak`.

    Returns:
      kick_slices_dict : dict
          {df_index: [np.ndarray kick_1, np.ndarray kick_2, ...]}
    """

    kick_slices_dict = {}
    idx_list = list(df.index)
    n_rows = len(idx_list)

    def _tqm_update(i, total):
        if not tqm_bar or total == 0:
            return
        pct = int((i + 1) * 100 / total)
        bar_len = 30
        done = int(bar_len * pct / 100)
        bar = '█' * done + '-' * (bar_len - done)
        print(f"\r[KICK_PROC_TQM] |{bar}| {i + 1}/{total} ({pct}%)", end='')

    for i, idx in enumerate(idx_list):
        _tqm_update(i, n_rows)
        row = df.loc[idx]

        path = row.get(col_path, None)
        kicks = row.get(col_kick_times, [])

        if not isinstance(path, str) or not os.path.isfile(path):
            continue
        if not isinstance(kicks, (list, tuple)) or len(kicks) == 0:
            continue

        try:
            y, sr = librosa.load(path, sr=sr_target, mono=True)
            if y is None or len(y) == 0:
                continue

            pre_s = pre_ms / 1000.0
            post_s = post_ms / 1000.0
            tail_extra_s = tail_extra_ms / 1000.0

            slices = []

            for t in kicks:
                # 1) initial window
                start_t = max(0.0, float(t) - pre_s)
                end_t = min(len(y) / sr, float(t) + post_s)

                start_samp = int(start_t * sr)
                end_samp = int(end_t * sr)
                if end_samp <= start_samp:
                    continue

                y_slice = y[start_samp:end_samp]

                # 2) fade in/out
                y_slice = _kick_1011_apply_fades(y_slice, sr, fade_ms=fade_ms)

                # 3) trim extra noise based on peak
                peak = np.max(np.abs(y_slice))
                if peak <= 0:
                    continue

                thr = peak * noise_floor_ratio
                above = np.where(np.abs(y_slice) >= thr)[0]
                if above.size == 0:
                    continue

                first_idx = int(max(0, above[0]))
                last_idx = int(min(len(y_slice) - 1, above[-1] + int(tail_extra_s * sr)))

                if last_idx <= first_idx:
                    continue

                y_slice = y_slice[first_idx:last_idx]

                # 4) re-normalize
                peak2 = np.max(np.abs(y_slice))
                if peak2 > 0:
                    y_slice = (y_slice / peak2) * norm_target_peak

                slices.append(y_slice.astype(np.float32))

            if len(slices) > 0:
                kick_slices_dict[idx] = slices

        except Exception:
            # silent fail per row; locator already tracks errors
            continue

    if tqm_bar and n_rows > 0:
        print()  # newline

    return kick_slices_dict


# -----######-----###### CORE FUNCTION 3: KICK WRITER -----######-----######
def _kick_1011_write_GET_kicks(
    df,
    kick_slices_dict,
    out_root,
    col_path='Path',
    sr_write=44100,
    txt_suffix='_kick_paths.txt',
    tqm_bar=True
):
    """
    KICK WRITER:
    Write processed kick slices to disk with ID + timestamp naming.

    For each df index present in `kick_slices_dict`:
      - Extracts base name of source path.
      - Takes first 13 characters as ID (id13).
      - Creates subfolder inside out_root:
            _mm_dd_hh-ss__{id13}_KICKS
      - Writes kicks as:
            {id13}_kick_01.wav
            {id13}_kick_02.wav
            ...
      - Writes a text file in that folder:
            {id13}_kick_paths.txt (or with txt_suffix)
        listing all exported paths (one per line).

    Returns:
      exported_paths : list of all .wav paths written.
    """

    os.makedirs(out_root, exist_ok=True)

    idx_list = list(kick_slices_dict.keys())
    n_rows = len(idx_list)
    exported_paths = []

    # One timestamp code for the whole batch
    time_code = datetime.now().strftime("%m_%d_%H-%M")  # mm_dd_hh-ss

    def _tqm_update(i, total):
        if not tqm_bar or total == 0:
            return
        pct = int((i + 1) * 100 / total)
        bar_len = 30
        done = int(bar_len * pct / 100)
        bar = '█' * done + '-' * (bar_len - done)
        print(f"\r[KICK_WRITE_TQM] |{bar}| {i + 1}/{total} ({pct}%)", end='')

    for i, idx in enumerate(idx_list):
        _tqm_update(i, n_rows)

        row = df.loc[idx]
        path = row.get(col_path, None)
        if not isinstance(path, str) or not os.path.isfile(path):
            continue

        base_no_ext = os.path.splitext(os.path.basename(path))[0]
        id13 = base_no_ext[:13] if len(base_no_ext) >= 13 else base_no_ext

        # Folder: _mm_dd_hh-ss__id_KICKS
        subfolder_name = f"_{time_code}__{id13}_KICKS"
        out_folder = os.path.join(out_root, subfolder_name)
        os.makedirs(out_folder, exist_ok=True)

        slices = kick_slices_dict[idx]
        local_paths = []

        for k_idx, y_slice in enumerate(slices, start=1):
            out_name = f"{id13}_kick_{k_idx:02d}.wav"
            out_path = os.path.join(out_folder, out_name)

            sf.write(out_path, y_slice, sr_write, subtype="PCM_16")
            exported_paths.append(out_path)
            local_paths.append(out_path)

        # txt with paths
        if len(local_paths) > 0:
            txt_name = f"{id13}{txt_suffix}"
            txt_path = os.path.join(out_folder, txt_name)
            try:
                with open(txt_path, "w", encoding="utf-8") as f:
                    for p in local_paths:
                        f.write(p + "\n")
            except Exception:
                pass  # do not kill whole run if txt fails

    if tqm_bar and n_rows > 0:
        print()  # newline

    return exported_paths


# ----- sub-function: fades (shared) -----#
def _kick_1011_apply_fades(y_slice, sr, fade_ms=5.0):
    """
    Small linear fade in/out to avoid clicks on one-shots.
    """
    if y_slice.size == 0:
        return y_slice

    fade_samps = int(sr * fade_ms / 1000.0)
    fade_samps = max(1, min(fade_samps, len(y_slice) // 2))

    window = np.ones_like(y_slice, dtype=float)
    fade_in = np.linspace(0.0, 1.0, fade_samps)
    fade_out = np.linspace(1.0, 0.0, fade_samps)

    window[:fade_samps] *= fade_in
    window[-fade_samps:] *= fade_out

    return y_slice * window
