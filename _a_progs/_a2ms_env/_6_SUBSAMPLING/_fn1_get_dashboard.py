# ===================== 0_FNS (DASHBOARD PDF) =====================
import matplotlib.pyplot as plt
import librosa.display
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np

# -----######-----###### CORE FUNCTION 4: KICK PDF STORY -----######-----######
def _kick_1011_pdf_GET_story(
    df,
    main_text,
    col_path='Path',
    pdf_out_path=None,
    dpi=200,
    tqm_bar=True
):
    """
    Build a multi-page PDF with dashboards for each kick sample in df[col_path].

    - First page:
        * Title + main_text.
        * List of all kick filenames.
    - Then one page per kick:
        * Waveform + envelope.
        * Magnitude spectrum.
        * Spectrogram.
        * Core stats: duration, peak, RMS, crest factor, rough f0.

    Inputs:
        df           : DataFrame with at least column col_path (kick .wav paths)
        main_text    : str, free text description for the first page
        col_path     : name of column with file paths (default 'Path')
        pdf_out_path : optional, explicit PDF path. If None, uses folder of first path.
        dpi          : DPI for pages
        tqm_bar      : bool, print TQM progress bar

    Output:
        pdf_out_path : str or None
    """

    # ---------------- SMALL HELPERS ----------------
    def _safe_db(x, floor=-120.0):
        x = float(x)
        if x <= 0.0:
            return floor
        return 20.0 * np.log10(x)

    def _tqm_update(i, total, msg=""):
        if not tqm_bar or total == 0:
            return
        pct = int((i + 1) * 100 / total)
        bar_len = 30
        done = int(bar_len * pct / 100)
        bar = "█" * done + "-" * (bar_len - done)
        print(f"\r[KICK_PDF_TQM] |{bar}| {i + 1}/{total} ({pct}%) {msg}", end="")

    # ---------------- VALIDATE INPUT ----------------
    if col_path not in df.columns:
        print(f"[ERROR] column '{col_path}' not in df")
        return None

    # filter only existing files
    paths = []
    for p in df[col_path].tolist():
        if isinstance(p, str) and os.path.isfile(p):
            paths.append(p)

    if len(paths) == 0:
        print("[ERROR] No valid paths found in df.")
        return None

    # Decide PDF output path
    if pdf_out_path is None:
        # pdf in the same folder as the first kick (same place as txt & wavs)
        first_folder = os.path.dirname(paths[0])
        pdf_out_path = os.path.join(first_folder, "kicks_story.pdf")

    os.makedirs(os.path.dirname(pdf_out_path), exist_ok=True)

    # ---------------- CREATE PDF ----------------
    with PdfPages(pdf_out_path) as pdf:

        # ===== COVER PAGE =====
        fig = plt.figure(figsize=(8.5, 11), dpi=dpi)
        ax = fig.add_subplot(111)
        ax.axis("off")

        title = "KICK SAMPLE STORY"
        ax.text(
            0.5, 0.9, title,
            ha="center", va="center",
            fontsize=20, fontweight="bold"
        )

        # main_text block
        if main_text:
            ax.text(
                0.5, 0.72,
                main_text,
                ha="center", va="top",
                fontsize=11,
                wrap=True,
                bbox=dict(boxstyle="round,pad=0.5",
                          facecolor="#f5f5f5",
                          edgecolor="#999999")
            )

        # list of files
        ax.text(
            0.05, 0.55,
            "Kick files:",
            ha="left", va="top",
            fontsize=12, fontweight="bold"
        )

        y_line = 0.53
        dy = 0.022
        for i, p in enumerate(paths):
            base = os.path.basename(p)
            ax.text(
                0.06, y_line,
                f"{i+1:02d}. {base}",
                ha="left", va="top",
                fontsize=9
            )
            y_line -= dy
            if y_line < 0.08:
                break  # don't overflow the cover page

        pdf.savefig(fig)
        plt.close(fig)

        # ===== PAGES PER KICK =====
        total_kicks = len(paths)
        for i, path_in in enumerate(paths):
            _tqm_update(i, total_kicks, msg="rendering pages...")

            try:
                y, sr = librosa.load(path_in, sr=None, mono=True)
            except Exception as e:
                print(f"\n[WARN] Could not load {path_in}: {e}")
                continue

            if y.size == 0:
                print(f"\n[WARN] Empty audio: {path_in}")
                continue

            # ---- core stats ----
            dur_sec = len(y) / float(sr)
            eps = 1e-12
            peak = float(np.max(np.abs(y)))
            rms = float(np.sqrt(np.mean(y ** 2)) + eps)
            peak_db = _safe_db(peak)
            rms_db = _safe_db(rms)
            crest = peak / (rms + eps)

            # rough f0
            f0_hz = None
            try:
                f0_series = librosa.yin(y, fmin=20, fmax=200, sr=sr)
                f0_valid = f0_series[np.isfinite(f0_series)]
                if f0_valid.size > 0:
                    f0_hz = float(np.median(f0_valid))
            except Exception:
                f0_hz = None

            # envelope
            win_env = max(1, int(0.001 * sr))
            kernel = np.ones(win_env) / win_env
            env = np.convolve(np.abs(y), kernel, mode="same")

            # spectrum
            fft = np.fft.rfft(y * np.hanning(len(y)))
            freqs = np.fft.rfftfreq(len(y), 1.0 / sr)
            mag_db = 20 * np.log10(np.abs(fft) + eps)

            # spectrogram
            n_fft = 1024
            hop_length = max(1, int(0.0015 * sr))
            D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, window="hann")
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            t = np.arange(len(y)) / float(sr)

            # ---- FIGURE FOR THIS KICK ----
            fig, axes = plt.subplots(2, 2, figsize=(11, 8.5), dpi=dpi)
            fig.suptitle(os.path.basename(path_in), fontsize=14, fontweight="bold")

            # Waveform + env
            ax_wave = axes[0, 0]
            ax_wave.plot(t, y, linewidth=1.0, label="Waveform")
            env_norm = env / (np.max(env) + eps)
            ax_wave.plot(
                t,
                env_norm * np.max(np.abs(y)),
                linewidth=0.9,
                alpha=0.8,
                label="Envelope",
            )
            ax_wave.axhline(0.0, color="gray", linewidth=0.5)
            ax_wave.set_title("Waveform & Envelope")
            ax_wave.set_xlabel("Time (s)")
            ax_wave.set_ylabel("Amplitude")
            ax_wave.grid(alpha=0.2)
            ax_wave.legend(loc="upper right", fontsize=8, frameon=False)

            # Spectrum
            ax_spec = axes[0, 1]
            valid = (freqs >= 20) & (freqs <= 5000)
            ax_spec.plot(freqs[valid], mag_db[valid], linewidth=1.0)
            ax_spec.set_title("Magnitude Spectrum")
            ax_spec.set_xlabel("Frequency (Hz)")
            ax_spec.set_ylabel("Level (dB)")
            ax_spec.grid(alpha=0.2)
            if f0_hz is not None and 20 <= f0_hz <= 5000:
                ax_spec.axvline(f0_hz, color="red", linestyle="--", linewidth=0.8)
                ax_spec.text(
                    f0_hz,
                    np.max(mag_db[valid]),
                    f"f0 ≈ {f0_hz:.1f} Hz",
                    color="red",
                    fontsize=8,
                    va="bottom",
                )

            # Spectrogram
            ax_sgram = axes[1, 0]
            img = librosa.display.specshow(
                S_db,
                sr=sr,
                hop_length=hop_length,
                x_axis="time",
                y_axis="hz",
                ax=ax_sgram,
                cmap="magma",
            )
            ax_sgram.set_title("Spectrogram (dB)")
            fig.colorbar(img, ax=ax_sgram, format="%+2.0f dB")

            # Stats box
            ax_stats = axes[1, 1]
            ax_stats.axis("off")

            stats_lines = [
                f"Duration: {dur_sec*1000:.1f} ms",
                f"Sample rate: {sr} Hz",
                f"Peak: {peak:.4f} ({peak_db:.1f} dBFS)",
                f"RMS:  {rms:.4f} ({rms_db:.1f} dBFS)",
                f"Crest factor: {crest:.2f}",
            ]
            if f0_hz is not None:
                stats_lines.append(f"Fundamental (approx): {f0_hz:.1f} Hz")

            text_y = 0.9
            ax_stats.text(
                0.05,
                text_y,
                "Kick Stats",
                fontsize=12,
                fontweight="bold",
                ha="left",
                va="top",
            )
            text_y -= 0.1

            for line in stats_lines:
                ax_stats.text(
                    0.05,
                    text_y,
                    line,
                    fontsize=10,
                    ha="left",
                    va="top",
                )
                text_y -= 0.08

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            pdf.savefig(fig)
            plt.close(fig)

        if tqm_bar:
            print()  # newline

    print(f"[SUCCESS] Kick PDF story saved -> {pdf_out_path}")
    return pdf_out_path



