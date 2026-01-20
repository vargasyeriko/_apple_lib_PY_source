# -----######-----###### CORE IMPORTABLE FUNCTION (All → AIFF 44.1/16/Stereo + Tags + Verify) -----######-----###### #
import os, sys, shutil, subprocess, tempfile
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

# Tagging
from mutagen import File as MutaFile
from mutagen.aiff import AIFF
from mutagen.id3 import (
    ID3, ID3NoHeaderError, ID3BadUnsynchData,
    TIT2, TPE1, TPE2, TALB, TCON, TDRC, TRCK, TPOS, COMM, TBPM, TKEY,
    TPUB, TSRC, TPE3, TCOM, TENC, APIC, CTOC, CHAP
)

# -------------------- helpers (no ASCII banner for sub-fns) -------------------- #
def _safe_get_first(d, key):
    if d is None: return None
    v = d.get(key)
    if v is None: return None
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v

def _as_int_pair(text):
    if not text: return None, None
    s = str(text)
    if '/' in s:
        a,b = s.split('/',1)
        return (a.strip() or None), (b.strip() or None)
    return (s.strip() or None), None

def _ensure_id3(aiff_path):
    a = AIFF(aiff_path)
    if a.tags is None:
        a.add_tags()
    return a

def _copy_id3_frames(src_id3, dst_id3):
    # Copy common frames + chapters/artwork; ignore oddities that fail to serialize.
    for frame in list(src_id3.values()):
        try:
            if isinstance(frame, APIC):
                dst_id3.add(APIC(encoding=frame.encoding, mime=frame.mime, type=frame.type, desc=frame.desc, data=frame.data))
            elif isinstance(frame, COMM):
                dst_id3.add(COMM(encoding=frame.encoding, lang=frame.lang, desc=frame.desc, text=frame.text))
            elif isinstance(frame, (TIT2, TPE1, TPE2, TALB, TCON, TDRC, TRCK, TPOS, TBPM, TKEY, TPUB, TSRC, TPE3, TCOM, TENC)):
                dst_id3.add(type(frame)(encoding=frame.encoding, text=frame.text))
            elif isinstance(frame, (CTOC, CHAP)):
                dst_id3.add(frame)
            else:
                # Pass through for other safe T* frames
                dst_id3.add(frame)
        except Exception:
            # Skip non-serializable frames without killing the run
            pass

