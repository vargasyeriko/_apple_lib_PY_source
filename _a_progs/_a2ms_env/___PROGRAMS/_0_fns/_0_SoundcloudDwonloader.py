import re, json, time
import requests
import pandas as pd
from datetime import datetime
from tqdm import tqdm

def _soundcloud_1808_pl2name_GET_df(playlist_links, genre="", purchase_date=""):
    """
    Input:
      - playlist_links: str | list/Series[Index] of SoundCloud playlist URLs
      - genre: optional string; if empty, prompts once for the batch
      - purchase_date: optional 'YYYY-MM-DD' (blank = keep empty purchase fields)
    Output:
      - pandas.DataFrame with columns:
        ['src_playlist','track_title','track_artist','track_url','track_id','error',
         'genre','mix_name','remixers','label','key','bpm',
         'release_year','release_month','release_day',
         'purchase_year','purchase_month','purchase_day','new_name']
    """
    def _as_list(x):
        if isinstance(x, (list, tuple, pd.Series, pd.Index)): return list(x)
        return [x]

    def _request(url):
        return requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }, timeout=25)

    def _scrape_tracks(pl_url):
        html = _request(pl_url).text
        m = re.search(r"window\.__sc_hydration\s*=\s*(\[[\s\S]*?\])\s*;", html)
        if not m: 
            return []
        try:
            hydration = json.loads(m.group(1))
        except Exception:
            return []
        pl_objs = [o for o in hydration if isinstance(o, dict) and str(o.get("hydratable","")).startswith("playlist")]
        tracks = []
        for obj in pl_objs:
            data = obj.get("data") or {}
            tlist = data.get("tracks") or (data.get("playlist") or {}).get("tracks") or []
            for t in tlist:
                u = t.get("user") or {}
                tracks.append({
                    "src_playlist": pl_url,
                    "track_title": t.get("title",""),
                    "track_artist": u.get("username","") or u.get("permalink",""),
                    "track_url": t.get("permalink_url","") or "",
                    "track_id": t.get("id"),
                    "error": ""
                })
        return tracks

    links = _as_list(playlist_links)
    rows = []
    for pl in tqdm(links, desc="TQM • Scraping playlists", unit="playlist"):
        try:
            got = _scrape_tracks(str(pl).strip())
            if not got:
                rows.append({"src_playlist": pl, "track_title":"","track_artist":"","track_url":"","track_id":None,"error":"no_tracks"})
            else:
                rows.extend(got)
        except Exception as e:
            rows.append({"src_playlist": pl, "track_title":"","track_artist":"","track_url":"","track_id":None,"error":str(e)})
        time.sleep(0.8)

    df = pd.DataFrame(rows, columns=["src_playlist","track_title","track_artist","track_url","track_id","error"])
    if df.empty:
        return df

    # --- Batch genre & purchase split ---
    if not genre:
        try:
            genre = input("Enter GENRE for this batch: ").strip()
        except Exception:
            genre = ""
    df["genre"] = genre

    py = pm = pdm = ""
    if purchase_date:
        try:
            pdt = datetime.strptime(purchase_date, "%Y-%m-%d")
            py, pm, pdm = str(pdt.year), f"{pdt.month:02d}", f"{pdt.day:02d}"
        except Exception:
            py = pm = pdm = ""
    df["purchase_year"] = py
    df["purchase_month"] = pm
    df["purchase_day"] = pdm

    # --- Parsing heuristics ---
    for c in ["mix_name","remixers","label","key","bpm","release_year","release_month","release_day"]:
        if c not in df.columns: df[c] = ""

    rx_mix = re.compile(r"\(([^)]*?(?:mix|edit|version|dub|instrumental)[^)]*)\)", re.IGNORECASE)
    rx_remix = re.compile(r"\(([^)]*?remix[^)]*)\)", re.IGNORECASE)
    rx_key_music = re.compile(r"\b([A-G](?:#|b)?\s?(?:maj(?:or)?|min(?:or)?|m|M))\b")
    rx_key_camelot = re.compile(r"\b(1[0-2]|[1-9])[AB]\b", re.IGNORECASE)
    rx_bpm = re.compile(r"\b(\d{2,3})\s?bpm\b", re.IGNORECASE)
    rx_bpm_brackets = re.compile(r"\[(\d{2,3})\]")

    mix_list, remixers_list, key_list, bpm_list = [], [], [], []
    for t in tqdm(df["track_title"].fillna("").astype(str).tolist(), desc="TQM • Parsing titles", unit="track"):
        mix = ""
        m = rx_mix.search(t)
        if m: mix = m.group(1).strip()

        rem = ""
        mr = rx_remix.search(t)
        if mr:
            inner = mr.group(1)
            rem = re.split(r"remix", inner, flags=re.IGNORECASE)[0].strip(" -&x,").strip()

        key_val = ""
        mk = rx_key_music.search(t)
        if mk:
            key_val = mk.group(1).strip().replace("major","maj").replace("minor","min")
        else:
            kc = rx_key_camelot.search(t)
            if kc: key_val = kc.group(0).upper()

        bpm_val = ""
        mb = rx_bpm.search(t) or rx_bpm_brackets.search(t)
        if mb: bpm_val = mb.group(1)

        mix_list.append(mix)
        remixers_list.append(rem)
        key_list.append(key_val)
        bpm_list.append(bpm_val)

    df["mix_name"] = df["mix_name"].where(df["mix_name"].ne(""), mix_list)
    df["remixers"] = df["remixers"].where(df["remixers"].ne(""), remixers_list)
    df["key"] = df["key"].where(df["key"].ne(""), key_list)
    df["bpm"] = df["bpm"].where(df["bpm"].ne(""), bpm_list)

    def nz(x): return "" if pd.isna(x) else str(x)

    df["new_name"] = (
        "TRkw_" + df["track_title"].map(nz) +
        "_ARkw_" + df["track_artist"].map(nz) +
        "_MXkw_" + df["mix_name"].map(nz) +
        "_KYkw_" + df["key"].map(nz) +
        "_BPkw_" + df["bpm"].map(nz) +
        "_GNkw_" + df["genre"].map(nz) +
        "_RMkw_" + df["remixers"].map(nz) +
        "_LBkw_" + df["label"].map(nz) +
        "_RYkw_" + df["release_year"].map(nz) + "_" + df["release_month"].map(nz) + "_" + df["release_day"].map(nz) +
        "_PYkw_" + df["purchase_year"].map(nz) + "_" + df["purchase_month"].map(nz) + "_" + df["purchase_day"].map(nz)
    ).str.replace(r"[\/\\:*?\"<>|]", "_", regex=True)

    return df

