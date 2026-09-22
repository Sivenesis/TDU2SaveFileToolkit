"""
tdu2_level_engine.py

Core Player Level & Progression Engine for Test Drive Unlimited 2 (TDU2).
Provides structured definitions for all 4 skills, 21 sections, and 141+ in-game objectives,
along with save state extraction, points recalculation, dual-layer synchronization,
and safe repacking/encryption.
"""

import sys
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import tdu2_save_tool
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    import tdu2_save_tool

import tdu2_casino_catalog as cc


def popcount(val: int) -> int:
    """Returns number of set bits in an integer."""
    return bin(int(val)).count("1")


# Progression Level Thresholds
SKILL_THRESHOLDS = [
    0,      # Lvl 0
    125,    # Lvl 1
    300,    # Lvl 2
    525,    # Lvl 3
    825,    # Lvl 4
    1200,   # Lvl 5
    1650,   # Lvl 6
    2175,   # Lvl 7
    2795,   # Lvl 8
    3510,   # Lvl 9
    4320,   # Lvl 10
    5225,   # Lvl 11
    6225,   # Lvl 12
    7355,   # Lvl 13
    8615,   # Lvl 14
    10000,  # Lvl 15
]

DISCOVERY_THRESHOLDS = SKILL_THRESHOLDS + [
    11500,  # Lvl 16
    13000,  # Lvl 17
    14500,  # Lvl 18
]

AREA_NAMES = [
    "Ibiza Area 1",
    "Ibiza Area 2",
    "Hawaii Area 1",
    "Hawaii Area 2",
    "Hawaii Area 3",
    "Hawaii Area 4",
]

AREA_MAX_ROADS = [467, 924, 309, 1144, 426, 998]

AREA_MAX_CRUISING_PTS = [2080, 2080, 2425, 2640, 2550, 2725]  # Sum = 14500


def points_to_level(pts: int, is_discovery: bool = False) -> int:
    """Calculate skill level (0 to 15 or 18) based on points."""
    thresholds = DISCOVERY_THRESHOLDS if is_discovery else SKILL_THRESHOLDS
    pts = max(0, pts)
    level = 0
    for lvl, threshold in enumerate(thresholds):
        if pts >= threshold:
            level = lvl
        else:
            break
    return min(level, len(thresholds) - 1)


def level_progress_info(pts: int, is_discovery: bool = False) -> Dict[str, Any]:
    """Calculate level, current xp, next level threshold, and progress percentage."""
    thresholds = DISCOVERY_THRESHOLDS if is_discovery else SKILL_THRESHOLDS
    max_level = len(thresholds) - 1
    lvl = points_to_level(pts, is_discovery)
    cur_threshold = thresholds[lvl]
    if lvl >= max_level:
        next_threshold = thresholds[max_level]
        pct = 100.0
    else:
        next_threshold = thresholds[lvl + 1]
        needed = next_threshold - cur_threshold
        gained = pts - cur_threshold
        pct = round((gained / needed) * 100.0, 1) if needed > 0 else 100.0
    return {
        "level": lvl,
        "max_level": max_level,
        "points": pts,
        "max_points": thresholds[-1],
        "current_threshold": cur_threshold,
        "next_threshold": next_threshold,
        "percent": min(100.0, max(0.0, pct)),
    }

# Master 300-entry EventXPs vector representing 100% completed objectives in TDU2,
# extracted and reconciled from 100% reference profiles (KSAYWOOD, EDENGAMES, Furry).
MASTER_MAX_EVENT_XPS: List[int] = [
    1, 1, 1, 50, 1, 1, 10, 10, 5, 20, 1, 1, 1, 1, 1, 1, 20, 0, 0, 100,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 50, 20, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 20, 15, 20, 10, 50, 50, 20, 1, 1, 1, 1,
    1, 1, 1, 20, 15, 15, 15, 10, 10, 10, 10, 1, 30, 30, 20, 20, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 25, 15, 1, 0,
    0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 4, 4, 3, 3, 3, 3, 4, 4, 3,
    3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]

COMPETITION_XPS_INDICES: List[int] = [
    3, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
    70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88,
    89, 90, 91, 92, 93, 94, 97, 98, 99, 139, 140, 141, 142
]

DISCOVERY_XPS_INDICES: List[int] = [
    129, 130, 131, 143, 144, 145, 146, 147, 148, 149, 150, 151, 189,
    191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202
]

COLLECTION_XPS_INDICES: List[int] = [
    0, 1, 2, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16,
    100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128,
    138, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 188
]

SOCIAL_XPS_INDICES: List[int] = [
    8, 9, 10, 19, 95, 96, 132, 133, 134, 135, 136, 137,
    152, 153, 154, 155, 176, 177, 178, 183, 185, 186
]

SKILL_XPS_INDICES: Dict[str, List[int]] = {
    "competition": COMPETITION_XPS_INDICES,
    "discovery": DISCOVERY_XPS_INDICES,
    "collection": COLLECTION_XPS_INDICES,
    "social": SOCIAL_XPS_INDICES,
}