def _map_generic_to_id3(vtags, dst_id3, pictures=None):
    # Generic (Vorbis/FLAC/WAV INFO) → ID3
    title   = _safe_get_first(vtags, "title")
    artist  = _safe_get_first(vtags, "artist")
    album   = _safe_get_first(vtags, "album")
    albumartist = _safe_get_first(vtags, "albumartist") or _safe_get_first(vtags, "album artist")
    genre   = _safe_get_first(vtags, "genre")
    date    = _safe_get_first(vtags, "date") or _safe_get_first(vtags, "year")
    comment = _safe_get_first(vtags, "comment") or _safe_get_first(vtags, "description")
    bpm     = _safe_get_first(vtags, "bpm")
    key_    = _safe_get_first(vtags, "initialkey") or _safe_get_first(vtags, "key")
    label   = _safe_get_first(vtags, "label") or _safe_get_first(vtags, "publisher")
    isrc    = _safe_get_first(vtags, "isrc")
    remixer = _safe_get_first(vtags, "remixer")
    composer= _safe_get_first(vtags, "composer")
    encoder = _safe_get_first(vtags, "encoder") or _safe_get_first(vtags, "encodedby") or _safe_get_first(vtags, "encoded_by")
    trk     = _safe_get_first(vtags, "tracknumber")
    dsk     = _safe_get_first(vtags, "discnumber")

    if title:   dst_id3.add(TIT2(encoding=3, text=str(title)))
    if artist:  dst_id3.add(TPE1(encoding=3, text=str(artist)))
    if album:   dst_id3.add(TALB(encoding=3, text=str(album)))
    if albumartist: dst_id3.add(TPE2(encoding=3, text=str(albumartist)))
    if genre:   dst_id3.add(TCON(encoding=3, text=str(genre)))
    if date:    dst_id3.add(TDRC(encoding=3, text=str(date)))
    if comment: dst_id3.add(COMM(encoding=3, lang="eng", desc="", text=str(comment)))
    if bpm:     dst_id3.add(TBPM(encoding=3, text=str(bpm)))
    if key_:    dst_id3.add(TKEY(encoding=3, text=str(key_)))
    if label:   dst_id3.add(TPUB(encoding=3, text=str(label)))
    if isrc:    dst_id3.add(TSRC(encoding=3, text=str(isrc)))
    if remixer: dst_id3.add(TPE3(encoding=3, text=str(remixer)))
    if composer:dst_id3.add(TCOM(encoding=3, text=str(composer)))
    if encoder: dst_id3.add(TENC(encoding=3, text=str(encoder)))

    if trk:
        n, d = _as_int_pair(trk)
        if n or d:
            dst_id3.add(TRCK(encoding=3, text=[f"{n or ''}/{d or ''}".strip('/')]))
    if dsk:
        n, d = _as_int_pair(dsk)
        if n or d:
            dst_id3.add(TPOS(encoding=3, text=[f"{n or ''}/{d or ''}".strip('/')]))

    if pictures:
        for pic in pictures:
            try:
                dst_id3.add(APIC(encoding=3, mime=getattr(pic, "mime", None) or "image/jpeg", type=3, desc=u"", data=getattr(pic, "data", b"")))
            except Exception:
                pass

def _copy_all_tags_to_aiff(src_path, aiff_path):
    """
    After encoding, write a clean ID3 tag set into the AIFF.
    Priority:
      1) If source has ID3 → copy frames
      2) Else, map Vorbis/FLAC/WAV INFO → ID3; copy artwork when possible
    """
    dst_aiff = _ensure_id3(aiff_path)
    dst_id3 = dst_aiff.tags

    src = MutaFile(src_path)
    if src is None:
        dst_aiff.save()
        return

    # Direct ID3 → ID3
    try:
        src_id3 = getattr(src, "tags", None)
        if isinstance(src_id3, ID3) or (src_id3 and any(k.startswith("T") or k in ("APIC","COMM","CTOC","CHAP") for k in src_id3.keys())):
            try:
                _copy_id3_frames(src_id3, dst_id3)
                dst_aiff.save()
                return
            except Exception:
                pass
    except Exception:
        pass

    # Generic mapping (Vorbis/FLAC/WAV INFO, MP4 atoms won't map fully)
    vtags = getattr(src, "tags", {}) or {}
    pictures = []
    try:
        # FLAC: embedded pictures
        if hasattr(src, "pictures") and getattr(src, "pictures", None):
            pictures = src.pictures
        elif hasattr(src, "tags") and "METADATA_BLOCK_PICTURE" in src.tags:
            pictures = []  # base64 case skipped (mutagen handles some variants)
    except Exception:
        pictures = []

    try:
        _map_generic_to_id3(vtags, dst_id3, pictures=pictures)
    except Exception:
        pass

    dst_aiff.save()

def _verify_aiff_ok(aiff_path):
    try:
        t = AIFF(aiff_path)
        _ = t.info.length  # raises if broken
        return True, None
    except Exception as e:
        return False, str(e)

def _exts_casefold(exts):
    # normalize to a case-insensitive set, include upper/lower/Title variants
    s = set()
    for e in exts or []:
        if not e: continue
        ee = e if e.startswith(".") else "."+e
        base = ee.lower()
        s.add(base)
        s.add(base.upper())
        s.add(base.capitalize())
    return s

