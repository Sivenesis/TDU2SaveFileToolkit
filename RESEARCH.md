# Technical Research & Reverse Engineering Guide: Test Drive Unlimited 2 Save File Systems

A technical reference manual detailing the file structures, cryptographic algorithms, serialization formats, reverse-engineering methodology, and system architecture for *Test Drive Unlimited 2* (PC).

This document serves as an engineering blueprint for researchers, modders, and AI coding agents seeking to understand, maintain, extend, or fork this toolkit.

---

## 1. Research Scope and Objectives

The primary engineering objective of this project was to construct a robust, cross-platform save game editor and decryptor for *Test Drive Unlimited 2* with the following architectural constraints:

1. **Zero External Dependencies**: All cryptographic, binary decoding, file serialization, web serving, and database lookups must execute exclusively using the Python standard library (`hashlib`, `struct`, `http.server`, `urllib`, `pathlib`, `json`, `shutil`).
2. **In-Place Cryptographic Round-Tripping**: Save files must decrypt, mutate, and re-encrypt while preserving Eden Games engine compliance, ensuring that untouched data blocks remain byte-identical and internal container checksums remain valid.
3. **Lossless Garage & Profile Editing**: Vehicle swapping, tuning, and profile attributes must operate without desynchronizing global vehicle indices, corrupting garage capacities, or causing game engine crashes.

---

## 2. Save Game Directory Structure and File Roles

*Test Drive Unlimited 2* organizes save data in a hierarchical directory structure under the user's standard Windows Documents location:
```
%USERPROFILE%\Documents\Eden Games\Test Drive Unlimited 2\savegame\
```

The directory is divided into two distinct levels: global system/registry files located directly at the root of `savegame\`, and individual player profile subdirectories containing encrypted game containers and media assets.

### 2.1 Root Level Files

The root `savegame\` folder contains the global profile catalog and hardware configuration:

| File Name | Format | Size | Functional Role |
| :--- | :--- | :--- | :--- |
| `ProfileList.dat` | Binary Registry | Variable (10B header + 257B/profile) | Global profile catalog. Lists all registered player profile aliases and internal index markers. Read by the game engine at boot to populate the player selection screen. Used by this toolkit to automatically discover valid profile names. |
| `SystemDefault` | Binary Configuration | 628 bytes | Global engine and hardware defaults. Stores baseline display resolution, refresh rate, aspect ratio, MSAA antialiasing, shader quality, audio devices, and controller detection flags before any user profile is selected. |

### 2.2 Profile Subdirectory Architecture (`<ProfileName>\`)

Each profile created in TDU2 receives a dedicated directory named after the in-game profile alias (e.g., `<ProfileName>\`). Within each profile directory, data is strictly organized into functional subfolders:

```
%USERPROFILE%\Documents\Eden Games\Test Drive Unlimited 2\savegame\
|-- ProfileList.dat
|-- SystemDefault
`-- <ProfileName>\
    |-- PLAYERSAVE\
    |   |-- DATA
    |   |-- KEYMAP
    |   |-- OPTIONS
    |   `-- *.bak
    |-- AVATAR\
    |   `-- PHOTO00
    |-- LICENCES\
    |   |-- LIC_00
    |   |-- LIC_01
    |   `-- ... (LIC_02 to LIC_07)
    |-- PHOTOS\
    |   |-- 0000000X.JPG
    |   `-- PHOTO08X.JPG
    `-- STICKERS\
        |-- 0000.STI
        `-- 0004.STI
```

### 2.3 Directory and File Breakdown

