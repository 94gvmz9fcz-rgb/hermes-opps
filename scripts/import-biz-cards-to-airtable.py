#!/usr/bin/env python3
"""
Import 20 biz card contacts to Airtable CRM.
Usage: python3 scripts/import-biz-cards-to-airtable.py <airtable_token>
"""

import json, subprocess, sys
from pathlib import Path

CONTACTS_PATH = Path("/opt/data/repo/crm-cards/parsed-contacts.json")
BASE_ID = "app6l2hwxinBLwHCa"
TABLE = "Contacts"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/import-biz-cards-to-airtable.py <airtable_token>")
        sys.exit(1)

    token = sys.argv[1]
    contacts = json.loads(CONTACTS_PATH.read_text())

    corrections = {
        "20260622_010904214_iOS": {"name": "Ben Burris", "company": "10ZiG", "phone": "(985) 773-0150"},
        "20260622_015215724_iOS": {"name": "Corey Hulen", "company": "Mattermost", "phone": "650-667-8512"},
        "20260622_020410440_iOS": {"name": "Jacqueline Stewart", "company": "Epoch Concepts", "phone": "813.428.4875"},
        "20260622_020419608_iOS": {"name": "Kevin Connors", "company": "Nutanix", "phone": "+1-240-778-9924"},
        "20260622_020429332_iOS": {"name": "Jade McKeon", "company": "McKeon Sales", "phone": ""},
        "20260622_021930502_iOS": {"name": "Stephen Landry", "company": "Dell Technologies", "phone": "+1 443-280-7154"},
        "20260622_021938102_iOS": {"name": "Doug Marco", "company": "SentinelOne", "phone": "(703) 338-2124"},
        "20260622_021947979_iOS": {"name": "James Phinnessee", "company": "Schneider Electric Federal", "phone": "725-340-4170"},
        "20260622_022027385_iOS": {"name": "Taylor Pierce", "company": "SentinelOne", "phone": "(518) 289-2138"},
        "20260622_022035049_iOS": {"name": "Steve Larzelere", "company": "Splunk", "phone": "+1 303.210.0860"},
        "20260622_022048806_iOS": {"name": "Megan Potcer", "company": "Lyme Technology Solutions", "phone": "(603) 676-3621"},
        "20260622_022059159_iOS": {"name": "Keegan Turcotte", "company": "Hewlett Packard Enterprise", "phone": "478 997 2441"},
        "20260622_022110564_iOS": {"name": "Mike Daigle", "company": "SEM Shred", "phone": ""},
        "20260622_022123592_iOS": {"name": "Darris Curry", "company": "Thinklogical / Belden", "phone": "808.518.7135"},
        "20260622_022134200_iOS": {"name": "Mari Celestine", "company": "Thinklogical / Belden", "phone": "520.635.3423"},
        "20260622_022202413_iOS": {"name": "Vince Clarke", "company": "AVI-SPL", "phone": "425 691 0120"},
        "20260622_022216147_iOS": {"name": "John Zavitsanos", "company": "Forte", "phone": "703-888-6863"},
        "20260622_022229158_iOS": {"name": "Steve Villoria", "company": "Media Pointe", "phone": ""},
        "20260622_022244046_iOS": {"name": "Jared Colvig", "company": "Cradlepoint / Ericsson", "phone": "+1 210-517-3433"},
        "20260622_022301754_iOS": {"name": "Heidi Benoit", "company": "Belkin", "phone": ""},
        "20260622_022314573_iOS": {"name": "Mackenzie Fisher", "company": "Hewlett Packard Enterprise", "phone": "+1 571 499 3518"},
        "20260622_022330037_iOS": {"name": "Tammy Sprague", "company": "Ericsson", "phone": "+1 910-494-2349"},
        "20260622_022343056_iOS": {"name": "Travis Denardo", "company": "Racktop Systems", "phone": "540.818.4090"},
    }

    url = "https://api.airtable.com/v0/" + BASE_ID + "/" + TABLE
    auth_val = "Bearer " + token

    added = 0
    skipped = 0
    seen = set()

    for contact in contacts:
        img = contact.get("source_image", "")
        corr = corrections.get(img, {})

        name = corr.get("name", contact.get("name", ""))
        company = corr.get("company", contact.get("company", ""))
        phone = corr.get("phone", contact.get("phone", ""))
        email = contact.get("email", "") or ""

        if not name:
            print("  SKIP", img, "- no name")
            skipped += 1
            continue

        dedup = name + "|" + company
        if dedup in seen:
            print("  SKIP", name, "- duplicate")
            skipped += 1
            continue
        seen.add(dedup)

        phone_clean = phone.replace(chr(10), " ").strip()
        email_clean = email

        fields = {"Name": name, "Company": company, "Phone": phone_clean}
        if email_clean:
            fields["Email"] = email_clean

        payload = json.dumps({"fields": fields})

        result = subprocess.run(
            ["curl", "-s", "-X", "POST", url,
             "-H", "Authorization: " + auth_val,
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0:
            resp = json.loads(result.stdout)
            if "id" in resp:
                added += 1
                print("  OK", name, "-", company)
            else:
                err = resp.get("error", {}).get("message", "?")
                print("  FAIL", name, ":", err)
        else:
            print("  FAIL", name, ": HTTP error")

    print("")
    print("Added:", added, "| Skipped:", skipped, "| Total:", added + skipped)

if __name__ == "__main__":
    main()