def _ffmpeg_encode_to_aiff(src_path, dst_path):
    """
    Robust ffmpeg call:
    - force AIFF PCM 16-bit big-endian, 44.1kHz, stereo
    - strip container metadata (we'll write fresh ID3 next)
    - disable video/subs
    - choose first audio stream explicitly
    """
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-y",
        "-i", str(src_path),
        "-map", "0:a:0",
        "-vn", "-sn",
        "-ar", "44100",
        "-ac", "2",
        "-c:a", "pcm_s16be",
        "-map_metadata", "-1",
        str(dst_path)
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode == 0

# -----######-----###### CORE IMPORTABLE FUNCTION (per-file) -----######-----###### #
def _aiff_0109_onefile_GET_status_path(
    file_in,
    out_dir=None
):
    """
    Convert a single file → AIFF (44.1kHz / 16-bit / stereo), always re-encode (even AIFF).
    Returns (status, path_out). status in {"ok", "broken", "fail"}.
    """
    src_path = Path(file_in)
    if out_dir is None:
        out_dir = src_path.parent
    else:
        out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    dst_path = out_dir / (src_path.stem + ".aiff")

    # Atomic write via temp file to avoid half-written outputs
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td) / (src_path.stem + ".aiff")

        ok = _ffmpeg_encode_to_aiff(src_path, tmp_path)
        if not ok or not tmp_path.exists():
            return "fail", None

        # Write tags/artwork (best-effort; never fatal)
        try:
            _copy_all_tags_to_aiff(src_path, tmp_path)
        except Exception:
            pass

        # Verify playable
        v_ok, v_err = _verify_aiff_ok(tmp_path)
        if not v_ok:
            # Move the broken file out with suffix
            broken_dst = dst_path.with_stem(dst_path.stem + "_BROKEN")
            try:
                broken_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(tmp_path), str(broken_dst))
            except Exception:
                pass
            return "broken", broken_dst if broken_dst.exists() else dst_path

        # All good: move into place
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_path), str(dst_path))

    return "ok", dst_path