| Relative Path | Format | Role and Content Description |
| :--- | :--- | :--- |
| `PLAYERSAVE\` | Directory | Dedicated container folder housing all active encrypted gameplay files. The core save containers do not reside loose in the profile root; they are strictly contained inside `PLAYERSAVE\`. The folder name is also an integral component of the cryptographic key derivation string. |
| `PLAYERSAVE\DATA` | Encrypted Container | Primary game progression container. Stores player finances (Driver Money, Casino Points), experience levels (Overall, Competition, Collection, Social, Cruising), real estate ownership (61 houses and yachts), vehicle garage slots (archetypes, paint, rims, tuning stages, mileage), discovered roads, wrecks, events, and furniture/material bitmasks. Encrypted via DES-CBC with target identifier `"DATA"`. |
| `PLAYERSAVE\KEYMAP` | Encrypted Container | Player input mappings and controller bindings. Stores customized key assignments for keyboard, mouse, XInput gamepads, DirectInput steering wheels, pedal deadzones, force feedback linearity/gain, and gear shifter layouts. Encrypted via DES-CBC with target identifier `"KEYMAP"`. |
| `PLAYERSAVE\OPTIONS` | Encrypted Container | Player gameplay preferences and settings. Stores camera perspectives (cockpit, hood, bumper, chase), driving assistance levels (Full Assists, Sport, Hardcore), HUD visibility toggles, GPS map zoom, measurement units (MPH/KMH), voice chat flags, and custom audio channel volumes. Encrypted via DES-CBC with target identifier `"OPTIONS"`. |
| `PLAYERSAVE\*.bak` | Encrypted Backup | Safety backup snapshots created automatically by the game engine or save editors prior to write operations. |
| `AVATAR\PHOTO00` | Binary Portrait | Player character facial portrait snapshot. Captured during character creation or updated at cosmetic surgery clinics and clothing boutiques; displayed on the in-game driver's license ID card. |
| `LICENCES\` | Directory | Driving school examination records. Contains individual license files (`LIC_00` through `LIC_07`) corresponding to vehicle categories (Classic C4/C3, Off-Road B4/B3, Asphalt A7/A6, A5/A4, etc.), tracking completion times, medals (Gold, Silver, Bronze), and penalty points. |
| `PHOTOS\` | Directory | In-game photographs captured by the player. Standard JPEG images (`*.JPG`) taken using the handheld camera or tourist photo spots across Ibiza and Hawaii, embedded with in-game viewpoint metadata. |
| `STICKERS\` | Directory | Custom vehicle decals and liveries. Binary files (`*.STI`) created in the vehicle Sticker Shop, recording vinyl coordinates, scale, rotation, layer hierarchy, colors, and opacity. |

---

## 3. Save Container Architecture and Binary Layout

Every primary save file inside `PLAYERSAVE\` (`DATA`, `KEYMAP`, `OPTIONS`) is structured as a wrapped cryptographic container composed of an encrypted payload followed by an authentic Eden Games verification footer:

```
+-------------------------------------------------------------------------+
| OFFSET RANGE    | SIZE         | DESCRIPTION                            |
+-------------------------------------------------------------------------+
| 0x0000 - (N-FL) | N - FL bytes | DES-CBC Encrypted Payload (XMBF Chunks)|
| (N-FL) - N      | FL bytes     | Authentic Eden Games Container Footer  |
+-------------------------------------------------------------------------+
```

### 3.1 Container Footer Structure

The container footer length `FL` is dynamic and calculated directly from the trailing byte of the file:
```
FL = 2 + 8 + fname_len + 2 + 1
```

Where:
- **Last Byte (`file[-1]`)**: 1-byte unsigned integer indicating the ASCII target filename length (`fname_len`). E.g., `4` for `DATA` (FL = 17), `6` for `KEYMAP` (FL = 19), `7` for `OPTIONS` (FL = 20).
- **Bytes `0x00 - 0x01`**: ASCII magic boundary marker `##` (`0x23 0x23`).
- **Bytes `0x02 - 0x09`**: 8-byte Profile CRC identifier (`zlib.crc32(profile_name) & 0xffff` encoded as an 8-byte little-endian integer).
- **Bytes `0x0A - (0x0A + fname_len)`**: ASCII target filename string (`"DATA"`, `"KEYMAP"`, or `"OPTIONS"`).
- **Next 2 Bytes**: ASCII magic boundary marker `##` (`0x23 0x23`).
- **Final Byte**: Filename length byte (`fname_len`).

### 3.2 Decrypted Stream Framing and Chunk Architecture

When the ciphertext payload is decrypted via DES-CBC, the resulting stream is not raw XMBF directly. Instead, the game engine wraps the XMBF stream inside a chunk-framed container:

