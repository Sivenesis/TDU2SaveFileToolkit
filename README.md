# Test Drive Unlimited 2 Save File Toolkit (WebGUI)

A zero-dependency local web interface and editing engine for *Test Drive Unlimited 2* save files on Windows PC.

---

## Overview

This toolkit provides an offline, browser-based interface for inspecting, editing, tuning, and repairing TDU2 PC save files. The software runs entirely on the Python standard library with no external third-party dependencies or installations required.

### Core Capabilities
- **Player Profile Editing**: Edit Driver Money (up to $999,999,999), Casino Points (up to 999,999,999 Cp), and Overall Player Level (1 to 73).
- **All-in-One Unlocker**: Unlock all 383 authentic furniture items, all 61 living and garage materials, and the Casino furniture.
- **Garage Showroom & Vehicle Swapping**: View owned properties and parked vehicles across Ibiza and Hawaii. Swap any vehicle to any model from the complete 359-car database.
- **Performance Tuning**: Adjust individual tuning stages (Acceleration, Top Speed, Braking from Level 0 to 4) or apply one-click maximum tuning per car.
- **Decrypted Save File Manipulation**: Unpack `DATA`, `KEYMAP`, and `OPTIONS` containers into formatted JSON and raw binary templates in a dedicated `decrypt/` folder, with one-click re-encryption and packaging back to game-ready saves.
- **Automated Backup Manager**: Generates safety backups before every write operation and provides a built-in restoration interface.

---

## Instructions for Use

### Prerequisites
- Windows 7, 8, 10, or 11
- Python 3.8 or newer installed and available in your system `PATH`
- No additional libraries or `pip` packages are required

### Quick Start
1. Run `Run_WebGUI.bat` (or `Run_WebGUI_Silent.vbs` to run in the background without a persistent console window).
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8282
   ```
3. In the header profile selector, select your profile and click **Load Profile**.
4. Use the three dedicated tabs to inspect and edit your game data:
   - **Tab 1: Player Profile Editor**: Update money, casino points, and level, or unlock furniture and decor. Click **Save Profile Changes** to write changes to disk.
   - **Tab 2: Garage Editor**: Browse owned properties. Use the **Tune** button to set performance stages (0 to 4) or click **Max All (Lvl 4)**. Use the **Swap Car** button to replace a car model.
   - **Tab 3: Save Files Manipulation**: Click **Unpack Save to decrypt/** to export human-readable `.json` files. After manual edits, click **Pack from decrypt/ to Game-Ready Save** to re-encrypt and install. Previous versions can be restored at any time from the Backups table.

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