# -----######-----###### CORE IMPORTABLE FUNCTION (SoundCloud DF Downloader — DF['src_playlist'] → files) -----######-----###### #
import os, re, json, shutil
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

try:
    import pandas as pd
except Exception:
    pd = None


# --- internal: env checks (no ASCII) ---
def _sc__ensure_ffmpeg():
    from shutil import which
    return which("ffmpeg") is not None

def _sc__safe_name(s):
    # filesystem-safe slug
    s = str(s or "").strip()
    s = re.sub(r"[\\/:*?\"<>|\n\r\t]", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:200] if s else "unnamed"

def _sc__build_opts(out_dir, ext, prefer_bitrate, archive_path, cookies_path):
    # postproc: convert to target ext
    postproc = []
    if ext.lower() in ("mp3", "wav", "aiff"):
        postproc = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": ext.lower(),
            "preferredquality": str(prefer_bitrate) if ext.lower()=="mp3" else "0",
        }]

    # Filename template: Uploader - Title [id].ext inside out_dir
    outtmpl = str(Path(out_dir) / "%(uploader)s - %(title)s [%(id)s].%(ext)s")

    opts = {
        "outtmpl": outtmpl,
        "noplaylist": False,              # if a playlist URL appears, we’ll let yt-dlp handle entries
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "retries": 5,
        "continuedl": True,
        "format": "bestaudio/best",
        "concurrent_fragment_downloads": 4,
        "writethumbnail": False,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "postprocessors": postproc,
        "restrictfilenames": False,
        "windowsfilenames": False,
        "nooverwrites": True,            # do NOT overwrite existing files
        "download_archive": str(archive_path),  # skip already downloaded ids
    }
    if cookies_path:
        opts["cookiefile"] = str(cookies_path)
    return opts

def _sc__extract_saved_path(info):
    cand = None
    if not info:
        return None
    # Try direct
    if "requested_downloads" in info and info["requested_downloads"]:
        cand = info["requested_downloads"][0].get("filepath")
    # Playlist entry?
    if not cand and "entries" in info and info["entries"]:
        e = info["entries"][0]
        if e and "requested_downloads" in e and e["requested_downloads"]:
            cand = e["requested_downloads"][0].get("filepath")
        elif e and "filepath" in e:
            cand = e["filepath"]
    if not cand and "filepath" in info:
        cand = info["filepath"]
    return Path(cand) if cand else None

