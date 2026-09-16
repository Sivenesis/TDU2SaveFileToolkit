# Test Drive Unlimited 2 Save File Toolkit (WebGUI) v2.0.2

A zero-dependency local web interface and editing engine for *Test Drive Unlimited 2* save files on Windows PC.

WARNING: TOOLKIT EDITS ACTUAL SAVE FILES IN DOCUMENTS OR USER-SPECIFIED FOLDERS. CREATE BACKUPS BEFORE ANY OPERATION.
---

## Overview

This toolkit provides an offline, browser-based interface for inspecting, editing, tuning, repairing, and managing online/offline status for TDU2 PC save files. The software runs entirely on the Python standard library with no external third-party dependencies or installations required.

### Core Capabilities
- **Save Path Detection & Active Path Isolation (v2.0.2)**: Automatically inspects the standard Windows Documents folder by default (`Documents\Eden Games\Test Drive Unlimited 2\savegame`). When a custom path is configured, discovery is strictly isolated to the active directory, displaying clean profile entries (`<Profile> [Online/Offline]`) and preventing cross-directory pollution in the dropdown and registry status tables.
- **Tab 1: Player Profile Editor**:
  - **Player Finances & Level**: Edit Driver Money (up to $2,147,483,648), Casino Points (up to 2,147,483,648 Cp), and Overall Player Level (1 to 73).
  - **Profile Mode Status**: Live status indicator and quick toggle between Single-Player Offline and Multiplayer Online modes.
  - **Casino Furniture Unlocker (v2.0.2)**: One-click unlock for the exclusive Casino furniture suite for residences and penthouses.
- **Tab 2: Garage Editor**:
  - **Garage Showroom**: Browse all owned properties and parked vehicles across Ibiza and Hawaii with slot occupancy metrics.
  - **Vehicle Model Swapping**: Safely swap any owned vehicle with any model from the complete 359-vehicle catalog.
  - **Performance Tuning**: Adjust individual tuning stages (Acceleration, Top Speed, Braking from Level 0 to 4) or apply one-click maximum tuning per car.
- **Tab 3: Save Files Manipulation**:
  - **Decrypted Save File Manipulation**: Unpack encrypted `DATA`, `KEYMAP`, and `OPTIONS` containers into formatted JSON and raw binary templates in a dedicated `decrypt/` folder, with one-click re-encryption and packaging back to game-ready saves.
  - **Automated Backup Manager**: Generates safety backups before every write operation and provides a built-in restoration interface.
- **Tab 4: Online Mode Switcher**:
  - **Online vs. Offline Mode Switcher**: Inspects and toggles profiles between Single-Player Offline and Multiplayer Online mode. Synchronously patches `ProfileList.dat` (byte 256: `0xFF`=Online, `0x00`=Offline) and the encrypted `OPTIONS` container (`IsOnlineEnabledProfile`).
  - **Online Account Credentials Management**: Configure multiplayer credentials when switching to online mode—either clone credentials from an existing registered profile or enter custom login credentials.
  - **Progression Transfer into Server-Registered Profiles**: Fixes multiplayer "Invalid Nickname" server rejections. Injects full offline progress (cash, houses, tuned cars, discovered roads) directly into an existing server-registered online profile while 100% preserving the target's online nickname, 8-byte Profile UUID, DLC tokens (`Extends`), and credentials.

---

## Instructions for Use

### Prerequisites
- Windows 7, 8, 10, or 11
- Python 3.8 or newer installed and available in your system `PATH` *(Note for Windows 7 & 8: install Python 3.8.10 with SP1/KB2999226, as Python 3.9+ dropped Win7/8 support)*
- A modern web browser (Google Chrome, Mozilla Firefox, Microsoft Edge, Opera, or Supermium)
- No additional libraries or `pip` packages are required

