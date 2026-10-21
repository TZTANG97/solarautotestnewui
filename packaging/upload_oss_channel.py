# -*- coding: utf-8 -*-
"""Upload SolarAutoTest update channel (latest.json + zip) to Aliyun OSS.

Defaults match EMKU bucket qgongye (Shanghai), under prefix solarautotest/updates/.
Credentials are NEVER committed: load from env or EMKU ENV_环境切换.env.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_BUCKET = "qgongye"
DEFAULT_ENDPOINT = "oss-cn-shanghai.aliyuncs.com"
DEFAULT_PREFIX = "solarautotest/updates"
DEFAULT_EMKU_DIR = Path(r"E:\EMKU")


def _find_emku_env(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p
    # Avoid hardcoding non-ASCII path (Windows console encoding issues)
    for cand in sorted(DEFAULT_EMKU_DIR.glob("ENV*.env")):
        return cand
    for cand in sorted(DEFAULT_EMKU_DIR.glob("*.env")):
        if "OSS_ACCESS_KEY_ID" in cand.read_text(encoding="utf-8", errors="ignore"):
            return cand
    return DEFAULT_EMKU_DIR / "ENV_环境切换.env"


def _load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            out[key] = val
    return out


def _resolve_creds(emku_env: Path) -> tuple[str, str, str, str]:
    file_env = _load_dotenv(emku_env)
    ak = (
        os.getenv("OSS_ACCESS_KEY_ID")
        or os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        or file_env.get("OSS_ACCESS_KEY_ID")
        or ""
    ).strip()
    sk = (
        os.getenv("OSS_ACCESS_KEY_SECRET")
        or os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        or file_env.get("OSS_ACCESS_KEY_SECRET")
        or ""
    ).strip()
    bucket = (
        os.getenv("SOLARAUTOTEST_OSS_BUCKET")
        or os.getenv("OSS_BUCKET")
        or file_env.get("OSS_BUCKET")
        or DEFAULT_BUCKET
    ).strip()
    endpoint = (
        os.getenv("SOLARAUTOTEST_OSS_ENDPOINT")
        or os.getenv("OSS_ENDPOINT")
        or file_env.get("OSS_ENDPOINT")
        or DEFAULT_ENDPOINT
    ).strip()
    if not ak or not sk:
        raise SystemExit(
            "Missing OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET. "
            f"Set env or provide EMKU env file: {emku_env}"
        )
    return ak, sk, bucket, endpoint


def main() -> int:
    ap = argparse.ArgumentParser(description="Upload SolarAutoTest OSS update channel")
    ap.add_argument("--dir", required=True, help="Local channel dir with latest.json + zip")
    ap.add_argument("--prefix", default=DEFAULT_PREFIX)
    ap.add_argument("--emku-env", default="", help="Optional path to EMKU .env; auto-find ENV*.env under E:\\EMKU")
    ap.add_argument("--public-read", action="store_true", help="Set ACL public-read on uploaded objects")
    ap.add_argument(
        "--core-only",
        action="store_true",
        help="Skip blobs/ HEAD+upload; only latest.json, zip, files-latest.json",
    )
    args = ap.parse_args()

    try:
        import oss2
    except ImportError:
        print("oss2 not installed. Use EMKU venv python, e.g.:", file=sys.stderr)
        print(r"  E:\EMKU\backend_fastapi\.venv\Scripts\python.exe packaging\upload_oss_channel.py ...", file=sys.stderr)
        return 2

    channel_dir = Path(args.dir).resolve()
    json_path = channel_dir / "latest.json"
    if not json_path.is_file():
        raise SystemExit(f"latest.json not found: {json_path}")

    try:
        import json as _json

        manifest = _json.loads(json_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise SystemExit(f"invalid latest.json: {exc}") from exc

    zip_name = str(manifest.get("zip_name") or "").strip()
    if zip_name:
        zip_path = channel_dir / zip_name
        if not zip_path.is_file():
            raise SystemExit(f"latest.json zip_name missing on disk: {zip_path}")
    else:
        # Fallback: prefer newest mtime (NOT lexical sort — 20260915.zip sorts after 20260915.1325.zip)
        zips = list(channel_dir.glob("SolarAutoTest-Setup-*.zip"))
        if not zips:
            raise SystemExit(f"No SolarAutoTest-Setup-*.zip in {channel_dir}")
        zip_path = max(zips, key=lambda p: p.stat().st_mtime)

    emku_env = _find_emku_env(args.emku_env.strip() or None)
    print(f"Using EMKU env: {emku_env}")
    ak, sk, bucket_name, endpoint = _resolve_creds(emku_env)
    prefix = args.prefix.strip().strip("/")
    ep = endpoint
    if not ep.startswith("http"):
        ep = "https://" + ep

    auth = oss2.Auth(ak, sk)
    bucket = oss2.Bucket(auth, ep, bucket_name)

    uploads: list[tuple[str, Path, bool]] = [
        (f"{prefix}/latest.json", json_path, False),
        (f"{prefix}/{zip_path.name}", zip_path, False),
    ]
    # Fixed first-install URL: always overwrite SolarAutoTest-Setup-latest.zip
    stable_name = str(manifest.get("stable_zip_name") or "SolarAutoTest-Setup-latest.zip").strip()
    stable_local = channel_dir / stable_name
    if not stable_local.is_file():
        # Publish-HttpChannel should have copied it; fallback to versioned zip content
        stable_local = zip_path
    if stable_local.is_file():
        uploads.append((f"{prefix}/{stable_name}", stable_local, False))

    # Incremental channel: files manifests (always overwrite) + content-addressed blobs (skip if exists)
    for name in (
        str(manifest.get("files_name") or "files-latest.json").strip(),
        str(manifest.get("files_versioned") or "").strip(),
    ):
        if not name:
            continue
        p = channel_dir / name
        if p.is_file():
            uploads.append((f"{prefix}/{name}", p, False))

    blobs_dir = channel_dir / "blobs"
    blob_uploads = 0
    blob_skipped = 0
    # --core-only：只传 latest/zip/manifest，跳过 blobs HEAD（网络不稳时避免卡死）
    core_only = bool(getattr(args, "core_only", False))
    if blobs_dir.is_dir() and not core_only:
        for blob in sorted(blobs_dir.iterdir()):
            if not blob.is_file():
                continue
            # sha256 hex filenames only
            if not re.fullmatch(r"[0-9a-fA-F]{64}", blob.name):
                continue
            uploads.append((f"{prefix}/blobs/{blob.name}", blob, True))

    headers = {}
    if args.public_read:
        headers["x-oss-object-acl"] = "public-read"

    for key, path, skip_if_exists in uploads:
        if skip_if_exists:
            try:
                meta = bucket.head_object(key)
                if int(meta.content_length) == path.stat().st_size:
                    blob_skipped += 1
                    continue
            except Exception:
                pass
            blob_uploads += 1
        print(f"PUT oss://{bucket_name}/{key}  <-  {path}  ({path.stat().st_size} bytes)")
        bucket.put_object_from_file(key, str(path), headers=headers or None)

    public_base = f"https://{bucket_name}.{endpoint.replace('https://', '').replace('http://', '')}/{prefix}"
    print("")
    print("[OK] Uploaded SolarAutoTest update channel")
    print(f"  channel = {public_base}")
    print(f"  latest  = {public_base}/latest.json")
    print(f"  zip     = {public_base}/{zip_path.name}")
    print(f"  stable  = {public_base}/{stable_name}  (固定下载地址)")
    if (channel_dir / "files-latest.json").is_file():
        print(f"  files   = {public_base}/files-latest.json  (增量清单)")
        print(f"  blobs   = {public_base}/blobs/  (+{blob_uploads} new, skip {blob_skipped})")
    # Sanity: HEAD core objects
    for key, _, skip_if_exists in uploads:
        if skip_if_exists:
            continue
        meta = bucket.head_object(key)
        print(f"  head {key}: {meta.content_length} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
