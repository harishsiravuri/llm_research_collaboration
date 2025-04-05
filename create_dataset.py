import requests
import time
import json
from tqdm import tqdm

# Optional: add your email to help OpenAlex track usage
HEADERS = {
    "User-Agent": "Illinois-Research-Collector/0.1 (mailto:EMAIL@gmail.com)"
}

BASE_URL = "https://api.openalex.org"

def get_illinois_institutions():
    """Fetch institutions with 'Illinois' in the name."""
    institutions = []
    cursor = "*"
    while True:
        url = f"{BASE_URL}/institutions?filter=display_name.search:Illinois&per-page=200&cursor={cursor}"
        r = requests.get(url, headers=HEADERS).json()
        institutions.extend(r["results"])
        if "meta" in r and r["meta"]["next_cursor"]:
            cursor = r["meta"]["next_cursor"]
        else:
            break
        time.sleep(1)  # avoid hitting rate limits
    return institutions


# Fetch open access works for a given institution ID
# Note: This function is limited to 50 works per institution as there is 50 per page.

def get_works_for_institution(institution_id, max_works=50):
    """Fetch open access works for a given institution ID."""
    works = []
    cursor = "*"
    fetched = 0
    while fetched < max_works:
        url = f"{BASE_URL}/works?filter=authorships.institutions.id:{institution_id},open_access.is_oa:true&per-page=50&cursor={cursor}"
        r = requests.get(url, headers=HEADERS).json()
        for work in r["results"]:
            works.append({
                "title": work.get("title"),
                "abstract": work.get("abstract_inverted_index"),
                "authors": [auth["author"]["display_name"] for auth in work.get("authorships", [])],
                "institution": institution_id
            })
        fetched += len(r["results"])
        if "meta" in r and r["meta"]["next_cursor"]:
            cursor = r["meta"]["next_cursor"]
        else:
            break
        time.sleep(1)
    return works

def main():
    all_works = []
    illinois_institutions = get_illinois_institutions()
    print(f"Found {len(illinois_institutions)} institutions in Illinois.")
    
    for inst in tqdm(illinois_institutions, desc="Collecting works"):
        works = get_works_for_institution(inst["id"])
        for w in works:
            w["institution_name"] = inst["display_name"]
        all_works.extend(works)

    # Save to JSON file
    with open("illinois_open_research.json", "w") as f:
        json.dump(all_works, f, indent=2)

    print(f"Saved {len(all_works)} open-access works.")

if __name__ == "__main__":
    main()
