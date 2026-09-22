"""
tdu2_casino_catalog.py

Full catalog of all Casino Island progression skills, sections, and objectives for TDU2.
Defines 4 skills, 15 sections, and 146 in-game objectives with points, targets, and save mappings.
"""

from typing import Dict, List, Any

CASINO_SKILL_THRESHOLDS: Dict[str, List[int]] = {
    "competition": [0, 1000, 2000, 3000, 4000],  # 4 levels, 1000 pts / level
    "discovery": [0, 500, 1000],                 # 2 levels, 500 pts / level
    "collection": [0, 500, 1000],                # 2 levels, 500 pts / level
    "social": [0, 500, 1000]                     # 2 levels, 500 pts / level
}


def casino_points_to_level(skill: str, pts: int) -> int:
    """Calculates skill level (0 to 4 or 0 to 2) for Casino based on points."""
    thresholds = CASINO_SKILL_THRESHOLDS.get(skill, [0, 1000])
    pts = max(0, pts)
    lvl = 0
    for l, t in enumerate(thresholds):
        if pts >= t:
            lvl = l
        else:
            break
    return min(lvl, len(thresholds) - 1)


def casino_level_progress_info(skill: str, pts: int) -> Dict[str, Any]:
    """Calculates casino skill level, current points, next threshold, and percentage."""
    thresholds = CASINO_SKILL_THRESHOLDS.get(skill, [0, 1000])
    max_lvl = len(thresholds) - 1
    lvl = casino_points_to_level(skill, pts)
    cur_t = thresholds[lvl]
    if lvl >= max_lvl:
        next_t = thresholds[max_lvl]
        pct = 100.0
    else:
        next_t = thresholds[lvl + 1]
        needed = next_t - cur_t
        gained = pts - cur_t
        pct = round((gained / needed) * 100.0, 1) if needed > 0 else 100.0
    return {
        "level": lvl,
        "max_level": max_lvl,
        "points": min(thresholds[-1], max(0, pts)),
        "max_points": thresholds[-1],
        "current_threshold": cur_t,
        "next_threshold": next_t,
        "percent": min(100.0, max(0.0, pct))
    }