```
+-------------------------------------------------------------------------+
| OFFSET RANGE    | SIZE     | DESCRIPTION                                |
+-------------------------------------------------------------------------+
| 0x0000 - 0x0003 | 4 bytes  | Partial / Chunk Payload Size (Little-Endian|
| 0x0004 - 0x0007 | 4 bytes  | Reserved / Flags                           |
| 0x0008 - 0x000B | 4 bytes  | Total Uncompressed XMBF Size (Little-Endian|
| 0x000C - 0x000F | 4 bytes  | Reserved / Alignment Padding               |
| 0x0010 - End    | Variable | Sequential 4096-Byte Chunks + Checksums    |
+-------------------------------------------------------------------------+
```

Each chunk inside the payload follows this layout:
1. **Data Payload**: Up to 4096 bytes (`c_len = min(remaining_bytes, 4096)`).
2. **Block Padding**: Padded to an 8-byte boundary (`p_len = (c_len + 7) & ~7`).
3. **Eden-SHA1 Checksum**: 20 bytes proprietary Eden-SHA1 hash computed over the unpadded chunk data.
4. **Chunk Alignment**: 4 bytes padding (total 24 bytes following the padded data block).

Concatenating the unpadded chunk payloads produces the authentic raw binary XMBF data stream (`b'XMBF\x01...'`).

---

## 4. Cryptographic Engine Reverse Engineering

### 4.1 DES-CBC Key and Initialization Vector (IV) Derivation
The encryption standard employed by Eden Games is DES (Data Encryption Standard) operating in Cipher Block Chaining (CBC) mode with an 8-byte block size.

The encryption key and IV are derived deterministically from two parameters:
1. The **Profile Name** (case-sensitive string).
2. The **Target File Name** (e.g., `"DATA"`, `"KEYMAP"`, `"OPTIONS"`).

#### Key Derivation Routine
1. Compute the 8-byte Profile CRC identifier:
   ```python
   crc = zlib.crc32(profile_name.encode('latin1')) & 0xffff
   profile_crc_bytes = crc.to_bytes(8, 'little')
   ```
2. Construct the key derivation seed string by combining 6 leading spaces, the first 2 bytes of `profile_crc_bytes`, the constant string `"PLAYERSAVE"`, and the target filename in ASCII:
   ```python
   key_str = b'      ' + profile_crc_bytes[:2] + b'PLAYERSAVE' + target_filename.encode('ascii')
   ```
3. Pass the key derivation string through Eden Games' 6-round Feistel KDF (reverse-engineered from engine address `0x0055cdf0`), which utilizes 6 static 64-bit permutation tables to generate the 56-bit DES file key.
4. Derive the 8-byte Initialization Vector (IV) directly from `profile_crc_bytes`:
   ```python
   iv_L, iv_R = struct.unpack('>II', profile_crc_bytes)
   ```

### 4.2 Zero-Dependency DES Implementation
To eliminate external dependencies on OpenSSL, C compilers, or third-party packages, a pure-Python DES-CBC engine was developed:
- **Fast 32-bit Bitwise Permutations**: Initial Permutation (IP) and Final Permutation (FP) mapping 64-bit blocks into `(L, R)` integer pairs.
- **16-Round Feistel Cipher**: Standard DES Key Schedule (PC-1, PC-2, round shifts) and 8 substitution boxes (S1 through S8).
- **CBC Chaining**: In CBC decryption, each plaintext block is reconstructed via `dec_L ^ prev_L` and `dec_R ^ prev_R`, initialized with the derived IV.

### 4.3 Proprietary Eden-SHA1 Chunk Integrity Checksum
Eden Games uses a custom variant of the standard SHA-1 cryptographic hash to verify data chunk integrity:
- Instead of packing 16 32-bit big-endian words sequentially from 64-byte input blocks, the algorithm extracts each of the 16 message words from a single byte offset:
  ```python
  W = [blk[i * 4 + 3] for i in range(16)]
  ```
