#!/usr/bin/env python3
"""
Test Drive Unlimited 2 (TDU2) Save Game Tool - Streamlined WebGUI Backend Server
Provides a zero-dependency local HTTP server and REST API for tdu2_save_tool.py.
Completely sanitized: no personal paths, no hardcoded user credentials, no native dependencies.
"""

import os
import sys
import json
import zlib
import struct
import shutil
import datetime
import mimetypes
import webbrowser
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import secrets

# Import the core TDU2 save engine from local directory
import tdu2_save_tool as core

TOOLKIT_VERSION = "2.0.5"
PORT = 8282
SESSION_TOKEN = secrets.token_hex(16)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB payload limit

WORKSPACE_DIR = Path(__file__).parent.resolve()
WEB_DIR = WORKSPACE_DIR / 'web'
BACKUPS_DIR = WORKSPACE_DIR / 'Backups'
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
DECRYPT_DIR = WORKSPACE_DIR / 'decrypt'
DECRYPT_DIR.mkdir(parents=True, exist_ok=True)

# Custom savegame root or profile directory (configured at runtime or via API/CLI)
CUSTOM_SAVEGAME_DIR = None

# Global in-memory cache of currently loaded save state
loaded_save_state = {
    "source_path": None,
    "profile_name": None,
    "footer": None,
    "target_filename": "DATA",
    "raw_xmbf": None,
    "root_name": None,
    "data_dict": None,
    "is_live_documents": False,
    "last_backup_path": None
}

# Load TDU2 Vehicle Database (359 vehicles reverse-engineered from game archives)
CARS_DATABASE_PATH = WORKSPACE_DIR / 'cars_database.json'
CARS_DB = {}
if CARS_DATABASE_PATH.is_file():
    try:
        with open(CARS_DATABASE_PATH, 'r', encoding='utf-8') as f:
            CARS_DB = json.load(f)
    except Exception as e:
        print(f"[!] Warning loading cars_database.json: {e}")

# Load TDU2 Houses Database (61 authentic player houses: 19 Ibiza, 42 Hawaii)
HOUSES_DATABASE_PATH = WORKSPACE_DIR / 'houses_database.json'
HOUSES_DB = {}
KNOWN_HOUSE_HCS = {}
if HOUSES_DATABASE_PATH.is_file():
    try:
        with open(HOUSES_DATABASE_PATH, 'r', encoding='utf-8') as f:
            HOUSES_DB = json.load(f)
            KNOWN_HOUSE_HCS = {int(k): v for k, v in HOUSES_DB.get('known_hcs', {}).items()}
    except Exception as e:
        print(f"[!] Warning loading houses_database.json: {e}")


def resolve_house_info(house_hc: int, slot_count: int = 0) -> dict:
    """
    Resolves a 64-bit HouseHC into authentic house name, island, level, and capacity.
    """
    if house_hc in KNOWN_HOUSE_HCS:
        info = dict(KNOWN_HOUSE_HCS[house_hc])
        info['house_id'] = str(house_hc)
        info['house_hc'] = str(house_hc)
        info['house_hex'] = f"0x{house_hc:016X}"
        info['display_name'] = f"{info['island']} - {info['name']}"
        return info

    # Fallback resolution using byte analysis
    try:
        raw = struct.pack(">Q", house_hc)
        be_chars = "".join([chr(b) if 32 <= b < 127 else "" for b in raw[:4]])
        if b'L' in raw[:4] or 'L' in be_chars:
            island = "Hawaii"
        elif raw[0] in [0x49, 0x32] or 'IB' in be_chars or 'ID' in be_chars:
            island = "Ibiza"
        elif raw[0] == 0x5F and (raw[3] == 0x95 or raw[1] in [ord('C'), ord('E'), ord('D')]):
            island = "Ibiza"
        else:
            island = "Hawaii"
    except Exception:
        island = "Hawaii"

    slots = slot_count if slot_count in [2, 4, 6, 8] else 4
    level = 4 if slots == 8 else (3 if slots == 6 else (1 if slots == 2 else 2))
    name = f"{island} Residence ({slots}-Car Garage)"
    return {
        "house_id": str(house_hc),
        "house_hc": str(house_hc),
        "house_hex": f"0x{house_hc:016X}",
        "name": name,
        "display_name": name,
        "island": island,
        "level": level,
        "slots": slots,
        "spot": "Owned House"
    }


def create_operation_backup(source_path: Path, profile_name: str, operation: str = "Edit") -> Path:
    """
    Creates an organized, timestamped backup in the dedicated Backups/<Profile>/ directory.
    Pattern: <Profile>_DATA_<Operation>_<YYYYMMDD_HHMMSS>.bak
    """
    source_p = Path(source_path)
    if not source_p.is_file():
        return None

    prof = profile_name or "Player"
    prof_backup_dir = BACKUPS_DIR / prof
    prof_backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    op_clean = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in operation)
    backup_filename = f"{prof}_DATA_{op_clean}_{timestamp}.bak"
    backup_path = prof_backup_dir / backup_filename

    shutil.copy2(source_p, backup_path)
    # Also create a quick .bak in save folder for legacy compatibility
    try:
        shutil.copy2(source_p, source_p.with_suffix('.bak'))
    except Exception:
        pass

    loaded_save_state["last_backup_path"] = str(backup_path)
    return backup_path


def get_profile_backups_list(profile_name: str) -> list:
    """
    Returns a sorted list of backups for the specified profile from the Backups/<Profile> folder.
    """
    if not profile_name:
        return []

    prof_dir = BACKUPS_DIR / profile_name
    backups = []
    if prof_dir.is_dir():
        for b_file in prof_dir.glob("*.bak"):
            stat = b_file.stat()
            # Extract operation from filename: <Profile>_DATA_<Operation>_<Timestamp>.bak
            parts = b_file.stem.split('_')
            operation = "Backup"
            if len(parts) >= 4 and parts[1] == 'DATA':
                operation = "_".join(parts[2:-2]) if len(parts) > 4 else parts[2]
            
            backups.append({
                "filename": b_file.name,
                "operation": operation,
                "path": str(b_file.resolve()),
                "size": stat.st_size,
                "size_formatted": f"{round(stat.st_size / 1024, 1)} KB",
                "timestamp": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "mtime": stat.st_mtime
            })

    # Sort descending by modification time (newest first)
    backups.sort(key=lambda x: x["mtime"], reverse=True)
    return backups