# -----######-----###### CORE IMPORTABLE FUNCTION (batch) -----######-----###### #
def _aiff_0109_all2aiff_GET_summary(
    root_folder,
    out_root=None,
    audio_extensions=None,
    dry_run="n",
    src_action="keep",          # "keep" | "move" | "trash"
    src_action_move_dir=None,   # required if src_action == "move"
    overwrite="n"               # "y" to overwrite existing AIFF at dst, else skip creating duplicate
):
    """
    Recursively convert *major* audio types to AIFF (CDJ-safe 44.1/16/stereo) with tags & artwork.
    - Always re-encodes, even for AIFF sources (to guarantee target spec)
    - Mirrors folder structure under out_root (if provided)
    - Case-insensitive extension handling
    - macOS junk skipped
    - TQM progress bar + compact summary
    - Post-success actions on sources: keep | move | trash

    Returns:
      summary dict with counts and lists per status.
    """
    root = Path(root_folder)

    # If user doesn't pass, we include a broad set of common types
    if audio_extensions is None:
        audio_extensions = [
            ".flac", ".wav", ".mp3", ".aiff", ".aif",
            ".m4a", ".aac", ".alac", ".ogg", ".oga", ".wv", ".aifc"
        ]
    exts_all = _exts_casefold(audio_extensions)

    # Collect candidates (skip macOS junk)
    all_files = [
        p for p in root.rglob("*")
        if p.is_file()
        and not p.name.startswith("._")
        and p.name != ".DS_Store"
        and (p.suffix in exts_all)
    ]

    # Compute outputs + decide skips
    targets = []
    for src_path in all_files:
        rel = src_path.relative_to(root)
        out_dir = (Path(out_root) / rel.parent) if out_root else src_path.parent
        dst_path = out_dir / (src_path.stem + ".aiff")

        if dry_run.lower().startswith("y"):
            targets.append((src_path, out_dir, dst_path, "todo"))
        else:
            # If overwrite == 'n' and AIFF already exists in destination, skip re-creating file
            if dst_path.exists() and not overwrite.lower().startswith("y"):
                # Still *verify* later if the existing AIFF matches spec? We assume OK for speed.
                # If you want forced re-encode, set overwrite='y'.
                continue
            targets.append((src_path, out_dir, dst_path, "todo"))

    # ----- TQM BAR -----
    pbar = tqdm(total=len(targets), desc="TQM | All → AIFF 44.1/16/stereo", unit="file")

    stats = {
        "ok": 0, "broken": 0, "fail": 0,
        "skipped_existing": 0,
        "total_scanned": len(all_files),
        "total_planned": len(targets),
        "ok_paths": [], "broken_paths": [], "fail_paths": [], "skipped_paths": []
    }

    # If dry-run: just preview names and return summary
    if dry_run.lower().startswith("y"):
        for (src_path, out_dir, dst_path, _) in targets:
            pbar.set_postfix_str(f"DRY-RUN → {src_path.name}")
            pbar.update(1)
            stats["skipped_paths"].append(str(src_path))
        pbar.close()
        return stats

    # Convert
    for (src_path, out_dir, dst_path, _) in targets:
        # If we got here and the destination exists but overwrite == 'n', mark skipped
        if dst_path.exists() and not overwrite.lower().startswith("y"):
            stats["skipped_existing"] += 1
            stats["skipped_paths"].append(str(dst_path))
            pbar.set_postfix_str(f"SKIP (exists): {dst_path.name}")
            pbar.update(1)
            continue

        status, outp = _aiff_0109_onefile_GET_status_path(src_path, out_dir=out_dir)
        if status == "ok":
            stats["ok"] += 1
            stats["ok_paths"].append(str(outp))
            pbar.set_postfix_str(f"OK: {src_path.name}")
            # Post-success action on source
            try:
                if src_action == "trash":
                    # move to user Trash if available; fallback to unlink
                    try:
                        from send2trash import send2trash
                        send2trash(str(src_path))
                    except Exception:
                        src_path.unlink(missing_ok=True)
                elif src_action == "move":
                    if not src_action_move_dir:
                        raise ValueError("src_action_move_dir is required when src_action='move'")
                    dst_dir_move = Path(src_action_move_dir); dst_dir_move.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src_path), str(dst_dir_move / src_path.name))
                else:
                    pass  # keep
            except Exception:
                # Non-fatal; keep going
                pass

        elif status == "broken":
            stats["broken"] += 1
            stats["broken_paths"].append(str(outp))
            pbar.set_postfix_str(f"BROKEN: {src_path.name}")
        else:
            stats["fail"] += 1
            stats["fail_paths"].append(str(src_path))
            pbar.set_postfix_str(f"FAIL: {src_path.name}")

        pbar.update(1)

    pbar.close()

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{stamp}] === SUMMARY ===\n"
        f"Total scanned:     {stats['total_scanned']}\n"
        f"Planned to convert:{stats['total_planned']}\n"
        f"Converted OK:      {stats['ok']}\n"
        f"Broken (tagged):   {stats['broken']}\n"
        f"Failed:            {stats['fail']}\n"
        f"Skipped (exists):  {stats['skipped_existing']}\n"
    )
    return stats


# -----######-----###### CORE IMPORTABLE FUNCTION (Erase everything but AIFF) -----######-----###### #
import os
from pathlib import Path
from tqdm import tqdm