def _sc__download_one(url, out_dir, ext, prefer_bitrate, archive_path, cookies_path):
    try:
        import yt_dlp
    except Exception as e:
        raise RuntimeError("yt-dlp not installed. Run: pip install yt-dlp") from e

    if ext.lower() in ("mp3","wav","aiff") and not _sc__ensure_ffmpeg():
        raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg")

    ydl_opts = _sc__build_opts(out_dir, ext, prefer_bitrate, archive_path, cookies_path)

    # progress hook (quiet by default; reserved for future per-fragment logs)
    def _hook(_d): 
        pass
    ydl_opts["progress_hooks"] = [_hook]

    meta = {
        "source_url": url, "title": None, "uploader": None, "duration_sec": None,
        "id": None, "ext": None, "requested_ext": ext.lower(), "filepath": None,
        "filesize_approx": None, "filesize_bytes": None, "error": None, "status": None
    }

    # Detect “already downloaded” quickly via archive line (best-effort);
    # yt-dlp itself will skip by archive and return fast.
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # When skipped by archive, info may be None → try to probe id via “simulate”
            if not info:
                try:
                    sim_opts = ydl_opts.copy()
                    sim_opts.update({"skip_download": True})
                    with yt_dlp.YoutubeDL(sim_opts) as ydl_sim:
                        info = ydl_sim.extract_info(url, download=False)
                        meta["status"] = "skipped_archive"
                except Exception:
                    meta["status"] = "skipped_archive"
            else:
                meta["status"] = "downloaded"

        if info:
            meta["title"] = info.get("title")
            meta["uploader"] = info.get("uploader")
            meta["duration_sec"] = info.get("duration")
            meta["id"] = info.get("id")
            meta["ext"] = info.get("ext")
            meta["filesize_approx"] = info.get("filesize_approx")

        saved = _sc__extract_saved_path(info)
        if saved and saved.exists():
            meta["filepath"] = str(saved)
            meta["filesize_bytes"] = saved.stat().st_size
        else:
            # If archive skip, try to resolve the existing path on disk by building the expected pattern:
            if meta.get("id") and meta.get("title") and meta.get("uploader"):
                # Try any ext since postproc could differ
                base_glob = f"{_sc__safe_name(meta['uploader'])} - {_sc__safe_name(meta['title'])} [{meta['id']}]"
                candidates = list(Path(out_dir).glob(base_glob + ".*"))
                if candidates:
                    meta["filepath"] = str(candidates[0])
                    meta["filesize_bytes"] = candidates[0].stat().st_size
        return meta

    except yt_dlp.utils.DownloadError as e:
        meta["error"] = f"DownloadError: {e}"
        meta["status"] = "failed"
        return meta
    except Exception as e:
        meta["error"] = str(e)
        meta["status"] = "failed"
        return meta


# -----######-----###### MAIN IMPORTABLE FUNCTION -----######-----###### #
def _sc_1808_df_GET_audio_for_src_playlist_APPEND(
    df_tracks,
    out_dir,                  # REQUIRED: you provide this absolute path
    ext="mp3",                # "mp3" (320), "wav", "aiff"
    prefer_bitrate=320,       # only for mp3
    cookies_path=None         # optional path to cookies.txt for authenticated access
):
    """
    From df_tracks['src_playlist'] SoundCloud URLs, download audio into out_dir.
    - Never overwrites existing files (yt-dlp nooverwrites + archive).
    - Re-running will only add new tracks (download archive).
    - Appends result columns to df_tracks and returns the augmented DF.

    Columns appended/updated:
      dl_title, dl_uploader, dl_duration_sec, dl_id, dl_ext, dl_requested_ext,
      dl_filepath, dl_filesize_approx, dl_filesize_bytes, dl_error, dl_status

    Notes:
      * For private/unlisted but accessible to you, pass a cookies.txt exported from your browser.
      * Only download content you own or have rights to and respect the site’s TOS.
    """
    if pd is None:
        raise RuntimeError("pandas is required. Run: pip install pandas")

    if "src_playlist" not in df_tracks.columns:
        raise ValueError("DataFrame must contain a 'src_playlist' column with SoundCloud URLs.")

    out_dir = Path(out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    archive_path = out_dir / "_download_archive.txt"   # tracks already fetched
    archive_path.touch(exist_ok=True)

    # Prepare output columns
    add_cols = [
        "dl_title","dl_uploader","dl_duration_sec","dl_id","dl_ext","dl_requested_ext",
        "dl_filepath","dl_filesize_approx","dl_filesize_bytes","dl_error","dl_status"
    ]
    df_out = df_tracks.copy()
    for c in add_cols:
        if c not in df_out.columns:
            df_out[c] = None

    urls = df_out["src_playlist"].astype(str).fillna("").tolist()

    # TQM BAR
    for i, url in enumerate(tqdm(urls, desc="TQM • Downloading SoundCloud audio", unit="url")):
        url_s = url.strip()
        if not url_s:
            df_out.at[i, "dl_status"] = "skip_empty"
            continue
        md = _sc__download_one(
            url=url_s,
            out_dir=out_dir,
            ext=ext,
            prefer_bitrate=prefer_bitrate,
            archive_path=archive_path,
            cookies_path=(Path(cookies_path).expanduser() if cookies_path else None)
        )

        df_out.at[i, "dl_title"]            = md.get("title")
        df_out.at[i, "dl_uploader"]         = md.get("uploader")
        df_out.at[i, "dl_duration_sec"]     = md.get("duration_sec")
        df_out.at[i, "dl_id"]               = md.get("id")
        df_out.at[i, "dl_ext"]              = md.get("ext")
        df_out.at[i, "dl_requested_ext"]    = md.get("requested_ext")
        df_out.at[i, "dl_filepath"]         = md.get("filepath")
        df_out.at[i, "dl_filesize_approx"]  = md.get("filesize_approx")
        df_out.at[i, "dl_filesize_bytes"]   = md.get("filesize_bytes")
        df_out.at[i, "dl_error"]            = md.get("error")
        df_out.at[i, "dl_status"]           = md.get("status")

    return df_out