CASINO_CATALOG: Dict[str, Any] = {
    "competition": {
        "id": "competition",
        "name": "Competition",
        "max_points": 4000,
        "max_level": 4,
        "sections": {
            "slot_machine": {
                "id": "slot_machine",
                "name": "Slot machine",
                "skill": "competition",
                "objectives": [
                    {"id": "cas_sm_prize_high_life", "name": "Win 13 of the 26 combinations on the High-Life slot machine", "points": 50, "type": "slot_prize", "slot_idx": 4, "target": 13},
                    {"id": "cas_sm_prize_fashion", "name": "Win 2 of the 4 combinations on the Fashion slot machine", "points": 100, "type": "slot_prize", "slot_idx": 1, "target": 2},
                    {"id": "cas_sm_prize_poker", "name": "Win 4 of the 9 combinations on the Poker slot machine", "points": 75, "type": "slot_prize", "slot_idx": 3, "target": 4},
                    {"id": "cas_sm_prize_beach", "name": "Win 5 of the 10 combinations on the Beach slot machine", "points": 75, "type": "slot_prize", "slot_idx": 5, "target": 5},
                    {"id": "cas_sm_prize_classic", "name": "Win 6 of the 10 combinations on the Classic slot machine", "points": 100, "type": "slot_prize", "slot_idx": 2, "target": 6},
                    {"id": "cas_sm_prize_tdu2", "name": "Win 6 of the 9 combinations on the TDU 2 slot machine", "points": 50, "type": "slot_prize", "slot_idx": 0, "target": 6},
                    {"id": "cas_sm_jackpot", "name": "Win at least 1 jackpot at slot machines", "points": 20, "type": "slot_jackpot", "target": 1},
                    {"id": "cas_sm_win_10000", "name": "Win $10 000 at slot machines", "points": 50, "type": "slot_money", "target": 10000},
                ]
            },
            "poker_cashgame": {
                "id": "poker_cashgame",
                "name": "Poker and Cash Game",
                "skill": "competition",
                "objectives": [
                    {"id": "cas_pcg_win_10", "name": "Win 10 hands in Cash game", "points": 125, "type": "poker_win_hands", "target": 10},
                    {"id": "cas_pcg_win_25", "name": "Win 25 hands in Cash game", "points": 65, "type": "poker_win_hands", "target": 25},
                    {"id": "cas_pcg_streak_3", "name": "Win 3 hands in a row in Cash game", "points": 100, "type": "poker_streak", "target": 3},
                    {"id": "cas_pcg_streak_5", "name": "Win 5 hands in a row in Cash game", "points": 30, "type": "poker_streak", "target": 5},
                    {"id": "cas_pcg_win_50", "name": "Win 50 hands in Cash game", "points": 30, "type": "poker_win_hands", "target": 50},
                    {"id": "cas_pcg_flush", "name": "Win one hand with a flush at a poker table", "points": 35, "type": "poker_hand_combo", "combo_idx": 5, "target": 1},
                    {"id": "cas_pcg_full_house", "name": "Win one hand with a full house at a poker table", "points": 25, "type": "poker_hand_combo", "combo_idx": 6, "target": 1},
                    {"id": "cas_pcg_straight", "name": "Win one hand with a straight at a poker table", "points": 35, "type": "poker_hand_combo", "combo_idx": 4, "target": 1},
                    {"id": "cas_pcg_three_kind", "name": "Win one hand with a three of a kind at a poker table", "points": 40, "type": "poker_hand_combo", "combo_idx": 3, "target": 1},
                    {"id": "cas_pcg_one_pair", "name": "Win one hand with one pair at a poker table", "points": 75, "type": "poker_hand_combo", "combo_idx": 1, "target": 1},
                    {"id": "cas_pcg_two_pairs", "name": "Win one hand with two pair at a poker table", "points": 75, "type": "poker_hand_combo", "combo_idx": 2, "target": 1},
                    {"id": "cas_pcg_win_1000", "name": "Win $1,000 in Cash game", "points": 125, "type": "poker_money", "target": 1000},
                    {"id": "cas_pcg_win_10000", "name": "Win $10,000 in Cash game", "points": 25, "type": "poker_money", "target": 10000},
                    {"id": "cas_pcg_win_2500", "name": "Win $2,500 in Cash game", "points": 50, "type": "poker_money", "target": 2500},
                ]
            },
            "poker_tournament": {
                "id": "poker_tournament",
                "name": "Poker tournament",
                "skill": "competition",
                "objectives": [
                    {"id": "cas_pt_top5_lvl1", "name": "Finish at least 5th in the 1st level of the Tournament", "points": 150, "type": "tourn_rank", "sat_idx": 0, "max_rank": 5, "target": 1},
                    {"id": "cas_pt_top5_lvl2", "name": "Finish at least 5th in the 2nd level of the Tournament", "points": 50, "type": "tourn_rank", "sat_idx": 1, "max_rank": 5, "target": 1},
                    {"id": "cas_pt_top5_lvl3", "name": "Finish at least 5th in the 3rd level of the Tournament", "points": 30, "type": "tourn_rank", "sat_idx": 2, "max_rank": 5, "target": 1},
                    {"id": "cas_pt_top5_lvl4", "name": "Finish at least 5th in the 4th level of the Tournament", "points": 15, "type": "tourn_rank", "sat_idx": 3, "max_rank": 5, "target": 1},
                    {"id": "cas_pt_win_lvl1", "name": "Win the 1st level of the Tournament", "points": 150, "type": "tourn_rank", "sat_idx": 0, "max_rank": 1, "target": 1},
                    {"id": "cas_pt_win_lvl2", "name": "Win the 2nd level of the Tournament", "points": 75, "type": "tourn_rank", "sat_idx": 1, "max_rank": 1, "target": 1},
                    {"id": "cas_pt_win_lvl3", "name": "Win the 3rd level of the Tournament", "points": 50, "type": "tourn_rank", "sat_idx": 2, "max_rank": 1, "target": 1},
                    {"id": "cas_pt_win_lvl4", "name": "Win the last level of the Tournament", "points": 30, "type": "tourn_rank", "sat_idx": 3, "max_rank": 1, "target": 1},
                    {"id": "cas_pt_win_2", "name": "Win 2 Tournaments", "points": 30, "type": "tourn_total_wins", "target": 2},
                    {"id": "cas_pt_win_25k", "name": "Win $25,000 in Tournament", "points": 125, "type": "tourn_money", "target": 25000},
                    {"id": "cas_pt_win_100k", "name": "Win $100,000 in Tournament", "points": 25, "type": "tourn_money", "target": 100000},
                ]
            },
            "roulette": {
                "id": "roulette",
                "name": "Roulette",
                "skill": "competition",
                "objectives": [
                    {"id": "cas_roul_streak_3", "name": "Win 3 times in a row at roulette", "points": 100, "type": "roul_streak", "target": 3},
                    {"id": "cas_roul_streak_5", "name": "Win 5 times in a row at roulette", "points": 25, "type": "roul_streak", "target": 5},
                    {"id": "cas_roul_bet_black_red", "name": "Win one time on Black or Red", "points": 35, "type": "roul_combo", "combo_idx": 0, "target": 1},
                    {"id": "cas_roul_bet_column", "name": "Win one time on Column", "points": 35, "type": "roul_combo", "combo_idx": 1, "target": 1},
                    {"id": "cas_roul_bet_even_odd", "name": "Win one time on Even or Odd", "points": 35, "type": "roul_combo", "combo_idx": 2, "target": 1},
                    {"id": "cas_roul_bet_six_line", "name": "Win one time on Six line", "points": 20, "type": "roul_combo", "combo_idx": 3, "target": 1},
                    {"id": "cas_roul_bet_0_00", "name": "Win one time on a 0 or 00", "points": 25, "type": "roul_green", "target": 1},
                    {"id": "cas_roul_bet_corner", "name": "Win one time on a Corner", "points": 20, "type": "roul_combo", "combo_idx": 4, "target": 1},
                    {"id": "cas_roul_bet_dozen", "name": "Win one time on a Dozen", "points": 35, "type": "roul_combo", "combo_idx": 5, "target": 1},
                    {"id": "cas_roul_bet_half", "name": "Win one time on a Half", "points": 35, "type": "roul_combo", "combo_idx": 6, "target": 1},
                    {"id": "cas_roul_bet_hsplit", "name": "Win one time on a Horizontal split", "points": 10, "type": "roul_combo", "combo_idx": 7, "target": 1},
                    {"id": "cas_roul_bet_straight_up", "name": "Win one time on a Straight-up number", "points": 25, "type": "roul_combo", "combo_idx": 8, "target": 1},
                    {"id": "cas_roul_bet_street", "name": "Win one time on a Street", "points": 10, "type": "roul_combo", "combo_idx": 9, "target": 1},
                    {"id": "cas_roul_bet_trio", "name": "Win one time on a Trio", "points": 10, "type": "roul_combo", "combo_idx": 10, "target": 1},
                    {"id": "cas_roul_bet_vsplit", "name": "Win one time on a Vertical split", "points": 10, "type": "roul_combo", "combo_idx": 11, "target": 1},
                    {"id": "cas_roul_win_10000", "name": "Win $10,000 at roulette", "points": 25, "type": "roul_money", "target": 10000},
                    {"id": "cas_roul_win_2500", "name": "Win $2,500 at roulette", "points": 50, "type": "roul_money", "target": 2500},
                    {"id": "cas_roul_win_500", "name": "Win $500 at roulette", "points": 125, "type": "roul_money", "target": 500},
                ]
            },
            "sit_and_go": {
                "id": "sit_and_go",
                "name": "Sit & Go Poker",
                "skill": "competition",
                "objectives": [
                    {"id": "cas_sng_1st_priv", "name": "Finish 1st at a Sit & Go private table", "points": 25, "type": "sng_priv_rank", "rank_idx": 0, "target": 1},
                    {"id": "cas_sng_1st_pub", "name": "Finish 1st at a Sit & Go table of 6 or 10 players", "points": 25, "type": "sng_pub_rank", "rank_idx": 0, "target": 1},
                    {"id": "cas_sng_2nd_pub", "name": "Finish 2nd at a Sit & Go table of 6 or 10 players", "points": 25, "type": "sng_pub_rank", "rank_idx": 1, "target": 1},
                    {"id": "cas_sng_3rd_pub", "name": "Finish 3rd at a Sit & Go table of 6 or 10 players", "points": 25, "type": "sng_pub_rank", "rank_idx": 2, "target": 1},
                    {"id": "cas_sng_4th_pub", "name": "Finish 4th at a Sit & Go table of 6 or 10 players", "points": 25, "type": "sng_pub_rank", "rank_idx": 3, "target": 1},
                    {"id": "cas_sng_5th_pub", "name": "Finish 5th at a Sit & Go table of 6 or 10 players", "points": 25, "type": "sng_pub_rank", "rank_idx": 4, "target": 1},
                    {"id": "cas_sng_flop_10", "name": "Win 10 hands before the Flop in Sit & Go", "points": 10, "type": "sng_before_flop", "target": 10},
                    {"id": "cas_sng_flop_20", "name": "Win 20 hands before the Flop in Sit & Go", "points": 25, "type": "sng_before_flop", "target": 20},
                    {"id": "cas_sng_turn_10", "name": "Win 10 hands before the Turn in Sit & Go", "points": 50, "type": "sng_before_turn", "target": 10},
                    {"id": "cas_sng_river_10", "name": "Win 10 hands before the River in Sit & Go", "points": 100, "type": "sng_before_river", "target": 10},
                    {"id": "cas_sng_win_25", "name": "Win 25 hands in Sit & Go", "points": 125, "type": "sng_win_hands", "target": 25},
                    {"id": "cas_sng_win_75", "name": "Win 75 hands in Sit & Go", "points": 50, "type": "sng_win_hands", "target": 75},
                    {"id": "cas_sng_streak_3", "name": "Win 3 hands in a row in Sit & Go", "points": 125, "type": "sng_streak", "target": 3},
                    {"id": "cas_sng_streak_5", "name": "Win 5 hands in a row in Sit & Go", "points": 50, "type": "sng_streak", "target": 5},
                    {"id": "cas_sng_win_5000", "name": "Win $5,000 in Sit & Go", "points": 125, "type": "sng_money", "target": 5000},
                    {"id": "cas_sng_win_20000", "name": "Win $20,000 in Sit & Go", "points": 50, "type": "sng_money", "target": 20000},
                    {"id": "cas_sng_win_50000", "name": "Win $50,000 in Sit & Go", "points": 25, "type": "sng_money", "target": 50000},
                ]
            },
            "casino_racing": {
                "id": "casino_racing",
                "name": "Casino racing",
                "skill": "competition",
                "objectives": [
                    {"id": "cas_race_lobby_245", "name": "Beat the time in the Lobby Race Against the Clock (< 2:45.00)", "points": 225, "type": "race_time", "field": "_time_attack_best_score", "target": 16500},
                    {"id": "cas_race_lobby_230", "name": "Beat the time in the Lobby Race Against the Clock (< 2:30.00)", "points": 150, "type": "race_time", "field": "_time_attack_best_score", "target": 15000},
                    {"id": "cas_race_vip_245", "name": "Beat the time in the VIP Race Against the Clock (< 2:45.00)", "points": 225, "type": "race_time", "field": "_time_attack_vip_best_score", "target": 16500},
                    {"id": "cas_race_vip_230", "name": "Beat the time in the VIP Race Against the Clock (< 2:30.00)", "points": 150, "type": "race_time", "field": "_time_attack_vip_best_score", "target": 15000},
                ]
            }
        }
    },
    "discovery": {
        "id": "discovery",
        "name": "Discovery",
        "max_points": 1000,
        "max_level": 2,
        "sections": {
            "casino_games": {
                "id": "casino_games",
                "name": "Casino games",
                "skill": "discovery",
                "objectives": [
                    {"id": "cas_disc_race_island", "name": "Do the race around the island", "points": 50, "type": "prog_counter", "field": "_time_attack_played_count", "target": 1},
                    {"id": "cas_disc_roul_hist", "name": "Look at the History on roulette", "points": 20, "type": "prog_bool", "field": "_roulette_used_historic", "target": 1},
                    {"id": "cas_disc_roul_rebet", "name": "Use the Rebet button on roulette", "points": 20, "type": "prog_bool", "field": "_roulette_used_rebet", "target": 1},
                    {"id": "cas_disc_roul_seen_12", "name": "See 12 of the possible numbers drawn at roulette", "points": 50, "type": "roul_seen_nums", "target": 12},
                    {"id": "cas_disc_roul_seen_24", "name": "See 24 of the possible numbers drawn at roulette", "points": 10, "type": "roul_seen_nums", "target": 24},
                    {"id": "cas_disc_roul_seen_0_00", "name": "See the 0 or 00 drawn at roulette", "points": 10, "type": "roul_seen_green", "target": 1},
                    {"id": "cas_disc_roul_all_bets", "name": "Place all the different kinds of bets at roulette", "points": 15, "type": "roul_played_bets", "target": 16},
                    {"id": "cas_disc_sm_2lines_10", "name": "Play 10 times with 2 lines activated at slot machine", "points": 50, "type": "sm_played_field", "field": "_played_with_2_lines", "target": 10},
                    {"id": "cas_disc_sm_3lines_20", "name": "Play 20 times with 3 lines activated at slot machine", "points": 25, "type": "sm_played_field", "field": "_played_with_3_lines", "target": 20},
                    {"id": "cas_disc_sm_5lines_30", "name": "Play 30 times with 5 lines activated at slot machine", "points": 15, "type": "sm_played_field", "field": "_played_with_5_lines", "target": 30},
                    {"id": "cas_disc_sm_9lines_40", "name": "Play 40 times with 9 lines activated at slot machine", "points": 10, "type": "sm_played_field", "field": "_played_with_9_lines", "target": 40},
                    {"id": "cas_disc_sm_respin_10", "name": "Play 10 times with the respin mode of a slot machine", "points": 35, "type": "sm_played_field", "field": "_play_by_relaunch_count", "target": 10},
                    {"id": "cas_disc_sm_respin_25", "name": "Play 25 times with the respin mode of a slot machine", "points": 15, "type": "sm_played_field", "field": "_play_by_relaunch_count", "target": 25},
                    {"id": "cas_disc_sm_3types", "name": "Play 3 types of slot machine", "points": 35, "type": "sm_types_count", "target": 3},
                    {"id": "cas_disc_sm_6types", "name": "Play each type of slot machine", "points": 10, "type": "sm_types_count", "target": 6},
                    {"id": "cas_disc_pcg_each_table", "name": "Play each Cash Game table in the casino", "points": 60, "type": "pcg_tables_count", "target": 12},
                    {"id": "cas_disc_sng_pub_each_table", "name": "Play each Public Sit & Go table", "points": 50, "type": "sng_pub_tables_count", "target": 12},
                    {"id": "cas_disc_sng_priv_free", "name": "Play one game of Private free Sit & go", "points": 20, "type": "sng_priv_played", "idx": 0, "target": 1},
                    {"id": "cas_disc_sng_priv_paying", "name": "Play one game of Private paying Sit & go", "points": 20, "type": "sng_priv_played", "idx": 1, "target": 1},
                    {"id": "cas_disc_pt_part_lvl1", "name": "Participate to level 1 of the poker tournament", "points": 75, "type": "tourn_played", "sat_idx": 0, "target": 1},
                    {"id": "cas_disc_pt_part_lvl2", "name": "Participate to level 2 of the poker tournament", "points": 50, "type": "tourn_played", "sat_idx": 1, "target": 1},
                    {"id": "cas_disc_pt_part_lvl3", "name": "Participate to level 3 of the poker tournament", "points": 25, "type": "tourn_played", "sat_idx": 2, "target": 1},
                    {"id": "cas_disc_pt_part_lvl4", "name": "Participate to level 4 of the poker tournament", "points": 15, "type": "tourn_played", "sat_idx": 3, "target": 1},
                ]
            },
            "emotes_and_cocktails": {
                "id": "emotes_and_cocktails",
                "name": "Emotes and cocktails",
                "skill": "discovery",
                "objectives": [
                    {"id": "cas_disc_drink_50", "name": "Drink a $50 cocktail", "points": 50, "type": "drink_cocktail_tier", "drink_idx": 0, "target": 1},
                    {"id": "cas_disc_drink_200", "name": "Drink a $200 cocktail", "points": 30, "type": "drink_cocktail_tier", "drink_idx": 1, "target": 1},
                    {"id": "cas_disc_drink_500", "name": "Drink a $500 cocktail", "points": 15, "type": "drink_cocktail_tier", "drink_idx": 2, "target": 1},
                    {"id": "cas_disc_drink_1000", "name": "Drink a $1,000 cocktail", "points": 10, "type": "drink_cocktail_tier", "drink_idx": 3, "target": 1},
                    {"id": "cas_disc_emote_table_8", "name": "Play 8 emotes at a poker table", "points": 25, "type": "emotes_played_count", "target": 8},
                    {"id": "cas_disc_emote_table_16", "name": "Play half of the emotes at the poker table at least once.", "points": 15, "type": "emotes_played_count", "target": 16},
                    {"id": "cas_disc_emote_table_32", "name": "Play all of the emotes at the poker table at least once.", "points": 10, "type": "emotes_played_count", "target": 32},
                ]
            },
            "features_and_actions": {
                "id": "features_and_actions",
                "name": "Features and actions",
                "skill": "discovery",
                "objectives": [
                    {"id": "cas_disc_talk_cashier", "name": "Go talk to the cashier", "points": 30, "type": "prog_counter", "field": "_cashier_seen_with_success_count", "target": 1},
                    {"id": "cas_disc_buy_clothing", "name": "Buy an item of clothing from the shop", "points": 30, "type": "bitfield_popcount", "field": "_cloth_bought", "target": 1},
                    {"id": "cas_disc_enter_car_hall", "name": "Enter the car in the hall", "points": 25, "type": "prog_bool", "field": "_hall_car_seen", "target": 1},
                    {"id": "cas_disc_enter_car_vip", "name": "Enter the car on the VIP terrace", "points": 10, "type": "prog_bool", "field": "_vip_car_seen", "target": 1},
                    {"id": "cas_disc_access_vip", "name": "Access to the VIP terrace", "points": 15, "type": "vip_access", "target": 1},
                    {"id": "cas_disc_inspect_vip", "name": "Inspect exclusive rewards on the VIP Terrace", "points": 10, "type": "bitfield_popcount", "field": "_satellite_prize_inspected_flag", "target": 3},
                    {"id": "cas_disc_look_rankings", "name": "Look at the rankings", "points": 15, "type": "prog_bool", "field": "_rankings_seen", "target": 1},
                    {"id": "cas_disc_look_mylife", "name": "Look at your own MyTDULife profile", "points": 15, "type": "prog_bool", "field": "_look_at_mylife_done", "target": 1},
                    {"id": "cas_disc_photo_avatar", "name": "Take a picture of your avatar in MyTDULife", "points": 10, "type": "prog_bool", "field": "_photo_mode_used", "target": 1},
                ]
            }
        }
    },
    "collection": {
        "id": "collection",
        "name": "Collection",
        "max_points": 1000,
        "max_level": 2,
        "sections": {
            "cocktails_and_emotes": {
                "id": "cocktails_and_emotes",
                "name": "Cocktails and emotes",
                "skill": "collection",
                "objectives": [
                    {"id": "cas_coll_unlock_cocktails_10", "name": "Unlock 10 cocktails", "points": 150, "type": "bitfield_popcount", "field": "_cocktail_unlock_flag", "target": 10},
                    {"id": "cas_coll_unlock_cocktails_15", "name": "Unlock the 15 cocktails", "points": 100, "type": "bitfield_popcount", "field": "_cocktail_unlock_flag", "target": 15},
                    {"id": "cas_coll_unlock_emotes_15", "name": "Unlock 15 emotes", "points": 150, "type": "bitfield_popcount", "field": "_emote_unlock_flag", "target": 15},
                    {"id": "cas_coll_unlock_emotes_25", "name": "Unlock 25 emotes", "points": 75, "type": "bitfield_popcount", "field": "_emote_unlock_flag", "target": 25},
                    {"id": "cas_coll_unlock_emotes_32", "name": "Unlock all the emotes", "points": 25, "type": "bitfield_popcount", "field": "_emote_unlock_flag", "target": 32},
                ]
            },
            "shopping": {
                "id": "shopping",
                "name": "Shopping",
                "skill": "collection",
                "objectives": [
                    {"id": "cas_coll_cloth_third", "name": "Own one third of the shop's clothes", "points": 100, "type": "bitfield_popcount", "field": "_cloth_bought", "target": 8},
                    {"id": "cas_coll_cloth_two_thirds", "name": "Own two thirds of the shop's clothes", "points": 35, "type": "bitfield_popcount", "field": "_cloth_bought", "target": 16},
                    {"id": "cas_coll_cloth_all", "name": "Own all the shop's clothes", "points": 20, "type": "bitfield_popcount", "field": "_cloth_bought", "target": 25},
                    {"id": "cas_coll_shoes_4", "name": "Own four pairs of shoes", "points": 50, "type": "bitfield_popcount", "field": "_shoes_bought", "target": 4},
                    {"id": "cas_coll_glasses_2", "name": "Own two pairs of sunglasses", "points": 50, "type": "bitfield_popcount", "field": "_glasses_bought", "target": 2},
                ]
            },
            "exclusive_rewards": {
                "id": "exclusive_rewards",
                "name": "Exclusive rewards",
                "skill": "collection",
                "objectives": [
                    {"id": "cas_coll_car_hall", "name": "Possess one car of the casino", "points": 50, "type": "prog_bool", "field": "_hall_car_won", "target": 1},
                    {"id": "cas_coll_car_vip", "name": "Possess the two cars of the casino", "points": 20, "type": "prog_two_cars", "target": 2},
                    {"id": "cas_coll_exclusive_clothes", "name": "Win the exclusive clothing set", "points": 100, "type": "prog_bool", "field": "_cloth_chic_set", "target": 1},
                    {"id": "cas_coll_exclusive_furniture", "name": "Win the exclusive house furniture set", "points": 25, "type": "prog_bool", "field": "_furniture_chic_set", "target": 1},
                    {"id": "cas_coll_exclusive_stickers", "name": "Win the exclusive stickers set", "points": 50, "type": "prog_bool", "field": "_sticker_set", "target": 1},
                ]
            }
        }
    },
    "social": {
        "id": "social",
        "name": "Social",
        "max_points": 1000,
        "max_level": 2,
        "sections": {
            "cocktails": {
                "id": "cocktails",
                "name": "Cocktails",
                "skill": "social",
                "objectives": [
                    {"id": "cas_soc_drink_poker_10", "name": "Drink 10 cocktails at a Poker table", "points": 100, "type": "prog_counter", "field": "_cocktail_drink_count_on_poker", "target": 10},
                    {"id": "cas_soc_drink_poker_25", "name": "Drink 25 cocktails at a Poker table", "points": 30, "type": "prog_counter", "field": "_cocktail_drink_count_on_poker", "target": 25},
                    {"id": "cas_soc_receive_cocktails_10", "name": "Get 10 cocktails offered by other players", "points": 25, "type": "array_sum", "field": "_cocktail_received_array", "target": 10},
                    {"id": "cas_soc_offer_cocktails_5", "name": "Offer a cocktail to 5 different players", "points": 100, "type": "array_nonzero", "field": "_cocktail_different_players_offered_to", "target": 5},
                    {"id": "cas_soc_offer_cocktails_15", "name": "Offer a cocktail to 15 different players", "points": 25, "type": "array_nonzero", "field": "_cocktail_different_players_offered_to", "target": 15},
                ]
            },
            "meeting_people": {
                "id": "meeting_people",
                "name": "Meeting people",
                "skill": "social",
                "objectives": [
                    {"id": "cas_soc_friends_3", "name": "Get 3 friends", "points": 75, "type": "prog_counter", "field": "_friend_count", "target": 3},
                    {"id": "cas_soc_friends_5", "name": "Get 5 friends", "points": 25, "type": "prog_counter", "field": "_friend_count", "target": 5},
                    {"id": "cas_soc_vip_status", "name": "Get the VIP status (level 5)", "points": 50, "type": "prog_bool", "field": "_vip_status", "target": 1},
                    {"id": "cas_soc_friends_accept_invite", "name": "Your friends have accepted your invitation to join your session 10 times.", "points": 20, "type": "prog_counter", "field": "_session_invite_friend_count", "target": 10},
                ]
            },
            "playing_with_people": {
                "id": "playing_with_people",
                "name": "Playing with people",
                "skill": "social",
                "objectives": [
                    {"id": "cas_soc_look_other_profile", "name": "Consult the MyTDULife profile of another player", "points": 40, "type": "prog_bool", "field": "_look_at_mylife_of_other_done", "target": 1},
                    {"id": "cas_soc_create_sng_priv", "name": "Create and play one private Sit & Go game", "points": 100, "type": "prog_counter", "field": "_sitandgo_created_private_count", "target": 1},
                    {"id": "cas_soc_join_sng_priv", "name": "Join and play one private Sit & go game", "points": 25, "type": "prog_counter", "field": "_sitandgo_joined_private_count", "target": 1},
                    {"id": "cas_soc_sng_5_no_quit", "name": "Participate into 5 Sit & Go games without quitting", "points": 100, "type": "prog_counter", "field": "_sitandgo_played_to_the_end", "target": 5},
                    {"id": "cas_soc_pcg_opponents_10", "name": "Play a Cash game Poker against 10 different players", "points": 100, "type": "array_nonzero", "field": "_cash_game_unique_opponents_array", "target": 10},
                    {"id": "cas_soc_pcg_opponents_25", "name": "Play a Cash game Poker against 25 different players", "points": 35, "type": "array_nonzero", "field": "_cash_game_unique_opponents_array", "target": 25},
                    {"id": "cas_soc_part_3_tourn", "name": "Participate in 3 poker tournaments", "points": 25, "type": "tourn_total_played", "target": 3},
                    {"id": "cas_soc_take_money_500", "name": "Take $500 from the same player in a Poker Cash game", "points": 100, "type": "prog_counter", "field": "_cash_game_money_taken_from_opponent", "target": 500},
                    {"id": "cas_soc_take_money_2500", "name": "Take $2,500 from the same player in a Poker Cash game", "points": 25, "type": "prog_counter", "field": "_cash_game_money_taken_from_opponent", "target": 2500},
                ]
            }
        }
    }
}