- The message schedule expansion, round functions, and constant additions follow standard SHA-1 logic across 80 steps.
- When saving, each 4096-byte chunk is re-hashed using `eden_sha1`, and the 20-byte digest is written into the stream. If any byte within a chunk is altered without updating its corresponding Eden-SHA1 hash, the game displays a "Save file is damaged" error and refuses to load.

---

## 5. Binary XMBF Serialization & In-Place Mutation

The decrypted payload inside `DATA` is stored in the **XMBF** format (eXtensible Model Binary Format), an Eden Games proprietary binary object tree resembling compiled XML or BSON.

### 5.1 XMBF Structure
```
+-------------------------------------------------------------------------+
| OFFSET | FIELD          | TYPE    | DESCRIPTION                         |
+-------------------------------------------------------------------------+
| 0x0000 | Magic Header   | 4 bytes | 'XMBF' (0x58 0x4D 0x42 0x46)        |
| 0x0004 | Version        | 4 bytes | Engine schema version               |
| 0x0008 | Tag Table Ofs  | 4 bytes | Offset to dictionary string table   |
| 0x000C | Tag Table Len  | 4 bytes | Count of unique node tag strings    |
| 0x0010 | Root Node Data | Var     | Recursive tree of typed nodes       |
+-------------------------------------------------------------------------+
```

### 5.2 Node Type Definitions
Each node in an XMBF stream begins with a 1-byte type identifier:

| Type ID | Designation | Structure |
| :--- | :--- | :--- |
| `0x01` | String | 2-byte length prefix followed by UTF-8 or ASCII string bytes. |
| `0x02` | 32-bit Integer | 4-byte big-endian signed/unsigned integer. |
| `0x03` | Float | 4-byte IEEE 754 single-precision float. |
| `0x04` | 64-bit Integer | 8-byte big-endian integer (used for HouseHC and bitmasks). |
| `0x05` | Binary Buffer | 4-byte length prefix followed by raw byte payload. |
| `0x06` | Array / List | 4-byte element count prefix followed by sequential typed elements. |
| `0x07` | Object / Dict | 2-byte tag index, 4-byte child length, followed by key-value pairs. |

### 5.3 In-Place Surgical Patching vs. Synthetic Re-encoding
A major technical finding during reverse engineering was that **fully synthetic re-serialization of the XMBF tree causes game engine instability**. 

The TDU2 game engine expects exact node alignments and preserves specific internal offset relationships. If a tool reconstructs the XMBF tree from generic dictionaries, differences in dictionary key order or tag indices cause the game to reject the save.

#### The Surgical Patching Solution
Rather than re-encoding the entire document:
1. The tool retains the decrypted binary file (`DATA.dec`) as a golden structural template.
2. When an attribute is edited (e.g., `Driver.Money` or `PlayerLevels.Level`), the tool navigates the binary template to the exact byte offset of the target node.
3. If the data type is fixed-width (such as 32-bit integers, 64-bit integers, or floats), the bytes are overwritten in place without changing overall file length.
4. If a dynamic array is mutated (such as `SoldedFurnitures` or `Garage` cars), the node's length is recalculated, parent container length headers are updated recursively upwards, and subsequent offsets are adjusted accordingly.

This ensures byte-for-byte binary parity across all untouched game nodes.

---

## 6. Vehicle Identification, Swapping & Tuning Architecture

### 6.1 Reverse Engineering the Vehicle Database
Save files store cars in `PlayerData.Garage` using an integer field called `Archetype`. In vanilla saves, this number was previously undocumented, appearing as arbitrary integers (e.g., `650`, `117`, `352`).

To construct a comprehensive vehicle catalog:
1. The game's packed asset archives (`.big` and `.map` files) were unpacked.
2. The core databases `db_data.cpr` and `db_us.cpr` were decompressed and decoded.
3. Cross-referencing `_id_car` in `DBCarPhysicsData` with the string table hashes in `db_us` revealed that `_id_car` directly maps to the savegame `Archetype`.
4. A 359-vehicle database (`cars_database.json`) was generated, capturing:
   - Manufacturer / Brand (Ferrari, Bugatti, Pagani, Koenigsegg, Aston Martin, etc.)
   - Model and Variant Name (e.g., Veyron 16.4 Grand Sport Sang Bleu, Zonda Tricolore)
   - Horsepower (BHP), Top Speed (km/h), Acceleration (0-100 km/h)
   - Dealership Purchase Price

