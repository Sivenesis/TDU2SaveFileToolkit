import json
import urllib.request
import urllib.parse
import sys

BASE_URL = "http://127.0.0.1:8282"
SESSION_TOKEN = None

def get_token():
    global SESSION_TOKEN
    if not SESSION_TOKEN:
        req = urllib.request.Request(f"{BASE_URL}/")
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
            import re
            m = re.search(r'name="toolkit-token"\s+content="([^"]+)"', html)
            if m:
                SESSION_TOKEN = m.group(1)
            else:
                raise ValueError("Could not extract toolkit-token from index.html")
    return SESSION_TOKEN

def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post(path, payload):
    token = get_token()
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Toolkit-Token": token
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_web_api():
    print("=== Testing Web API Endpoints ===")
    
    # 1. Profiles
    profiles_data = get("/api/profiles")
    assert profiles_data.get("success"), "Failed to fetch profiles"
    profiles = profiles_data.get("profiles", [])
    print(f"1. /api/profiles returned {len(profiles)} profiles.")
    assert len(profiles) > 0, "No profiles found"
    
    # 2. Cars Catalog
    catalog_data = get("/api/cars-catalog")
    assert catalog_data.get("success"), "Failed to fetch cars catalog"
    catalog_cars = catalog_data.get("cars", [])
    print(f"2. /api/cars-catalog returned {len(catalog_cars)} catalog vehicles.")
    assert len(catalog_cars) >= 350, f"Expected >= 350 cars, got {len(catalog_cars)}"
    
    # Verify vehicle options in catalog
    cars_with_options = [c for c in catalog_cars if c.get("has_options")]
    print(f"   Vehicles with options: {len(cars_with_options)} / {len(catalog_cars)}")
    assert len(cars_with_options) > 150, "Expected > 150 vehicles with options"
    sample_car = next(c for c in cars_with_options if c.get("colors") and c.get("rims"))
    print(f"   Sample car: {sample_car['name']} (Arch #{sample_car['archetype']}) - {len(sample_car['colors'])} colors, {len(sample_car['rims'])} rims")
    
    # 3. Load Save
    target_prof = profiles[0]
    print(f"3. Loading profile '{target_prof['profile_name']}' from '{target_prof['id']}' via POST /api/load...")
    load_resp = post("/api/load", {"path": target_prof["id"]})
    assert load_resp.get("success"), f"Load failed: {load_resp}"
    summary = load_resp.get("summary", {})
    garage_cars = summary.get("garage", {}).get("cars", [])
    print(f"   Successfully loaded. Garage cars: {len(garage_cars)}")
    assert len(garage_cars) > 0, "No garage cars returned in summary"
    
    # Find a car to customize
    target_car = None
    for c in garage_cars:
        if not c.get("is_empty") and c.get("has_options"):
            target_car = c
            break
            
    if not target_car:
        target_car = garage_cars[0]
        
    print(f"4. Selected car for customization test: Slot #{target_car['slot'] + 1} ({target_car['name']})")
    print(f"   Current Specs: Paint={target_car['paint_indice']} ({target_car['color_name']}), Rim={target_car['rim_indice']} ({target_car['rim_name']}), Interior={target_car['interior_indice']} ({target_car['interior_name']})")
    
    # Find catalog entry for this car
    cat_entry = next((c for c in catalog_cars if c["archetype"] == target_car["archetype"]), None)
    assert cat_entry, f"Catalog entry not found for archetype {target_car['archetype']}"
    
    orig_paint = target_car["paint_indice"]
    orig_rim = target_car["rim_indice"]
    orig_int = target_car["interior_indice"]
    
    # Choose different options
    new_paint = (orig_paint + 1) % len(cat_entry["colors"]) if cat_entry.get("colors") else orig_paint
    new_rim = (orig_rim + 1) % len(cat_entry["rims"]) if cat_entry.get("rims") else orig_rim
    chosen_color_entry = cat_entry["colors"][new_paint] if cat_entry.get("colors") else None
    interiors = chosen_color_entry.get("interiors", []) if chosen_color_entry else []
    new_int = interiors[0]["index"] if interiors else 0
    
    print(f"   Requesting customization: paint_indice={new_paint}, rim_indice={new_rim}, interior_indice={new_int}...")
    cust_resp = post("/api/customize-car", {
        "slot": target_car["slot"],
        "paint_indice": new_paint,
        "rim_indice": new_rim,
        "interior_indice": new_int
    })
    
    assert cust_resp.get("success"), f"Customization API failed: {cust_resp}"
    print(f"   API Response message: {cust_resp.get('message')}")
    print(f"   Backup created at: {cust_resp.get('backup_path')}")
    
    updated_summary = cust_resp.get("summary", {})
    updated_car = updated_summary.get("garage", {}).get("cars", [])[target_car["slot"]]
    print(f"   Updated Specs: Paint={updated_car['paint_indice']} ({updated_car['color_name']}), Rim={updated_car['rim_indice']} ({updated_car['rim_name']}), Interior={updated_car['interior_indice']} ({updated_car['interior_name']})")
    
    assert updated_car["paint_indice"] == new_paint
    assert updated_car["rim_indice"] == new_rim
    assert updated_car["interior_indice"] == new_int
    
    # 5. Revert back to original options
    print(f"5. Reverting customization back to original options (paint={orig_paint}, rim={orig_rim}, int={orig_int})...")
    revert_resp = post("/api/customize-car", {
        "slot": target_car["slot"],
        "paint_indice": orig_paint,
        "rim_indice": orig_rim,
        "interior_indice": orig_int
    })
    assert revert_resp.get("success"), f"Revert failed: {revert_resp}"
    reverted_car = revert_resp.get("summary", {}).get("garage", {}).get("cars", [])[target_car["slot"]]
    assert reverted_car["paint_indice"] == orig_paint
    print("   Successfully reverted to original specification.")
    
    print("\nSUCCESS: All Web API endpoints and customization workflows verified!")
    return True

if __name__ == "__main__":
    if not test_web_api():
        sys.exit(1)
