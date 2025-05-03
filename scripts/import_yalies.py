#!/usr/bin/env python3
#scripts/import_yalies.py
import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("YALIES_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Missing YALIES_API_TOKEN in your environment")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}
BASE_URL = "https://api.yalies.io/v2"
PEOPLE_ENDPOINT = f"{BASE_URL}/people"

def fetch_all_people():
    people = []
    page = 0
    page_size = 100
    while True:
        payload = {
            "query": "",
            "filters": {},
            "page": page,
            "page_size": page_size
        }
        resp = requests.post(PEOPLE_ENDPOINT, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # Attempt to extract list of person objects
        if isinstance(data, list):
            batch = data
        elif "people" in data:
            batch = data["people"]
        elif "data" in data:
            batch = data["data"]
        else:
            # fallback: single object
            batch = [data]
        if not batch:
            break
        people.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return people

def get_or_create(conn, table, name_field, value):
    cur = conn.execute(
        f"SELECT {table[:-1].lower()}_id FROM {table} WHERE {name_field} = ?",
        (value,)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        f"INSERT INTO {table} ({name_field}) VALUES (?)",
        (value,)
    )
    return cur.lastrowid

def main():
    conn = sqlite3.connect("lux.sqlite")
    conn.row_factory = sqlite3.Row

    people = fetch_all_people()
    print(f"Fetched {len(people)} people from Yalies.io")

    for p in people:
        netid = p.get("netid")
        name  = f"{p.get('first_name','')} {p.get('last_name','')}".strip()
        pronouns = p.get("pronouns")
        college  = p.get("college")
        year     = p.get("year")
        profile  = p.get("profile") or ""

        # Insert into Users, including cas_username
        cur = conn.execute("""
            INSERT OR IGNORE INTO Users
              (cas_username, name, pronoun, residential_college, college_year, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            netid,
            name,
            pronouns,
            college,
            str(year) if year is not None else None,
            profile
        ))
        # If it already existed, fetch its user_id
        if cur.lastrowid:
            user_id = cur.lastrowid
        else:
            user_id = conn.execute(
                "SELECT user_id FROM Users WHERE cas_username = ?",
                (netid,)
            ).fetchone()["user_id"]

        # Majors
        major = p.get("major")
        if major:
            mid = get_or_create(conn, "Majors", "name", major)
            conn.execute(
                "INSERT OR IGNORE INTO User_Majors (user_id, major_id) VALUES (?, ?)",
                (user_id, mid)
            )

    conn.commit()
    conn.close()
    print("Import complete.")

if __name__ == "__main__":
    main()
