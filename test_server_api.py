#!/usr/bin/env python3
"""
Exhaustive test suite for TDU2 Save File Toolkit Revision 2.
Tests all endpoints, profile editing, car swapping, car tuning, furniture unlock,
dedicated Backups/ creation, unpack/pack, and cryptographic verification.
"""

import sys
import time
import json
import shutil
import urllib.request
import urllib.error
import threading
from pathlib import Path

# Add revision2 directory to sys.path
TEST_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(TEST_DIR))

import tdu2_webgui as server_mod
import tdu2_save_tool as core

PORT = 8284

def run_tests():
    print("=" * 68)
    print("  RUNNING EXHAUSTIVE INTEGRATION TESTS (REVISION 2)")
    print("=" * 68)

    # Start server thread
    httpd = server_mod.HTTPServer(('127.0.0.1', PORT), server_mod.TDU2WebHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    base_url = f"http://127.0.0.1:{PORT}"

    # 1. Test Static Files
    for path in ['/', '/app.css', '/app.js']:
        req = urllib.request.urlopen(f"{base_url}{path}")
        assert req.status == 200
        assert len(req.read()) > 0
    print("[+] 1. Static Files (/ , /app.css , /app.js): OK")

    # 2. Test Profiles API
    req = urllib.request.urlopen(f"{base_url}/api/profiles")
    assert req.status == 200
    prof_data = json.loads(req.read().decode('utf-8'))
    assert prof_data["success"] is True
    assert len(prof_data["profiles"]) > 0
    print(f"[+] 2. Discovered Profiles: OK ({len(prof_data['profiles'])} profiles found)")

    # 3. Test Load Profile using sandbox copy
    sandbox_dir = TEST_DIR / "test_sandbox"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    test_save = sandbox_dir / "DATA"
    
    # Locate a source DATA file or decrypted template
    test_profile = "TestPlayer"
    source_dec = None
    for cand in [TEST_DIR / "data.dec", TEST_DIR.parent / "data.dec"]:
        if cand.is_file():
            source_dec = cand
            break

    if source_dec:
        dec_bytes = source_dec.read_bytes()
        enc_bytes = core.encrypt_save_file(dec_bytes, test_profile, "DATA")
        test_save.write_bytes(enc_bytes)
    else:
        source_save = None
        for cand in [TEST_DIR / "PLAYERSAVE" / "DATA", TEST_DIR.parent / "PLAYERSAVE" / "DATA"]:
            if cand.is_file():
                source_save = cand
                break
        if source_save:
            src_bytes = source_save.read_bytes()
            det_prof = core.detect_profile_name(source_save, src_bytes)
            pt, _, _ = core.decrypt_save_file(src_bytes, det_prof, "DATA")
            enc_bytes = core.encrypt_save_file(pt, test_profile, "DATA")
            test_save.write_bytes(enc_bytes)
        else:
            raise FileNotFoundError("No test save source found (data.dec or PLAYERSAVE/DATA).")

    load_payload = json.dumps({"path": str(test_save), "profile": test_profile}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/load", data=load_payload, headers={"Content-Type": "application/json"})
    load_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert load_res["success"] is True
    summary = load_res["summary"]
    assert summary["profile_name"] == test_profile
    assert summary["overall_level"] == 49, f"Expected level 49, got {summary['overall_level']}"
    assert summary["garage"]["count"] >= 1
    assert len(summary["garage"]["houses"]) >= 1
    print(f"[+] 3. Profile Loaded: OK (Profile: {summary['profile_name']}, Level {summary['overall_level']}, ${summary['money']:,}, {summary['garage']['count']} cars in {len(summary['garage']['houses'])} houses)")

    # 4. Test Direct Profile Editing (Tab 1)
    edit_payload = json.dumps({
        "money": 75000000,
        "casino_points": 3500000,
        "level": 73
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/edit-profile", data=edit_payload, headers={"Content-Type": "application/json"})
    edit_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert edit_res["success"] is True
    assert edit_res["summary"]["money"] == 75000000
    assert edit_res["summary"]["casino_points"] == 3500000
    assert edit_res["summary"]["overall_level"] == 73
    assert edit_res["backup_path"] is not None
    assert Path(edit_res["backup_path"]).is_file()
    print(f"[+] 4. Tab 1 - Direct Profile Editing: OK (Money: $75M, Casino: 3.5M, Lvl: 73; Backup: {Path(edit_res['backup_path']).name})")

    # 5. Test Furniture & Materials Unlock (Tab 1)
    furn_payload = b'{}'
    req = urllib.request.Request(f"{base_url}/api/unlock-furniture", data=furn_payload, headers={"Content-Type": "application/json"})
    furn_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert furn_res["success"] is True
    f_stat = furn_res["summary"]["furniture"]
    assert f_stat["unlocked_count"] == 383
    assert f_stat["materials_unlocked"] == 61
    assert f_stat["casino_vip_unlocked"] is True
    assert f_stat["is_max_unlocked"] is True
    assert Path(furn_res["backup_path"]).is_file()
    print(f"[+] 5. Tab 1 - Unlock All Furniture: OK (383 Items, 61 Materials, Casino VIP: Active; Backup: {Path(furn_res['backup_path']).name})")

    # 6. Test Cars Catalog (Tab 2)
    req = urllib.request.urlopen(f"{base_url}/api/cars-catalog")
    assert req.status == 200
    cat_res = json.loads(req.read().decode('utf-8'))
    assert cat_res["success"] is True
    assert cat_res["count"] == 359
    print(f"[+] 6. Tab 2 - Vehicle Catalog: OK ({cat_res['count']} vehicles available)")

    # 7. Test Car Model Swap (Tab 2)
    # Swap Slot 0 to Bugatti Veyron Sang Bleu (Arch #650)
    swap_payload = json.dumps({"slot": 0, "new_archetype": 650}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/swap-car-catalog", data=swap_payload, headers={"Content-Type": "application/json"})
    swap_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert swap_res["success"] is True
    assert swap_res["summary"]["garage"]["cars"][0]["archetype"] == 650
    assert "Bugatti" in swap_res["summary"]["garage"]["cars"][0]["brand"]
    assert Path(swap_res["backup_path"]).is_file()
    print(f"[+] 7. Tab 2 - Car Model Swap (Slot #1 -> Bugatti Sang Bleu): OK (Backup: {Path(swap_res['backup_path']).name})")

    # 8. Test Car Tuning (Tab 2)
    # Max Tune Slot 0 (Level 4 all)
    tune_payload = json.dumps({"slot": 0, "max_tune": True}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/tune-car", data=tune_payload, headers={"Content-Type": "application/json"})
    tune_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert tune_res["success"] is True
    upg0 = tune_res["summary"]["garage"]["cars"][0]["upgrades"]
    assert upg0["acceleration"] == 4 and upg0["top_speed"] == 4 and upg0["braking"] == 4
    assert Path(tune_res["backup_path"]).is_file()
    print(f"[+] 8. Tab 2 - Car Tuning (Slot #1 -> Max Lvl 4): OK (Backup: {Path(tune_res['backup_path']).name})")

    # Custom Tune Slot 1
    if len(tune_res["summary"]["garage"]["cars"]) > 1:
        tune_custom_payload = json.dumps({"slot": 1, "acceleration": 3, "top_speed": 2, "braking": 1}).encode('utf-8')
        req = urllib.request.Request(f"{base_url}/api/tune-car", data=tune_custom_payload, headers={"Content-Type": "application/json"})
        tc_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        assert tc_res["success"] is True
        upg1 = tc_res["summary"]["garage"]["cars"][1]["upgrades"]
        assert upg1["acceleration"] == 3 and upg1["top_speed"] == 2 and upg1["braking"] == 1
        print(f"[+] 8b. Tab 2 - Custom Tuning (Slot #2 -> Accel:3, Spd:2, Brk:1): OK")

    # 9. Test Manual Backup Creation (Tab 3)
    bak_payload = json.dumps({"label": "ManualTest"}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/create-backup", data=bak_payload, headers={"Content-Type": "application/json"})
    bak_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert bak_res["success"] is True
    assert Path(bak_res["backup_path"]).is_file()
    print(f"[+] 9. Tab 3 - Manual Backup Created: OK ({Path(bak_res['backup_path']).name})")

    # 10. Test Backups List API (Tab 3)
    req = urllib.request.urlopen(f"{base_url}/api/backups")
    assert req.status == 200
    blist_res = json.loads(req.read().decode('utf-8'))
    assert blist_res["success"] is True
    assert blist_res["count"] >= 4
    for b in blist_res["backups"]:
        assert Path(b["path"]).is_file()
    print(f"[+] 10. Tab 3 - Dedicated Backups Manager: OK ({blist_res['count']} backups registered)")

    # 11. Test Unpack & Pack (Tab 3)
    # Also place dummy or real KEYMAP/OPTIONS in test folder to test multi-file unpack
    km_data = core.encrypt_save_file(b'XMBF\x01\x00\x00\x00', test_profile, "KEYMAP")
    (sandbox_dir / "KEYMAP").write_bytes(km_data)

    req = urllib.request.Request(f"{base_url}/api/unpack", data=b'{}', headers={"Content-Type": "application/json"})
    unpack_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert unpack_res["success"] is True
    dec_dir = Path(unpack_res["decrypt_dir"])
    assert dec_dir.is_dir()
    assert (dec_dir / "DATA.json").is_file()
    assert (dec_dir / "DATA.dec").is_file()
    assert (dec_dir / "metadata.json").is_file()
    assert (dec_dir / "pack_save.bat").is_file()
    print(f"[+] 11. Tab 3 - Unpack Save to decrypt/: OK ({unpack_res['unpacked_count']} files unpacked in {dec_dir.name}/)")

    req = urllib.request.Request(f"{base_url}/api/pack", data=b'{}', headers={"Content-Type": "application/json"})
    pack_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert pack_res["success"] is True
    gr_dir = Path(pack_res["game_ready_dir"])
    assert gr_dir.is_dir()
    assert (gr_dir / "DATA").is_file()
    print(f"[+] 11b. Tab 3 - Pack from decrypt/ to Game-Ready: OK ({', '.join(pack_res['packed_files'])})")

    # 12. Test Backup Restoration (Tab 3)
    first_backup = blist_res["backups"][0]["path"]
    rest_payload = json.dumps({"backup_path": first_backup}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/restore-backup", data=rest_payload, headers={"Content-Type": "application/json"})
    rest_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert rest_res["success"] is True
    print(f"[+] 12. Tab 3 - Restore Backup: OK")

    # 13. Verify House Adding Endpoints Are Completely Removed
    try:
        req = urllib.request.Request(f"{base_url}/api/acquire-house", data=b'{}', headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req)
        assert False, "Endpoint /api/acquire-house should not exist!"
    except urllib.error.HTTPError as e:
        assert e.code == 404
    print("[+] 13. Verified Removal of House Adding API: 404 Not Found (Confirmed)")

    # 14. Cryptographic Validation with Core Engine
    enc_data = test_save.read_bytes()
    pt, footer, fn = core.decrypt_save_file(enc_data, test_profile, "DATA")
    root, final_dict = core.decode_xmbf_to_dict(pt)
    assert root == "PlayerData"
    print("[+] 14. Cryptographic DES-CBC & Eden-SHA1 Round-Trip: 100% VALID & VERIFIED")

    # Cleanup sandbox
    shutil.rmtree(sandbox_dir, ignore_errors=True)

    print("\n" + "=" * 68)
    print("  ALL REVISION 2 BACKEND & ARCHITECTURE TESTS PASSED 100%!")
    print("=" * 68 + "\n")

if __name__ == '__main__':
    run_tests()
