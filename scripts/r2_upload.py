#!/usr/bin/env python3
"""
r2_upload.py — S3-compatible PUT to Cloudflare R2 (offsite backup target).

Usage: python3 r2_upload.py <local_file> [<r2_key>]
  - <r2_key> defaults to the local filename (basename).
  - Reads creds from /opt/data/tmp/.cf_config.json (token/account_id) plus
    R2_ACCESS_KEY/R2_SECRET env vars, OR from hardcoded fallback envs:
    R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY (standard S3 names).

Prints "R2_UPLOAD_OK <key> <bytes>" on success, non-zero exit on failure.
No external deps — pure stdlib sigv4.
"""
import json, os, sys, hashlib, hmac, datetime, urllib.request, urllib.error, pathlib

CONF = pathlib.Path("/opt/data/tmp/.cf_config.json")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()

def sigv4(ak, sk, region, host, method, path, query, headers, payload_hash):
    # canonical request
    canonical_headers = "".join(f"{k.lower()}:{v.strip()}\n" for k, v in sorted(headers.items()))
    signed_headers = ";".join(sorted(k.lower() for k in headers))
    canonical_request = "\n".join([method, path, query, canonical_headers, signed_headers, payload_hash])
    # string to sign
    now = datetime.datetime.now(datetime.timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    scope = f"{date_stamp}/{region}/s3/aws4_request"
    sts = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, sha256_hex(canonical_request.encode())])
    k_date = sign(("AWS4" + sk).encode(), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, "s3")
    k_signing = sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, sts.encode(), hashlib.sha256).hexdigest()
    auth = f"AWS4-HMAC-SHA256 Credential={ak}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"
    return auth, amz_date

def main():
    if len(sys.argv) < 2:
        print("usage: r2_upload.py <local_file> [<r2_key>]", file=sys.stderr)
        sys.exit(2)
    local = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local)
    conf = json.loads(CONF.read_text())
    account = conf["account_id"]
    ak = os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("R2_ACCESS_KEY")
    sk = os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("R2_SECRET")
    if not ak or not sk:
        print("R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY not set", file=sys.stderr)
        sys.exit(2)
    bucket = os.environ.get("R2_BUCKET", "hermes-backups")
    host = f"{account}.r2.cloudflarestorage.com"
    path = f"/{bucket}/{key}"
    data = open(local, "rb").read()
    payload_hash = sha256_hex(data)
    headers = {
        "host": host,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": "PLACEHOLDER",
        "content-type": "application/octet-stream",
    }
    # x-amz-date must match between headers and signature; do it properly
    now = datetime.datetime.now(datetime.timezone.utc)
    headers["x-amz-date"] = now.strftime("%Y%m%dT%H%M%SZ")
    auth, _ = sigv4(ak, sk, "auto", host, "PUT", path, "", headers, payload_hash)
    headers["Authorization"] = auth
    req = urllib.request.Request(f"https://{host}{path}", data=data, method="PUT")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            print(f"R2_UPLOAD_OK {key} {len(data)} bytes status={r.status}")
    except urllib.error.HTTPError as e:
        print(f"R2_UPLOAD_FAIL {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