### 6.2 Vehicle Swapping Mechanics
When a user swaps a car in Tab 2:
1. The tool locates the specific slot in `PlayerData.Garage` using its global index (0 to N-1).
2. The `Archetype` integer is updated to the selected vehicle's ID.
3. The car's visual configuration, color codes, and upgrade blocks are initialized or preserved.
4. The car's `IndexInGarage` (its 0-based bay position within the specific house) is strictly preserved.
5. The global slot order is maintained so other vehicles are not shifted or displaced.

### 6.3 Performance Tuning Structure
Vehicle tuning is stored inside each car's `Car Upgrades` dictionary:
```json
"Car Upgrades": {
  "Acceleration": 4,
  "Top Speed": 4,
  "Braking": 4
}
```
- Each category accepts an integer value from `0` (stock) to `4` (maximum dealer tuning).
- The game engine reads these values when loading vehicle physics into memory. Setting all three axes to `4` unlocks maximum stage performance without requiring the player to complete dealership tuning challenges.

---

## 7. Real Estate & Garage Property Mapping (`DBHouse`)

### 7.1 House Identification and 64-Bit HouseHC
Every vehicle in `PlayerData.Garage` is assigned to a residential property via a 64-bit integer field named `House`.

By reverse-engineering `DBHouse` inside `db_data.cpr`, the relationship between savegame `House` values and physical game properties was established:
- Each property in the game has a unique spot code (e.g., `EPH_L0C_1254I`, `EPH_L3DI_5067I`, `EPH_L5Y_0362I`).
- The 64-bit `HouseHC` is a packed binary representation encoding the island identifier (`0x49` for Ibiza, `0x48` or `L` for Hawaii), house class/level, and internal spot coordinate hashes.

### 7.2 The 61 Authentic Player Houses
The game features exactly 61 purchasable player houses (19 on Ibiza, 42 on Hawaii):

| Level | Capacity | Star Rating | Examples |
| :--- | :--- | :--- | :--- |
| Level 0 | 2 Cars | 0 / 5 Stars | Caravan (Ibiza), Mokuleia shack (Hawaii) |
| Level 1 | 2 Cars | 1 / 5 Stars | Fontanelles house, Seaside apartment, Kaakahi Spring |
| Level 2 | 4 Cars | 2 / 5 Stars | Cala Moli residence, Portinatx residence, Barber stilt house |
| Level 3 | 6 Cars | 3 / 5 Stars | Sa Cala house, Eivissa house, Zenith loft, Honolulu loft |
| Level 4 | 8 Cars | 4 / 5 Stars | Black Point House, Mineral House, Hydro House, Falls House |
| Level 5 | 6 Cars | 5 / 5 Stars | Luxury Yacht (Ibiza), Luxury Yacht (Hawaii) |

### 7.3 Discrepancy Resolution: Sa Cala House vs. Eivissa House
During database construction, an inversion was identified in earlier community tools between two Level 3, 6-car residences in Ibiza Area 2:
- **Sa Cala house**: Spot `EPH_L3DI_5067I`, Buy Price $602,000, HouseHC `5279481567775327652` (`0x49447C83957885A4`).
- **Eivissa house**: Spot `EPH_L3DI_3346I`, Buy Price $590,000, HouseHC `5279481563447002020` (`0x49447C82937B83A4`).

Analysis of the third and fourth bytes confirmed:
- `0x82` correlates with spot prefix `3346` (Eivissa).
- `0x83` correlates with spot prefix `5067` (Sa Cala).

This correction was incorporated into `houses_database.json` to ensure vehicles display in their authentic residences.

---

## 8. Player Progression and Unlock Mechanics

### 8.1 Player Level Algorithm (1 to 73)
Player progression in TDU2 is composed of four distinct disciplines:
1. **Competition / Racing**: 0 to 15 levels
2. **Collection**: 0 to 15 levels
3. **Social**: 0 to 15 levels
4. **Discovery / Cruising**: 0 to 18 levels