# Comprehensive definitions of all in-game skills, sections, and objectives
OBJECTIVES_CATALOG = {
    "competition": {
        "id": "competition",
        "name": "Competition",
        "max_points": 10000,
        "max_level": 15,
        "sections": {
            "racing_school": {
                "id": "racing_school",
                "name": "Racing School",
                "skill": "competition",
                "objectives": [
                    {"id": "rs_c4", "name": "Obtain C4 license", "island": "Ibiza", "points": 100, "type": "toggle", "license_idx": 3, "xp_idx": 24},
                    {"id": "rs_b4", "name": "Obtain B4 license", "island": "Ibiza", "points": 100, "type": "toggle", "license_idx": 7, "xp_idx": 25},
                    {"id": "rs_a7_a6", "name": "Obtain A7 - A6 license", "island": "Ibiza", "points": 100, "type": "toggle", "license_idx": 6, "xp_idx": 26},
                    {"id": "rs_c3", "name": "Obtain C3 license", "island": "Hawaii", "points": 100, "type": "toggle", "license_idx": 4, "xp_idx": 27},
                    {"id": "rs_b3", "name": "Obtain B3 license", "island": "Hawaii", "points": 100, "type": "toggle", "license_idx": 5, "xp_idx": 28},
                    {"id": "rs_a5_a4", "name": "Obtain A5 - A4 license", "island": "Hawaii", "points": 100, "type": "toggle", "license_idx": 0, "xp_idx": 29},
                    {"id": "rs_a3_a2", "name": "Obtain A3 - A2 license", "island": "Hawaii", "points": 100, "type": "toggle", "license_idx": 1, "xp_idx": 30},
                    {"id": "rs_a1", "name": "Obtain A1 license", "island": "Hawaii", "points": 100, "type": "toggle", "license_idx": 2, "xp_idx": 31},
                ]
            },
            "championships": {
                "id": "championships",
                "name": "Championships",
                "skill": "competition",
                "objectives": [
                    {"id": "champ_c4", "name": "Win C4 championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 4, "xp_idx": 32},
                    {"id": "champ_c4_high", "name": "Win C4 High championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 5, "xp_idx": 33},
                    {"id": "champ_b4", "name": "Win B4 championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 2, "xp_idx": 34},
                    {"id": "champ_b4_high", "name": "Win B4 High championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 3, "xp_idx": 35},
                    {"id": "champ_a7", "name": "Win A7 championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 0, "xp_idx": 36},
                    {"id": "champ_a7_high", "name": "Win A7 High championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 1, "xp_idx": 37},
                    {"id": "champ_a6", "name": "Win A6 championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 8, "xp_idx": 38},
                    {"id": "champ_a6_high", "name": "Win A6 High championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 9, "xp_idx": 39},
                    {"id": "champ_a5", "name": "Win A5 championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 10, "xp_idx": 40},
                    {"id": "champ_a5_high", "name": "Win A5 High championship", "island": "Ibiza", "points": 155, "type": "toggle", "contest_idx": 11, "xp_idx": 41},
                    {"id": "champ_c3", "name": "Win C3 championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 6, "xp_idx": 42},
                    {"id": "champ_c3_high", "name": "Win C3 High championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 7, "xp_idx": 43},
                    {"id": "champ_b3", "name": "Win B3 championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 12, "xp_idx": 44},
                    {"id": "champ_b3_high", "name": "Win B3 High championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 13, "xp_idx": 45},
                    {"id": "champ_a4", "name": "Win A4 championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 14, "xp_idx": 46},
                    {"id": "champ_a4_high", "name": "Win A4 High championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 15, "xp_idx": 47},
                    {"id": "champ_a3", "name": "Win A3 championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 16, "xp_idx": 48},
                    {"id": "champ_a3_high", "name": "Win A3 High championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 17, "xp_idx": 49},
                    {"id": "champ_a2", "name": "Win A2 championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 18, "xp_idx": 50},
                    {"id": "champ_a2_high", "name": "Win A2 High championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 19, "xp_idx": 51},
                    {"id": "champ_a1", "name": "Win A1 championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 20, "xp_idx": 52},
                    {"id": "champ_a1_high", "name": "Win A1 High championship", "island": "Hawaii", "points": 155, "type": "toggle", "contest_idx": 21, "xp_idx": 53},
                ]
            },
            "cups": {
                "id": "cups",
                "name": "Cups",
                "skill": "competition",
                "objectives": [
                    {"id": "cup_ibiza_1", "name": "Win Ibiza cup Area 1", "island": "Ibiza", "points": 1250, "type": "toggle", "contest_idx": 22, "xp_idx": 54},
                    {"id": "cup_hawaii_1", "name": "Win Hawaii cup Area 1", "island": "Hawaii", "points": 1250, "type": "toggle", "contest_idx": 23, "xp_idx": 55},
                    {"id": "cup_hawaii_2", "name": "Win Hawaii cup Area 2", "island": "Hawaii", "points": 1250, "type": "toggle", "contest_idx": 24, "xp_idx": 56},
                ]
            },
            "duels": {
                "id": "duels",
                "name": "Duel",
                "skill": "competition",
                "objectives": [
                    {"id": "duel_miami", "name": "Win duel against Miami Harris", "island": "Ibiza", "points": 208, "type": "toggle", "duel_idx": 0, "xp_idx": 57},
                    {"id": "duel_ryan", "name": "Win duel against Ryan Wilder", "island": "Ibiza", "points": 208, "type": "toggle", "duel_idx": 1, "xp_idx": 58},
                    {"id": "duel_tess", "name": "Win duel against Tess Wintory", "island": "Hawaii", "points": 208, "type": "toggle", "duel_idx": 2, "xp_idx": 59},
                    {"id": "duel_chris", "name": "Win duel against Chris Wilder", "island": "Hawaii", "points": 208, "type": "toggle", "duel_idx": 3, "xp_idx": 60},
                    {"id": "duel_stuart", "name": "Win duel against Stuart Wintory", "island": "Hawaii", "points": 208, "type": "toggle", "duel_idx": 4, "xp_idx": 61},
                ]
            },
            "multiplayer": {
                "id": "multiplayer",
                "name": "Multiplayer Challenges",
                "skill": "competition",
                "objectives": [
                    {"id": "multi_ranked_50", "name": "Win 50 ranked multi challenges", "island": "Global", "points": 1000, "type": "counter", "target": 50, "stat_field": "MultiRaceWon", "xp_idx": 95},
                ]
            },
            "instant_challenges": {
                "id": "instant_challenges",
                "name": "Instant Challenges",
                "skill": "competition",
                "objectives": [
                    {"id": "instant_cha_50", "name": "Win 50 instant challenges", "island": "Global", "points": 1000, "type": "counter", "target": 50, "stat_field": "ExtraChaWon", "xp_idx": 3},
                ]
            }
        }
    },
    "discovery": {
        "id": "discovery",
        "name": "Discovery",
        "max_points": 14500,
        "max_level": 18,
        "sections": {
            "roads": {
                "id": "roads",
                "name": "Roads",
                "skill": "discovery",
                "objectives": [
                    # Ibiza Area 1
                    {"id": "road_ibiza_1_10", "name": "Discover 10% of roads in Ibiza Area 1", "island": "Ibiza Area 1", "points": 40, "type": "road_tier", "area_idx": 0, "pct_target": 10},
                    {"id": "road_ibiza_1_25", "name": "Discover 25% of roads in Ibiza Area 1", "island": "Ibiza Area 1", "points": 50, "type": "road_tier", "area_idx": 0, "pct_target": 25},
                    {"id": "road_ibiza_1_50", "name": "Discover 50% of roads in Ibiza Area 1", "island": "Ibiza Area 1", "points": 90, "type": "road_tier", "area_idx": 0, "pct_target": 50},
                    {"id": "road_ibiza_1_75", "name": "Discover 75% of roads in Ibiza Area 1", "island": "Ibiza Area 1", "points": 120, "type": "road_tier", "area_idx": 0, "pct_target": 75},
                    {"id": "road_ibiza_1_100", "name": "Discover 100% of roads in Ibiza Area 1", "island": "Ibiza Area 1", "points": 150, "type": "road_tier", "area_idx": 0, "pct_target": 100},
                    # Ibiza Area 2
                    {"id": "road_ibiza_2_10", "name": "Discover 10% of roads in Ibiza Area 2", "island": "Ibiza Area 2", "points": 40, "type": "road_tier", "area_idx": 1, "pct_target": 10},
                    {"id": "road_ibiza_2_25", "name": "Discover 25% of roads in Ibiza Area 2", "island": "Ibiza Area 2", "points": 50, "type": "road_tier", "area_idx": 1, "pct_target": 25},
                    {"id": "road_ibiza_2_50", "name": "Discover 50% of roads in Ibiza Area 2", "island": "Ibiza Area 2", "points": 90, "type": "road_tier", "area_idx": 1, "pct_target": 50},
                    {"id": "road_ibiza_2_75", "name": "Discover 75% of roads in Ibiza Area 2", "island": "Ibiza Area 2", "points": 120, "type": "road_tier", "area_idx": 1, "pct_target": 75},
                    {"id": "road_ibiza_2_100", "name": "Discover 100% of roads in Ibiza Area 2", "island": "Ibiza Area 2", "points": 150, "type": "road_tier", "area_idx": 1, "pct_target": 100},
                    # Hawaii Area 1
                    {"id": "road_hawaii_1_10", "name": "Discover 10% of roads in Hawaii Area 1", "island": "Hawaii Area 1", "points": 40, "type": "road_tier", "area_idx": 2, "pct_target": 10},
                    {"id": "road_hawaii_1_25", "name": "Discover 25% of roads in Hawaii Area 1", "island": "Hawaii Area 1", "points": 50, "type": "road_tier", "area_idx": 2, "pct_target": 25},
                    {"id": "road_hawaii_1_50", "name": "Discover 50% of roads in Hawaii Area 1", "island": "Hawaii Area 1", "points": 90, "type": "road_tier", "area_idx": 2, "pct_target": 50},
                    {"id": "road_hawaii_1_75", "name": "Discover 75% of roads in Hawaii Area 1", "island": "Hawaii Area 1", "points": 120, "type": "road_tier", "area_idx": 2, "pct_target": 75},
                    {"id": "road_hawaii_1_100", "name": "Discover 100% of roads in Hawaii Area 1", "island": "Hawaii Area 1", "points": 150, "type": "road_tier", "area_idx": 2, "pct_target": 100},
                    # Hawaii Area 2
                    {"id": "road_hawaii_2_10", "name": "Discover 10% of roads in Hawaii Area 2", "island": "Hawaii Area 2", "points": 40, "type": "road_tier", "area_idx": 3, "pct_target": 10},
                    {"id": "road_hawaii_2_25", "name": "Discover 25% of roads in Hawaii Area 2", "island": "Hawaii Area 2", "points": 50, "type": "road_tier", "area_idx": 3, "pct_target": 25},
                    {"id": "road_hawaii_2_50", "name": "Discover 50% of roads in Hawaii Area 2", "island": "Hawaii Area 2", "points": 90, "type": "road_tier", "area_idx": 3, "pct_target": 50},
                    {"id": "road_hawaii_2_75", "name": "Discover 75% of roads in Hawaii Area 2", "island": "Hawaii Area 2", "points": 120, "type": "road_tier", "area_idx": 3, "pct_target": 75},
                    {"id": "road_hawaii_2_100", "name": "Discover 100% of roads in Hawaii Area 2", "island": "Hawaii Area 2", "points": 150, "type": "road_tier", "area_idx": 3, "pct_target": 100},
                    # Hawaii Area 3
                    {"id": "road_hawaii_3_10", "name": "Discover 10% of roads in Hawaii Area 3", "island": "Hawaii Area 3", "points": 40, "type": "road_tier", "area_idx": 4, "pct_target": 10},
                    {"id": "road_hawaii_3_25", "name": "Discover 25% of roads in Hawaii Area 3", "island": "Hawaii Area 3", "points": 50, "type": "road_tier", "area_idx": 4, "pct_target": 25},
                    {"id": "road_hawaii_3_50", "name": "Discover 50% of roads in Hawaii Area 3", "island": "Hawaii Area 3", "points": 90, "type": "road_tier", "area_idx": 4, "pct_target": 50},
                    {"id": "road_hawaii_3_75", "name": "Discover 75% of roads in Hawaii Area 3", "island": "Hawaii Area 3", "points": 120, "type": "road_tier", "area_idx": 4, "pct_target": 75},
                    {"id": "road_hawaii_3_100", "name": "Discover 100% of roads in Hawaii Area 3", "island": "Hawaii Area 3", "points": 150, "type": "road_tier", "area_idx": 4, "pct_target": 100},
                    # Hawaii Area 4
                    {"id": "road_hawaii_4_10", "name": "Discover 10% of roads in Hawaii Area 4", "island": "Hawaii Area 4", "points": 40, "type": "road_tier", "area_idx": 5, "pct_target": 10},
                    {"id": "road_hawaii_4_25", "name": "Discover 25% of roads in Hawaii Area 4", "island": "Hawaii Area 4", "points": 50, "type": "road_tier", "area_idx": 5, "pct_target": 25},
                    {"id": "road_hawaii_4_50", "name": "Discover 50% of roads in Hawaii Area 4", "island": "Hawaii Area 4", "points": 90, "type": "road_tier", "area_idx": 5, "pct_target": 50},
                    {"id": "road_hawaii_4_75", "name": "Discover 75% of roads in Hawaii Area 4", "island": "Hawaii Area 4", "points": 120, "type": "road_tier", "area_idx": 5, "pct_target": 75},
                    {"id": "road_hawaii_4_100", "name": "Discover 100% of roads in Hawaii Area 4", "island": "Hawaii Area 4", "points": 150, "type": "road_tier", "area_idx": 5, "pct_target": 100},
                ]
            },
            "events": {
                "id": "events",
                "name": "Events",
                "skill": "discovery",
                "objectives": [
                    {"id": "ev_ibiza_1_20", "name": "Win 20 events in Ibiza Area 1", "island": "Ibiza Area 1", "points": 500, "type": "toggle", "area_idx": 0, "is_add": False, "xp_idx": 143},
                    {"id": "ev_ibiza_1_add", "name": "Win 4 additional events in Ibiza Area 1", "island": "Ibiza Area 1", "points": 260, "type": "toggle", "area_idx": 0, "is_add": True, "xp_idx": 191},
                    {"id": "ev_ibiza_2_20", "name": "Win 20 events in Ibiza Area 2", "island": "Ibiza Area 2", "points": 500, "type": "toggle", "area_idx": 1, "is_add": False, "xp_idx": 144},
                    {"id": "ev_ibiza_2_add", "name": "Win 4 additional events in Ibiza Area 2", "island": "Ibiza Area 2", "points": 260, "type": "toggle", "area_idx": 1, "is_add": True, "xp_idx": 192},
                    {"id": "ev_hawaii_1_15", "name": "Win 15 events in Hawaii Area 1", "island": "Hawaii Area 1", "points": 500, "type": "toggle", "area_idx": 2, "is_add": False, "xp_idx": 145},
                    {"id": "ev_hawaii_1_add", "name": "Win 3 additional events in Hawaii Area 1", "island": "Hawaii Area 1", "points": 260, "type": "toggle", "area_idx": 2, "is_add": True, "xp_idx": 193},
                    {"id": "ev_hawaii_2_15", "name": "Win 15 events in Hawaii Area 2", "island": "Hawaii Area 2", "points": 500, "type": "toggle", "area_idx": 3, "is_add": False, "xp_idx": 146},
                    {"id": "ev_hawaii_2_add", "name": "Win 3 additional events in Hawaii Area 2", "island": "Hawaii Area 2", "points": 260, "type": "toggle", "area_idx": 3, "is_add": True, "xp_idx": 194},
                    {"id": "ev_hawaii_3_15", "name": "Win 15 events in Hawaii Area 3", "island": "Hawaii Area 3", "points": 500, "type": "toggle", "area_idx": 4, "is_add": False, "xp_idx": 130},
                    {"id": "ev_hawaii_3_add", "name": "Win 3 additional events in Hawaii Area 3", "island": "Hawaii Area 3", "points": 260, "type": "toggle", "area_idx": 4, "is_add": True, "xp_idx": 195},
                    {"id": "ev_hawaii_4_15", "name": "Win 15 events in Hawaii Area 4", "island": "Hawaii Area 4", "points": 500, "type": "toggle", "area_idx": 5, "is_add": False, "xp_idx": 130},
                    {"id": "ev_hawaii_4_add", "name": "Win 3 additional events in Hawaii Area 4", "island": "Hawaii Area 4", "points": 260, "type": "toggle", "area_idx": 5, "is_add": True, "xp_idx": 196},
                ]
            },
            "wrecks": {
                "id": "wrecks",
                "name": "Treasure Hunt",
                "skill": "discovery",
                "objectives": [
                    {"id": "wr_ibiza_1_10", "name": "Find 10 wrecks in Ibiza Area 1", "island": "Ibiza Area 1", "points": 250, "type": "toggle", "area_idx": 0, "is_add": False, "xp_idx": 147},
                    {"id": "wr_ibiza_1_add", "name": "Find 4 additional wrecks in Ibiza Area 1", "island": "Ibiza Area 1", "points": 220, "type": "toggle", "area_idx": 0, "is_add": True, "xp_idx": 197},
                    {"id": "wr_ibiza_2_10", "name": "Find 10 wrecks in Ibiza Area 2", "island": "Ibiza Area 2", "points": 250, "type": "toggle", "area_idx": 1, "is_add": False, "xp_idx": 148},
                    {"id": "wr_ibiza_2_add", "name": "Find 4 additional wrecks in Ibiza Area 2", "island": "Ibiza Area 2", "points": 220, "type": "toggle", "area_idx": 1, "is_add": True, "xp_idx": 198},
                    {"id": "wr_hawaii_1_10", "name": "Find 10 wrecks in Hawaii Area 1", "island": "Hawaii Area 1", "points": 250, "type": "toggle", "area_idx": 2, "is_add": False, "xp_idx": 149},
                    {"id": "wr_hawaii_1_add", "name": "Find 3 additional wrecks in Hawaii Area 1", "island": "Hawaii Area 1", "points": 220, "type": "toggle", "area_idx": 2, "is_add": True, "xp_idx": 199},
                    {"id": "wr_hawaii_2_10", "name": "Find 10 wrecks in Hawaii Area 2", "island": "Hawaii Area 2", "points": 250, "type": "toggle", "area_idx": 3, "is_add": False, "xp_idx": 150},
                    {"id": "wr_hawaii_2_add", "name": "Find 3 additional wrecks in Hawaii Area 2", "island": "Hawaii Area 2", "points": 220, "type": "toggle", "area_idx": 3, "is_add": True, "xp_idx": 200},
                    {"id": "wr_hawaii_3_10", "name": "Find 10 wrecks in Hawaii Area 3", "island": "Hawaii Area 3", "points": 250, "type": "toggle", "area_idx": 4, "is_add": False, "xp_idx": 151},
                    {"id": "wr_hawaii_3_add", "name": "Find 3 additional wrecks in Hawaii Area 3", "island": "Hawaii Area 3", "points": 220, "type": "toggle", "area_idx": 4, "is_add": True, "xp_idx": 201},
                    {"id": "wr_hawaii_4_10", "name": "Find 10 wrecks in Hawaii Area 4", "island": "Hawaii Area 4", "points": 250, "type": "toggle", "area_idx": 5, "is_add": False, "xp_idx": 189},
                    {"id": "wr_hawaii_4_add", "name": "Find 3 additional wrecks in Hawaii Area 4", "island": "Hawaii Area 4", "points": 220, "type": "toggle", "area_idx": 5, "is_add": True, "xp_idx": 202},
                ]
            },
            "photographer": {
                "id": "photographer",
                "name": "Photographer",
                "skill": "discovery",
                "objectives": [
                    {"id": "photo_ibiza_20", "name": "Find the 20 viewpoints on Ibiza", "island": "Ibiza", "points": 250, "type": "toggle", "island_idx": 0, "count": 20, "xp_idx": 129},
                    {"id": "photo_hawaii_20", "name": "Find the 20 viewpoints on Hawaii", "island": "Hawaii", "points": 250, "type": "toggle", "island_idx": 1, "count": 20, "xp_idx": 131},
                ]
            }
        }
    },
    "collection": {
        "id": "collection",
        "name": "Collection",
        "max_points": 10000,
        "max_level": 15,
        "sections": {
            "vehicles": {
                "id": "vehicles",
                "name": "Vehicles",
                "skill": "collection",
                "objectives": [
                    {"id": "car_1", "name": "Own 1 vehicle", "island": "Global", "points": 75, "type": "counter_step", "target": 1, "group": "cars", "xp_idx": 0},
                    {"id": "car_3", "name": "Own 3 different vehicles", "island": "Global", "points": 175, "type": "counter_step", "target": 3, "group": "cars", "xp_idx": 1},
                    {"id": "car_6", "name": "Own 6 different vehicles", "island": "Global", "points": 350, "type": "counter_step", "target": 6, "group": "cars", "xp_idx": 2},
                    {"id": "car_10", "name": "Own 10 different vehicles", "island": "Global", "points": 500, "type": "counter_step", "target": 10, "group": "cars", "xp_idx": 4},
                    {"id": "car_15", "name": "Own 15 different vehicles", "island": "Global", "points": 600, "type": "counter_step", "target": 15, "group": "cars", "xp_idx": 5},
                    {"id": "car_20", "name": "Own 20 different vehicles", "island": "Global", "points": 700, "type": "counter_step", "target": 20, "group": "cars", "xp_idx": 11},
                    {"id": "car_25", "name": "Own 25 different vehicles", "island": "Global", "points": 750, "type": "counter_step", "target": 25, "group": "cars", "xp_idx": 12},
                    {"id": "car_30", "name": "Own 30 different vehicles", "island": "Global", "points": 800, "type": "counter_step", "target": 30, "group": "cars", "xp_idx": 13},
                    {"id": "car_40", "name": "Own 40 different vehicles", "island": "Global", "points": 950, "type": "counter_step", "target": 40, "group": "cars", "xp_idx": 14},
                    {"id": "car_50", "name": "Own 50 different vehicles", "island": "Global", "points": 1350, "type": "counter_step", "target": 50, "group": "cars", "xp_idx": 15},
                ]
            },
            "houses_furniture": {
                "id": "houses_furniture",
                "name": "Houses and Furniture",
                "skill": "collection",
                "objectives": [
                    {"id": "house_1", "name": "Own 1 house", "island": "Global", "points": 75, "type": "counter_step", "target": 1, "group": "houses", "xp_idx": 138},
                    {"id": "house_3", "name": "Own 3 houses", "island": "Global", "points": 175, "type": "counter_step", "target": 3, "group": "houses", "xp_idx": 188},
                    {"id": "house_6", "name": "Own 6 houses", "island": "Global", "points": 400, "type": "counter_step", "target": 6, "group": "houses", "xp_idx": 16},
                    {"id": "house_10", "name": "Own 10 houses", "island": "Global", "points": 800, "type": "counter_step", "target": 10, "group": "houses", "xp_idx": 16},
                    {"id": "house_15", "name": "Own 15 houses", "island": "Global", "points": 1200, "type": "counter_step", "target": 15, "group": "houses", "xp_idx": 16},
                    {"id": "furn_5", "name": "Own 5 pieces of furniture", "island": "Global", "points": 30, "type": "counter_step", "target": 5, "group": "furnitures", "xp_idx": 16},
                    {"id": "furn_10", "name": "Own 10 pieces of furniture", "island": "Global", "points": 70, "type": "counter_step", "target": 10, "group": "furnitures", "xp_idx": 16},
                    {"id": "furn_20", "name": "Own 20 pieces of furniture", "island": "Global", "points": 100, "type": "counter_step", "target": 20, "group": "furnitures", "xp_idx": 16},
                    {"id": "furn_35", "name": "Own 35 pieces of furniture", "island": "Global", "points": 200, "type": "counter_step", "target": 35, "group": "furnitures", "xp_idx": 16},
                ]
            },
            "clothes": {
                "id": "clothes",
                "name": "Clothes",
                "skill": "collection",
                "objectives": [
                    {"id": "clothes_5", "name": "Own 5 items of clothing", "island": "Global", "points": 30, "type": "counter_step", "target": 5, "group": "clothes", "xp_idx": 100},
                    {"id": "clothes_10", "name": "Own 10 items of clothing", "island": "Global", "points": 70, "type": "counter_step", "target": 10, "group": "clothes", "xp_idx": 101},
                    {"id": "clothes_20", "name": "Own 20 items of clothing", "island": "Global", "points": 100, "type": "counter_step", "target": 20, "group": "clothes", "xp_idx": 102},
                    {"id": "clothes_30", "name": "Own 30 items of clothing", "island": "Global", "points": 150, "type": "counter_step", "target": 30, "group": "clothes", "xp_idx": 103},
                ]
            },
            "haircuts": {
                "id": "haircuts",
                "name": "Haircuts",
                "skill": "collection",
                "objectives": [
                    {"id": "hair_2", "name": "Buy 2 different haircuts", "island": "Global", "points": 20, "type": "counter_step", "target": 2, "group": "haircuts", "xp_idx": 6},
                    {"id": "hair_5", "name": "Buy 5 different haircuts", "island": "Global", "points": 50, "type": "counter_step", "target": 5, "group": "haircuts", "xp_idx": 6},
                    {"id": "hair_10", "name": "Buy 10 different haircuts", "island": "Global", "points": 80, "type": "counter_step", "target": 10, "group": "haircuts", "xp_idx": 6},
                ]
            },
            "cosmetic_clinic": {
                "id": "cosmetic_clinic",
                "name": "Cosmetic clinic",
                "skill": "collection",
                "objectives": [
                    {"id": "clinic_4", "name": "Have 4 operations in Cosmetic Clinic", "island": "Global", "points": 100, "type": "counter", "target": 4, "stat_field": "NbSurgeries", "store_in_driver": True, "xp_idx": 114},
                ]
            },
            "stickers": {
                "id": "stickers",
                "name": "Stickers Shop",
                "skill": "collection",
                "objectives": [
                    {"id": "stickers_2", "name": "Buy a sticker from 2 different sticker boards", "island": "Global", "points": 10, "type": "counter_step", "target": 2, "group": "stickers", "xp_idx": 156},
                    {"id": "stickers_5", "name": "Buy a sticker from 5 different sticker boards", "island": "Global", "points": 30, "type": "counter_step", "target": 5, "group": "stickers", "xp_idx": 157},
                    {"id": "stickers_10", "name": "Buy a sticker from 10 different sticker boards", "island": "Global", "points": 60, "type": "counter_step", "target": 10, "group": "stickers", "xp_idx": 158},
                ]
            }
        }
    },
    "social": {
        "id": "social",
        "name": "Social",
        "max_points": 10000,
        "max_level": 15,
        "sections": {
            "friends": {
                "id": "friends",
                "name": "Friends",
                "skill": "social",
                "objectives": [
                    {"id": "friends_5", "name": "Have 5 friends in TDU2", "island": "Global", "points": 100, "type": "counter_linear", "target": 5, "pts_per_unit": 20, "stat_field": "NbFriendsJoined", "xp_idx": 8},
                    {"id": "friends_invite_10", "name": "Invite 10 friends to your home", "island": "Global", "points": 200, "type": "counter_linear", "target": 10, "pts_per_unit": 20, "stat_field": "NbFriendsInvited", "xp_idx": 9},
                ]
            },
            "club": {
                "id": "club",
                "name": "Club",
                "skill": "social",
                "objectives": [
                    {"id": "club_member", "name": "Become a Club member", "island": "Global", "points": 100, "type": "toggle_stat", "target": 1, "stat_field": "NbClubJoiner", "xp_idx": 10},
                    {"id": "club_internal_50", "name": "Play 50 challenges against members of your Club", "island": "Global", "points": 1000, "type": "counter_linear", "target": 50, "pts_per_unit": 20, "stat_field": "ClubWon", "xp_idx": 133},
                    {"id": "club_vs_50", "name": "Play 50 Versus Club challenges", "island": "Global", "points": 2500, "type": "counter_linear", "target": 50, "pts_per_unit": 50, "stat_field": "InterClubWonByTeam", "xp_idx": 134},
                    {"id": "club_level_2", "name": "Reach Club level 2", "island": "Global", "points": 200, "type": "rank_step", "target_rank": 2, "xp_idx": 136},
                    {"id": "club_level_3", "name": "Reach Club level 3", "island": "Global", "points": 500, "type": "rank_step", "target_rank": 3, "xp_idx": 137},
                ]
            },
            "crc": {
                "id": "crc",
                "name": "C.R.C.",
                "skill": "social",
                "objectives": [
                    {"id": "crc_played_25", "name": "Play 25 challenges in C.R.C.", "island": "Global", "points": 1000, "type": "counter_linear", "target": 25, "pts_per_unit": 40, "stat_field": "CrcChaRuns", "xp_idx": 176},
                    {"id": "crc_uploaded_15", "name": "Upload 15 challenges in C.R.C.", "island": "Global", "points": 300, "type": "counter_linear", "target": 15, "pts_per_unit": 20, "stat_field": "CrcChaWon", "xp_idx": 177},
                ]
            },
            "chase": {
                "id": "chase",
                "name": "Chase",
                "skill": "social",
                "objectives": [
                    {"id": "chase_cop_20", "name": "Play 'Chase mode' 20 times as a cop", "island": "Global", "points": 500, "type": "counter_linear", "target": 20, "pts_per_unit": 25, "stat_field": "ChaseHunterWon", "xp_idx": 135},
                    {"id": "chase_outlaw_20", "name": "Play 'Chase mode' 20 times as an outlaw", "island": "Global", "points": 500, "type": "counter_linear", "target": 20, "pts_per_unit": 25, "stat_field": "ChasePreyWon", "xp_idx": 96},
                    {"id": "chase_win_20", "name": "Win 20 chases", "island": "Global", "points": 900, "type": "chase_wins", "target": 20, "xp_idx": 19},
                ]
            },
            "coop": {
                "id": "coop",
                "name": "Co-op Challenges",
                "skill": "social",
                "objectives": [
                    {"id": "coop_ftl_30", "name": "Play 'Follow the leader' 30 times", "island": "Global", "points": 900, "type": "counter_linear", "target": 30, "pts_per_unit": 30, "stat_field": "FTLWon", "xp_idx": 152},
                    {"id": "coop_kyd_30", "name": "Play 'Keep your distance' 30 times", "island": "Global", "points": 900, "type": "counter_linear", "target": 30, "pts_per_unit": 30, "stat_field": "KYDWon", "xp_idx": 153},
                    {"id": "coop_codrive_20", "name": "Play in Co-Driving mode for at least 2 minutes, 20 times", "island": "Global", "points": 400, "type": "counter_linear", "target": 20, "pts_per_unit": 20, "stat_field": "NbCodrivingAsPilot", "xp_idx": 154},
                ]
            }
        }
    }
}


class TDU2LevelEngine:
    """Core progression controller for reading, editing, recalculating, and saving TDU2 save files."""

    def __init__(self, profile_path: str, profile_name: Optional[str] = None):
        self.profile_path = Path(profile_path)
        if profile_name:
            self.profile_name = profile_name
        else:
            self.profile_name = self.detect_profile_name(self.profile_path)

        self.raw_data: Optional[bytes] = None
        self.template_xmbf: Optional[bytes] = None
        self.raw_footer: Optional[bytes] = None
        self.save_filename: Optional[str] = None
        self.data_dict: Dict[str, Any] = {}

        self.load()

    @staticmethod
    def detect_profile_name(path: Path) -> str:
        """Find profile name from path like .../savegame/<ProfileName>/PLAYERSAVE/DATA."""
        parts = path.resolve().parts
        for i, part in enumerate(parts):
            if part.lower() == "savegame" and i + 1 < len(parts):
                return parts[i + 1]
            if part.lower() == "playersave" and i > 0:
                return parts[i - 1]
        return path.parent.name

    def load(self):
        """Decrypts and decodes the save file."""
        if not tdu2_save_tool:
            raise RuntimeError("tdu2_save_tool module is not available.")

        with open(self.profile_path, "rb") as f:
            self.raw_data = f.read()

        filename_str = self.profile_path.name
        self.template_xmbf, self.raw_footer, self.save_filename = tdu2_save_tool.decrypt_save_file(
            self.raw_data, self.profile_name, filename_str
        )
        _, self.data_dict = tdu2_save_tool.decode_xmbf_to_dict(self.template_xmbf)

    def get_overview_data(self) -> Dict[str, Any]:
        """Returns player summary and vital stats."""
        driver = self.data_dict.get("Driver", {})
        pl = self.data_dict.get("PlayerLevels", {})
        stats = self.data_dict.get("StatisticsData", {})

        # Base game progression
        skill_scores = self.calculate_skill_points()

        comp_info = level_progress_info(skill_scores["competition"], is_discovery=False)
        disc_info = level_progress_info(skill_scores["discovery"], is_discovery=True)
        coll_info = level_progress_info(skill_scores["collection"], is_discovery=False)
        soc_info = level_progress_info(skill_scores["social"], is_discovery=False)

        base_level = comp_info["level"] + disc_info["level"] + coll_info["level"] + soc_info["level"]

        # Casino progression
        casino_scores = self.calculate_casino_skill_points()
        cas_comp_info = cc.casino_level_progress_info("competition", casino_scores["competition"])
        cas_disc_info = cc.casino_level_progress_info("discovery", casino_scores["discovery"])
        cas_coll_info = cc.casino_level_progress_info("collection", casino_scores["collection"])
        cas_soc_info = cc.casino_level_progress_info("social", casino_scores["social"])

        casino_level = cas_comp_info["level"] + cas_disc_info["level"] + cas_coll_info["level"] + cas_soc_info["level"]
        total_casino_pts = casino_scores["competition"] + casino_scores["discovery"] + casino_scores["collection"] + casino_scores["social"]

        global_level = base_level + casino_level
        # Cap at 73 (63 base + 10 casino)
        global_level = min(73, max(1, global_level))

        # Cars count and houses count
        garage_list = self.data_dict.get("Garage", [])
        garage_cars = len(garage_list) if isinstance(garage_list, list) else 0
        mh = self.data_dict.get("MyHouse", {})
        houses_count = len(mh.get("House", [])) if isinstance(mh, dict) else 0

        casino_container = self.data_dict.get("Casino", {})
        casino_prog = casino_container.get("CasinoProgressionSave", {}) if isinstance(casino_container, dict) else {}

        return {
            "profile_name": self.profile_name,
            "global_level": global_level,
            "base_level": base_level,
            "casino_level": casino_level,
            "money": driver.get("Money", 0),
            "cars_owned": garage_cars,
            "houses_owned": houses_count,
            "club_rank": driver.get("LastSeenClubRank", 0),
            "skills": {
                "competition": comp_info,
                "discovery": disc_info,
                "collection": coll_info,
                "social": soc_info,
            },
            "casino_summary": {
                "level": casino_level,
                "max_level": 10,
                "points": total_casino_pts,
                "max_points": 7000,
                "percent": round((total_casino_pts / 7000.0) * 100.0, 1) if total_casino_pts > 0 else 0.0,
                "is_vip": casino_level >= 5 or bool(casino_prog.get("_vip_status", False)),
                "is_ace": casino_level >= 10 or bool(casino_container.get("_hasSeenCasinoACEStatusCinematic", False)),
            },
            "casino_skills": {
                "competition": cas_comp_info,
                "discovery": cas_disc_info,
                "collection": cas_coll_info,
                "social": cas_soc_info,
            },
            "roads_summary": {
                "unlocked": pl.get("AreaRoadsUnlocked", [0] * 6),
                "total": pl.get("AreaTotalRoads", AREA_MAX_ROADS),
            }
        }

    def get_full_state(self) -> Dict[str, Any]:
        """Extracts complete objective tree with current values and fulfillment states."""
        overview = self.get_overview_data()
        skills_data = {}

        for skill_id, skill_meta in OBJECTIVES_CATALOG.items():
            skill_dict = {
                "id": skill_id,
                "name": skill_meta["name"],
                "max_points": skill_meta["max_points"],
                "max_level": skill_meta["max_level"],
                "sections": {}
            }

            for sec_id, sec_meta in skill_meta["sections"].items():
                sec_dict = {
                    "id": sec_id,
                    "name": sec_meta["name"],
                    "skill": skill_id,
                    "objectives": []
                }

                for obj in sec_meta["objectives"]:
                    obj_state = self._extract_objective_state(obj)
                    sec_dict["objectives"].append(obj_state)

                skill_dict["sections"][sec_id] = sec_dict
            skills_data[skill_id] = skill_dict

        # Extract Casino skills and sections
        casino_skills_data = {}
        for skill_id, skill_meta in cc.CASINO_CATALOG.items():
            skill_dict = {
                "id": skill_id,
                "name": skill_meta["name"],
                "max_points": skill_meta["max_points"],
                "max_level": skill_meta["max_level"],
                "sections": {}
            }

            for sec_id, sec_meta in skill_meta["sections"].items():
                sec_dict = {
                    "id": sec_id,
                    "name": sec_meta["name"],
                    "skill": skill_id,
                    "objectives": []
                }

                for obj in sec_meta["objectives"]:
                    obj_state = self._extract_casino_objective_state(obj)
                    sec_dict["objectives"].append(obj_state)

                skill_dict["sections"][sec_id] = sec_dict
            casino_skills_data[skill_id] = skill_dict

        return {
            "overview": overview,
            "skills": skills_data,
            "casino_skills": casino_skills_data
        }

    def _extract_objective_state(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Inspects save file records to extract objective completion state and numeric values."""
        obj_id = obj["id"]
        obj_type = obj.get("type")
        points = obj.get("points", 0)

        completed = False
        current_value = 0
        target_value = obj.get("target", 1)

        lic = self.data_dict.get("PlayerLicenses", {})
        stats = self.data_dict.get("StatisticsData", {})
        driver = self.data_dict.get("Driver", {})
        pl = self.data_dict.get("PlayerLevels", {})

        rewards = self.data_dict.get("Rewards", {})
        event_xps = rewards.get("EventXPs", [])
        has_xps = bool(event_xps and any(x > 0 for x in event_xps))

        if has_xps and "xp_idx" in obj:
            idx = obj["xp_idx"]
            ev_val = event_xps[idx] if idx < len(event_xps) else 0
            max_val = MASTER_MAX_EVENT_XPS[idx] if idx < len(MASTER_MAX_EVENT_XPS) else 1
            if max_val <= 0:
                max_val = 1

            if obj_type == "toggle":
                completed = ev_val >= max_val
                current_value = ev_val
                target_value = max_val
            elif obj_type in ("counter", "counter_linear"):
                current_value = ev_val
                target_value = obj["target"]
                completed = current_value >= target_value
            elif obj_type == "counter_step":
                completed = ev_val >= max_val
                target_value = obj["target"]
                current_value = target_value if completed else 0
            elif obj_type in ("toggle_stat", "rank_step", "chase_wins"):
                completed = ev_val >= max_val
                current_value = ev_val
                target_value = max_val

        elif obj_type == "toggle":
            if "license_idx" in obj:
                idx = obj["license_idx"]
                licenses = lic.get("Licenses", [])
                if idx < len(licenses):
                    l = licenses[idx]
                    completed = bool(l.get("Passed", False) and l.get("PhotoIndex", -1) >= 0)
            elif "contest_idx" in obj:
                idx = obj["contest_idx"]
                contests = lic.get("Contests", [])
                if idx < len(contests):
                    c = contests[idx]
                    challenges = c.get("Challenge", [])
                    all_tries = all(ch.get("Try", False) for ch in challenges) if challenges else True
                    completed = bool(c.get("Passed", False) and c.get("Cup", -1) > 0 and all_tries)
            elif "duel_idx" in obj:
                idx = obj["duel_idx"]
                reward_cars = self.data_dict.get("Rewards", {}).get("RewardCars", [])
                solo_won = stats.get("SoloWon", 0)
                completed = bool(idx < len(reward_cars) and reward_cars[idx] > 0 and solo_won >= (idx + 1))
            elif "area_idx" in obj and obj.get("id", "").startswith("ev_"):
                # Events in area
                ev_save = self.data_dict.get("EventsSave", {})
                events = ev_save.get("Events", [])
                dlc_events = ev_save.get("DLCEvents", [])
                won_count = sum(1 for e in events if e.get("State") == 5) + sum(1 for e in dlc_events if e.get("State") == 5)
                area_idx = obj["area_idx"]
                cruising = pl.get("CruisingLevels", {}).get(f"Area_{area_idx}", 0)
                if obj.get("is_add"):
                    completed = (cruising >= (AREA_MAX_CRUISING_PTS[area_idx] * 0.8)) or (won_count >= 150)
                else:
                    completed = (cruising >= (AREA_MAX_CRUISING_PTS[area_idx] * 0.5)) or (won_count >= 50)
            elif "area_idx" in obj and obj.get("id", "").startswith("wr_"):
                # Treasure hunt wrecks
                wrecks = self.data_dict.get("Wrecks", {})
                area_idx = obj["area_idx"]
                if area_idx in (0, 1):
                    w_list = wrecks.get("Wrecks_IBIZA", [])
                else:
                    w_list = wrecks.get("Wrecks_HAWAI", [])
                taken_count = sum(1 for w in w_list if w.get("Taken", False))
                if obj.get("is_add"):
                    completed = taken_count >= (14 if area_idx in (0, 1) else 13)
                else:
                    completed = taken_count >= 10
            elif "island_idx" in obj:
                # Viewpoints (Photographer)
                photos = self.data_dict.get("PhotosGP", {}).get("PhotosGP", [])
                island_idx = obj["island_idx"]
                start = 0 if island_idx == 0 else 20
                end = 20 if island_idx == 0 else 40
                taken = sum(1 for p in photos[start:end] if p.get("Taken", False))
                current_value = taken
                target_value = 20
                completed = taken >= 20

        elif obj_type == "road_tier":
            area_idx = obj["area_idx"]
            target_pct = obj["pct_target"]
            unlocked = pl.get("AreaRoadsUnlocked", [0] * 6)
            totals = pl.get("AreaTotalRoads", AREA_MAX_ROADS)
            u = unlocked[area_idx] if area_idx < len(unlocked) else 0
            t = totals[area_idx] if area_idx < len(totals) and totals[area_idx] > 0 else AREA_MAX_ROADS[area_idx]
            cur_pct = round((u / t) * 100.0, 1)
            current_value = cur_pct
            target_value = target_pct
            completed = cur_pct >= target_pct

        elif obj_type == "counter":
            field = obj["stat_field"]
            if obj.get("store_in_driver"):
                val = driver.get(field, 0)
            else:
                if field == "MultiRaceWon":
                    val = max(stats.get("MultiRaceWon", 0), stats.get("MultiRankedWon", 0))
                elif field == "ExtraChaWon":
                    val = max(stats.get("ExtraChaWon", 0), stats.get("ICEvsBotWon", 0))
                else:
                    val = stats.get(field, 0)
            current_value = val
            target_value = obj["target"]
            completed = current_value >= target_value

        elif obj_type == "counter_linear":
            field = obj["stat_field"]
            val = stats.get(field, 0)
            current_value = val
            target_value = obj["target"]
            completed = current_value >= target_value

        elif obj_type == "counter_step":
            grp = obj.get("group")
            target_value = obj["target"]
            if grp == "cars":
                val = stats.get("NbCarDealerBuyCar", 0)
                g_list = self.data_dict.get("Garage", [])
                slots = len(g_list) if isinstance(g_list, list) else 0
                current_value = max(val, slots)
            elif grp == "houses":
                val = stats.get("NbHouseBought", 0)
                mh = self.data_dict.get("MyHouse", {})
                h_count = len(mh.get("House", [])) if isinstance(mh, dict) else 0
                current_value = max(val, h_count)
            elif grp == "furnitures":
                mh = self.data_dict.get("MyHouse", {})
                current_value = mh.get("NbBoughtFurnitures", 0) if isinstance(mh, dict) else 0
            elif grp == "clothes":
                current_value = stats.get("NbClothesBought", 0)
            elif grp == "haircuts":
                current_value = stats.get("NbHaircutsBought", driver.get("NbHaircuts", 0))
            elif grp == "stickers":
                current_value = stats.get("NbStickersBought", 0)
            completed = current_value >= target_value

        elif obj_type == "toggle_stat":
            field = obj["stat_field"]
            val = stats.get(field, 0)
            current_value = val
            target_value = obj["target"]
            completed = current_value >= target_value

        elif obj_type == "rank_step":
            rank = driver.get("LastSeenClubRank", 0)
            target_rank = obj["target_rank"]
            current_value = rank
            target_value = target_rank
            completed = rank >= target_rank

        elif obj_type == "chase_wins":
            ch = self.data_dict.get("Chase", {})
            wins = ch.get("PoliceVictories", 0) + ch.get("OutlawVictories", 0)
            current_value = wins
            target_value = obj["target"]
            completed = wins >= target_value

        earned_pts = points if completed else 0
        if obj_type == "counter_linear" and not completed and obj.get("pts_per_unit"):
            earned_pts = min(points, current_value * obj["pts_per_unit"])

        return {
            "id": obj_id,
            "name": obj["name"],
            "island": obj.get("island", "Global"),
            "points": points,
            "earned_points": earned_pts,
            "completed": completed,
            "current_value": current_value,
            "target_value": target_value,
            "type": obj_type
        }

    def _extract_casino_objective_state(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts completion state and numeric values for a Casino objective."""
        casino = self.data_dict.setdefault("Casino", {})
        prog = casino.setdefault("CasinoProgressionSave", {})

        obj_id = obj["id"]
        obj_type = obj.get("type")
        points = obj.get("points", 0)
        target = obj.get("target", 1)

        completed = False
        current_value = 0

        sms = prog.get("_array_save_slotmachines", [])
        rouls = prog.get("_array_save_roulettes", [])
        pcgs = prog.get("_array_save_poker_cashgame", [])
        sng_pubs = prog.get("_array_save_poker_sitandgo_public", [])
        sng_privs = prog.get("_array_save_poker_sitandgo_private", [])
        sats = prog.get("_array_save_poker_satellite", [])

        if obj_type == "slot_prize":
            idx = obj.get("slot_idx", 0)
            if idx < len(sms):
                won_arr = sms[idx].get("_p_won_combination_array", [])
                non_zeros = sum(1 for x in won_arr if x > 0)
                current_value = non_zeros
                completed = non_zeros >= target
        elif obj_type == "slot_jackpot":
            jp = sum(s.get("_jackpot_count", 0) for s in sms)
            jp_bits = any(s.get("_jackpot_won_bitfield", 0) > 0 for s in sms)
            current_value = jp if jp > 0 else (1 if jp_bits else 0)
            completed = (jp >= target) or jp_bits
        elif obj_type == "slot_money":
            m = sum(s.get("_money_won", 0) for s in sms)
            current_value = m
            completed = m >= target
        elif obj_type == "poker_win_hands":
            w = max((p.get("_win_count", 0) for p in pcgs), default=0)
            current_value = w
            completed = w >= target
        elif obj_type == "poker_streak":
            stk = max((p.get("_best_win_in_a_row", 0) for p in pcgs), default=0)
            current_value = stk
            completed = stk >= target
        elif obj_type == "poker_hand_combo":
            c_idx = obj.get("combo_idx", 0)
            val = 0
            for table in (pcgs + sng_pubs + sng_privs + sats):
                won_arr = table.get("_p_won_combination_array", [])
                if c_idx < len(won_arr) and won_arr[c_idx] > 0:
                    val = max(val, won_arr[c_idx])
            current_value = val
            completed = val >= target
        elif obj_type == "poker_money":
            m = sum(p.get("_money_won", 0) for p in pcgs)
            current_value = m
            completed = m >= target
        elif obj_type == "tourn_rank":
            sat_idx = obj.get("sat_idx", 0)
            max_rank = obj.get("max_rank", 1)
            ranks = sats[sat_idx].get("_ranks_count", []) if sat_idx < len(sats) else []
            wins = sum(ranks[:max_rank])
            current_value = wins
            completed = wins >= target
        elif obj_type == "tourn_total_wins":
            w = sum(s.get("_win_count", 0) for s in sats)
            current_value = w
            completed = w >= target
        elif obj_type == "tourn_money":
            m = sum(s.get("_money_won", 0) for s in sats)
            current_value = m
            completed = m >= target
        elif obj_type == "tourn_played":
            sat_idx = obj.get("sat_idx", 0)
            pl = sats[sat_idx].get("_play_count", 0) if sat_idx < len(sats) else 0
            current_value = pl
            completed = pl >= target
        elif obj_type == "tourn_total_played":
            pl = sum(s.get("_play_count", 0) for s in sats)
            current_value = pl
            completed = pl >= target
        elif obj_type == "roul_streak":
            stk = max((r.get("_best_win_in_a_row", 0) for r in rouls), default=0)
            current_value = stk
            completed = stk >= target
        elif obj_type == "roul_combo":
            c_idx = obj.get("combo_idx", 0)
            val = 0
            for r in rouls:
                won_arr = r.get("_p_won_combination_array", [])
                if c_idx < len(won_arr) and won_arr[c_idx] > 0:
                    val = max(val, won_arr[c_idx])
            current_value = val
            completed = val >= target
        elif obj_type == "roul_green":
            g = sum(r.get("_green_won_count", 0) for r in rouls)
            current_value = g
            completed = g >= target
        elif obj_type == "roul_money":
            m = sum(r.get("_money_won", 0) for r in rouls)
            current_value = m
            completed = m >= target
        elif obj_type == "roul_seen_nums":
            seen_arr = prog.get("_roulette_result_seen_array", [])
            cnt = sum(1 for x in seen_arr if x > 0)
            current_value = cnt
            completed = cnt >= target
        elif obj_type == "roul_seen_green":
            g = max((r.get("_green_seen_count", 0) for r in rouls), default=0)
            current_value = g
            completed = g >= target
        elif obj_type == "roul_played_bets":
            cnt = 0
            for r in rouls:
                played_arr = r.get("_p_played_combination_array", [])
                cnt = max(cnt, sum(1 for x in played_arr if x > 0))
            current_value = cnt
            completed = cnt >= target
        elif obj_type == "sng_priv_rank":
            r_idx = obj.get("rank_idx", 0)
            ranks = sng_privs[0].get("_ranks_count", []) if sng_privs else []
            val = ranks[r_idx] if r_idx < len(ranks) else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_pub_rank":
            r_idx = obj.get("rank_idx", 0)
            ranks = sng_pubs[0].get("_ranks_count", []) if sng_pubs else []
            val = ranks[r_idx] if r_idx < len(ranks) else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_before_flop":
            val = sng_pubs[0].get("_win_before_flop_count", 0) if sng_pubs else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_before_turn":
            val = sng_pubs[0].get("_win_before_turn_count", 0) if sng_pubs else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_before_river":
            val = sng_pubs[0].get("_win_before_river_count", 0) if sng_pubs else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_win_hands":
            val = sng_pubs[0].get("_win_count", 0) if sng_pubs else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_streak":
            val = sng_pubs[0].get("_best_win_in_a_row", 0) if sng_pubs else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sng_money":
            val = sum(s.get("_money_won", 0) for s in sng_pubs)
            current_value = val
            completed = val >= target
        elif obj_type == "sng_pub_tables_count":
            cnt = sum(1 for s in sng_pubs if s.get("_play_count", 0) >= 1)
            current_value = cnt
            completed = cnt >= target
        elif obj_type == "sng_priv_played":
            idx = obj.get("idx", 0)
            cnt = sng_privs[idx].get("_play_count", 0) if idx < len(sng_privs) else 0
            current_value = cnt
            completed = cnt >= target
        elif obj_type == "race_time":
            f = obj["field"]
            t = prog.get(f, 2147483647)
            current_value = t
            completed = 0 < t <= target
        elif obj_type == "prog_counter":
            f = obj["field"]
            val = prog.get(f, 0)
            current_value = val
            completed = val >= target
        elif obj_type == "prog_bool":
            f = obj["field"]
            val = prog.get(f, False)
            current_value = 1 if val else 0
            completed = bool(val)
        elif obj_type == "bitfield_popcount":
            f = obj["field"]
            val = popcount(prog.get(f, 0))
            current_value = val
            completed = val >= target
        elif obj_type == "drink_cocktail_tier":
            idx = obj.get("drink_idx", 0)
            arr = prog.get("_cocktail_drink_array", [])
            tier_indices = {0: [0], 1: [1], 2: [2, 5], 3: [3, 10]}
            idxs_to_check = tier_indices.get(idx, [idx])
            val = max((arr[i] if i < len(arr) else 0) for i in idxs_to_check)
            current_value = val
            completed = val >= target
        elif obj_type == "emotes_played_count":
            arr = prog.get("_emote_played_array", [])
            cnt = sum(1 for x in arr if x > 0)
            current_value = cnt
            completed = cnt >= target
        elif obj_type == "vip_access":
            val = bool(prog.get("_vip_status", False) and prog.get("_vip_terrace_seen", 0) >= 1)
            current_value = 1 if val else 0
            completed = val
        elif obj_type == "prog_two_cars":
            val = bool(prog.get("_hall_car_won", False) and prog.get("_vip_car_won", False))
            current_value = (1 if prog.get("_hall_car_won") else 0) + (1 if prog.get("_vip_car_won") else 0)
            completed = val
        elif obj_type == "array_sum":
            arr = prog.get(obj["field"], [])
            val = sum(arr) if isinstance(arr, list) else 0
            current_value = val
            completed = val >= target
        elif obj_type == "array_nonzero":
            arr = prog.get(obj["field"], [])
            val = sum(1 for x in arr if x > 0) if isinstance(arr, list) else 0
            current_value = val
            completed = val >= target
        elif obj_type == "sm_played_field":
            f = obj["field"]
            val = sum(s.get(f, 0) for s in sms)
            current_value = val
            completed = val >= target
        elif obj_type == "sm_types_count":
            cnt = sum(1 for s in sms if s.get("_play_count", 0) >= 1)
            current_value = cnt
            completed = cnt >= target
        elif obj_type == "pcg_tables_count":
            cnt = sum(1 for p in pcgs if p.get("_play_count", 0) >= 1)
            current_value = cnt
            completed = cnt >= target

        earned_pts = points if completed else 0
        return {
            "id": obj_id,
            "name": obj["name"],
            "island": "Casino Island",
            "points": points,
            "earned_points": earned_pts,
            "completed": completed,
            "current_value": current_value,
            "target_value": target,
            "type": obj_type
        }

    def calculate_skill_points(self) -> Dict[str, int]:
        """Calculates accurate points for each of the 4 base game skills based on objectives."""
        scores = {
            "competition": 0,
            "discovery": 0,
            "collection": 0,
            "social": 0
        }

        for skill_id, skill_meta in OBJECTIVES_CATALOG.items():
            pts_sum = 0
            for sec_id, sec_meta in skill_meta["sections"].items():
                for obj in sec_meta["objectives"]:
                    st = self._extract_objective_state(obj)
                    pts_sum += st["earned_points"]

            # Cap each skill at its maximum points
            scores[skill_id] = min(skill_meta["max_points"], pts_sum)

        # In discovery, factor in base cruising XP if save has exploration points higher than objective sum
        pl = self.data_dict.get("PlayerLevels", {})
        cruising_dict = pl.get("CruisingLevels", {})
        if isinstance(cruising_dict, dict):
            raw_cruising = sum(cruising_dict.values())
            scores["discovery"] = max(scores["discovery"], min(14500, raw_cruising))

        return scores

    def calculate_casino_skill_points(self) -> Dict[str, int]:
        """Calculates points for each of the 4 Casino skills based on objectives."""
        scores = {
            "competition": 0,
            "discovery": 0,
            "collection": 0,
            "social": 0
        }
        for skill_id, skill_meta in cc.CASINO_CATALOG.items():
            pts_sum = 0
            for sec_id, sec_meta in skill_meta["sections"].items():
                for obj in sec_meta["objectives"]:
                    st = self._extract_casino_objective_state(obj)
                    pts_sum += st["earned_points"]
            scores[skill_id] = min(skill_meta["max_points"], pts_sum)
        return scores

    def set_casino_objective(self, obj_id: str, value: Any):
        """Modifies a specific Casino objective state in CasinoProgressionSave."""
        found_obj = None
        for skill_meta in cc.CASINO_CATALOG.values():
            for sec_meta in skill_meta["sections"].values():
                for obj in sec_meta["objectives"]:
                    if obj["id"] == obj_id:
                        found_obj = obj
                        break
                if found_obj:
                    break
            if found_obj:
                break

        if not found_obj:
            raise KeyError(f"Casino objective ID {obj_id} not found in catalog.")

        casino = self.data_dict.setdefault("Casino", {})
        prog = casino.setdefault("CasinoProgressionSave", {})
        obj_type = found_obj.get("type")
        target = found_obj.get("target", 1)

        sms = prog.setdefault("_array_save_slotmachines", [{} for _ in range(6)])
        while len(sms) < 6:
            sms.append({})
        rouls = prog.setdefault("_array_save_roulettes", [{} for _ in range(3)])
        while len(rouls) < 3:
            rouls.append({})
        pcgs = prog.setdefault("_array_save_poker_cashgame", [{} for _ in range(12)])
        while len(pcgs) < 12:
            pcgs.append({})
        sng_pubs = prog.setdefault("_array_save_poker_sitandgo_public", [{} for _ in range(12)])
        while len(sng_pubs) < 12:
            sng_pubs.append({})
        sng_privs = prog.setdefault("_array_save_poker_sitandgo_private", [{} for _ in range(15)])
        while len(sng_privs) < 15:
            sng_privs.append({})
        sats = prog.setdefault("_array_save_poker_satellite", [{} for _ in range(4)])
        while len(sats) < 4:
            sats.append({})

        if obj_type == "slot_prize":
            idx = found_obj.get("slot_idx", 0)
            if idx < len(sms):
                won_arr = sms[idx].setdefault("_p_won_combination_array", [0] * 32)
                while len(won_arr) < 32:
                    won_arr.append(0)
                played_arr = sms[idx].setdefault("_p_played_combination_array", [0] * 32)
                while len(played_arr) < 32:
                    played_arr.append(0)
                seen_arr = sms[idx].setdefault("_p_seen_combination_array", [0] * 32)
                while len(seen_arr) < 32:
                    seen_arr.append(0)
                val = 1 if value else 0
                for i in range(32):
                    won_arr[i] = val
                    played_arr[i] = val
                    seen_arr[i] = val
                if value:
                    sms[idx]["_play_count"] = max(sms[idx].get("_play_count", 0), target)
        elif obj_type == "slot_jackpot":
            for s in sms:
                s["_jackpot_count"] = 1 if value else 0
                s["_jackpot_won_bitfield"] = 63 if value else 0
                if value:
                    s["_play_count"] = max(s.get("_play_count", 0), 1)
        elif obj_type == "slot_money":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for s in sms:
                s["_money_won"] = val
        elif obj_type == "poker_win_hands":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            pcgs[0]["_win_count"] = val
            if val > 0:
                pcgs[0]["_play_count"] = max(pcgs[0].get("_play_count", 0), val)
        elif obj_type == "poker_streak":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            pcgs[0]["_best_win_in_a_row"] = val
        elif obj_type == "poker_hand_combo":
            c_idx = found_obj.get("combo_idx", 0)
            for t in (pcgs + sng_pubs + sng_privs + sats):
                won_arr = t.setdefault("_p_won_combination_array", [0] * 10)
                while len(won_arr) <= c_idx:
                    won_arr.append(0)
                played_arr = t.setdefault("_p_played_combination_array", [0] * 10)
                while len(played_arr) <= c_idx:
                    played_arr.append(0)
                won_arr[c_idx] = 1 if value else 0
                played_arr[c_idx] = 1 if value else 0
                if value:
                    t["_win_count"] = max(t.get("_win_count", 0), 1)
                    t["_play_count"] = max(t.get("_play_count", 0), 1)
        elif obj_type == "poker_money":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for p in pcgs:
                p["_money_won"] = val
        elif obj_type == "tourn_rank":
            sat_idx = found_obj.get("sat_idx", 0)
            max_rank = found_obj.get("max_rank", 1)
            ranks = sats[sat_idx].setdefault("_ranks_count", [0] * 10)
            while len(ranks) < 10:
                ranks.append(0)
            if value:
                ranks[0] = max(ranks[0], 1)
                sats[sat_idx]["_play_count"] = max(sats[sat_idx].get("_play_count", 0), 1)
                sats[sat_idx]["_win_count"] = max(sats[sat_idx].get("_win_count", 0), 1)
            else:
                ranks[0] = 0
        elif obj_type == "tourn_total_wins":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sats[0]["_win_count"] = val
        elif obj_type == "tourn_money":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sats[0]["_money_won"] = val
        elif obj_type == "tourn_played":
            sat_idx = found_obj.get("sat_idx", 0)
            sats[sat_idx]["_play_count"] = 1 if value else 0
        elif obj_type == "tourn_total_played":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sats[0]["_play_count"] = val
        elif obj_type == "roul_streak":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for r in rouls:
                r["_best_win_in_a_row"] = val
        elif obj_type == "roul_combo":
            c_idx = found_obj.get("combo_idx", 0)
            for r in rouls:
                won_arr = r.setdefault("_p_won_combination_array", [0] * 16)
                while len(won_arr) <= c_idx:
                    won_arr.append(0)
                played_arr = r.setdefault("_p_played_combination_array", [0] * 16)
                while len(played_arr) <= c_idx:
                    played_arr.append(0)
                won_arr[c_idx] = 1 if value else 0
                played_arr[c_idx] = 1 if value else 0
                if value:
                    r["_win_count"] = max(r.get("_win_count", 0), 1)
                    r["_play_count"] = max(r.get("_play_count", 0), 1)
        elif obj_type == "roul_green":
            for r in rouls:
                r["_green_won_count"] = 2 if value else 0
                r["_green_played_count"] = 2 if value else 0
                r["_green_seen_count"] = 2 if value else 0
                if value:
                    r["_play_count"] = max(r.get("_play_count", 0), 1)
        elif obj_type == "roul_money":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for r in rouls:
                r["_money_won"] = val
        elif obj_type == "roul_seen_nums":
            arr = prog.setdefault("_roulette_result_seen_array", [0] * 38)
            while len(arr) < 38:
                arr.append(0)
            cnt = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for i in range(len(arr)):
                arr[i] = 1 if i < cnt else 0
        elif obj_type == "roul_seen_green":
            for r in rouls:
                r["_green_seen_count"] = 2 if value else 0
        elif obj_type == "roul_played_bets":
            for r in rouls:
                arr = r.setdefault("_p_played_combination_array", [0] * 16)
                while len(arr) < 16:
                    arr.append(0)
                for i in range(16):
                    arr[i] = 1 if value else 0
                if value:
                    r["_play_count"] = max(r.get("_play_count", 0), 16)
        elif obj_type == "sng_priv_rank":
            r_idx = found_obj.get("rank_idx", 0)
            ranks = sng_privs[0].setdefault("_ranks_count", [0] * 10)
            while len(ranks) < 10:
                ranks.append(0)
            ranks[r_idx] = 1 if value else 0
            if value:
                sng_privs[0]["_play_count"] = max(sng_privs[0].get("_play_count", 0), 1)
        elif obj_type == "sng_pub_rank":
            r_idx = found_obj.get("rank_idx", 0)
            ranks = sng_pubs[0].setdefault("_ranks_count", [0] * 10)
            while len(ranks) < 10:
                ranks.append(0)
            ranks[r_idx] = 1 if value else 0
            if value:
                sng_pubs[0]["_play_count"] = max(sng_pubs[0].get("_play_count", 0), 1)
        elif obj_type == "sng_before_flop":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sng_pubs[0]["_win_before_flop_count"] = val
        elif obj_type == "sng_before_turn":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sng_pubs[0]["_win_before_turn_count"] = val
        elif obj_type == "sng_before_river":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sng_pubs[0]["_win_before_river_count"] = val
        elif obj_type == "sng_win_hands":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sng_pubs[0]["_win_count"] = val
        elif obj_type == "sng_streak":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sng_pubs[0]["_best_win_in_a_row"] = val
        elif obj_type == "sng_money":
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sng_pubs[0]["_money_won"] = val
        elif obj_type == "sng_pub_tables_count":
            cnt = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for i in range(len(sng_pubs)):
                sng_pubs[i]["_play_count"] = 1 if i < cnt else 0
        elif obj_type == "sng_priv_played":
            idx = found_obj.get("idx", 0)
            if idx < len(sng_privs):
                sng_privs[idx]["_play_count"] = 1 if value else 0
        elif obj_type == "race_time":
            f = found_obj["field"]
            if value is True:
                prog[f] = 13443
                prog["_time_attack_played_count"] = max(prog.get("_time_attack_played_count", 0), 1)
            elif value is False:
                prog[f] = 2147483647
            else:
                prog[f] = int(value)
        elif obj_type == "prog_counter":
            f = found_obj["field"]
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            prog[f] = val
        elif obj_type == "prog_bool":
            f = found_obj["field"]
            prog[f] = bool(value)
            if f == "_vip_status" and value:
                casino["_hasSeenCasinoVIPStatusCinematic"] = True
                prog["_vip_terrace_seen"] = max(prog.get("_vip_terrace_seen", 0), 1)
            if f == "_furniture_chic_set":
                if value:
                    casino["unlockables0"] = casino.get("unlockables0", 0) | (1 << 54)
                else:
                    casino["unlockables0"] = casino.get("unlockables0", 0) & ~(1 << 54)
        elif obj_type == "bitfield_popcount":
            f = found_obj["field"]
            if isinstance(value, bool):
                if value:
                    if f == "_cocktail_unlock_flag":
                        prog[f] = prog.get(f, 0) | ((1 << target) - 1)
                    elif f == "_emote_unlock_flag":
                        prog[f] = 4294967295 if target == 32 else (prog.get(f, 0) | ((1 << target) - 1))
                    elif f == "_cloth_bought":
                        prog[f] = 33554431 if target >= 25 else (prog.get(f, 0) | ((1 << target) - 1))
                    elif f == "_shoes_bought":
                        prog[f] = 63
                    elif f == "_glasses_bought":
                        prog[f] = 15
                    elif f == "_satellite_prize_inspected_flag":
                        prog[f] = 7
                    else:
                        prog[f] = (1 << target) - 1
                else:
                    prog[f] = 0
            else:
                prog[f] = int(value)
        elif obj_type == "drink_cocktail_tier":
            arr = prog.setdefault("_cocktail_drink_array", [0] * 15)
            while len(arr) < 15:
                arr.append(0)
            idx = found_obj.get("drink_idx", 0)
            tier_indices = {0: [0], 1: [1], 2: [2, 5], 3: [3, 10]}
            idxs = tier_indices.get(idx, [idx])
            for i in idxs:
                if i < len(arr):
                    arr[i] = 5 if value else 0
        elif obj_type == "emotes_played_count":
            arr = prog.setdefault("_emote_played_array", [0] * 32)
            while len(arr) < 32:
                arr.append(0)
            cnt = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for i in range(len(arr)):
                arr[i] = 1 if i < cnt else 0
        elif obj_type == "vip_access":
            if value:
                prog["_vip_status"] = True
                prog["_vip_terrace_seen"] = max(prog.get("_vip_terrace_seen", 0), 1)
                casino["_hasSeenCasinoVIPStatusCinematic"] = True
                casino["_has_seen_vip_intro_cine"] = True
            else:
                prog["_vip_status"] = False
                prog["_vip_terrace_seen"] = 0
        elif obj_type == "prog_two_cars":
            prog["_hall_car_won"] = bool(value)
            prog["_vip_car_won"] = bool(value)
        elif obj_type == "array_sum":
            f = found_obj["field"]
            arr = prog.setdefault(f, [0] * 10)
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            arr[0] = val
        elif obj_type == "array_nonzero":
            f = found_obj["field"]
            arr = prog.setdefault(f, [0] * 32)
            while len(arr) < 32:
                arr.append(0)
            cnt = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for i in range(len(arr)):
                arr[i] = 1 if i < cnt else 0
        elif obj_type == "sm_played_field":
            f = found_obj["field"]
            val = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            sms[0][f] = val
            sms[0]["_play_count"] = max(sms[0].get("_play_count", 0), val)
        elif obj_type == "sm_types_count":
            cnt = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for i in range(len(sms)):
                sms[i]["_play_count"] = 1 if i < cnt else 0
        elif obj_type == "pcg_tables_count":
            cnt = target if (isinstance(value, bool) and value) else (0 if isinstance(value, bool) else int(value))
            for i in range(len(pcgs)):
                pcgs[i]["_play_count"] = 1 if i < cnt else 0

        self.sync_dual_layer()

    def set_objective(self, obj_id: str, value: Any):
        """Modifies a specific objective state in the underlying save structure."""
        if obj_id.startswith("cas_"):
            return self.set_casino_objective(obj_id, value)

        found_obj = None
        for skill_meta in OBJECTIVES_CATALOG.values():
            for sec_meta in skill_meta["sections"].values():
                for obj in sec_meta["objectives"]:
                    if obj["id"] == obj_id:
                        found_obj = obj
                        break
                if found_obj:
                    break
            if found_obj:
                break

        if not found_obj:
            raise KeyError(f"Objective ID {obj_id} not found in catalog.")

        obj_type = found_obj.get("type")
        lic = self.data_dict.setdefault("PlayerLicenses", {})
        stats = self.data_dict.setdefault("StatisticsData", {})
        driver = self.data_dict.setdefault("Driver", {})
        pl = self.data_dict.setdefault("PlayerLevels", {})
        phone = self.data_dict.setdefault("SCPhoneCalls", {})

        # Synchronize Rewards.EventXPs for in-game progression tracking
        if "xp_idx" in found_obj:
            idx = found_obj["xp_idx"]
            rewards = self.data_dict.setdefault("Rewards", {})
            event_xps = rewards.setdefault("EventXPs", [0] * 300)
            while len(event_xps) < 300:
                event_xps.append(0)

            max_val = MASTER_MAX_EVENT_XPS[idx] if idx < len(MASTER_MAX_EVENT_XPS) else 1
            if max_val <= 0:
                max_val = 1

            if obj_type in ("toggle", "counter_step", "toggle_stat", "rank_step", "chase_wins"):
                event_xps[idx] = max_val if bool(value) else 0
            elif obj_type in ("counter", "counter_linear"):
                event_xps[idx] = min(max_val, max(0, int(value)))

        if obj_type == "toggle":
            is_checked = bool(value)
            if "license_idx" in found_obj:
                idx = found_obj["license_idx"]
                licenses = lic.setdefault("Licenses", [])
                while len(licenses) <= idx:
                    licenses.append({"Passed": False, "Looked": False, "PhotoIndex": -1, "DrivingTest": []})
                l = licenses[idx]
                l["Passed"] = is_checked
                l["Looked"] = is_checked
                l["RemainingReward"] = 0 if is_checked else 1
                l["PhotoIndex"] = 1 if is_checked else -1
                for test in l.get("DrivingTest", []):
                    test["Success"] = is_checked
                    test["Try"] = is_checked
                    test["Score"] = 50000 if is_checked else 0

                def _is_lic_ok(i):
                    return i < len(licenses) and licenses[i].get("Passed") and licenses[i].get("PhotoIndex", -1) >= 0

                # Tier A: 6:A7 (1), 0:A5 (2), 1:A3 / 2:A1 (3)
                if _is_lic_ok(2) or _is_lic_ok(1):
                    lic["CurLicenseA"] = 3
                elif _is_lic_ok(0):
                    lic["CurLicenseA"] = 2
                elif _is_lic_ok(6):
                    lic["CurLicenseA"] = 1
                else:
                    lic["CurLicenseA"] = 0

                # Tier B: 7:B4 (1), 5:B3 (2)
                if _is_lic_ok(5):
                    lic["CurLicenseB"] = 2
                elif _is_lic_ok(7):
                    lic["CurLicenseB"] = 1
                else:
                    lic["CurLicenseB"] = 0

                # Tier C: 3:C4 (1), 4:C3 (2)
                if _is_lic_ok(4):
                    lic["CurLicenseC"] = 2
                elif _is_lic_ok(3):
                    lic["CurLicenseC"] = 1
                else:
                    lic["CurLicenseC"] = 0

            elif "contest_idx" in found_obj:
                idx = found_obj["contest_idx"]
                contests = lic.setdefault("Contests", [])
                while len(contests) <= idx:
                    contests.append({"Passed": False, "Cup": -1, "State": 0, "Challenge": []})
                c = contests[idx]
                c["Passed"] = is_checked
                c["Cup"] = 3 if is_checked else -1
                c["State"] = 3 if is_checked else 0
                c["Looked"] = is_checked
                c["RemainingReward"] = 0
                for ch in c.get("Challenge", []):
                    ch["Try"] = is_checked
                    ch["Score"] = 0
                    ch["ContestScores"] = [0.0] * 8 if is_checked else []

            elif "duel_idx" in found_obj:
                idx = found_obj["duel_idx"]
                rewards = self.data_dict.setdefault("Rewards", {})
                reward_cars = rewards.setdefault("RewardCars", [0] * 100)
                while len(reward_cars) <= idx:
                    reward_cars.append(0)
                reward_cars[idx] = 2 if is_checked else 0
                if is_checked:
                    stats["SoloWon"] = max(stats.get("SoloWon", 0), 100)

            elif "area_idx" in found_obj and found_obj["id"].startswith("ev_"):
                # Events in area
                ev_save = self.data_dict.setdefault("EventsSave", {})
                events = ev_save.setdefault("Events", [])
                target_state = 5 if is_checked else 0
                for e in events:
                    e["State"] = target_state

            elif "area_idx" in found_obj and found_obj["id"].startswith("wr_"):
                # Wrecks
                area_idx = found_obj["area_idx"]
                wrecks = self.data_dict.setdefault("Wrecks", {})
                target_list = wrecks.setdefault("Wrecks_IBIZA" if area_idx in (0, 1) else "Wrecks_HAWAI", [])
                for w in target_list:
                    w["Taken"] = is_checked
                    w["Looked"] = is_checked

            elif "island_idx" in found_obj:
                # Viewpoints
                photos = self.data_dict.setdefault("PhotosGP", {}).setdefault("PhotosGP", [])
                island_idx = found_obj["island_idx"]
                start = 0 if island_idx == 0 else 20
                end = 20 if island_idx == 0 else 40
                while len(photos) < end:
                    photos.append({"Taken": False})
                for i in range(start, min(len(photos), end)):
                    photos[i]["Taken"] = is_checked

        elif obj_type == "road_tier":
            area_idx = found_obj["area_idx"]
            target_pct = found_obj["pct_target"]
            is_checked = bool(value)
            unlocked = pl.setdefault("AreaRoadsUnlocked", [0] * 6)
            totals = pl.setdefault("AreaTotalRoads", AREA_MAX_ROADS)
            while len(unlocked) < 6:
                unlocked.append(0)
            while len(totals) < 6:
                totals.append(AREA_MAX_ROADS[len(totals)])
            if is_checked:
                needed = int(totals[area_idx] * (target_pct / 100.0))
                unlocked[area_idx] = max(unlocked[area_idx], needed)
            else:
                lower = int(totals[area_idx] * ((target_pct - 10) / 100.0)) if target_pct > 10 else 0
                unlocked[area_idx] = min(unlocked[area_idx], lower)

        elif obj_type in ("counter", "counter_linear"):
            val = int(value)
            field = found_obj["stat_field"]
            if found_obj.get("store_in_driver"):
                driver[field] = val
            else:
                stats[field] = val
                if field in ("MultiRaceWon", "MultiRankedWon"):
                    stats["MultiRaceWon"] = val
                    stats["MultiRankedWon"] = val
                    stats["MultiNonRankedWon"] = val
                    stats["MultiEliminatorWon"] = val
                    stats["MultiOrientationWon"] = val
                    stats["MultiSpeedWon"] = val
                    stats["MultiTrapWon"] = val
                elif field in ("ExtraChaWon", "ICEvsBotWon"):
                    stats["ExtraChaWon"] = val
                    stats["ICEvsBotWon"] = val
                    stats["ICEvsHumanWon"] = val

        elif obj_type == "counter_step":
            is_checked = bool(value)
            grp = found_obj.get("group")
            target = found_obj["target"]
            if grp == "cars":
                cur = stats.get("NbCarDealerBuyCar", 0)
                stats["NbCarDealerBuyCar"] = max(cur, target) if is_checked else min(cur, target - 1)
            elif grp == "houses":
                cur = stats.get("NbHouseBought", 0)
                stats["NbHouseBought"] = max(cur, target) if is_checked else min(cur, target - 1)
            elif grp == "furnitures":
                mh = self.data_dict.setdefault("MyHouse", {})
                cur = mh.get("NbBoughtFurnitures", 0)
                mh["NbBoughtFurnitures"] = max(cur, target) if is_checked else min(cur, target - 1)
            elif grp == "clothes":
                cur = stats.get("NbClothesBought", 0)
                stats["NbClothesBought"] = max(cur, target) if is_checked else min(cur, target - 1)
                phone["BeenInClothesShop"] = True
            elif grp == "haircuts":
                cur = stats.get("NbHaircutsBought", 0)
                new_val = max(cur, target) if is_checked else min(cur, target - 1)
                stats["NbHaircutsBought"] = new_val
                driver["NbHaircuts"] = new_val
                pl["HaircutsBought"] = [new_val] * 4
                phone["BeenInHairShop"] = True
            elif grp == "stickers":
                cur = stats.get("NbStickersBought", 0)
                stats["NbStickersBought"] = max(cur, target) if is_checked else min(cur, target - 1)
                phone["BeenInStickerShop"] = True

        elif obj_type == "toggle_stat":
            is_checked = bool(value)
            field = found_obj["stat_field"]
            stats[field] = found_obj["target"] if is_checked else 0

        elif obj_type == "rank_step":
            is_checked = bool(value)
            target_rank = found_obj["target_rank"]
            if is_checked:
                driver["LastSeenClubRank"] = max(driver.get("LastSeenClubRank", 0), target_rank)
            else:
                driver["LastSeenClubRank"] = min(driver.get("LastSeenClubRank", 0), target_rank - 1)

        elif obj_type == "chase_wins":
            is_checked = bool(value)
            ch = self.data_dict.setdefault("Chase", {})
            if is_checked:
                ch["PoliceVictories"] = 10
                ch["OutlawVictories"] = 10
                ch["OutlawMaxVictories"] = 10
                ch["Rewards"] = 10
            else:
                ch["PoliceVictories"] = 0
                ch["OutlawVictories"] = 0
                ch["OutlawMaxVictories"] = 0
                ch["Rewards"] = 0

        # Run dual-layer synchronization after modifying objective
        self.sync_dual_layer()

    def sync_dual_layer(self):
        """Synchronizes points trees and PlayerLevels with active objective states."""
        scores = self.calculate_skill_points()
        pl = self.data_dict.setdefault("PlayerLevels", {})
        pl["RacingLevel"] = scores["competition"]
        pl["CollectionLevel"] = scores["collection"]
        pl["SocialLevel"] = scores["social"]

        # Cruising levels distribution across 6 areas
        cruising_levels = pl.setdefault("CruisingLevels", {})
        unlocked_roads = pl.get("AreaRoadsUnlocked", [0] * 6)
        totals = pl.get("AreaTotalRoads", AREA_MAX_ROADS)

        total_discovery_pts = scores["discovery"]
        if total_discovery_pts >= 14500:
            for i in range(6):
                cruising_levels[f"Area_{i}"] = AREA_MAX_CRUISING_PTS[i]
                pl["AreaRoadsUnlocked"] = list(AREA_MAX_ROADS)
                pl["AirportUnlocked"] = True
                pl["NewsAirportSend"] = True
        else:
            for i in range(6):
                u = unlocked_roads[i] if i < len(unlocked_roads) else 0
                t = totals[i] if i < len(totals) and totals[i] > 0 else AREA_MAX_ROADS[i]
                ratio = min(1.0, u / t)
                area_pts = int(AREA_MAX_CRUISING_PTS[i] * ratio)
                cruising_levels[f"Area_{i}"] = max(cruising_levels.get(f"Area_{i}", 0), area_pts)

        # Base skill levels
        lvl_comp = points_to_level(scores["competition"], is_discovery=False)
        lvl_disc = points_to_level(scores["discovery"], is_discovery=True)
        lvl_coll = points_to_level(scores["collection"], is_discovery=False)
        lvl_soc = points_to_level(scores["social"], is_discovery=False)
        base_level = lvl_comp + lvl_disc + lvl_coll + lvl_soc

        # Casino skill levels
        cas_scores = self.calculate_casino_skill_points()
        cas_comp = cc.casino_points_to_level("competition", cas_scores["competition"])
        cas_disc = cc.casino_points_to_level("discovery", cas_scores["discovery"])
        cas_coll = cc.casino_points_to_level("collection", cas_scores["collection"])
        cas_soc = cc.casino_points_to_level("social", cas_scores["social"])
        casino_level = cas_comp + cas_disc + cas_coll + cas_soc

        global_level = base_level + casino_level
        driver = self.data_dict.setdefault("Driver", {})
        driver["Level"] = min(73, max(1, global_level))

        # Casino Status & Cinematics synchronization
        casino = self.data_dict.setdefault("Casino", {})
        prog = casino.setdefault("CasinoProgressionSave", {})
        if casino_level >= 5:
            prog["_vip_status"] = True
            casino["_hasSeenCasinoVIPStatusCinematic"] = True
            prog["_vip_terrace_seen"] = max(prog.get("_vip_terrace_seen", 0), 1)
        if casino_level >= 10:
            casino["_hasSeenCasinoACEStatusCinematic"] = True

    def apply_preset(self, preset_type: str, target: Optional[str] = None):
        """Applies batch presets: 'max_all', 'reset_all', 'max_skill', 'reset_skill', 'max_section', etc."""
        if preset_type == "max_all":
            self._max_all()
            self._max_casino()
        elif preset_type == "reset_all":
            self._reset_all()
            self._reset_casino()
        elif preset_type == "max_casino":
            self._max_casino()
        elif preset_type == "reset_casino":
            self._reset_casino()
        elif preset_type == "max_skill" and target in OBJECTIVES_CATALOG:
            for sec in OBJECTIVES_CATALOG[target]["sections"].values():
                for obj in sec["objectives"]:
                    self._set_obj_max(obj)
            rewards = self.data_dict.setdefault("Rewards", {})
            event_xps = rewards.setdefault("EventXPs", [0] * 300)
            while len(event_xps) < 300:
                event_xps.append(0)
            for idx in SKILL_XPS_INDICES.get(target, []):
                if idx < len(MASTER_MAX_EVENT_XPS):
                    event_xps[idx] = MASTER_MAX_EVENT_XPS[idx]
            if target == "discovery":
                pl = self.data_dict.setdefault("PlayerLevels", {})
                pl["AreaRoadsUnlocked"] = list(AREA_MAX_ROADS)
                pl["CruisingLevels"] = {f"Area_{i}": AREA_MAX_CRUISING_PTS[i] for i in range(6)}
                pl["AirportUnlocked"] = True
                rl = self.data_dict.setdefault("RoadLock", {})
                rl["Locks"] = [18446744073709551615] * 8700

        elif preset_type == "reset_skill" and target in OBJECTIVES_CATALOG:
            for sec in OBJECTIVES_CATALOG[target]["sections"].values():
                for obj in sec["objectives"]:
                    self._set_obj_min(obj)
            rewards = self.data_dict.setdefault("Rewards", {})
            event_xps = rewards.setdefault("EventXPs", [0] * 300)
            while len(event_xps) < 300:
                event_xps.append(0)
            for idx in SKILL_XPS_INDICES.get(target, []):
                if idx < len(event_xps):
                    event_xps[idx] = 0
            if target == "discovery":
                pl = self.data_dict.setdefault("PlayerLevels", {})
                pl["AreaRoadsUnlocked"] = [0] * 6
                pl["CruisingLevels"] = {f"Area_{i}": 0 for i in range(6)}
                rl = self.data_dict.setdefault("RoadLock", {})
                rl["Locks"] = [0] * 8700
        elif preset_type == "max_casino_skill" and target in cc.CASINO_CATALOG:
            self._max_casino_skill(target)
        elif preset_type == "reset_casino_skill" and target in cc.CASINO_CATALOG:
            self._reset_casino_skill(target)
        elif preset_type == "max_section":
            sec_meta = self._find_section(target)
            if sec_meta:
                for obj in sec_meta["objectives"]:
                    self._set_obj_max(obj)
        elif preset_type == "reset_section":
            sec_meta = self._find_section(target)
            if sec_meta:
                for obj in sec_meta["objectives"]:
                    self._set_obj_min(obj)
        elif preset_type == "max_casino_section":
            self._max_casino_section(target)
        elif preset_type == "reset_casino_section":
            self._reset_casino_section(target)
        self.sync_dual_layer()

    def _find_section(self, section_id: str) -> Optional[Dict[str, Any]]:
        for skill in OBJECTIVES_CATALOG.values():
            if section_id in skill["sections"]:
                return skill["sections"][section_id]
        return None

    def _set_obj_max(self, obj: Dict[str, Any]):
        t = obj.get("type")
        if t in ("toggle", "road_tier", "counter_step", "toggle_stat"):
            self.set_objective(obj["id"], True)
        elif t in ("counter", "counter_linear"):
            self.set_objective(obj["id"], obj["target"])
        elif t == "rank_step":
            self.set_objective(obj["id"], True)
        elif t == "chase_wins":
            self.set_objective(obj["id"], True)

    def _set_obj_min(self, obj: Dict[str, Any]):
        t = obj.get("type")
        if t in ("toggle", "road_tier", "counter_step", "toggle_stat"):
            self.set_objective(obj["id"], False)
        elif t in ("counter", "counter_linear"):
            self.set_objective(obj["id"], 0)
        elif t == "rank_step":
            self.set_objective(obj["id"], False)
        elif t == "chase_wins":
            self.set_objective(obj["id"], False)

    def _max_all(self):
        """Fulfills all objectives across all skills for 100% Level 73 max completion."""
        # 1. Licenses & Contests
        lic = self.data_dict.setdefault("PlayerLicenses", {})
        lic["CurLicenseA"] = 3
        lic["CurLicenseB"] = 2
        lic["CurLicenseC"] = 2
        licenses = lic.setdefault("Licenses", [])
        for i in range(8):
            while len(licenses) <= i:
                licenses.append({"Passed": True, "Looked": True, "PhotoIndex": 1, "DrivingTest": []})
            l = licenses[i]
            l["Passed"] = True
            l["Looked"] = True
            l["RemainingReward"] = 0
            l["PhotoIndex"] = 1
            for test in l.get("DrivingTest", []):
                test["Success"] = True
                test["Try"] = True
                test["Score"] = 50000

        contests = lic.setdefault("Contests", [])
        for i in range(25):
            while len(contests) <= i:
                contests.append({"Passed": True, "Cup": 3, "State": 3, "Challenge": []})
            c = contests[i]
            c["Passed"] = True
            c["Cup"] = 3
            c["State"] = 3
            c["Looked"] = True
            c["RemainingReward"] = 0
            for ch in c.get("Challenge", []):
                ch["Try"] = True
                ch["Score"] = 0
                ch["ContestScores"] = [0.0] * 8

        # 2. Roads & Cruising
        pl = self.data_dict.setdefault("PlayerLevels", {})
        pl["PlayedTheGame"] = True
        pl["TutoSeen"] = True
        pl["AirportUnlocked"] = True
        pl["NewsAirportSend"] = True
        pl["AreaRoadsUnlocked"] = list(AREA_MAX_ROADS)
        pl["AreaTotalRoads"] = list(AREA_MAX_ROADS)
        pl["CruisingLevels"] = {f"Area_{i}": AREA_MAX_CRUISING_PTS[i] for i in range(6)}
        pl["HaircutsBought"] = [10, 10, 10, 10]
        pl["RacingLevel"] = 10000
        pl["CollectionLevel"] = 10000
        pl["SocialLevel"] = 10000

        # Road discovery bitmask: all 8700 64-bit masks fully discovered
        rl = self.data_dict.setdefault("RoadLock", {})
        rl["Locks"] = [18446744073709551615] * 8700

        # 3. Events
        ev = self.data_dict.setdefault("EventsSave", {})
        for e in ev.setdefault("Events", []):
            e["State"] = 5
        for de in ev.setdefault("DLCEvents", []):
            de["State"] = 5

        # 4. Wrecks
        wr = self.data_dict.setdefault("Wrecks", {})
        for k in ["Wrecks_IBIZA", "Wrecks_HAWAI", "Wrecks_CASINO"]:
            for item in wr.setdefault(k, []):
                item["Taken"] = True
                item["Looked"] = True
                item["Tuto"] = True

        # 5. Photos
        ph = self.data_dict.setdefault("PhotosGP", {})
        ph["Active"] = True
        ph["GotIslandReward"] = [True, True, True]
        for p in ph.setdefault("PhotosGP", []):
            p["Taken"] = True

        # 6. Chase
        ch = self.data_dict.setdefault("Chase", {})
        ch["PoliceVictories"] = 20
        ch["OutlawVictories"] = 20
        ch["OutlawMaxVictories"] = 20
        ch["Rewards"] = 10
        ch["ResetNeeded"] = False

        # 7. Statistics
        stats = self.data_dict.setdefault("StatisticsData", {})
        stats["MultiRaceWon"] = 50
        stats["MultiRankedWon"] = 50
        stats["MultiNonRankedWon"] = 50
        stats["MultiEliminatorWon"] = 50
        stats["MultiOrientationWon"] = 50
        stats["MultiSpeedWon"] = 50
        stats["MultiTrapWon"] = 50
        stats["ExtraChaWon"] = 50
        stats["ICEvsBotWon"] = 50
        stats["ICEvsHumanWon"] = 50
        stats["SoloWon"] = 100
        stats["SoloLost"] = 0
        stats["NbFriendsJoined"] = 20
        stats["NbFriendsInvited"] = 20
        stats["NbClubJoiner"] = 1
        stats["ClubWon"] = 50
        stats["InterClubWonByTeam"] = 50
        stats["CrcChaRuns"] = 50
        stats["CrcChaWon"] = 50
        stats["ChaseHunterWon"] = 20
        stats["ChasePreyWon"] = 20
        stats["FTLWon"] = 30
        stats["KYDWon"] = 30
        stats["TimeInCoop"] = 3600.0
        stats["NbCodrivingAsPilot"] = 20
        stats["NbCarDealerBuyCar"] = 50
        stats["NbHouseBought"] = 20
        stats["NbClothesBought"] = 150
        stats["NbHaircutsBought"] = 40
        stats["NbStickersBought"] = 50

        # 8. Driver
        drv = self.data_dict.setdefault("Driver", {})
        drv["Level"] = 73
        drv["NbHaircuts"] = 40
        drv["NbSurgeries"] = 4
        drv["LastSeenClubRank"] = 3
        drv["HasBeenMillionaire"] = True

        # 9. SCPhoneCalls shop flags
        phone = self.data_dict.setdefault("SCPhoneCalls", {})
        phone["BeenInClothesShop"] = True
        phone["BeenInStickerShop"] = True
        phone["BeenInHairShop"] = True
        phone["BeenInSurgeryShop"] = True
        phone["BeenInPhotograph"] = True
        phone["BeenInCarWash"] = True
        phone["BeenInRSDirtHawai"] = True
        phone["BeenInRSClassicHawai"] = True

        # 10. Rewards & EventXPs (Master 300-entry progression vector)
        rewards = self.data_dict.setdefault("Rewards", {})
        rewards["EventXPs"] = list(MASTER_MAX_EVENT_XPS)
        rc = rewards.setdefault("RewardCars", [0] * 100)
        while len(rc) < 100:
            rc.append(0)
        for i in range(6):
            rc[i] = 1
        for i in range(6, 20):
            rc[i] = 2
        rewards["WreckSaveRepaired"] = True
        rewards["WreckSaveRepaired2012"] = True
        self._max_casino()

    def _reset_all(self):
        """Resets progression to clean beginning baseline."""
        lic = self.data_dict.setdefault("PlayerLicenses", {})
        lic["CurLicenseA"] = 0
        lic["CurLicenseB"] = 0
        lic["CurLicenseC"] = 0
        for l in lic.setdefault("Licenses", []):
            l["Passed"] = False
            l["Looked"] = False
            l["PhotoIndex"] = -1
            for test in l.get("DrivingTest", []):
                test["Success"] = False
                test["Try"] = False
                test["Score"] = 0

        for c in lic.setdefault("Contests", []):
            c["Passed"] = False
            c["Cup"] = -1
            c["State"] = 0
            for ch in c.get("Challenge", []):
                ch["Try"] = False
                ch["Score"] = 0
                ch["ContestScores"] = []

        pl = self.data_dict.setdefault("PlayerLevels", {})
        pl["RacingLevel"] = 0
        pl["CollectionLevel"] = 0
        pl["SocialLevel"] = 0
        pl["CruisingLevels"] = {f"Area_{i}": 0 for i in range(6)}
        pl["AreaRoadsUnlocked"] = [0] * 6

        rl = self.data_dict.setdefault("RoadLock", {})
        rl["Locks"] = [0] * 8700

        rewards = self.data_dict.setdefault("Rewards", {})
        rewards["EventXPs"] = [0] * 300
        rc = rewards.setdefault("RewardCars", [0] * 100)
        for i in range(len(rc)):
            rc[i] = 0
        rewards["WreckSaveRepaired"] = False
        rewards["WreckSaveRepaired2012"] = False

        stats = self.data_dict.setdefault("StatisticsData", {})
        for field in [
            "MultiRaceWon", "MultiRankedWon", "MultiNonRankedWon", "MultiEliminatorWon",
            "MultiOrientationWon", "MultiSpeedWon", "MultiTrapWon",
            "ExtraChaWon", "ICEvsBotWon", "ICEvsHumanWon", "SoloWon",
            "NbFriendsJoined", "NbFriendsInvited", "NbClubJoiner", "ClubWon", "InterClubWonByTeam",
            "CrcChaRuns", "CrcChaWon", "ChaseHunterWon", "ChasePreyWon",
            "FTLWon", "KYDWon", "TimeInCoop", "NbCodrivingAsPilot",
            "NbClothesBought", "NbHaircutsBought", "NbStickersBought"
        ]:
            stats[field] = 0

        drv = self.data_dict.setdefault("Driver", {})
        drv["Level"] = 1
        drv["NbHaircuts"] = 0
        drv["NbSurgeries"] = 0
        drv["LastSeenClubRank"] = 0
        self._reset_casino()

    def _find_casino_section(self, section_id: str) -> Optional[Dict[str, Any]]:
        for skill in cc.CASINO_CATALOG.values():
            if section_id in skill["sections"]:
                return skill["sections"][section_id]
        return None

    def _max_casino_skill(self, skill_id: str):
        if skill_id in cc.CASINO_CATALOG:
            for sec in cc.CASINO_CATALOG[skill_id]["sections"].values():
                for obj in sec["objectives"]:
                    self.set_casino_objective(obj["id"], True)

    def _reset_casino_skill(self, skill_id: str):
        if skill_id in cc.CASINO_CATALOG:
            for sec in cc.CASINO_CATALOG[skill_id]["sections"].values():
                for obj in sec["objectives"]:
                    self.set_casino_objective(obj["id"], False)

    def _max_casino_section(self, section_id: str):
        sec = self._find_casino_section(section_id)
        if sec:
            for obj in sec["objectives"]:
                self.set_casino_objective(obj["id"], True)

    def _reset_casino_section(self, section_id: str):
        sec = self._find_casino_section(section_id)
        if sec:
            for obj in sec["objectives"]:
                self.set_casino_objective(obj["id"], False)

    def _max_casino(self):
        """Fulfills all Casino objectives across all 4 skills for 10/10 Casino levels."""
        casino = self.data_dict.setdefault("Casino", {})
        prog = casino.setdefault("CasinoProgressionSave", {})

        casino["_hasSeenCasinoProgressionTutorial"] = True
        casino["_hasSeenCasinoVIPStatusCinematic"] = True
        casino["_hasSeenCasinoACEStatusCinematic"] = True
        casino["_has_seen_vip_intro_cine"] = True
        casino["unlockables0"] = casino.get("unlockables0", 0) | (1 << 54)

        prog["_vip_status"] = True
        prog["_vip_terrace_seen"] = 10
        prog["_cocktail_unlock_flag"] = 32767
        prog["_emote_unlock_flag"] = 4294967295
        prog["_cloth_bought"] = 33554431
        prog["_shoes_bought"] = 63
        prog["_glasses_bought"] = 15
        prog["_time_attack_best_score"] = 13443
        prog["_time_attack_vip_best_score"] = 14014
        prog["_time_attack_played_count"] = 10
        prog["_satellite_prize_inspected_flag"] = 7
        prog["_hall_car_seen"] = True
        prog["_hall_car_won"] = True
        prog["_vip_car_seen"] = True
        prog["_vip_car_won"] = True
        prog["_cloth_chic_set"] = True
        prog["_furniture_chic_set"] = True
        prog["_sticker_set"] = True
        prog["_roulette_used_historic"] = True
        prog["_roulette_used_rebet"] = True
        prog["_roulette_result_seen_array"] = [1] * 38
        prog["_green_seen_count"] = 5
        prog["_cocktail_drink_array"] = [5] * 15
        prog["_cocktail_offered_array"] = [5] * 15
        prog["_cocktail_received_array"] = [10] * 15
        prog["_cocktail_different_players_offered_to"] = [1] * 25
        prog["_emote_played_array"] = [1] * 32
        prog["_cashier_seen_with_success_count"] = 10
        prog["_rankings_seen"] = True
        prog["_look_at_mylife_done"] = True
        prog["_photo_mode_used"] = True
        prog["_cocktail_drink_count_on_poker"] = 25
        prog["_friend_count"] = 5
        prog["_session_invite_friend_count"] = 10
        prog["_look_at_mylife_of_other_done"] = True
        prog["_sitandgo_created_private_count"] = 5
        prog["_sitandgo_joined_private_count"] = 5
        prog["_sitandgo_played_to_the_end"] = 5
        prog["_cash_game_unique_opponents_array"] = [1] * 50
        prog["_cash_game_money_taken_from_opponent"] = 2500

        sms = []
        for i in range(6):
            sms.append({
                "_combination_count": 32,
                "_p_won_combination_array": [1] * 32,
                "_p_played_combination_array": [1] * 32,
                "_p_seen_combination_array": [1] * 32,
                "_jackpot_count": 1,
                "_jackpot_won_bitfield": 63,
                "_money_won": 10000,
                "_play_count": 10,
                "_played_with_2_lines": 10,
                "_played_with_3_lines": 20,
                "_played_with_5_lines": 30,
                "_played_with_9_lines": 40,
                "_play_by_relaunch_count": 25
            })
        prog["_array_save_slotmachines"] = sms

        rouls = []
        for i in range(3):
            rouls.append({
                "_combination_count": 16,
                "_best_win_in_a_row": 5,
                "_p_won_combination_array": [1] * 16,
                "_p_played_combination_array": [1] * 16,
                "_green_won_count": 2,
                "_green_seen_count": 2,
                "_money_won": 10000,
                "_play_count": 10
            })
        prog["_array_save_roulettes"] = rouls

        pcgs = []
        for i in range(12):
            pcgs.append({
                "_combination_count": 10,
                "_win_count": 50,
                "_best_win_in_a_row": 5,
                "_p_won_combination_array": [1] * 10,
                "_p_played_combination_array": [1] * 10,
                "_money_won": 10000,
                "_play_count": 10
            })
        prog["_array_save_poker_cashgame"] = pcgs

        sng_pubs = []
        for i in range(12):
            sng_pubs.append({
                "_combination_count": 10,
                "_ranks_count": [1] * 10,
                "_p_won_combination_array": [1] * 10,
                "_p_played_combination_array": [1] * 10,
                "_win_before_flop_count": 20,
                "_win_before_turn_count": 10,
                "_win_before_river_count": 10,
                "_win_count": 75,
                "_best_win_in_a_row": 5,
                "_money_won": 50000,
                "_play_count": 10
            })
        prog["_array_save_poker_sitandgo_public"] = sng_pubs

        sng_privs = []
        for i in range(15):
            sng_privs.append({
                "_combination_count": 10,
                "_ranks_count": [1] * 10,
                "_p_won_combination_array": [1] * 10,
                "_p_played_combination_array": [1] * 10,
                "_play_count": 10
            })
        prog["_array_save_poker_sitandgo_private"] = sng_privs

        sats = []
        for i in range(4):
            sats.append({
                "_combination_count": 10,
                "_ranks_count": [1] * 10,
                "_p_won_combination_array": [1] * 10,
                "_p_played_combination_array": [1] * 10,
                "_win_count": 2,
                "_money_won": 100000,
                "_play_count": 3
            })
        prog["_array_save_poker_satellite"] = sats

    def _reset_casino(self):
        """Resets all Casino objectives and status flags to baseline."""
        casino = self.data_dict.setdefault("Casino", {})
        casino["_hasSeenCasinoProgressionTutorial"] = False
        casino["_hasSeenCasinoVIPStatusCinematic"] = False
        casino["_hasSeenCasinoACEStatusCinematic"] = False
        casino["_has_seen_vip_intro_cine"] = False
        if "unlockables0" in casino:
            casino["unlockables0"] = casino["unlockables0"] & ~(1 << 54)

        prog = casino.setdefault("CasinoProgressionSave", {})
        prog["_vip_status"] = False
        prog["_vip_terrace_seen"] = 0
        prog["_cocktail_unlock_flag"] = 0
        prog["_emote_unlock_flag"] = 0
        prog["_cloth_bought"] = 0
        prog["_shoes_bought"] = 0
        prog["_glasses_bought"] = 0
        prog["_time_attack_best_score"] = 2147483647
        prog["_time_attack_vip_best_score"] = 2147483647
        prog["_time_attack_played_count"] = 0
        prog["_satellite_prize_inspected_flag"] = 0
        prog["_hall_car_seen"] = False
        prog["_hall_car_won"] = False
        prog["_vip_car_seen"] = False
        prog["_vip_car_won"] = False
        prog["_cloth_chic_set"] = False
        prog["_furniture_chic_set"] = False
        prog["_sticker_set"] = False
        prog["_roulette_used_historic"] = False
        prog["_roulette_used_rebet"] = False
        prog["_roulette_result_seen_array"] = [0] * 38
        prog["_green_seen_count"] = 0
        prog["_cocktail_drink_array"] = [0] * 15
        prog["_cocktail_offered_array"] = [0] * 15
        prog["_cocktail_received_array"] = [0] * 15
        prog["_cocktail_different_players_offered_to"] = [0] * 25
        prog["_emote_played_array"] = [0] * 32
        prog["_cashier_seen_with_success_count"] = 0
        prog["_rankings_seen"] = False
        prog["_look_at_mylife_done"] = False
        prog["_photo_mode_used"] = False
        prog["_cocktail_drink_count_on_poker"] = 0
        prog["_friend_count"] = 0
        prog["_session_invite_friend_count"] = 0
        prog["_look_at_mylife_of_other_done"] = False
        prog["_sitandgo_created_private_count"] = 0
        prog["_sitandgo_joined_private_count"] = 0
        prog["_sitandgo_played_to_the_end"] = 0
        prog["_cash_game_unique_opponents_array"] = [0] * 50
        prog["_cash_game_money_taken_from_opponent"] = 0

        sms = []
        for i in range(6):
            sms.append({
                "_combination_count": 32,
                "_p_won_combination_array": [0] * 32,
                "_p_played_combination_array": [0] * 32,
                "_p_seen_combination_array": [0] * 32,
                "_jackpot_count": 0,
                "_jackpot_won_bitfield": 0,
                "_money_won": 0,
                "_play_count": 0,
                "_played_with_2_lines": 0,
                "_played_with_3_lines": 0,
                "_played_with_5_lines": 0,
                "_played_with_9_lines": 0,
                "_play_by_relaunch_count": 0
            })
        prog["_array_save_slotmachines"] = sms

        rouls = []
        for i in range(3):
            rouls.append({
                "_combination_count": 16,
                "_best_win_in_a_row": 0,
                "_p_won_combination_array": [0] * 16,
                "_p_played_combination_array": [0] * 16,
                "_green_won_count": 0,
                "_green_seen_count": 0,
                "_money_won": 0,
                "_play_count": 0
            })
        prog["_array_save_roulettes"] = rouls

        pcgs = []
        for i in range(12):
            pcgs.append({
                "_combination_count": 10,
                "_win_count": 0,
                "_best_win_in_a_row": 0,
                "_p_won_combination_array": [0] * 10,
                "_p_played_combination_array": [0] * 10,
                "_money_won": 0,
                "_play_count": 0
            })
        prog["_array_save_poker_cashgame"] = pcgs

        sng_pubs = []
        for i in range(12):
            sng_pubs.append({
                "_combination_count": 10,
                "_ranks_count": [0] * 10,
                "_p_won_combination_array": [0] * 10,
                "_p_played_combination_array": [0] * 10,
                "_win_before_flop_count": 0,
                "_win_before_turn_count": 0,
                "_win_before_river_count": 0,
                "_win_count": 0,
                "_best_win_in_a_row": 0,
                "_money_won": 0,
                "_play_count": 0
            })
        prog["_array_save_poker_sitandgo_public"] = sng_pubs

        sng_privs = []
        for i in range(15):
            sng_privs.append({
                "_combination_count": 10,
                "_ranks_count": [0] * 10,
                "_p_won_combination_array": [0] * 10,
                "_p_played_combination_array": [0] * 10,
                "_play_count": 0
            })
        prog["_array_save_poker_sitandgo_private"] = sng_privs

        sats = []
        for i in range(4):
            sats.append({
                "_combination_count": 10,
                "_ranks_count": [0] * 10,
                "_p_won_combination_array": [0] * 10,
                "_p_played_combination_array": [0] * 10,
                "_win_count": 0,
                "_money_won": 0,
                "_play_count": 0
            })
        prog["_array_save_poker_satellite"] = sats


    def save(self, target_path: Optional[str] = None, backup_callback: Optional[Any] = None):
        """Re-encodes XMBF, creates safety backup, encrypts with DES-CBC and Eden-SHA1, and writes to disk."""
        if not tdu2_save_tool:
            raise RuntimeError("tdu2_save_tool module is not available.")

        dest = Path(target_path) if target_path else self.profile_path

        # 1. Create safety backup
        if backup_callback and dest.exists():
            try:
                backup_callback(dest, self.profile_name)
            except Exception as e:
                print(f"[!] Warning calling backup_callback: {e}")
        elif dest.exists():
            bak_path = dest.with_suffix(dest.suffix + ".bak")
            shutil.copy2(dest, bak_path)

        # 2. Encode dictionary to XMBF
        re_xmbf = tdu2_save_tool.encode_dict_to_xmbf(self.template_xmbf, self.data_dict)

        # 3. Encrypt container
        re_enc = tdu2_save_tool.encrypt_save_file(
            re_xmbf,
            self.profile_name,
            dest.name,
            original_footer=self.raw_footer
        )

        # 4. Atomic write
        tdu2_save_tool.atomic_write(dest, re_enc)

        # Reload state
        self.raw_data = re_enc
        self.template_xmbf = re_xmbf