def find_all_tdu2_profiles():
    """
    Scans Documents, custom paths, and local workspace for all valid TDU2 profile directories.
    Extracts online mode flags (from ProfileList.dat & OPTIONS) and saved account credentials.
    """
    profiles = []
    seen_paths = set()

    def add_candidate(folder_path, source_type, is_live=False):
        resolved = Path(folder_path).resolve()
        if resolved in seen_paths or not resolved.is_dir():
            return

        ps_dir = resolved if resolved.name.upper() == 'PLAYERSAVE' else (resolved / 'PLAYERSAVE')
        if not ps_dir.is_dir():
            has_saves = any((resolved / name).is_file() for name in ['DATA', 'KEYMAP', 'OPTIONS', 'DATA.json'])
            if not has_saves:
                return
            ps_dir = resolved

        seen_paths.add(resolved)
        data_file = ps_dir / 'DATA'
        data_json = ps_dir / 'DATA.json'
        opt_file = ps_dir / 'OPTIONS'
        km_file = ps_dir / 'KEYMAP'
        bak_file = ps_dir / 'DATA.bak'

        prof_name = None
        driver_name = None
        money = None
        last_mod = None

        if data_file.is_file():
            last_mod = datetime.datetime.fromtimestamp(data_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            try:
                with open(data_file, 'rb') as f:
                    file_bytes = f.read(512)
                prof_name = core.detect_profile_name(data_file, file_bytes)
            except Exception:
                pass

        if not prof_name:
            if ps_dir.name.upper() == 'PLAYERSAVE':
                prof_name = ps_dir.parent.name
            else:
                prof_name = ps_dir.name

        if data_json.is_file():
            try:
                with open(data_json, 'r', encoding='utf-8') as f:
                    dj = json.load(f)
                driver = dj.get('PlayerData', {}).get('Driver', {})
                driver_name = driver.get('Name')
                money = driver.get('Money')
            except Exception:
                pass

        # Online mode status analysis
        opt_is_online = None
        has_creds = False
        email_val = ""
        login_val = ""
        if opt_file.is_file():
            try:
                creds_info = core.get_profile_credentials(ps_dir, savegame_root=ps_dir.parent)
                opt_is_online = creds_info.get('is_online')
                login_val = creds_info.get('login_name', '') or ''
                email_val = creds_info.get('email', '') or ''
                pwd_val = creds_info.get('password', '') or ''
                has_creds = bool(email_val or pwd_val)
            except Exception:
                try:
                    with open(opt_file, 'rb') as of:
                        opt_b = of.read()
                    ox, _, _ = core.decrypt_save_file(opt_b, prof_name, 'OPTIONS')
                    _, o_dict = core.decode_xmbf_to_dict(ox)
                    opt_is_online = o_dict.get('IsOnlineEnabledProfile')
                    login_val = o_dict.get('LoginName', '') or ''
                    email_val = o_dict.get('Email', '') or ''
                    pwd_val = o_dict.get('Password', '') or ''
                    has_creds = bool(email_val or pwd_val)
                except Exception:
                    pass

        # Check ProfileList.dat in parent directories or known savegame root
        reg_is_online = None
        candidate_roots = [resolved, resolved.parent, resolved.parent.parent, ps_dir.parent, ps_dir.parent.parent]
        if CUSTOM_SAVEGAME_DIR:
            candidate_roots.extend([CUSTOM_SAVEGAME_DIR, CUSTOM_SAVEGAME_DIR.parent])
        else:
            def_root = core.find_default_savegame_dir()
            if def_root:
                candidate_roots.extend([def_root, def_root.parent])

        name_candidates = set()
        if prof_name:
            name_candidates.add(prof_name.lower())
        if resolved.name.upper() not in ['PLAYERSAVE', 'SAVEGAME']:
            name_candidates.add(resolved.name.lower())
        if resolved.parent and resolved.parent.name.upper() not in ['SAVEGAME', 'DOCUMENTS']:
            name_candidates.add(resolved.parent.name.lower())
        if ps_dir.parent and ps_dir.parent.name.upper() not in ['SAVEGAME', 'DOCUMENTS']:
            name_candidates.add(ps_dir.parent.name.lower())

        for cand_root in candidate_roots:
            if cand_root and cand_root.is_dir():
                pl_cand = cand_root / 'ProfileList.dat'
                if pl_cand.is_file():
                    try:
                        _, reg_recs = core.read_profile_list(pl_cand)
                        for r in reg_recs:
                            if r.get('name') and r['name'].lower() in name_candidates:
                                reg_is_online = r['is_online']
                                break
                    except Exception:
                        pass
            if reg_is_online is not None:
                break

        is_online = reg_is_online if reg_is_online is not None else (opt_is_online if opt_is_online is not None else False)
        mode_tag = "Online" if is_online else "Offline"

        display_label = f"{prof_name or resolved.name} [{mode_tag}]"

        online_status_obj = {
            "is_online": bool(is_online),
            "mode_label": "ONLINE" if is_online else "OFFLINE",
            "registry_online": reg_is_online,
            "options_online": opt_is_online,
            "has_credentials": has_creds,
            "login_name": login_val or prof_name or "Player",
            "email": email_val
        }

        profiles.append({
            "id": str(resolved),
            "display_name": display_label,
            "profile_name": prof_name or "Player",
            "driver_name": driver_name or prof_name or "Player",
            "money": money,
            "source": source_type,
            "is_live": is_live,
            "is_online": bool(is_online),
            "online_status": online_status_obj,
            "reg_flag": "0xFF (Online)" if reg_is_online else ("0x00 (Offline)" if reg_is_online is not None else "Not Registered"),
            "options_flag": bool(opt_is_online) if opt_is_online is not None else "Unknown",
            "has_credentials": has_creds,
            "email": email_val,
            "login_name": login_val or prof_name or "Player",
            "path": str(ps_dir),
            "data_path": str(data_file) if data_file.is_file() else None,
            "has_data": data_file.is_file(),
            "has_options": opt_file.is_file(),
            "has_keymap": km_file.is_file(),
            "has_backup": bak_file.is_file(),
            "last_modified": last_mod
        })


    # Strictly scan ONLY the current active save path:
    if CUSTOM_SAVEGAME_DIR and CUSTOM_SAVEGAME_DIR.exists():
        # Active path is CUSTOM_SAVEGAME_DIR: scan exclusively from this custom location
        try:
            if CUSTOM_SAVEGAME_DIR.is_file():
                add_candidate(CUSTOM_SAVEGAME_DIR.parent, "Custom Path", is_live=False)
            elif (CUSTOM_SAVEGAME_DIR / 'DATA').is_file() or (CUSTOM_SAVEGAME_DIR / 'PLAYERSAVE' / 'DATA').is_file():
                add_candidate(CUSTOM_SAVEGAME_DIR, "Custom Path", is_live=False)
            else:
                for sub in CUSTOM_SAVEGAME_DIR.glob('*'):
                    if sub.is_dir() and not sub.name.startswith('.'):
                        add_candidate(sub, "Custom Path", is_live=False)
        except Exception:
            pass
    else:
        # Active path is standard Windows Documents savegame directory
        try:
            doc_saves = core.find_default_savegame_dir() or (Path.home() / 'Documents' / 'Eden Games' / 'Test Drive Unlimited 2' / 'savegame')
            if doc_saves and doc_saves.is_dir():
                for p_dir in doc_saves.glob('*'):
                    if p_dir.is_dir() and not p_dir.name.startswith('.'):
                        add_candidate(p_dir, "Documents", is_live=True)
        except Exception:
            pass

        # Fallback to local workspace folders ONLY if Documents has zero profiles (e.g. clean dev/test environment)
        if not profiles:
            for local_name in ['PLAYERSAVE', 'examplesave', 'test_converted']:
                p_path = WORKSPACE_DIR / local_name
                if p_path.is_dir():
                    if local_name == 'examplesave':
                        for sub in p_path.glob('*'):
                            if sub.is_dir() and not sub.name.startswith('.'):
                                add_candidate(sub, "Local Example", is_live=False)
                    else:
                        add_candidate(p_path, "Local Workspace", is_live=False)

    return profiles



# Authentic TDU2 Level Progression Thresholds (Extracted from db_data.dec.cpr & tduw_db_data.dec.cpr)
SKILL_THRESHOLDS = [0, 125, 300, 525, 825, 1200, 1650, 2175, 2795, 3510, 4320, 5225, 6225, 7355, 8615, 10000]
CRUISING_THRESHOLDS = SKILL_THRESHOLDS + [11500, 13000, 14500]

def calc_skill_level(pts: int, thresholds: list) -> int:
    lvl = 0
    for i, req in enumerate(thresholds):
        if pts >= req:
            lvl = i
        else:
            break
    return lvl

def calculate_player_level(data_dict: dict) -> int:
    """
    Computes authentic overall player level (1-73).
    The global level is the sum of levels in the 4 skills:
    - Racing (0-15)
    - Collection (0-15)
    - Social (0-15)
    - Discovery / Cruising (0-18)
    """
    pd = data_dict.get('PlayerData', data_dict)
    driver = pd.get('Driver', {})
    if driver.get('Level'):
        return max(1, min(73, int(driver['Level'])))

    pl = pd.get('PlayerLevels', {})
    r_pts = pl.get('RacingLevel', 0)
    c_pts = pl.get('CollectionLevel', 0)
    s_pts = pl.get('SocialLevel', 0)
    cr_dict = pl.get('CruisingLevels', {})
    cr_pts = sum(cr_dict.values()) if isinstance(cr_dict, dict) else 0

    r_lvl = calc_skill_level(r_pts, SKILL_THRESHOLDS)
    c_lvl = calc_skill_level(c_pts, SKILL_THRESHOLDS)
    s_lvl = calc_skill_level(s_pts, SKILL_THRESHOLDS)
    cr_lvl = calc_skill_level(cr_pts, CRUISING_THRESHOLDS)

    total_lvl = r_lvl + c_lvl + s_lvl + cr_lvl
    return max(1, min(73, total_lvl))


def extract_save_summary(data_obj, prof_name, source_path):
    """
    Extracts high-level dashboard metrics, garage cars, and progress from PlayerData dict.
    Strictly preserves global array index for every slot.
    """
    driver = data_obj.get('Driver', {})
    levels = data_obj.get('PlayerLevels', {})
    licenses = data_obj.get('PlayerLicenses', {})
    garage = data_obj.get('Garage', [])
    wrecks = data_obj.get('Wrecks', {})
    photos = data_obj.get('PhotosGP', {})
    my_house_data = data_obj.get('MyHouse', {})

    # Calculate road discovery stats
    total_roads_arr = levels.get('AreaTotalRoads', [])
    unlocked_roads_arr = levels.get('AreaRoadsUnlocked', [])
    total_roads_count = sum(total_roads_arr) if isinstance(total_roads_arr, list) else 0
    unlocked_roads_count = sum(unlocked_roads_arr) if isinstance(unlocked_roads_arr, list) else 0
    road_pct = round((unlocked_roads_count / total_roads_count * 100), 1) if total_roads_count > 0 else 0.0

    # Cruising points
    cruising = levels.get('CruisingLevels', {})
    if not isinstance(cruising, dict):
        cruising = {}
    cruising_areas_clean = {
        'Area_0': int(cruising.get('Area_0', 0)),
        'Area_1': int(cruising.get('Area_1', 0)),
        'Area_2': int(cruising.get('Area_2', 0)),
        'Area_3': int(cruising.get('Area_3', 0)),
        'Area_4': int(cruising.get('Area_4', 0)),
        'Area_5': int(cruising.get('Area_5', 0)),
    }
    cruising_pts = sum(cruising_areas_clean.values())
    max_cruising = 14500
    cruising_pct = round((cruising_pts / max_cruising * 100), 1) if max_cruising > 0 else 0.0

    # Wrecks (authentic 80 wrecks)
    ibiza_wrecks = wrecks.get('Wrecks_IBIZA', [])[:28]
    hawaii_wrecks = wrecks.get('Wrecks_HAWAI', [])[:52]
    found_wrecks = sum(1 for w in ibiza_wrecks if w.get('Taken')) + sum(1 for w in hawaii_wrecks if w.get('Taken'))

    # Photos
    photo_list = photos.get('PhotosGP', [])
    found_photos = sum(1 for p in photo_list if p.get('Taken'))

    # Licenses
    license_list = licenses.get('Licenses', [])
    passed_licenses = sum(1 for l in license_list if l.get('Passed'))

    # Garage list & grouping by authentic owned house
    car_list = []
    house_groups = {}

    for idx, c_entry in enumerate(garage):
        car_data = c_entry.get('Car', {})
        archetype_id = car_data.get('Archetype', 0)
        house_hc = c_entry.get('House', 0)
        car_db_entry = CARS_DB.get(str(archetype_id), {})
        is_empty = (archetype_id == 0 or car_data.get('Status') == 2 or car_data.get('ID') == 4294967295)

        if car_db_entry:
            brand_name = car_db_entry.get('brand', '')
            model_name = car_db_entry.get('model', '')
            version_name = car_db_entry.get('version', '')
            full_name = car_db_entry.get('name', f"Vehicle #{idx + 1}")
            bhp = car_db_entry.get('power_bhp', 0)
            top_speed = car_db_entry.get('top_speed', 0)
            accel = car_db_entry.get('acceleration', 0)
            catalog_price = car_db_entry.get('price', 0)
        else:
            brand_name = car_data.get('Brand', '')
            model_name = car_data.get('Name', '')
            version_name = ''
            full_name = "Empty Garage Slot" if is_empty else (car_data.get('Name') or f"Vehicle #{idx + 1}")
            bhp = 0
            top_speed = 0
            accel = 0
            catalog_price = car_data.get('Price', 0)

        upgrades = car_data.get('Car Upgrades', {})
        odometer = round(car_data.get('OdometerKms', 0.0), 1)

        accel_lvl = upgrades.get('Acceleration', 0) if isinstance(upgrades, dict) else 0
        speed_lvl = upgrades.get('Top Speed', 0) if isinstance(upgrades, dict) else 0
        brake_lvl = upgrades.get('Braking', 0) if isinstance(upgrades, dict) else 0
        tuning_stage = max(accel_lvl, speed_lvl, brake_lvl)
        is_max_tune = (accel_lvl == 4 and speed_lvl == 4 and brake_lvl == 4)

        car_item = {
            "index": idx,
            "slot": idx,  # Global index in PlayerData.Garage (0..N-1)
            "bay": c_entry.get('IndexInGarage', 0) + 1,
            "archetype": archetype_id,
            "id": car_data.get('ID', 0),
            "status": car_data.get('Status', 0),
            "is_empty": is_empty,
            "name": full_name,
            "brand": brand_name,
            "model": model_name,
            "version": version_name,
            "power_bhp": bhp,
            "top_speed": top_speed,
            "acceleration": accel,
            "price": catalog_price,
            "mileage": odometer,
            "house_id": str(house_hc),
            "house_hc": str(house_hc),
            "upgrades": {
                "acceleration": accel_lvl,
                "top_speed": speed_lvl,
                "braking": brake_lvl
            },
            "tuning_stage": tuning_stage,
            "is_max_tune": is_max_tune
        }
        car_list.append(car_item)
        if house_hc not in house_groups:
            house_groups[house_hc] = []
        house_groups[house_hc].append(car_item)

    # Build structured houses array
    houses_list = []
    for h_hc, h_cars in house_groups.items():
        h_info = resolve_house_info(h_hc, len(h_cars))
        occupied_cnt = sum(1 for c in h_cars if not c['is_empty'])
        houses_list.append({
            "house_id": str(h_hc),
            "house_hc": str(h_hc),
            "house_hex": h_info['house_hex'],
            "name": h_info['name'],
            "display_name": h_info['display_name'],
            "island": h_info['island'],
            "level": h_info['level'],
            "slots_total": h_info['slots'],
            "slots_occupied": occupied_cnt,
            "cars": h_cars
        })

    # Sort houses: Ibiza first, then Hawaii; within island, sort by Level
    houses_list.sort(key=lambda h: (0 if h['island'] == 'Ibiza' else 1, h['level'], h['name']))

    # Furniture & Materials statistics
    sold_furn = my_house_data.get('SoldedFurnitures', [])
    sold_mats = my_house_data.get('SoldedMaterials', [])
    furn_unlocked_cnt = sum(1 for f in sold_furn if f != 0)
    mats_unlocked_cnt = sum(1 for m in sold_mats if m != 0)
    casino_u0 = data_obj.get('Casino', {}).get('unlockables0', 0)
    casino_furn_unlocked = bool((casino_u0 >> 54) & 1)

    is_live = False
    try:
        doc_dir = Path.home() / 'Documents' / 'Eden Games' / 'Test Drive Unlimited 2' / 'savegame'
        is_live = doc_dir in Path(source_path).parents or str(doc_dir).lower() in str(source_path).lower()
    except Exception:
        pass

    backups_list = get_profile_backups_list(prof_name)

    # Extract online status from OPTIONS if available
    ps_dir = Path(source_path).parent
    opt_file = ps_dir / 'OPTIONS'
    active_online = False
    active_login = driver.get('Name') or prof_name
    active_email = ""
    active_has_creds = False
    if opt_file.is_file():
        try:
            with open(opt_file, 'rb') as of:
                ob = of.read()
            ox, _, _ = core.decrypt_save_file(ob, prof_name, 'OPTIONS')
            _, od = core.decode_xmbf_to_dict(ox)
            active_online = bool(od.get('IsOnlineEnabledProfile', False))
            active_login = od.get('LoginName', '') or active_login
            active_email = od.get('Email', '') or ''
            active_has_creds = bool(active_email or od.get('Password'))
        except Exception:
            pass

    return {
        "profile_name": prof_name,
        "driver_name": driver.get('Name') or prof_name,
        "source_path": str(source_path),
        "is_live_documents": is_live,
        "online_status": {
            "is_online": active_online,
            "mode_label": "ONLINE" if active_online else "OFFLINE",
            "login_name": active_login,
            "email": active_email,
            "has_credentials": active_has_creds
        },
        "money": driver.get('Money', 0),
        "casino_points": driver.get('NbCoupon', 0),
        "overall_level": calculate_player_level(data_obj),
        "levels": {
            "racing": levels.get('RacingLevel', 0),
            "collection": levels.get('CollectionLevel', 0),
            "social": levels.get('SocialLevel', 0),
            "cruising_points": cruising_pts,
            "cruising_max": max_cruising,
            "cruising_pct": cruising_pct,
            "areas": cruising_areas_clean
        },
        "roads": {
            "discovered": unlocked_roads_count,
            "total": total_roads_count,
            "percentage": road_pct
        },
        "licenses": {
            "passed": passed_licenses,
            "total": len(license_list)
        },
        "garage": {
            "count": sum(1 for c in car_list if not c['is_empty']),
            "total_slots": len(garage),
            "houses": houses_list,
            "cars": car_list
        },
        "collectibles": {
            "wrecks_found": found_wrecks,
            "wrecks_total": 80,
            "photos_taken": found_photos,
            "photos_total": len(photo_list),
            "houses_count": len(houses_list)
        },
        "furniture": {
            "unlocked_count": furn_unlocked_cnt,
            "total_count": 383,
            "materials_unlocked": mats_unlocked_cnt,
            "materials_total": 61,
            "casino_vip_unlocked": casino_furn_unlocked,
            "casino_furniture_unlocked": casino_furn_unlocked,
            "is_max_unlocked": (furn_unlocked_cnt >= 383 and mats_unlocked_cnt >= 61 and casino_furn_unlocked)
        },
        "backups": {
            "count": len(backups_list),
            "latest": backups_list[0] if backups_list else None,
            "list": backups_list
        }
    }


def load_save_file(target_path_str, profile_name_override=None):
    """
    Loads and decrypts DATA save file, caching state in memory.
    """
    global loaded_save_state
    target = Path(target_path_str).resolve()

    if target.is_dir():
        data_file = target / 'DATA'
        if not data_file.exists():
            data_file = target / 'PLAYERSAVE' / 'DATA'
    else:
        data_file = target

    if not data_file.is_file():
        raise FileNotFoundError(f"Save file DATA not found at: {target}")

    with open(data_file, 'rb') as f:
        file_bytes = f.read()

    prof_name = profile_name_override or core.detect_profile_name(data_file, file_bytes)

    # Decrypt save container
    xmbf_bytes, footer, fname = core.decrypt_save_file(file_bytes, prof_name, data_file.name)
    root_name, data_obj = core.decode_xmbf_to_dict(xmbf_bytes)

    if root_name != 'PlayerData':
        raise ValueError(f"Expected root 'PlayerData', found '{root_name}'")

    is_live = False
    try:
        doc_dir = Path.home() / 'Documents' / 'Eden Games' / 'Test Drive Unlimited 2' / 'savegame'
        is_live = doc_dir in data_file.parents or str(doc_dir).lower() in str(data_file).lower()
    except Exception:
        pass

    loaded_save_state = {
        "source_path": str(data_file),
        "profile_name": prof_name,
        "footer": footer,
        "target_filename": data_file.name,
        "raw_xmbf": xmbf_bytes,
        "root_name": root_name,
        "data_dict": data_obj,
        "is_live_documents": is_live,
        "last_backup_path": None
    }

    summary = extract_save_summary(data_obj, prof_name, data_file)
    return summary


# ==============================================================================
# REST API & STATIC HTTP HANDLER
# ==============================================================================

class TDU2WebHandler(BaseHTTPRequestHandler):

    def _apply_cors_headers(self):
        origin = self.headers.get('Origin')
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.hostname in ('127.0.0.1', 'localhost'):
                self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Toolkit-Token')

    def send_json(self, data, status_code=200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self._apply_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status_code=400):
        self.send_json({"success": False, "error": str(message)}, status_code=status_code)

    def do_OPTIONS(self):
        self.send_response(200)
        self._apply_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # --- API: PROFILES ---
        if path == '/api/profiles':
            try:
                profiles = find_all_tdu2_profiles()
                def_root = core.find_default_savegame_dir() or (Path.home() / 'Documents' / 'Eden Games' / 'Test Drive Unlimited 2' / 'savegame')
                self.send_json({
                    "success": True,
                    "version": TOOLKIT_VERSION,
                    "profiles": profiles,
                    "custom_dir": str(CUSTOM_SAVEGAME_DIR.resolve()) if CUSTOM_SAVEGAME_DIR else None,
                    "default_dir": str(def_root) if def_root else None,
                    "decrypt_dir": str(DECRYPT_DIR.resolve()),
                    "active_profile": loaded_save_state["profile_name"],
                    "active_path": loaded_save_state["source_path"],
                    "is_live_documents": loaded_save_state["is_live_documents"]
                })
            except Exception as e:
                self.send_error_json(f"Failed to scan profiles: {e}")
            return

        # --- API: STATUS & ACTIVE SUMMARY ---
        elif path in ('/api/status', '/api/summary'):
            if loaded_save_state["data_dict"] and loaded_save_state["source_path"]:
                try:
                    summary = extract_save_summary(
                        loaded_save_state["data_dict"],
                        loaded_save_state["profile_name"],
                        loaded_save_state["source_path"]
                    )
                    self.send_json({"success": True, "loaded": True, "summary": summary})
                except Exception as e:
                    self.send_error_json(f"Failed to generate summary: {e}")
            else:
                self.send_json({
                    "success": True,
                    "loaded": False,
                    "message": "No profile loaded. Select a profile from the dropdown."
                })
            return

        # --- API: CARS DATABASE & CATALOG ---
        elif path == '/api/cars-database':
            self.send_json({"success": True, "cars": CARS_DB, "count": len(CARS_DB)})
            return

        elif path == '/api/cars-catalog':
            cars_list = []
            for k, v in CARS_DB.items():
                entry = dict(v)
                entry['archetype'] = int(k)
                entry['id'] = int(k)
                cars_list.append(entry)
            cars_list.sort(key=lambda c: (c.get('brand', ''), c.get('name', '')))
            self.send_json({"success": True, "cars": cars_list, "count": len(cars_list)})
            return

        # --- API: HOUSES DATABASE ---
        elif path == '/api/houses-database':
            self.send_json({"success": True, "houses": HOUSES_DB.get('houses', [])})
            return

        # --- API: BACKUPS LIST ---
        elif path == '/api/backups':
            prof = loaded_save_state["profile_name"]
            backups = get_profile_backups_list(prof)
            self.send_json({"success": True, "profile": prof, "backups": backups, "count": len(backups)})
            return

        # --- API: RAW JSON ---
        elif path == '/api/raw-json':
            if not loaded_save_state["data_dict"]:
                self.send_error_json("No save loaded.")
                return
            self.send_json({"success": True, "data": loaded_save_state["data_dict"]})
            return

        # --- STATIC ASSETS ---
        rel_path = path.lstrip('/')
        if not rel_path or rel_path == 'index.html':
            target_file = WEB_DIR / 'index.html'
        else:
            target_file = (WEB_DIR / rel_path).resolve()

        # Prevent directory traversal
        try:
            target_file.relative_to(WEB_DIR.resolve())
        except ValueError:
            self.send_error(403, "Forbidden")
            return

        if target_file.is_file():
            mime, _ = mimetypes.guess_type(str(target_file))
            mime = mime or 'application/octet-stream'
            try:
                with open(target_file, 'rb') as f:
                    content = f.read()
                if target_file.name == 'index.html':
                    content = content.replace(b'__SESSION_TOKEN__', SESSION_TOKEN.encode('utf-8'))
                self.send_response(200)
                self.send_header('Content-Type', f"{mime}; charset=utf-8" if 'text' in mime or 'javascript' in mime else mime)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Internal Error: {e}")
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        global CUSTOM_SAVEGAME_DIR
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        if content_len > MAX_CONTENT_LENGTH:
            self.send_error_json("Payload too large (max 10MB).", status_code=413)
            return

        # Security check: require matching X-Toolkit-Token for all mutating POST requests
        token = self.headers.get('X-Toolkit-Token')
        if token != SESSION_TOKEN:
            self.send_error_json("Unauthorized: Missing or invalid X-Toolkit-Token.", status_code=403)
            return

        post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'

        try:
            payload = json.loads(post_body.decode('utf-8')) if post_body else {}
        except Exception:
            payload = {}

        # --- LOAD SAVE ---
        if path == '/api/load':
            target_path = payload.get('path')
            profile_override = payload.get('profile')

            if not target_path:
                self.send_error_json("Parameter 'path' is required.")
                return

            p = Path(target_path).resolve()

            # Path containment check: ensure target path is within allowed directories
            allowed_roots = [
                WORKSPACE_DIR.resolve(),
                BACKUPS_DIR.resolve(),
                DECRYPT_DIR.resolve(),
            ]
            if CUSTOM_SAVEGAME_DIR:
                allowed_roots.append(CUSTOM_SAVEGAME_DIR.resolve())
            def_root = core.find_default_savegame_dir()
            if def_root:
                allowed_roots.append(def_root.resolve())

            is_allowed = False
            for r in allowed_roots:
                try:
                    p.relative_to(r)
                    is_allowed = True
                    break
                except ValueError:
                    pass

            if not is_allowed:
                self.send_error_json("Access denied: Target path is outside permitted save directories.", status_code=400)
                return

            try:
                summary = load_save_file(str(p), profile_override)
                self.send_json({
                    "success": True,
                    "message": f"Successfully loaded profile: {summary['driver_name']}",
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to load save: {e}")
            return

        # --- CUSTOM SAVE DIRECTORY CONFIGURATION ---
        elif path in ('/api/save-directory', '/api/directory'):
            reset = payload.get('reset', False)
            if reset:
                CUSTOM_SAVEGAME_DIR = None
                profiles = find_all_tdu2_profiles()
                self.send_json({
                    "success": True,
                    "reset": True,
                    "custom_dir": None,
                    "profiles": profiles,
                    "message": "Reset to default Documents savegame directory."
                })
                return

            dir_input = payload.get('directory') or payload.get('path')
            if not dir_input:
                self.send_error_json("Parameter 'directory' or 'path' is required.")
                return

            p = Path(dir_input).resolve()
            if not p.is_dir():
                self.send_error_json(f"Path does not exist or is not a directory: {p}")
                return

            # Validate that the directory contains recognizable TDU2 structures
            has_tdu2_structure = (
                (p / 'ProfileList.dat').is_file() or
                (p / 'DATA').is_file() or
                (p / 'PLAYERSAVE').is_dir() or
                any((sub / 'PLAYERSAVE').is_dir() or (sub / 'DATA').is_file() for sub in p.iterdir() if sub.is_dir())
            )
            if not has_tdu2_structure:
                self.send_error_json(f"Selected folder does not appear to be a valid TDU2 savegame folder or profile directory: {p}")
                return

            CUSTOM_SAVEGAME_DIR = p
            profiles = find_all_tdu2_profiles()
            self.send_json({
                "success": True,
                "custom_dir": str(p),
                "profiles": profiles,
                "message": f"Applied custom path: {p} ({len(profiles)} profile(s) found)"
            })
            return

        # --- PROFILE ONLINE / OFFLINE MODE SWITCHER ---
        elif path in ('/api/switch-mode', '/api/switch'):
            prof_name = payload.get('profile') or payload.get('profile_name')
            target_online = payload.get('target_online')
            login_name = payload.get('login_name') or payload.get('login')
            email = payload.get('email')
            password = payload.get('password')
            clone_from = payload.get('clone_from')

            if not prof_name:
                self.send_error_json("Parameter 'profile' (or 'profile_name') is required.")
                return

            custom_root = CUSTOM_SAVEGAME_DIR or core.find_default_savegame_dir()
            try:
                res = core.switch_profile_mode(
                    profile_name=prof_name,
                    savegame_root=custom_root,
                    target_online=target_online,
                    login_name=login_name,
                    email=email,
                    password=password,
                    clone_from=clone_from
                )
                summary = None
                if loaded_save_state["profile_name"] and loaded_save_state["profile_name"].lower() == prof_name.lower():
                    summary = extract_save_summary(
                        loaded_save_state["data_dict"],
                        loaded_save_state["profile_name"],
                        Path(loaded_save_state["source_path"])
                    )
                res["target_online"] = (res.get("new_mode") == "ONLINE")
                res["summary"] = summary
                res["profiles"] = find_all_tdu2_profiles()
                self.send_json(res)
            except Exception as e:
                self.send_error_json(f"Failed to switch profile mode: {e}")
            return

        # --- CLONE PROGRESSION INTO ONLINE PROFILE ---
        elif path == '/api/clone-progression':
            source = payload.get('source') or payload.get('source_profile')
            target = payload.get('target') or payload.get('target_profile')
            copy_keymap = payload.get('copy_keymap', False)

            if not source or not target:
                self.send_error_json("Parameters 'source' (or 'source_profile') and 'target' (or 'target_profile') are required.")
                return

            custom_root = CUSTOM_SAVEGAME_DIR or core.find_default_savegame_dir()
            try:
                res = core.clone_progression(
                    src_profile=source,
                    dst_profile=target,
                    savegame_root=custom_root,
                    copy_keymap=copy_keymap,
                    backup=True
                )
                summary = None
                if loaded_save_state["profile_name"]:
                    active_lower = loaded_save_state["profile_name"].lower()
                    if active_lower == target.lower():
                        summary = load_save_file(loaded_save_state["source_path"], target)
                    elif active_lower == source.lower():
                        summary = extract_save_summary(
                            loaded_save_state["data_dict"],
                            loaded_save_state["profile_name"],
                            Path(loaded_save_state["source_path"])
                        )
                res["summary"] = summary
                res["target_summary"] = summary or {"profile_name": target}
                res["profiles"] = find_all_tdu2_profiles()
                self.send_json(res)
            except Exception as e:
                self.send_error_json(f"Failed to clone progression: {e}")
            return



        # --- DIRECT PROFILE EDITING (TAB 1) ---
        elif path == '/api/edit-profile':
            if not loaded_save_state["data_dict"] or not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please load a save first.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                data_obj = loaded_save_state["data_dict"]
                prof_name = loaded_save_state["profile_name"]
                footer = loaded_save_state["footer"]
                target_fname = loaded_save_state["target_filename"]
                raw_xmbf = loaded_save_state["raw_xmbf"]
                root_name = loaded_save_state["root_name"]

                # 1. Automatic safety backup
                bak_path = create_operation_backup(save_path, prof_name, "ProfileEdit")

                # 2. Straight numeric updates (level editing temporarily disabled - WIP)
                data_obj, msg = core.edit_player_profile(
                    data_obj,
                    money=payload.get('money'),
                    casino_points=payload.get('casino_points')
                )

                # 3. Encrypt and save
                new_xmbf = core.encode_dict_to_xmbf(raw_xmbf, {root_name: data_obj}, root_name)
                enc_save = core.encrypt_save_file(new_xmbf, prof_name, target_fname, footer)

                core.atomic_write(save_path, enc_save)

                loaded_save_state["raw_xmbf"] = new_xmbf
                summary = extract_save_summary(data_obj, prof_name, save_path)

                self.send_json({
                    "success": True,
                    "message": msg,
                    "backup_path": str(bak_path.resolve()) if bak_path else None,
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to edit profile: {e}")
            return

        # --- UNLOCK CASINO FURNITURE (TAB 1) ---
        elif path in ('/api/unlock-casino-furniture', '/api/unlock-furniture'):
            if not loaded_save_state["data_dict"] or not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please load a save first.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                data_obj = loaded_save_state["data_dict"]
                prof_name = loaded_save_state["profile_name"]
                footer = loaded_save_state["footer"]
                target_fname = loaded_save_state["target_filename"]
                raw_xmbf = loaded_save_state["raw_xmbf"]
                root_name = loaded_save_state["root_name"]

                bak_path = create_operation_backup(save_path, prof_name, "FurnitureUnlock")

                data_obj, msg = core.unlock_all_furniture(data_obj)

                new_xmbf = core.encode_dict_to_xmbf(raw_xmbf, {root_name: data_obj}, root_name)
                enc_save = core.encrypt_save_file(new_xmbf, prof_name, target_fname, footer)

                core.atomic_write(save_path, enc_save)

                loaded_save_state["raw_xmbf"] = new_xmbf
                summary = extract_save_summary(data_obj, prof_name, save_path)

                self.send_json({
                    "success": True,
                    "message": msg,
                    "backup_path": str(bak_path.resolve()) if bak_path else None,
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to unlock furniture: {e}")
            return

        # --- SWAP CAR MODEL FROM CATALOG (TAB 2) ---
        elif path == '/api/swap-car-catalog':
            if not loaded_save_state["data_dict"] or not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please load a save first.")
                return

            slot = payload.get('slot')
            new_archetype = payload.get('new_archetype') or payload.get('archetype') or payload.get('id')

            if slot is None or new_archetype is None:
                self.send_error_json("Parameters 'slot' and 'new_archetype' are required.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                data_obj = loaded_save_state["data_dict"]
                prof_name = loaded_save_state["profile_name"]
                footer = loaded_save_state["footer"]
                target_fname = loaded_save_state["target_filename"]
                raw_xmbf = loaded_save_state["raw_xmbf"]
                root_name = loaded_save_state["root_name"]

                slot_int = int(slot)
                bak_path = create_operation_backup(save_path, prof_name, f"CarSwap_Slot{slot_int+1}")

                core.swap_garage_car_archetype(data_obj, slot_int, int(new_archetype), CARS_DB)

                new_xmbf = core.encode_dict_to_xmbf(raw_xmbf, {root_name: data_obj}, root_name)
                enc_save = core.encrypt_save_file(new_xmbf, prof_name, target_fname, footer)

                core.atomic_write(save_path, enc_save)

                loaded_save_state["raw_xmbf"] = new_xmbf
                summary = extract_save_summary(data_obj, prof_name, save_path)

                car_entry = CARS_DB.get(str(new_archetype), {})
                car_name = car_entry.get('name', f"Archetype #{new_archetype}")

                self.send_json({
                    "success": True,
                    "message": f"Successfully swapped Garage Slot #{slot_int + 1} to {car_name}",
                    "car_name": car_name,
                    "backup_path": str(bak_path.resolve()) if bak_path else None,
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to swap car: {e}")
            return

        # --- TUNE / UPGRADE CAR (TAB 2) ---
        elif path == '/api/tune-car':
            if not loaded_save_state["data_dict"] or not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please load a save first.")
                return

            slot = payload.get('slot')
            if slot is None:
                self.send_error_json("Parameter 'slot' is required.")
                return

            max_tune = bool(payload.get('max_tune', False))
            accel = payload.get('acceleration')
            speed = payload.get('top_speed') if payload.get('top_speed') is not None else payload.get('speed')
            braking = payload.get('braking')

            try:
                save_path = Path(loaded_save_state["source_path"])
                data_obj = loaded_save_state["data_dict"]
                prof_name = loaded_save_state["profile_name"]
                footer = loaded_save_state["footer"]
                target_fname = loaded_save_state["target_filename"]
                raw_xmbf = loaded_save_state["raw_xmbf"]
                root_name = loaded_save_state["root_name"]

                slot_int = int(slot)
                op_name = f"CarTuneMax_Slot{slot_int+1}" if max_tune else f"CarTune_Slot{slot_int+1}"
                bak_path = create_operation_backup(save_path, prof_name, op_name)

                data_obj, msg = core.tune_garage_car(
                    data_obj,
                    slot_int,
                    acceleration=accel,
                    top_speed=speed,
                    braking=braking,
                    max_tune=max_tune
                )

                new_xmbf = core.encode_dict_to_xmbf(raw_xmbf, {root_name: data_obj}, root_name)
                enc_save = core.encrypt_save_file(new_xmbf, prof_name, target_fname, footer)

                core.atomic_write(save_path, enc_save)

                loaded_save_state["raw_xmbf"] = new_xmbf
                summary = extract_save_summary(data_obj, prof_name, save_path)

                self.send_json({
                    "success": True,
                    "message": msg,
                    "backup_path": str(bak_path.resolve()) if bak_path else None,
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to tune car: {e}")
            return

        # --- SWAP POSITIONS BETWEEN SLOTS (TAB 2) ---
        elif path == '/api/swap-slots':
            if not loaded_save_state["data_dict"] or not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please load a save first.")
                return

            slot_a = payload.get('slot_a')
            slot_b = payload.get('slot_b')

            if slot_a is None or slot_b is None:
                self.send_error_json("Parameters 'slot_a' and 'slot_b' are required.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                data_obj = loaded_save_state["data_dict"]
                prof_name = loaded_save_state["profile_name"]
                footer = loaded_save_state["footer"]
                target_fname = loaded_save_state["target_filename"]
                raw_xmbf = loaded_save_state["raw_xmbf"]
                root_name = loaded_save_state["root_name"]

                a_int, b_int = int(slot_a), int(slot_b)
                bak_path = create_operation_backup(save_path, prof_name, f"SwapSlots_{a_int+1}_{b_int+1}")

                core.swap_garage_slots(data_obj, a_int, b_int)

                new_xmbf = core.encode_dict_to_xmbf(raw_xmbf, {root_name: data_obj}, root_name)
                enc_save = core.encrypt_save_file(new_xmbf, prof_name, target_fname, footer)

                core.atomic_write(save_path, enc_save)

                loaded_save_state["raw_xmbf"] = new_xmbf
                summary = extract_save_summary(data_obj, prof_name, save_path)

                self.send_json({
                    "success": True,
                    "message": f"Successfully swapped Garage Slot #{a_int + 1} with Slot #{b_int + 1}",
                    "backup_path": str(bak_path.resolve()) if bak_path else None,
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to swap slots: {e}")
            return

        # --- CREATE MANUAL BACKUP (TAB 3) ---
        elif path == '/api/create-backup':
            if not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                prof_name = loaded_save_state["profile_name"]
                label = payload.get('label') or "Manual"
                bak_path = create_operation_backup(save_path, prof_name, label)

                self.send_json({
                    "success": True,
                    "message": f"Manual backup created: {bak_path.name}",
                    "backup_path": str(bak_path.resolve()),
                    "backups": get_profile_backups_list(prof_name)
                })
            except Exception as e:
                self.send_error_json(f"Failed to create backup: {e}")
            return

        # --- RESTORE BACKUP (TAB 3) ---
        elif path == '/api/restore-backup':
            if not loaded_save_state["source_path"]:
                self.send_error_json("No active save file loaded.")
                return

            save_path = Path(loaded_save_state["source_path"])
            prof_name = loaded_save_state["profile_name"]
            backup_target = payload.get('backup_path')

            if backup_target:
                cand_p = Path(backup_target)
                if not cand_p.is_absolute():
                    cand_p = (BACKUPS_DIR / prof_name / backup_target).resolve()
                else:
                    cand_p = cand_p.resolve()

                # Strictly verify containment within BACKUPS_DIR
                try:
                    cand_p.relative_to(BACKUPS_DIR.resolve())
                    bak_path = cand_p
                except ValueError:
                    self.send_error_json("Access denied: Backup path must reside within the Backups directory.", status_code=400)
                    return
            else:
                # Default to nearest .bak in save directory
                bak_path = save_path.with_suffix('.bak')

            if not bak_path.is_file():
                self.send_error_json(f"Backup file not found at: {bak_path}")
                return

            try:
                # Safety backup of current state before restore
                create_operation_backup(save_path, prof_name, "PreRestore")

                core.atomic_write(save_path, bak_path.read_bytes())
                summary = load_save_file(str(save_path), prof_name)

                self.send_json({
                    "success": True,
                    "message": f"Successfully restored backup from {bak_path.name}",
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to restore backup: {e}")
            return

        # --- UNPACK SAVE FILES TO decrypt/ (TAB 3) ---
        elif path == '/api/unpack':
            if not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please select and load a profile first.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                save_dir = save_path.parent
                prof_name = loaded_save_state["profile_name"]
                DECRYPT_DIR.mkdir(parents=True, exist_ok=True)

                unpacked_files = []
                manifest = {
                    "profile_name": prof_name,
                    "source_dir": str(save_dir.resolve()),
                    "unpacked_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "files": {}
                }

                # Unpack DATA container only (KEYMAP and OPTIONS are strictly protected from tampering)
                target_names = ['DATA']
                for tname in target_names:
                    candidate = None
                    for fn in [tname, tname.lower(), tname.capitalize()]:
                        p = save_dir / fn
                        if p.is_file():
                            candidate = p
                            break

                    if not candidate:
                        continue

                    raw_bytes = candidate.read_bytes()
                    try:
                        xmbf_bytes, footer, real_name = core.decrypt_save_file(raw_bytes, prof_name, tname)
                        root_name, data_obj = core.decode_xmbf_to_dict(xmbf_bytes)

                        dec_path = DECRYPT_DIR / f"{tname}.dec"
                        dec_path.write_bytes(xmbf_bytes)
                        unpacked_files.append(f"{tname}.dec")

                        json_path = DECRYPT_DIR / f"{tname}.json"
                        with open(json_path, 'w', encoding='utf-8') as jf:
                            json.dump({root_name: data_obj}, jf, indent=2, ensure_ascii=False)
                        unpacked_files.append(f"{tname}.json")

                        manifest["files"][tname] = {
                            "root_name": root_name,
                            "footer_hex": footer.hex() if footer else "",
                            "target_filename": tname,
                            "source_file": str(candidate.resolve()),
                            "size": len(raw_bytes)
                        }
                    except Exception as ex:
                        print(f"Warning: Failed to decrypt {tname}: {ex}")

                # Save metadata.json
                meta_path = DECRYPT_DIR / "metadata.json"
                with open(meta_path, 'w', encoding='utf-8') as mf:
                    json.dump(manifest, mf, indent=2)

                # Save pack_save.bat helper script into decrypt/
                bat_path = DECRYPT_DIR / "pack_save.bat"
                bat_content = (
                    "@echo off\r\n"
                    "cd /d \"%~dp0\"\r\n"
                    "echo ======================================================================\r\n"
                    "echo Packing Decrypted TDU2 Save File (DATA)\r\n"
                    "echo ======================================================================\r\n"
                    "python ..\\tdu2_save_tool.py pack . -o game_ready\\\r\n"
                    "echo.\r\n"
                    "echo Game-ready files packed into decrypt\\game_ready\\\r\n"
                    "pause\r\n"
                )
                bat_path.write_text(bat_content, encoding='utf-8')

                self.send_json({
                    "success": True,
                    "message": f"Successfully unpacked DATA save file into 'decrypt/' folder.",
                    "decrypt_dir": str(DECRYPT_DIR.resolve()),
                    "unpacked_files": unpacked_files,
                    "unpacked_count": len(manifest["files"]),
                    "profile": prof_name
                })
            except Exception as e:
                self.send_error_json(f"Failed to unpack save: {e}")
            return

        # --- PACK SAVE FILES FROM decrypt/ (TAB 3) ---
        elif path == '/api/pack':
            if not loaded_save_state["source_path"]:
                self.send_error_json("No save file loaded. Please select and load a profile first.")
                return

            try:
                save_path = Path(loaded_save_state["source_path"])
                save_dir = save_path.parent
                prof_name = loaded_save_state["profile_name"]

                meta_path = DECRYPT_DIR / "metadata.json"
                manifest = {}
                if meta_path.is_file():
                    try:
                        with open(meta_path, 'r', encoding='utf-8') as mf:
                            manifest = json.load(mf)
                    except Exception:
                        pass

                if manifest.get("profile_name"):
                    prof_name = manifest["profile_name"]

                game_ready_dir = DECRYPT_DIR / "game_ready"
                game_ready_dir.mkdir(parents=True, exist_ok=True)

                # Find all .json files in DECRYPT_DIR (excluding metadata.json)
                json_candidates = list(DECRYPT_DIR.glob('*.json'))
                json_files = [j for j in json_candidates if j.name.lower() != 'metadata.json']

                if not json_files:
                    self.send_error_json(f"No save JSON files found in {DECRYPT_DIR}. Please unpack first.")
                    return

                packed_files = []
                last_bak = None
                new_data_dict = None
                new_data_raw_xmbf = None

                for jf in json_files:
                    stem = jf.stem.upper()
                    # Safeguard: never pack or overwrite KEYMAP or OPTIONS
                    if stem != 'DATA':
                        continue
                    with open(jf, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)

                    template_dec = DECRYPT_DIR / f"{stem}.dec"
                    if template_dec.is_file():
                        template_bytes = template_dec.read_bytes()
                    elif (save_dir / stem).is_file():
                        template_bytes, _, _ = core.decrypt_save_file((save_dir / stem).read_bytes(), prof_name, stem)
                    else:
                        continue

                    original_footer = None
                    if manifest.get("files", {}).get(stem, {}).get("footer_hex"):
                        original_footer = bytes.fromhex(manifest["files"][stem]["footer_hex"])
                    elif stem == loaded_save_state.get("target_filename") and loaded_save_state.get("footer"):
                        original_footer = loaded_save_state["footer"]

                    root_name = manifest.get("files", {}).get(stem, {}).get("root_name")
                    new_xmbf = core.encode_dict_to_xmbf(template_bytes, json_data, root_name)
                    enc_save = core.encrypt_save_file(new_xmbf, prof_name, stem, original_footer)

                    # 1. Output to game_ready/ folder
                    core.atomic_write(game_ready_dir / stem, enc_save)

                    # 2. Live save directory write with safety backup (when confirmed)
                    install_to_live = payload.get('install_to_live', False)
                    if install_to_live:
                        live_target = save_dir / stem
                        if live_target.is_file():
                            last_bak = create_operation_backup(live_target, prof_name, f"PrePack_{stem}")
                        core.atomic_write(live_target, enc_save)

                    packed_files.append(stem)

                    if stem == 'DATA':
                        _, new_data_dict = core.decode_xmbf_to_dict(new_xmbf)
                        new_data_raw_xmbf = new_xmbf

                if new_data_dict and new_data_raw_xmbf:
                    loaded_save_state["raw_xmbf"] = new_data_raw_xmbf
                    loaded_save_state["data_dict"] = new_data_dict
                    summary = extract_save_summary(new_data_dict, prof_name, save_path)
                else:
                    summary = extract_save_summary(loaded_save_state["data_dict"], prof_name, save_path)

                target_desc = "live save and 'decrypt/game_ready/'" if payload.get('install_to_live', False) else "'decrypt/game_ready/'"
                self.send_json({
                    "success": True,
                    "message": f"Successfully packed {len(packed_files)} file(s) ({', '.join(packed_files)}) from 'decrypt/' to {target_desc}.",
                    "packed_files": packed_files,
                    "installed_to_live": bool(payload.get('install_to_live', False)),
                    "game_ready_dir": str(game_ready_dir.resolve()),
                    "backup_path": str(last_bak.resolve()) if last_bak else None,
                    "summary": summary
                })
            except Exception as e:
                self.send_error_json(f"Failed to pack save: {e}")
            return

        else:
            self.send_error(404, f"API endpoint '{path}' not found.")


def run_server(port=PORT, auto_open=True, custom_dir=None):
    global CUSTOM_SAVEGAME_DIR
    if custom_dir:
        CUSTOM_SAVEGAME_DIR = Path(custom_dir).resolve()
    elif os.environ.get('TDU2_SAVEGAME_PATH'):
        p_env = Path(os.environ['TDU2_SAVEGAME_PATH']).resolve()
        if p_env.exists():
            CUSTOM_SAVEGAME_DIR = p_env

    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, TDU2WebHandler)
    url = f"http://127.0.0.1:{port}"
    def_dir = core.find_default_savegame_dir()
    print("=" * 68)
    print(f"  TDU2 SAVE FILE TOOLKIT v{TOOLKIT_VERSION} - HTTP SERVER READY")
    print(f"  URL:          {url}")
    print(f"  Default Path: {def_dir or 'Documents'}")
    if CUSTOM_SAVEGAME_DIR:
        print(f"  Custom Path:  {CUSTOM_SAVEGAME_DIR}")
    print(f"  Backups:      {BACKUPS_DIR}")
    print("=" * 68)

    if auto_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server shutdown.")
        httpd.server_close()


if __name__ == '__main__':
    auto_open = '--no-browser' not in sys.argv
    p = PORT
    c_dir = None
    for i, a in enumerate(sys.argv):
        if a == '--port' and i + 1 < len(sys.argv):
            p = int(sys.argv[i+1])
        elif a in ('--dir', '--save-dir') and i + 1 < len(sys.argv):
            c_dir = sys.argv[i+1]
        elif a in ('-v', '--version'):
            print(f"TDU2 Save File Toolkit WebGUI v{TOOLKIT_VERSION}")
            sys.exit(0)

    run_server(port=p, auto_open=auto_open, custom_dir=c_dir)