The overall player level is calculated as the sum of these four categories:
```
Total Level = Racing Level + Collection Level + Social Level + Cruising Level
```
- **Base Game Maximum**: Level 60 (15 + 15 + 15 + 15).
- **Offline DLCs Maximum**: Level 63.
- **Online & Casino DLC Maximum**: Level 73.

Setting `Driver.Level` directly in `PlayerData.Driver` without exceeding 73 allows the player profile to display maximum prestige without corrupting leaderboard statistics.

> [!NOTE]
> **Known Issue:** Level editing doesn't work on online profiles (Work in progress). On online profiles, the game engine verifies experience points and sub-discipline achievements against server-side session sync, which overrides manual `Driver.Level` modifications.

### 8.2 Currency Caps
- **Driver Money ($)**: Stored as a 32-bit integer in `Driver.Money`. Clamped between `0` and `2,147,483,648`.
- **Casino Points (Cp)**: Stored as a 32-bit integer in `Driver.NbCoupon`. Clamped between `0` and `2,147,483,648`.

### 8.3 Furniture and Materials Unlocker
- `PlayerData.MyHouse.SoldedFurnitures`: An array containing 383 integer entries representing catalog furniture items. Setting non-zero identifiers unlocks all pieces across all styles.
- `PlayerData.MyHouse.SoldedMaterials`: An array of 61 interior wall, floor, and trim materials.
- `PlayerData.Casino.unlockables0`: A 64-bit bitmask field. Bit 54 (`(unlockables0 >> 54) & 1`) governs the VIP Penthouse suite decor package. Setting this bit unlocks the exclusive casino furniture suite.

---

## 9. WebGUI Architecture & Communication Pipeline

### 9.1 Zero-Dependency HTTP Server
The application serves both the static web frontend and dynamic JSON API endpoints using Python's `http.server.HTTPServer` and `BaseHTTPRequestHandler`.

Key design choices:
- Single-process, multi-threaded request handling for fast local response times.
- MIME type resolution for `.html`, `.css`, `.js`, and `.json`.
- Automatic port fallback if `8282` is occupied.
- Option `--no-browser` for headless testing or background deployment.

### 9.2 REST API Specification

All mutating endpoints (`POST`) require the `X-Toolkit-Token` header matching the server's per-session token.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/profiles` | Scans active save directory (default Documents or custom path) and returns profiles with online status. |
| `POST` | `/api/load` | Validates path boundary and loads save metrics for active profile. |
| `POST` | `/api/save-directory` | Validates and configures a custom TDU2 save directory, or resets to default Documents. |
| `POST` | `/api/edit-profile` | Updates Money (up to $2,147,483,648), Casino Points (up to 2,147,483,648 Cp), and Level (1-73). |
| `POST` | `/api/unlock-casino-furniture` | Unlocks the VIP Penthouse suite decor and casino furniture set. |
| `GET` | `/api/cars-catalog` | Serves the 359-vehicle database for model swap selection. |
| `POST` | `/api/swap-car-catalog` | Replaces the vehicle model in a designated garage slot. |
| `POST` | `/api/tune-car` | Sets tuning stages (0-4) for Acceleration, Top Speed, and Braking for a car. |
| `POST` | `/api/swap-slots` | Swaps positions and properties between two garage slots. |
| `POST` | `/api/unpack` | Decrypts `DATA`, `KEYMAP`, `OPTIONS` and exports formatted JSON into `decrypt/`. |
| `POST` | `/api/pack` | Compiles JSON into binary XMBF and game-ready saves (supports `install_to_live: bool`). |
| `GET` | `/api/backups` | Lists timestamped `.bak` files available for the current profile. |
| `POST` | `/api/create-backup` | Creates a timestamped manual backup in `Backups/<Profile>/`. |
| `POST` | `/api/restore-backup` | Restores a selected backup file (strictly constrained to `Backups/`). |
| `POST` | `/api/switch-mode` | Toggles Online/Offline status across `ProfileList.dat` and `OPTIONS` with transaction rollback. |
| `POST` | `/api/clone-progression` | Transfers full offline progression into a registered online profile, preserving server identity. |

