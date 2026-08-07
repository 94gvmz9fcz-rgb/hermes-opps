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

def prune(account, ak, sk, bucket, keep_days=14):
    """List R2 objects and delete those older than keep_days (parsed from key
    dates like hermes-backup-YYYY-MM-DD.tar.gz). Returns (deleted, kept)."""
    import re
    host = f"{account}.r2.cloudflarestorage.com"
    def req(method, path, query=""):
        now = datetime.datetime.now(datetime.timezone.utc)
        amz = now.strftime("%Y%m%dT%H%M%SZ")
        headers = {"host": host, "x-amz-content-sha256": sha256_hex(b""), "x-amz-date": amz}
        ch = "".join(f"{k.lower()}:{v.strip()}\n" for k, v in sorted(headers.items()))
        sh = ";".join(sorted(headers.keys()))
        ds = now.strftime("%Y%m%d")
        scope = f"{ds}/auto/s3/aws4_request"
        cr = "\n".join(["GET" if method == "GET" else "DELETE", path, query, ch, sh, sha256_hex(b"")])
        sts = "\n".join(["AWS4-HMAC-SHA256", amz, scope, sha256_hex(cr.encode())])
        k1 = sign(("AWS4" + sk).encode(), ds); k2 = sign(k1, "auto"); k3 = sign(k2, "s3"); k4 = sign(k3, "aws4_request")
        sig = hmac.new(k4, sts.encode(), hashlib.sha256).hexdigest()
        headers["Authorization"] = f"AWS4-HMAC-SHA256 Credential={ak}/{scope}, SignedHeaders={sh}, Signature={sig}"
        url = f"https://{host}{path}" + (f"?{query}" if query else "")
        r = urllib.request.Request(url, method=method)
        for k, v in headers.items():
            r.add_header(k, v)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()[:200]
    # list
    status, body = req("GET", f"/{bucket}", "list-type=2")
    deleted = kept = 0
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(body)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        for c in root.findall(".//s3:Contents", ns):
            key = c.findtext("s3:Key", "", ns)
            m = re.search(r"(\d{4})-(\d{2})-(\d{2})", key)
            if not m:
                kept += 1
                continue
            d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if (datetime.date.today() - d).days > keep_days:
                req("DELETE", f"/{bucket}/{key}")
                deleted += 1
            else:
                kept += 1
    except Exception as e:
        print(f"R2_PRUNE_ERR {e} (status {status}, body {body[:120]})", file=sys.stderr)
        return
    print(f"R2_PRUNE_OK deleted={deleted} kept={kept}")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--prune":
        conf = json.loads(CONF.read_text())
        ak = os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("R2_ACCESS_KEY")
        sk = os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("R2_SECRET")
        bucket = os.environ.get("R2_BUCKET", "hermes-backups")
        if not ak or not sk:
            print("R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY not set", file=sys.stderr)
            sys.exit(2)
        prune(conf["account_id"], ak, sk, bucket)
        return
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