### Quick Start
1. Run `Run_WebGUI.bat` (or `Run_WebGUI_Silent.vbs` to run in the background without a persistent console window).
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8282
   ```
3. In the header profile selector, select your profile and click **Load Profile**.
   - *If your saves are stored in an alternate directory*, click **Custom Path...** (or click the prompt *"Can't see your profiles? Specify custom savegame path"*), enter your folder, and click **Apply Path**. You can reset back to standard Documents at any time with one click.
4. Use the four dedicated tabs to inspect, edit, and manage your game data:
    - **Tab 1: Player Profile Editor**: Update money (up to $2,147,483,648), casino points (up to 2,147,483,648 Cp), and level, view online status, or unlock casino furniture. Click **Save Profile Changes** to write changes to disk.
   - **Tab 2: Garage Editor**: Browse owned properties. Use the **Tune** button to set performance stages (0 to 4) or click **Max All (Lvl 4)**. Use the **Swap Car** button to replace a car model.
   - **Tab 3: Save Files Manipulation**: Click **Unpack Save to decrypt/** to export human-readable `.json` files. After manual edits, click **Pack from decrypt/ to Game-Ready Save** to re-encrypt and install. Previous versions can be restored at any time from the Backups table.
   - **Tab 4: Online Mode Switcher**: View all registered profiles, their `ProfileList.dat` flags, and `OPTIONS` container states. One-click switch between Online and Offline modes, configure multiplayer login credentials, or clone progression from an offline save into a registered online profile.

---

## Command-Line Interface (CLI)

The underlying core engine `tdu2_save_tool.py` can also be run directly from the command line:

```bash
# View help and version
python tdu2_save_tool.py --version

# Switch a profile to online mode with custom credentials
python tdu2_save_tool.py switch "PlayerName" --mode online --login "MyNick" --email "user@example.com" --password "secret"

# Switch a profile to online mode by cloning credentials from another profile
python tdu2_save_tool.py switch "PlayerName" --mode online --clone-from "RegisteredOnlineProfile"

# Switch a profile back to offline mode
python tdu2_save_tool.py switch "PlayerName" --mode offline

# Clone progression from an offline profile into a registered online profile
python tdu2_save_tool.py clone-progression "OfflineProfile" "OnlineProfile" --dir "C:\Path\To\savegame"
```

---

## Known Issues

> [!NOTE]
> **Known issue:** Level editing doesn't work on online profiles (Work in progress).

---

## Important Notice: Manual Backups

> [!IMPORTANT]
> Always make a manual backup of your entire game save folder before using this toolkit or any other third-party save editor.
>
> Default save path:
> ```
> %USERPROFILE%\Documents\Eden Games\Test Drive Unlimited 2\savegame\
> ```
> Copy your profile folder to a safe location outside the game directory. While this tool automatically creates timestamped backups in `Backups/<ProfileName>/` prior to any disk write, maintaining external, independent copies ensures your data is protected against unexpected hardware failures, filesystem issues, or third-party conflicts.

---

## Warning: Property Names in Garage Editor

> [!WARNING]
> Due to differences between internal game engine hashcodes, internal spot identifiers, and localization string tables, certain residential properties may display names in the garage list that differ from in-game real estate agency listings.
>
> All vehicle storage slots, global slot indices, performance tuning, and vehicle swapping operate strictly as intended regardless of property naming differences. Vehicle placements and save structures remain intact and will not corrupt your savegame.

---

## AI Disclosure

This toolkit, including its backend architecture, reverse-engineering analysis routines, clientside interface, and accompanying documentation, was developed with the assistance of artificial intelligence pair-programming systems. All code and cryptographic implementations have been verified through automated test suites and real-world game save round-trips.

---

## Disclaimer and Limitation of Liability

The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

In no event shall the authors, contributors, or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software. This includes, without limitation, loss of save data, savegame corruption, profile resets, game crashes, multiplayer restrictions, or any other direct, indirect, incidental, or consequential damages. Use this utility entirely at your own risk.

---

## Copyright and Non-Affiliation Disclaimer

*Test Drive Unlimited 2* and associated trademarks, trade names, and logos are the property of Eden Games, Atari, and their respective owners.

This project is an independent, non-commercial open-source research tool created by community enthusiasts. It is not affiliated with, sponsored by, endorsed by, or associated with Eden Games, Atari, or any of their parent companies, subsidiaries, or affiliates.