### 9.3 Security Architecture, Atomic Operations & File Isolation (v2.0.3 - v2.0.5)

Versions 2.0.3 - 2.0.5 implement an enterprise-grade local security posture and container safeguards:
- **Origin Hardening & CSRF Protection**: Wildcard `Access-Control-Allow-Origin: *` was completely removed. Responses strictly validate the `Origin` header to permit only local loopback traffic (`127.0.0.1` and `localhost`). In addition, the server generates an ephemeral cryptographically secure random token (`secrets.token_hex(16)`) at startup and injects it into `<meta name="toolkit-token">`. All state-mutating requests (`POST`) require this token via the `X-Toolkit-Token` header.
- **Path Boundary Containment**: To prevent path traversal attacks, static file serving and backup restoration enforce strict `pathlib.Path.relative_to` checks against `web/` and `Backups/` respectively. The `/api/load` endpoint verifies containment within registered save folders, while `/api/save-directory` verifies valid TDU2 file markers before changing active search paths.
- **Atomic File Writes**: Direct file stream writing (`with open(..., 'wb')`) was eliminated across the entire toolkit. All writes are performed via `atomic_write()`: writing to a temporary file (`.tmp_<pid>`), flushing, executing `os.fsync()`, and executing `os.replace()`. This ensures that power cuts, app crashes, or antivirus locks cannot produce corrupted zero-byte save files.
- **Transactional Rollback**: Multi-file mutations (e.g. modifying both `ProfileList.dat` and `OPTIONS` in mode switching) create pre-operation backups and roll back modified files if any subsequent step encounters an error.
- **KEYMAP and OPTIONS File Isolation**: DirectInput/XInput hardware controller mappings in `KEYMAP` and user preferences in `OPTIONS` are strictly isolated and protected from unintentional overwriting. Synthetic re-serialization of `KEYMAP` is blocked to prevent controller corruption. `OPTIONS` is only modified when synchronizing `IsOnlineEnabledProfile` during mode switching.
- **Level Editing Investigation (WIP)**: Direct modification of `Driver.Level` was paused in the WebGUI because TDU2 dynamically computes overall driver level from 4 category point trees (`PlayerLevels`).
- **Payload Denial of Service Prevention**: Requests exceeding `MAX_CONTENT_LENGTH = 10 * 1024 * 1024` (10 MB) are rejected immediately with HTTP 413 (Payload Too Large).
- **Credential Privacy**: Online account passwords in the decrypted `OPTIONS` container are kept strictly internal to backend conversion routines and are never transmitted across HTTP API responses.

---

## 10. Guidance for Modders and AI Agents

When extending or modifying this codebase:

1. **Do Not Synthesize Raw XMBF from Scratch**: Always maintain the decrypted original file (`DATA.dec`) as a structural baseline and perform in-place or targeted offset updates.
2. **Maintain Slot Continuity**: In `PlayerData.Garage`, never delete elements from the garage array or change array length arbitrarily; empty garage bays must be represented with `Vehicle: 0` and `Status: 0`. Deleting entries shifts global indices and causes the game to misplace vehicles across houses.
3. **Respect 64-Bit Alignment**: Fields like `HouseHC` and bitmask registers (`unlockables0`) require 8-byte big-endian packing (`struct.pack('>Q', val)`). Truncating to 32 bits corrupts house associations.
4. **Preserve Container Footers**: Always retain the original container footer bytes and target filename length during unpacking (`metadata.json`) so the packaging pipeline can recalculate valid checksums and maintain authentic profile association.
5. **Always Run the Test Suite**: Before committing changes, execute:
   ```bash
   python test_server_api.py
   ```
   This runs a 25-stage automated integration and security test suite verifying static file delivery, profile editing, car swapping, stage tuning, backup restoration, unpack/pack cryptographic round-tripping, DES-CBC integrity, CSRF token validation, path traversal blocking, backup containment, and payload limits.
