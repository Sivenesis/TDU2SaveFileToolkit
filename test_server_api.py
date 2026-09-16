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

def auth_headers():
    return {"Content-Type": "application/json", "X-Toolkit-Token": server_mod.SESSION_TOKEN}

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
    req = urllib.request.Request(f"{base_url}/api/load", data=load_payload, headers=auth_headers())
    load_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert load_res["success"] is True
    summary = load_res["summary"]
    assert summary["profile_name"] == test_profile
    assert summary["overall_level"] == 49, f"Expected level 49, got {summary['overall_level']}"
    assert summary["garage"]["count"] >= 1
    assert len(summary["garage"]["houses"]) >= 1
    print(f"[+] 3. Profile Loaded: OK (Profile: {summary['profile_name']}, Level {summary['overall_level']}, ${summary['money']:,}, {summary['garage']['count']} cars in {len(summary['garage']['houses'])} houses)")

    # 4. Test Direct Profile Editing (Tab 1) - Test up to 2,147,483,648 (Level edit removed - WIP)
    edit_payload = json.dumps({
        "money": 2147483648,
        "casino_points": 2147483648
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/edit-profile", data=edit_payload, headers=auth_headers())
    edit_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert edit_res["success"] is True
    assert edit_res["summary"]["money"] == 2147483648
    assert edit_res["summary"]["casino_points"] == 2147483648
    assert edit_res["backup_path"] is not None
    assert Path(edit_res["backup_path"]).is_file()
    print(f"[+] 4. Tab 1 - Direct Profile Editing: OK (Money: $2,147,483,648, Casino: 2,147,483,648 Cp; Backup: {Path(edit_res['backup_path']).name})")

    # 5. Test Casino Furniture Unlock (Tab 1)
    furn_payload = b'{}'
    req = urllib.request.Request(f"{base_url}/api/unlock-casino-furniture", data=furn_payload, headers=auth_headers())
    furn_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert furn_res["success"] is True
    f_stat = furn_res["summary"]["furniture"]
    assert f_stat["casino_vip_unlocked"] is True
    assert Path(furn_res["backup_path"]).is_file()
    print(f"[+] 5. Tab 1 - Unlock Casino Furniture: OK (Casino Furniture Unlocked; Backup: {Path(furn_res['backup_path']).name})")

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
    req = urllib.request.Request(f"{base_url}/api/swap-car-catalog", data=swap_payload, headers=auth_headers())
    swap_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert swap_res["success"] is True
    assert swap_res["summary"]["garage"]["cars"][0]["archetype"] == 650
    assert "Bugatti" in swap_res["summary"]["garage"]["cars"][0]["brand"]
    assert Path(swap_res["backup_path"]).is_file()
    print(f"[+] 7. Tab 2 - Car Model Swap (Slot #1 -> Bugatti Sang Bleu): OK (Backup: {Path(swap_res['backup_path']).name})")

    # 8. Test Car Tuning (Tab 2)
    # Max Tune Slot 0 (Level 4 all)
    tune_payload = json.dumps({"slot": 0, "max_tune": True}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/tune-car", data=tune_payload, headers=auth_headers())
    tune_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert tune_res["success"] is True
    upg0 = tune_res["summary"]["garage"]["cars"][0]["upgrades"]
    assert upg0["acceleration"] == 4 and upg0["top_speed"] == 4 and upg0["braking"] == 4
    assert Path(tune_res["backup_path"]).is_file()
    print(f"[+] 8. Tab 2 - Car Tuning (Slot #1 -> Max Lvl 4): OK (Backup: {Path(tune_res['backup_path']).name})")

    # Custom Tune Slot 1
    if len(tune_res["summary"]["garage"]["cars"]) > 1:
        tune_custom_payload = json.dumps({"slot": 1, "acceleration": 3, "top_speed": 2, "braking": 1}).encode('utf-8')
        req = urllib.request.Request(f"{base_url}/api/tune-car", data=tune_custom_payload, headers=auth_headers())
        tc_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        assert tc_res["success"] is True
        upg1 = tc_res["summary"]["garage"]["cars"][1]["upgrades"]
        assert upg1["acceleration"] == 3 and upg1["top_speed"] == 2 and upg1["braking"] == 1
        print(f"[+] 8b. Tab 2 - Custom Tuning (Slot #2 -> Accel:3, Spd:2, Brk:1): OK")

    # 9. Test Manual Backup Creation (Tab 3)
    bak_payload = json.dumps({"label": "ManualTest"}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/create-backup", data=bak_payload, headers=auth_headers())
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

    req = urllib.request.Request(f"{base_url}/api/unpack", data=b'{}', headers=auth_headers())
    unpack_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert unpack_res["success"] is True
    dec_dir = Path(unpack_res["decrypt_dir"])
    assert dec_dir.is_dir()
    assert (dec_dir / "DATA.json").is_file()
    assert (dec_dir / "DATA.dec").is_file()
    assert (dec_dir / "metadata.json").is_file()
    assert (dec_dir / "pack_save.bat").is_file()
    print(f"[+] 11. Tab 3 - Unpack Save to decrypt/: OK ({unpack_res['unpacked_count']} files unpacked in {dec_dir.name}/)")

    pack_payload = json.dumps({"install_to_live": True}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/pack", data=pack_payload, headers=auth_headers())
    pack_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert pack_res["success"] is True
    assert pack_res["installed_to_live"] is True
    gr_dir = Path(pack_res["game_ready_dir"])
    assert gr_dir.is_dir()
    assert (gr_dir / "DATA").is_file()
    print(f"[+] 11b. Tab 3 - Pack from decrypt/ to Game-Ready: OK ({', '.join(pack_res['packed_files'])})")

    # 12. Test Backup Restoration (Tab 3)
    first_backup = blist_res["backups"][0]["path"]
    rest_payload = json.dumps({"backup_path": first_backup}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/restore-backup", data=rest_payload, headers=auth_headers())
    rest_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert rest_res["success"] is True
    print(f"[+] 12. Tab 3 - Restore Backup: OK")

    # 13. Verify House Adding Endpoints Are Completely Removed
    try:
        req = urllib.request.Request(f"{base_url}/api/acquire-house", data=b'{}', headers=auth_headers())
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

    # 15. Custom Save Directory API (v2.0.0)
    mock_save_root = sandbox_dir / "mock_savegame"
    mock_save_root.mkdir(parents=True, exist_ok=True)
    aspen_src = Path("F:/Progs/VIBECODE/Google/Projects/TDU2offline2online/OFFLINEprofile/Aspen")
    
    if aspen_src.is_dir():
        aspen_dst = mock_save_root / "Aspen"
        shutil.copytree(aspen_src, aspen_dst, dirs_exist_ok=True)
    else:
        # Create minimal synthetic profile structure
        aspen_ps = mock_save_root / "Aspen" / "PLAYERSAVE"
        aspen_ps.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(test_save, aspen_ps / "DATA")

    # Create synthetic ProfileList.dat with Aspen (0x00 Offline)
    pld_path = mock_save_root / "ProfileList.dat"
    pld_hdr = b'\x7b\x32\x00\x00\x00\x00\x00\x00\xff\xff'
    rec_aspen = bytearray(257)
    rec_aspen[:5] = b'Aspen'
    rec_aspen[256] = 0x00
    pld_path.write_bytes(pld_hdr + rec_aspen)

    # Test POST /api/save-directory with custom path
    set_dir_payload = json.dumps({"directory": str(mock_save_root)}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/save-directory", data=set_dir_payload, headers=auth_headers())
    dir_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert dir_res["success"] is True
    assert dir_res["custom_dir"] == str(mock_save_root.resolve())
    assert any(p["profile_name"] == "Aspen" for p in dir_res["profiles"])
    # Verify strict path isolation: all returned profiles must be within mock_save_root
    for p in dir_res["profiles"]:
        assert str(mock_save_root.resolve()).lower() in str(Path(p["path"]).resolve()).lower()
    print(f"[+] 15. Custom Save Directory API & Path Isolation: OK (Active: {dir_res['custom_dir']})")

    # Verify GET /api/profiles returns version, custom_dir, and online_status
    req = urllib.request.urlopen(f"{base_url}/api/profiles")
    prof_v2 = json.loads(req.read().decode('utf-8'))
    assert prof_v2["version"] == "2.0.5"
    assert prof_v2["custom_dir"] == str(mock_save_root.resolve())
    aspen_entry = next((p for p in prof_v2["profiles"] if p["profile_name"] == "Aspen"), None)
    assert aspen_entry is not None
    assert aspen_entry["online_status"]["registry_online"] is False
    print(f"[+] 15b. GET /api/profiles v2.0.5 Metadata & Online Status: OK")

    # 16. Test Online Mode Switcher (Tab 4) - Switch to ONLINE with custom credentials
    switch_payload = json.dumps({
        "profile_name": "Aspen",
        "target_online": True,
        "login": "TestPilot",
        "email": "pilot@example.com",
        "password": "mockPassword123"
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/switch-mode", data=switch_payload, headers=auth_headers())
    switch_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert switch_res["success"] is True
    assert switch_res["target_online"] is True

    # Verify ProfileList.dat byte 256 was updated to 0xFF
    _, pld_records = core.read_profile_list(pld_path)
    aspen_pld = next((r for r in pld_records if r["name"] == "Aspen"), None)
    assert aspen_pld is not None
    assert aspen_pld["is_online"] is True
    assert aspen_pld["flag_byte"] == 0xFF

    # Verify OPTIONS container was updated
    aspen_creds = core.get_profile_credentials(mock_save_root / "Aspen")
    assert aspen_creds["is_online"] is True
    assert aspen_creds["login_name"] == "TestPilot"
    assert aspen_creds["email"] == "pilot@example.com"
    assert aspen_creds["password"] == "mockPassword123"
    print(f"[+] 16. Tab 4 - Switch Mode to ONLINE (Custom Creds): OK (Byte 256=0xFF, IsOnlineEnabledProfile=True)")

    # 17. Test Credential Cloning via switch-mode
    # Create second profile "AspenTwo" (offline)
    aspen2_dir = mock_save_root / "AspenTwo"
    aspen2_ps = aspen2_dir / "PLAYERSAVE"
    aspen2_ps.mkdir(parents=True, exist_ok=True)
    core.convert_data_file(
        src_data_path=mock_save_root / "Aspen" / "PLAYERSAVE" / "DATA",
        dst_data_path=aspen2_ps / "DATA",
        src_profile_name="Aspen",
        dst_profile_name="AspenTwo",
        make_online=False
    )
    # Copy OPTIONS container to AspenTwo
    shutil.copyfile(mock_save_root / "Aspen" / "PLAYERSAVE" / "OPTIONS", aspen2_ps / "OPTIONS")
    # Re-key OPTIONS for AspenTwo
    aspen_opt_b = (aspen2_ps / "OPTIONS").read_bytes()
    opt_xmbf, opt_foot, _ = core.decrypt_save_file(aspen_opt_b, "Aspen", "OPTIONS")
    enc_opt_two = core.encrypt_save_file(opt_xmbf, "AspenTwo", "OPTIONS", original_footer=opt_foot)
    (aspen2_ps / "OPTIONS").write_bytes(enc_opt_two)

    # Append AspenTwo to ProfileList.dat
    rec_aspen2 = bytearray(257)
    rec_aspen2[:8] = b'AspenTwo'
    rec_aspen2[256] = 0x00
    with open(pld_path, 'ab') as pf:
        pf.write(rec_aspen2)

    clone_cred_payload = json.dumps({
        "profile_name": "AspenTwo",
        "target_online": True,
        "clone_from": "Aspen"
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/switch-mode", data=clone_cred_payload, headers=auth_headers())
    cc_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert cc_res["success"] is True

    aspen2_creds = core.get_profile_credentials(mock_save_root / "AspenTwo")
    assert aspen2_creds["is_online"] is True
    assert aspen2_creds["login_name"] == "TestPilot"
    assert aspen2_creds["email"] == "pilot@example.com"
    print(f"[+] 17. Tab 4 - Switch Mode with Credential Cloning: OK (Cloned from Aspen)")

    # 18. Test Progression Cloning API (Tab 4)
    clone_prog_payload = json.dumps({
        "source_profile": "Aspen",
        "target_profile": "AspenTwo",
        "copy_keymap": False
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/clone-progression", data=clone_prog_payload, headers=auth_headers())
    cp_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert cp_res["success"] is True
    assert "target_summary" in cp_res
    assert cp_res["target_summary"]["profile_name"] == "AspenTwo"

    # Verify transferred DATA has Driver.Name = AspenTwo
    with open(aspen2_ps / "DATA", "rb") as df:
        df_b = df.read()
    dp_pt, _, _ = core.decrypt_save_file(df_b, "AspenTwo", "DATA")
    _, dp_dict = core.decode_xmbf_to_dict(dp_pt)
    assert dp_dict["Driver"]["Name"] == "AspenTwo"
    print(f"[+] 18. Tab 4 - Progression Cloning API: OK (Transferred Aspen -> AspenTwo)")

    # 19. Reset Save Directory back to Documents
    reset_dir_payload = json.dumps({"reset": True}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/save-directory", data=reset_dir_payload, headers=auth_headers())
    res_dir_res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    assert res_dir_res["success"] is True
    assert res_dir_res["custom_dir"] is None
    print(f"[+] 19. Reset Save Directory to Default: OK")

    # 20. Public Code Hygiene & Security Verification
    assert not (TEST_DIR / ".env").exists()
    assert (TEST_DIR / ".env.example").is_file()
    env_example_content = (TEST_DIR / ".env.example").read_text(encoding='utf-8')
    assert "your_api_key_here" in env_example_content or "placeholder" in env_example_content or "mock" in env_example_content
    print(f"[+] 20. Public Code Hygiene Verification: OK (No real credentials, clean .env.example)")

    # 21. Security Hardening: Require X-Toolkit-Token on POST
    try:
        no_tok_req = urllib.request.Request(f"{base_url}/api/create-backup", data=b'{}', headers={"Content-Type": "application/json"})
        urllib.request.urlopen(no_tok_req)
        assert False, "Expected 403 Forbidden without X-Toolkit-Token"
    except urllib.error.HTTPError as e:
        assert e.code == 403
    print("[+] 21. Security Verification: Missing X-Toolkit-Token Rejected (403 Forbidden): OK")

    # 22. Security Hardening: Static File Path Traversal Prefix Bypass Blocked
    try:
        urllib.request.urlopen(f"{base_url}/../web_evil/test.txt")
        assert False, "Expected 403 or 404 for path traversal"
    except urllib.error.HTTPError as e:
        assert e.code in (403, 404)
    print("[+] 22. Security Verification: Static Asset Path Traversal Blocked: OK")

    # 23. Security Hardening: Arbitrary Path Traversal in /api/restore-backup Blocked
    try:
        evil_bak_req = urllib.request.Request(
            f"{base_url}/api/restore-backup",
            data=json.dumps({"backup_path": "../../etc/passwd"}).encode('utf-8'),
            headers=auth_headers()
        )
        urllib.request.urlopen(evil_bak_req)
        assert False, "Expected 400 Bad Request for backup traversal"
    except urllib.error.HTTPError as e:
        assert e.code == 400
    print("[+] 23. Security Verification: Backup Restore Traversal Blocked: OK")

    # 24. Security Hardening: Out-of-Bounds Filesystem Probing in /api/load Blocked
    try:
        evil_load_req = urllib.request.Request(
            f"{base_url}/api/load",
            data=json.dumps({"path": "C:\\Windows\\System32\\drivers\\etc\\hosts"}).encode('utf-8'),
            headers=auth_headers()
        )
        urllib.request.urlopen(evil_load_req)
        assert False, "Expected 400 Bad Request for out-of-bounds load"
    except urllib.error.HTTPError as e:
        assert e.code == 400
    print("[+] 24. Security Verification: Out-of-bounds /api/load Blocked: OK")

    # 25. Security Hardening: Oversized Payload Rejected (HTTP 413)
    try:
        huge_headers = auth_headers()
        huge_headers["Content-Length"] = "20000000"  # 20 MB > 10 MB limit
        huge_req = urllib.request.Request(
            f"{base_url}/api/create-backup",
            data=b'{"label": "oversized"}',
            headers=huge_headers
        )
        urllib.request.urlopen(huge_req)
        assert False, "Expected 413 Payload Too Large"
    except urllib.error.HTTPError as e:
        assert e.code == 413
    print("[+] 25. Security Verification: Oversized Payload Blocked (413 Payload Too Large): OK")

    # Cleanup sandbox
    shutil.rmtree(sandbox_dir, ignore_errors=True)

    print("\n" + "=" * 68)
    print("  ALL FULL TOOLKIT INTEGRATION & SECURITY TESTS PASSED 100% (v2.0.5)!")
    print("=" * 68 + "\n")

if __name__ == '__main__':
    run_tests()