def _cleanup_2208_keepaiff_GET_removed_files(root_folder, dry_run="n"):
    """
    Recursively erase everything but AIFF (.aiff/.aif) files.
    Skips system junk (.DS_Store, ._*).
    
    Inputs:
      root_folder : str/Path → folder to clean
      dry_run     : "y" = preview only, "n" = actually delete
    
    Returns:
      dict summary with counts
    """
    root = Path(root_folder)

    # Collect all files
    all_files = [p for p in root.rglob("*") if p.is_file()]
    # Keep only those NOT AIFF
    targets = [
        p for p in all_files
        if p.suffix.lower() not in (".aiff", ".aif")
        and not p.name.startswith("._")
        and p.name != ".DS_Store"
    ]

    # Progress bar
    pbar = tqdm(total=len(targets), desc="TQM • Cleaning non-AIFF files", unit="file")

    removed, skipped = 0, 0
    for f in targets:
        if dry_run.lower().startswith("y"):
            pbar.set_postfix_str(f"DRY-RUN: would remove {f.name}")
            skipped += 1
        else:
            try:
                f.unlink()
                removed += 1
                pbar.set_postfix_str(f"Removed {f.name}")
            except Exception as e:
                skipped += 1
                pbar.set_postfix_str(f"⚠️ Skip {f.name}: {e}")
        pbar.update(1)

    pbar.close()

    summary = {
        "total_files": len(all_files),
        "removed": removed,
        "skipped": skipped,
        "kept_aiff": len(all_files) - len(targets),
    }

    print(
        f"Done cleanup.\n"
        f" • Total files scanned: {summary['total_files']}\n"
        f" • Removed: {summary['removed']}\n"
        f" • Skipped (errors/dry-run): {summary['skipped']}\n"
        f" • Kept AIFF: {summary['kept_aiff']}\n"
    )
    return summary



#### GET DF 
# ----------------------------######----------------------------#
#   0_FNS  (CORE IMPORTABLE FUNCTION)                           #
# ----------------------------######----------------------------#

import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from mutagen.aiff import AIFF


# -------------------- helpers (no ASCII banner for sub-fns) -------------------- #
def _clean_kw(s):
    if s is None:
        return ""
    return (
        str(s)
        .strip()
        .replace(" ", "_").replace("/", "___").replace(",", "_")
        .replace("(", "").replace(")", "").replace("!", "")
        .replace("&", "and").replace("’", "").replace("'", "")
        .replace("¿", "").replace("¡", "").replace(":", "")
        .replace(";", "")
    )

def _safe_text(frame):
    try:
        if frame is None:
            return ""
        if hasattr(frame, "text"):
            t = frame.text
            if isinstance(t, (list, tuple)):
                return str(t[0]) if t else ""
            return str(t)
        return str(frame)
    except Exception:
        return ""

def _read_aiff_id3(aiff_path):
    out = {
        "title": "",
        "artist": "",
        "genre": "",
        "label": "",
        "release_date": "",
        "bpm": "",
        "key": "",
        "comment": "",
    }

    try:
        a = AIFF(aiff_path)
        tags = a.tags
        if tags is None:
            return out

        out["title"]        = _safe_text(tags.get("TIT2"))
        out["artist"]       = _safe_text(tags.get("TPE1"))
        out["genre"]        = _safe_text(tags.get("TCON"))
        out["label"]        = _safe_text(tags.get("TPUB"))
        out["release_date"] = _safe_text(tags.get("TDRC"))
        out["bpm"]          = _safe_text(tags.get("TBPM"))
        out["key"]          = _safe_text(tags.get("TKEY"))

        comm = tags.getall("COMM") if hasattr(tags, "getall") else []
        if comm:
            out["comment"] = _safe_text(comm[0])

        return out
    except Exception:
        return out

def _extract_mix_from_title(title_clean):
    tl = (title_clean or "").lower()
    if any(k in tl for k in ["remix", "mix", "edit", "version", "rework"]):
        return title_clean if title_clean else "original"
    return "original"

def _norm_bpm(bpm_raw):
    if not bpm_raw:
        return ""
    try:
        x = float(str(bpm_raw).strip())
        if x <= 0:
            return ""
        return str(int(round(x)))
    except Exception:
        return _clean_kw(bpm_raw)

def _clip_len(s, n):
    s = "" if s is None else str(s)
    return s[:n]

