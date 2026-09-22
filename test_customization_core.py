import os
import sys
import json
from pathlib import Path
import tdu2_save_tool as core
import tdu2_webgui as webgui

def test_customization_pipeline():
    print("=== Testing Core Customization & Save Roundtrip ===")
    save_dir = Path(r"C:\Users\Ponker\Documents\Eden Games\Test Drive Unlimited 2\savegame")
    if not save_dir.exists():
        print(f"Save dir not found: {save_dir}")
        return False
        
    profiles = [p.name for p in save_dir.iterdir() if p.is_dir()]
    if not profiles:
        print("No save profiles found!")
        return False
        
    found = False
    for prof_name in profiles:
        save_path = save_dir / prof_name / "PLAYERSAVE" / "DATA"
        if not save_path.is_file():
            continue
        try:
            file_bytes = save_path.read_bytes()
            xmbf_bytes, footer, fname = core.decrypt_save_file(file_bytes, prof_name, save_path.name)
            root_name, data_obj = core.decode_xmbf_to_dict(xmbf_bytes)
            if root_name != "PlayerData":
                continue
            summary = webgui.extract_save_summary(data_obj, prof_name, save_path)
            cars = summary.get("garage", {}).get("cars", [])
            if cars:
                print(f"Profile '{prof_name}' has {len(cars)} garage vehicles.")
                found = True
                break
        except Exception as e:
            continue

    if not found:
        print("No profile with cars found!")
        return False
    
    # Find a vehicle with options
    target_idx = None
    target_car = None
    car_entry = None
    for c in cars:
        arch = str(c.get("archetype"))
        db_entry = webgui.CARS_DB.get(arch)
        if db_entry and db_entry.get("has_options") and db_entry.get("colors") and db_entry.get("rims"):
            target_idx = c["index"]
            target_car = c
            car_entry = db_entry
            break
            
    if target_idx is None:
        target_idx = 0
        target_car = cars[0]
        car_entry = webgui.CARS_DB.get(str(target_car.get("archetype")), {})
        
    print(f"Selected target vehicle for test:")
    print(f"  Slot #{target_idx + 1}: {target_car['name']} (Archetype #{target_car['archetype']})")
    print(f"  Initial Paint: {target_car['paint_indice']} ({target_car.get('color_name')})")
    print(f"  Initial Rims:  {target_car['rim_indice']} ({target_car.get('rim_name')})")
    print(f"  Initial Trim:  {target_car['interior_indice']} ({target_car.get('interior_name')})")
    
    # Choose new options from car_entry
    colors = car_entry.get("colors", [])
    rims = car_entry.get("rims", [])
    
    if colors:
        chosen_color = colors[-1]
        new_paint_idx = chosen_color["index"]
        interiors = chosen_color.get("interiors", [])
        new_int_idx = interiors[-1]["index"] if interiors else 0
    else:
        new_paint_idx = 0
        new_int_idx = 0
        
    if rims:
        new_rim_idx = rims[-1]["index"]
    else:
        new_rim_idx = 0
        
    print(f"Testing application of new options:")
    print(f"  Setting Paint Indice:    {new_paint_idx}")
    print(f"  Setting Rim Indice:      {new_rim_idx}")
    print(f"  Setting Interior Indice: {new_int_idx}")
    
    # Deep copy data_obj or work on clone to avoid mutating save file on disk
    import copy
    test_data_obj = copy.deepcopy(data_obj)
    
    mod_obj, msg = core.customize_garage_car(
        test_data_obj,
        target_idx,
        paint_idx=new_paint_idx,
        rim_idx=new_rim_idx,
        interior_idx=new_int_idx,
        cars_db=webgui.CARS_DB
    )
    print(f"customize_garage_car message: {msg}")
    
    # Verify in dictionary
    slot_car = (mod_obj.get("PlayerData") or mod_obj)["Garage"][target_idx]["Car"]
    assert slot_car["PaintIndice"] == new_paint_idx
    assert slot_car["RimIndice"] == new_rim_idx
    assert slot_car["InteriorIndice"] == new_int_idx
    assert slot_car["PaintType"] == 0, f"Expected PaintType 0, got {slot_car['PaintType']}"
    assert slot_car["HasSticker"] is False
    assert slot_car["DeluxeMainColorR"] == 0
    
    # Test encode to XMBF
    new_xmbf = core.encode_dict_to_xmbf(xmbf_bytes, {root_name: mod_obj}, root_name)
    print(f"Encoded back to XMBF, size: {len(new_xmbf)} bytes")
    
    # Test encrypt to save container
    enc_save = core.encrypt_save_file(new_xmbf, prof_name, save_path.name, footer)
    print(f"Encrypted save container size: {len(enc_save)} bytes")
    
    # Test decrypting the freshly encrypted save container
    dec_xmbf2, dec_footer2, dec_fname2 = core.decrypt_save_file(enc_save, prof_name, save_path.name)
    root_name2, dec_data2 = core.decode_xmbf_to_dict(dec_xmbf2)
    assert root_name2 == root_name
    
    # Extract summary from re-decrypted save
    summary2 = webgui.extract_save_summary(dec_data2, prof_name, save_path)
    car2 = summary2["garage"]["cars"][target_idx]
    print(f"Re-decrypted summary vehicle in Slot #{target_idx + 1}:")
    print(f"  Paint:    {car2['paint_indice']} ({car2.get('color_name')})")
    print(f"  Rims:     {car2['rim_indice']} ({car2.get('rim_name')})")
    print(f"  Interior: {car2['interior_indice']} ({car2.get('interior_name')})")
    
    assert car2['paint_indice'] == new_paint_idx
    assert car2['rim_indice'] == new_rim_idx
    assert car2['interior_indice'] == new_int_idx
    
    print("\nSUCCESS: All core round-trip, crypto, serialization, and summary checks passed!")
    return True

if __name__ == "__main__":
    if not test_customization_pipeline():
        sys.exit(1)
