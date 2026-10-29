# Test Drive Unlimited 2 Save File Toolkit (WebGUI) v3.1.0

A zero-dependency local web interface and editing engine for _Test Drive Unlimited 2_ save files on Windows PC.

---

## Important Notice: Save File Editing & Backups

> [!IMPORTANT]
> This toolkit directly edits game save files on disk. Always make a manual backup of your entire savegame folder before editing. The toolkit automatically creates safety snapshots in `Backups/<ProfileName>/` prior to any disk write.

---

## Mod Notice: TDUWorld Compatibility

> [!WARNING]
> This toolkit is intended for use with _Test Drive Unlimited 2_ running the **TDUWorld** mod. An unmodded (clean) version of the game has not been tested.

---

## Features

- **Profile Editor**: Edit Driver Money (up to $2,147,483,648), Casino Points (up to 2,147,483,648 Cp), Driver Name (with UTF-8 byte capacity tracking), Odometer distance, Salon haircut visits, Active vehicle index, Millionaire milestone flag, and unlock Casino furniture.
- **Progression Editor**: Full level engine and objective manager for Global Level (0 to 73) and Casino Island across Competition, Discovery, Collection, and Social skills.
- **Garage Editor**: Browse properties and vehicles, swap car models from the complete 359-vehicle catalog, apply factory paint/wheels/interior trims, batch tune performance stages (S0–S4), clear garage slots cleanly, with built-in crash hazard guardrails blocking AI ambient traffic models.
- **Raw XMBF Tree Editor**: Hierarchical tree explorer and real-time search across 30,000+ nodes with type descriptors, byte offset inspection, and in-place scalar value mutations.
- **Backup Manager**: Create manual safety snapshots, search and restore previous save versions (supporting both legacy `.bak` files and full directory snapshots), and unpack/pack save containers to formatted JSON.
- **Online Mode Switcher (BETA)**: Switch profiles between Offline and Online modes, configure multiplayer credentials, and clone progression into server-registered profiles.
- **In-Place Binary Engine & RAM Verification**: 100% byte-fidelity in-place AST mutations with pre-commit cryptographic encryption/decryption round-trip verification in RAM before touching disk.

---

## Instructions for Use

1. Run `Run_WebGUI.bat` (or `Run_WebGUI_Silent.vbs` to run in the background).
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8282
   ```
3. Select your save profile from the dropdown and click **Load Profile** (or click **Custom Path...** to specify an alternate save location).
4. Make your desired modifications in any tab and click the respective save or apply button.

---

## Disclaimer and Limitation of Liability

The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors, contributors, or copyright holders be liable for any claim, damages, loss of save data, savegame corruption, profile resets, game crashes, or other liability arising from the use of this software. Use entirely at your own risk.

---

## Copyright and Non-Affiliation Disclaimer

_Test Drive Unlimited 2_ and associated trademarks, trade names, and logos are the property of Eden Games, Atari, and their respective owners. This project is an independent, non-commercial open-source research tool created by community enthusiasts. It is not affiliated with, sponsored by, endorsed by, or associated with Eden Games, Atari, or their affiliates.

---

## AI Disclosure

This toolkit, including its backend architecture, reverse-engineering analysis routines, clientside interface, and accompanying documentation, was developed with the assistance of artificial intelligence pair-programming systems.