def _build_kw_filename(title, artist_val, remix, key, bpm, genre_val, label_val, release_date_val, purchase_date_val, ext):
    new_name = (
        f"TRkw_{title}_ARkw_{artist_val}_MXkw_{remix}_KYkw_{key}_"
        f"BPkw_{bpm}_GNkw_{genre_val}_LBkw_{label_val}_RYkw_{release_date_val}_"
        f"PYkw_{purchase_date_val}{ext}"
    )
    if len(new_name) > 240:
        new_name = new_name[:230] + ext
    return new_name


# ----------------------------######----------------------------#
#   _id3_1901_kwname_GET_df_ready and rename                                #
# ----------------------------######----------------------------#
def _id3_1901_kwname_GET_df_ready(
    root_folder,
    custom_artist="",
    custom_genre="",
    custom_label="",
    custom_release_date="",
    custom_purchase_date="",
    audio_extensions=(".aiff", ".aif"),
    include_subfolders="y"
):
    """
    DF-generation:
    - Walk root_folder
    - Read AIFF ID3 tags
    - If title tag missing → use filename stem as title
    - Clean strings for kw-tag naming
    - Build 'new_name' + 'new_path'
    - OPTIONAL: Rename ONLY if user types YES

    Overrides:
      If custom_* == "", use tag-derived value (or fallback rules).
      If custom_* is provided, it wins.

    Returns:
      df with tag columns + cleaned columns + proposed new_name/new_path
    """
    root = Path(os.path.expanduser(str(root_folder))).resolve()

    exts = set([e.lower() if str(e).startswith(".") else f".{str(e).lower()}" for e in (audio_extensions or [])])

    if include_subfolders.lower().startswith("y"):
        files = [
            p for p in root.rglob("*")
            if p.is_file()
            and p.suffix.lower() in exts
            and not p.name.startswith("._")
            and p.name != ".DS_Store"
        ]
    else:
        files = [
            p for p in root.glob("*")
            if p.is_file()
            and p.suffix.lower() in exts
            and not p.name.startswith("._")
            and p.name != ".DS_Store"
        ]

    rows = []
    pbar = tqdm(total=len(files), desc="TQM | Read AIFF tags → DF", unit="file")

    for p in files:
        pbar.set_postfix_str(p.name[:40])

        # read tags (expects: title, artist, genre, label, release_date, bpm, key, comment)
        tags = _read_aiff_id3(str(p))

        title_raw   = (tags.get("title") or "").strip()
        artist_raw  = (tags.get("artist") or "").strip()
        genre_raw   = (tags.get("genre") or "").strip()
        label_raw   = (tags.get("label") or "").strip()
        rel_raw     = (tags.get("release_date") or "").strip()
        bpm_raw     = (tags.get("bpm") or "").strip()
        key_raw     = (tags.get("key") or "").strip()
        comm_raw    = (tags.get("comment") or "").strip()

        # fallback: title tag missing → filename stem
        if not title_raw:
            title_raw = p.stem

        # overrides only if user provides non-empty values
        artist_val = custom_artist if str(custom_artist).strip() else artist_raw
        genre_val  = custom_genre if str(custom_genre).strip() else genre_raw
        label_val  = custom_label if str(custom_label).strip() else label_raw
        release_date_val  = custom_release_date if str(custom_release_date).strip() else rel_raw
        purchase_date_val = custom_purchase_date if str(custom_purchase_date).strip() else ""

        # clean + trim (keep your exact rules)
        title_clean  = _clip_len(_clean_kw(title_raw), 25)
        artist_clean = _clip_len(_clean_kw(artist_val), 25)
        genre_clean  = _clean_kw(genre_val)
        label_clean  = _clean_kw(label_val)

        key_clean = _clean_kw(key_raw) if key_raw else "NA"
        bpm_clean = _norm_bpm(bpm_raw) if bpm_raw else "NA"

        release_date_clean  = _clean_kw(release_date_val) if release_date_val else "NA"
        purchase_date_clean = _clean_kw(purchase_date_val) if purchase_date_val else "NA"

        remix_clean = _extract_mix_from_title(title_clean)

        ext = p.suffix
        new_name = _build_kw_filename(
            title=title_clean,
            artist_val=artist_clean if artist_clean else "NA",
            remix=_clean_kw(remix_clean) if remix_clean else "original",
            key=key_clean if key_clean else "NA",
            bpm=bpm_clean if bpm_clean else "NA",
            genre_val=genre_clean if genre_clean else "NA",
            label_val=label_clean if label_clean else "NA",
            release_date_val=release_date_clean,
            purchase_date_val=purchase_date_clean,
            ext=ext
        )

        rows.append({
            "Path": str(p),
            "dir": str(p.parent),
            "file_name": p.name,
            "Name": p.stem,
            "Extension": p.suffix,

            # raw tag reads
            "title_raw": title_raw,
            "artist_raw": artist_raw,
            "genre_raw": genre_raw,
            "label_raw": label_raw,
            "release_date_raw": rel_raw,
            "purchase_date_raw": "",
            "bpm_raw": bpm_raw,
            "key_raw": key_raw,
            "comment_raw": comm_raw,

            # cleaned/used values
            "title": title_clean,
            "artist": artist_clean if artist_clean else "NA",
            "genre": genre_clean if genre_clean else "NA",
            "label": label_clean if label_clean else "NA",
            "release_date": release_date_clean,
            "purchase_date": purchase_date_clean,
            "bpm": bpm_clean,
            "key": key_clean,
            "remix": _clean_kw(remix_clean) if remix_clean else "original",

            # proposed outputs (NO renaming happens unless YES below)
            "new_name": new_name,
            "new_path": str(p.parent / new_name),
        })

        pbar.update(1)

    pbar.close()

    df = pd.DataFrame(rows)

    cols_front = ["Path", "new_name", "new_path", "title", "artist", "remix", "key", "bpm", "genre", "label", "release_date", "purchase_date"]
    cols_rest = [c for c in df.columns if c not in cols_front]
    df = df[cols_front + cols_rest] if len(df) else df

    # ==========================
    # RENAME STEP (ONLY IF YES)
    # ==========================
    do_rename = input("\n⚠️  Rename ALL files in this batch? Type YES to confirm: ").strip()
    if do_rename == "YES":
        pbar2 = tqdm(total=len(df), desc="TQM | Renaming files", unit="file")

        rename_status = []
        rename_error = []

        for i, row in df.iterrows():
            src = str(row["Path"])
            dst = str(row["new_path"])

            try:
                if src == dst:
                    rename_status.append("skip_same")
                    rename_error.append("")
                elif os.path.exists(dst):
                    rename_status.append("skip_exists")
                    rename_error.append("dst_exists")
                elif not os.path.isfile(src):
                    rename_status.append("missing_src")
                    rename_error.append("src_missing")
                else:
                    os.rename(src, dst)
                    df.at[i, "Path"] = dst
                    rename_status.append("renamed")
                    rename_error.append("")
            except Exception as e:
                rename_status.append("error")
                rename_error.append(str(e))

            pbar2.update(1)

        pbar2.close()

        df["rename_status"] = rename_status
        df["rename_error"] = rename_error

        # keep front columns consistent even after adding rename cols
        cols_front2 = cols_front + ["rename_status", "rename_error"]
        cols_rest2 = [c for c in df.columns if c not in cols_front2]
        df = df[cols_front2 + cols_rest2] if len(df) else df
    else:
        # keep schema stable, even if user skips
        df["rename_status"] = "preview_only"
        df["rename_error"] = ""

        cols_front2 = cols_front + ["rename_status", "rename_error"]
        cols_rest2 = [c for c in df.columns if c not in cols_front2]
        df = df[cols_front2 + cols_rest2] if len(df) else df

    return df