####### get txt 





# # ===================== 0_FNS (PROMPT EXPORTER) =====================
# import os
# import textwrap

# import os,pyperclip;


# ===================== 0_FNS (PROMPT EXPORTER) =====================
import os
import textwrap
import pyperclip


# -----######-----###### CORE FUNCTION: PROMPT TXT FOR _generate_kick -----######-----######
def _kick_1011_prompt_GET_generate_kick_txt(
    pdf_path,
    prompt_txt_path=None,
    tqm_bar=True
):
    """
    Build a ChatGPT-ready prompt text file for designing the _generate_kick function.

    Steps:
      1) Validates pdf_path.
      2) Creates (or overwrites) a .txt file with a detailed prompt that:
           - Tells ChatGPT what the PDF is.
           - Specifies the exact function name: _generate_kick
           - Specifies the exact signature: _generate_kick(path="")
           - Specifies that I must NOT need to modify anything.
           - Defines code structure (0_FNS + RUNNING STATEMENTS).
      3) Opens the folder where the PDF & TXT live.
      4) Copies the prompt text to clipboard and prints it.

    Inputs:
        pdf_path       : str, full path to the PDF file with kick dashboards.
        prompt_txt_path: optional explicit path for the .txt template.
                         If None, will create "<pdf_stem)_generate_kick_prompt.txt"
                         in the same folder as the PDF.
        tqm_bar        : bool, print a small TQM-style progress output.

    Output:
        prompt_txt_path: str, path to the created .txt file, or None on error.
    """

    def _tqm(step, total, msg=""):
        if not tqm_bar:
            return
        bar_len = 30
        frac = step / float(total)
        done = int(bar_len * frac)
        bar = "█" * done + "-" * (bar_len - done)
        print(f"\r[PROMPT_TQM] |{bar}| {step}/{total} {msg}", end="")

    total_steps = 3
    step = 0

    # 1) Validate PDF path
    step += 1
    _tqm(step, total_steps, "Checking PDF path...")
    if not isinstance(pdf_path, str) or not os.path.isfile(pdf_path):
        print(f"\n[ERROR] PDF not found: {pdf_path}")
        return None

    pdf_path_abs = os.path.abspath(pdf_path)
    pdf_folder = os.path.dirname(pdf_path_abs)
    pdf_stem = os.path.splitext(os.path.basename(pdf_path_abs))[0]

    # 2) Decide prompt txt path
    step += 1
    _tqm(step, total_steps, "Preparing prompt .txt path...")
    if prompt_txt_path is None:
        prompt_txt_path = os.path.join(
            pdf_folder,
            f"{pdf_stem}_generate_kick_prompt.txt"
        )
    else:
        prompt_txt_path = os.path.abspath(prompt_txt_path)

    # 3) Build and write prompt text
    step += 1
    _tqm(step, total_steps, "Writing prompt text...")
    prompt_text = textwrap.dedent(f"""
    PROMPT TO CHATGPT (WHEN PDF IS ATTACHED):

    I’ve attached a PDF that shows detailed analysis dashboards of several kick drum one-shots.
    Each page corresponds to a single kick sample — showing its waveform, spectrum, spectrogram,
    and stats.

    PDF file path (for your reference):
    {pdf_path_abs}

    I want you to generate a single Python function that creates 5 new kick drum samples that
    sound as close as possible to these examples, with maximum possible sound quality.

    Please read and follow these points exactly:

    ------------------------------------------------
    FUNCTION REQUIREMENTS

    - The function name must be exactly:
        _generate_kick

    - It must take one argument only:
        path = ""
      This is a string indicating the output folder where the 5 generated .wav files will be saved.

    - I must be able to run it as-is:
        - I should NOT need to modify anything inside the function definition.
        - I should NOT need to change the function signature.
        - I should only need to set the output path in the running code and call _generate_kick(path).

    - The function should:
        - Generate exactly 5 kick drum samples.
        - Save them as .wav files in the specified folder.
        - Return a Python list of the 5 exported .wav file paths.

    ------------------------------------------------
    SOUND & QUALITY RULES

    - Each generated kick should match the examples in the PDF as closely as possible in:
        - Duration and decay shape.
        - Low-end weight and fundamental pitch.
        - Balance between sub, punch, and click.
        - Overall transient shape and envelope.

    - Use high-quality synthesis only:
        - Use a smooth pitch envelope (downward bend) on the low-frequency body.
        - Use a separate click / transient layer (e.g., noise or filtered noise).
        - Use a well-shaped amplitude envelope (fast attack, exponential-style decay).
        - Avoid aliasing or harsh digital artefacts as much as possible.
        - Normalize each kick to just below 0 dBFS (around -0.3 to -0.5 dBFS) with no clipping.
        - Avoid clicks at the start/end (e.g., through proper fade-in/fade-out or envelope shape).

    ------------------------------------------------
    ALLOWED LIBRARIES

    - Only use these imports:

        import os
        import numpy as np
        import soundfile as sf

      Do NOT rely on any other audio/DSP libraries.

    ------------------------------------------------
    CODE STRUCTURE

    - Use this exact layout:

        # ===================== 0_FNS =====================
        # define the _generate_kick(path="") function here
        # plus any small helper functions it needs

        #!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
        # path = "/ABSOLUTE/OUTPUT/FOLDER"
        # generated_paths = _generate_kick(path)
        # print(generated_paths)

    - Inside _generate_kick(path=""):
        - Use the 'path' argument as the output folder.
        - Make sure the folder is created if it does not exist.
        - Write the 5 files as:
            kick_01.wav
            kick_02.wav
            kick_03.wav
            kick_04.wav
            kick_05.wav

    - USE OCR TO CHECK THE IMAGES IN THE PDF, THEY ARE SPECTROGRAMS FROM EACH SAMPLE:
        - CHECK IMAGES.
        - OPTICAL VIEW.
        - EXTRACT ALL FEATURES TO GIVE ME A CONDENSED FUNCTION TO GENERATE ACCORDINGLY.

    - The code you give me must be:
        - One single Python code block.
        - Ready to paste and run directly (no extra modifications).
        - With any extra explanation as comments inside the code, not outside.

    ------------------------------------------------
    FINAL TASK SUMMARY

    Read the attached PDF, infer the sonic character of those kicks, and then:

    - Write one complete Python code block that:
        1) Defines the _generate_kick(path="") function in the 0_FNS section.
        2) Includes a #!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#! section that:
            - Sets an example output path.
            - Calls _generate_kick(path).
            - Prints the returned list of generated file paths.

    - The user should not need to modify anything inside the function itself.
    - Focus on producing professional, production-ready kick samples with maximum quality.
    """).strip() + "\n"

    try:
        with open(prompt_txt_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
    except Exception as e:
        print(f"\n[ERROR] Could not write prompt txt: {e}")
        return None

    if tqm_bar:
        print()  # newline after TQM bar

    # --- open the folder where PDF/TXT live ---
    try:
        os.system(f"open '{pdf_folder}'")
    except Exception as e:
        print(f"[WARN] Could not open folder: {e}")

    # --- copy to clipboard & print in Jupyter ---
    try:
        pyperclip.copy(prompt_text)
        print("\n[PROMPT COPIED TO CLIPBOARD]\n")
    except Exception as e:
        print(f"[WARN] Could not copy to clipboard: {e}")

    print(prompt_text)
    print(f"\n[SUCCESS] _generate_kick prompt saved -> {prompt_txt_path}")
    return prompt_txt_path


# # -----######-----###### CORE FUNCTION: PROMPT TXT FOR _generate_kick -----######-----######
# def _kick_1011_prompt_GET_generate_kick_txt(
#     pdf_path,
#     prompt_txt_path=None,
#     tqm_bar=True
# ):
#     """
#     Build a ChatGPT-ready prompt text file for designing the _generate_kick function.

#     Steps:
#       1) Validates pdf_path.
#       2) Creates (or overwrites) a .txt file with a detailed prompt that:
#            - Tells ChatGPT what the PDF is.
#            - Specifies the exact function name: _generate_kick
#            - Specifies the exact signature: _generate_kick(path="")
#            - Specifies that I must NOT need to modify anything.
#            - Defines code structure (0_FNS + RUNNING STATEMENTS).
#       3) Returns the path to the .txt file.

#     Inputs:
#         pdf_path       : str, full path to the PDF file with kick dashboards.
#         prompt_txt_path: optional explicit path for the .txt template.
#                          If None, will create "<pdf_stem>_generate_kick_prompt.txt"
#                          in the same folder as the PDF.
#         tqm_bar        : bool, print a small TQM-style progress output.

#     Output:
#         prompt_txt_path: str, path to the created .txt file, or None on error.
#     """

#     def _tqm(step, total, msg=""):
#         if not tqm_bar:
#             return
#         bar_len = 30
#         frac = step / float(total)
#         done = int(bar_len * frac)
#         bar = "█" * done + "-" * (bar_len - done)
#         print(f"\r[PROMPT_TQM] |{bar}| {step}/{total} {msg}", end="")

#     total_steps = 3
#     step = 0

#     # 1) Validate PDF path
#     step += 1
#     _tqm(step, total_steps, "Checking PDF path...")
#     if not isinstance(pdf_path, str) or not os.path.isfile(pdf_path):
#         print(f"\n[ERROR] PDF not found: {pdf_path}")
#         return None

#     pdf_path_abs = os.path.abspath(pdf_path)
#     pdf_folder = os.path.dirname(pdf_path_abs)
#     pdf_stem = os.path.splitext(os.path.basename(pdf_path_abs))[0]

#     # 2) Decide prompt txt path
#     step += 1
#     _tqm(step, total_steps, "Preparing prompt .txt path...")
#     if prompt_txt_path is None:
#         prompt_txt_path = os.path.join(
#             pdf_folder,
#             f"{pdf_stem}_generate_kick_prompt.txt"
#         )
#     else:
#         prompt_txt_path = os.path.abspath(prompt_txt_path)

#     # 3) Build and write prompt text
#     step += 1
#     _tqm(step, total_steps, "Writing prompt text...")
#     prompt_text = textwrap.dedent(f"""
#     PROMPT TO CHATGPT (WHEN PDF IS ATTACHED):

#     I’ve attached a PDF that shows detailed analysis dashboards of several kick drum one-shots.
#     Each page corresponds to a single kick sample — showing its waveform, spectrum, spectrogram,
#     and stats.

#     PDF file path (for your reference):
#     {pdf_path_abs}

#     I want you to generate a single Python function that creates 5 new kick drum samples that
#     sound as close as possible to these examples, with maximum possible sound quality.

#     Please read and follow these points exactly:

#     ------------------------------------------------
#     FUNCTION REQUIREMENTS

#     - The function name must be exactly:
#         _generate_kick

#     - It must take one argument only:
#         path = ""
#       This is a string indicating the output folder where the 5 generated .wav files will be saved.

#     - I must be able to run it as-is:
#         - I should NOT need to modify anything inside the function definition.
#         - I should NOT need to change the function signature.
#         - I should only need to set the output path in the running code and call _generate_kick(path).

#     - The function should:
#         - Generate exactly 5 kick drum samples.
#         - Save them as .wav files in the specified folder.
#         - Return a Python list of the 5 exported .wav file paths.

#     ------------------------------------------------
#     SOUND & QUALITY RULES

#     - Each generated kick should match the examples in the PDF as closely as possible in:
#         - Duration and decay shape.
#         - Low-end weight and fundamental pitch.
#         - Balance between sub, punch, and click.
#         - Overall transient shape and envelope.

#     - Use high-quality synthesis only:
#         - Use a smooth pitch envelope (downward bend) on the low-frequency body.
#         - Use a separate click / transient layer (e.g., noise or filtered noise).
#         - Use a well-shaped amplitude envelope (fast attack, exponential-style decay).
#         - Avoid aliasing or harsh digital artefacts as much as possible.
#         - Normalize each kick to just below 0 dBFS (around -0.3 to -0.5 dBFS) with no clipping.
#         - Avoid clicks at the start/end (e.g., through proper fade-in/fade-out or envelope shape).

#     ------------------------------------------------
#     ALLOWED LIBRARIES

#     - Only use these imports:

#         import os
#         import numpy as np
#         import soundfile as sf

#       Do NOT rely on any other audio/DSP libraries.

#     ------------------------------------------------
#     CODE STRUCTURE

#     - Use this exact layout:

#         # ===================== 0_FNS =====================
#         # define the _generate_kick(path="") function here
#         # plus any small helper functions it needs

#         #!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
#         # path = "/ABSOLUTE/OUTPUT/FOLDER"
#         # generated_paths = _generate_kick(path)
#         # print(generated_paths)

#     - Inside _generate_kick(path=""):
#         - Use the 'path' argument as the output folder.
#         - Make sure the folder is created if it does not exist.
#         - Write the 5 files as:
#             kick_01.wav
#             kick_02.wav
#             kick_03.wav
#             kick_04.wav
#             kick_05.wav

#     - USE OCR TO CHECKK THE IMAGES IN THE PDF, THEY ARE SPECTROGRAMS FROM EACH SAMPLE :
#         - CHECK IMAGES .
#         - OPTICAL VIEW .
#         - EXTRACTO ALL FEAUTURES TO GIVE ME A CONDENCED FUNCTION TO GENERATE ACCORDINGLY 
        
#     - The code you give me must be:
#         - One single Python code block.
#         - Ready to paste and run directly (no extra modifications).
#         - With any extra explanation as comments inside the code, not outside.

#     ------------------------------------------------
#     FINAL TASK SUMMARY

#     Read the attached PDF, infer the sonic character of those kicks, and then:

#     - Write one complete Python code block that:
#         1) Defines the _generate_kick(path="") function in the 0_FNS section.
#         2) Includes a #!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#! section that:
#             - Sets an example output path.
#             - Calls _generate_kick(path).
#             - Prints the returned list of generated file paths.

#     - The user should not need to modify anything inside the function itself.
#     - Focus on producing professional, production-ready kick samples with maximum quality.
#     """).strip() + "\n"

#     try:
#         with open(prompt_txt_path, "w", encoding="utf-8") as f:
#             f.write(prompt_text)
#     except Exception as e:
#         print(f"\n[ERROR] Could not write prompt txt: {e}")
#         return None

#     if tqm_bar:
#         print()  # newline
#     txt=open(txt_path).read(); pyperclip.copy(txt); print(txt)
#     os.system(f"open '{os.path.dirname(txt_path)}'");t=open(txt_path).read();pyperclip.copy(t);print(t)

#     print(f"[SUCCESS] _generate_kick prompt saved -> {prompt_txt_path}")
#     return prompt_txt_path
