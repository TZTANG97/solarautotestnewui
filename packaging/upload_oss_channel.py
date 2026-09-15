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

    uploads = [
        (f"{prefix}/latest.json", json_path),
        (f"{prefix}/{zip_path.name}", zip_path),
    ]
    # Fixed first-install URL: always overwrite SolarAutoTest-Setup-latest.zip
    stable_name = str(manifest.get("stable_zip_name") or "SolarAutoTest-Setup-latest.zip").strip()
    stable_local = channel_dir / stable_name
    if not stable_local.is_file():
        # Publish-HttpChannel should have copied it; fallback to versioned zip content
        stable_local = zip_path
    if stable_local.is_file():
        uploads.append((f"{prefix}/{stable_name}", stable_local))

    headers = {}
    if args.public_read:
        headers["x-oss-object-acl"] = "public-read"

    for key, path in uploads:
        print(f"PUT oss://{bucket_name}/{key}  <-  {path}  ({path.stat().st_size} bytes)")
        bucket.put_object_from_file(key, str(path), headers=headers or None)

    public_base = f"https://{bucket_name}.{endpoint.replace('https://', '').replace('http://', '')}/{prefix}"
    print("")
    print("[OK] Uploaded SolarAutoTest update channel")
    print(f"  channel = {public_base}")
    print(f"  latest  = {public_base}/latest.json")
    print(f"  zip     = {public_base}/{zip_path.name}")
    print(f"  stable  = {public_base}/{stable_name}  (固定下载地址)")
    # Sanity: HEAD
    for key, _ in uploads:
        meta = bucket.head_object(key)
        print(f"  head {key}: {meta.content_length} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
