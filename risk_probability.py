#!/usr/bin/env python3
from dataclasses import dataclass
import itertools
import functools
from typing import Tuple

@dataclass
class PossibilityResult:
    wins: int = 0
    tie: int = 0
    lose: int = 0

    def total(self) -> int:
        return self.wins + self.tie + self.lose


@functools.lru_cache(maxsize=None)
def compute_possibilities_one_turn(attacker_dices: int, defender_dices: int) -> PossibilityResult:
    result = PossibilityResult()
    for attacker_dice_list in itertools.product(range(1, 7), repeat=attacker_dices):
        max_attacker_dice = max(*attacker_dice_list) if len(attacker_dice_list) > 1 else attacker_dice_list[0]
        for defender_dice_list in itertools.product(range(1, 7), repeat=defender_dices):
            max_defender_dice = max(*defender_dice_list) if len(defender_dice_list) > 1 else defender_dice_list[0]
            if max_attacker_dice > max_defender_dice:
                result.wins += 1
            elif max_attacker_dice == max_defender_dice:
                result.tie += 1
            else:
                result.lose += 1
    return result


@functools.lru_cache(maxsize=None)
def compute_win_rate_after_n_turns(attacker_dices: int, defender_dices: int, turns: int) -> float:
    possibilities_one_turn = compute_possibilities_one_turn(
            attacker_dices=attacker_dices,
            defender_dices=defender_dices)

    win_rate_one_turn = float(possibilities_one_turn.wins) / float(possibilities_one_turn.total())
    tie_rate_one_turn = float(possibilities_one_turn.tie) / float(possibilities_one_turn.total())

    win_rate = win_rate_one_turn
    for turn in range(1, turns):
        win_rate += (tie_rate_one_turn ** turn) * win_rate_one_turn

    return win_rate


def clamp_probability(p: float) -> float:
    return max(0., min(1., p))


def dices_for_fight(attacker_bataillons: int, defender_bataillons: int, fortress: bool) -> Tuple[int, int]:
    attacker_dices = min(attacker_bataillons, 3)
    defender_dices = min(defender_bataillons, 2)
    if defender_dices == 1 and fortress:
        defender_dices = 2

    return attacker_dices, defender_dices

@functools.lru_cache(maxsize=None)
def compute_win_rate_whole_fight(attacker_bataillons: int, defender_bataillons: int, fortress: bool) -> float:
    if attacker_bataillons == 0:
        return 0.
    elif defender_bataillons == 0:
        return 1.

    # How many bataillons for this turn
    attacker_dices, defender_dices = dices_for_fight(attacker_bataillons, defender_bataillons, fortress)
    win_rate = compute_win_rate_after_n_turns(attacker_dices, defender_dices, turns=6)
    lose_rate = clamp_probability(1. - win_rate)
    return clamp_probability(
            win_rate * compute_win_rate_whole_fight(attacker_bataillons, defender_bataillons - 1, fortress)
            + (1. - win_rate) * compute_win_rate_whole_fight(attacker_bataillons - 1, defender_bataillons, fortress)
    )


@functools.lru_cache(maxsize=None)
def compute_win_rate_whole_fight_with_n_remaining(attacker_bataillons: int, defender_bataillons: int, fortress: bool, remaining_bataillons) -> float:
    if attacker_bataillons == 0:
        return 0.
    elif defender_bataillons == 0:
        if attacker_bataillons == remaining_bataillons:
            return 1.
        else:
            return 0.
    elif attacker_bataillons < remaining_bataillons:
        return 0.

    # How many bataillons for this turn
    attacker_dices, defender_dices = dices_for_fight(attacker_bataillons, defender_bataillons, fortress)
    win_rate = compute_win_rate_after_n_turns(attacker_dices, defender_dices, turns=6)
    lose_rate = clamp_probability(1. - win_rate)
    return clamp_probability(
            win_rate * compute_win_rate_whole_fight_with_n_remaining(attacker_bataillons, defender_bataillons - 1, fortress, remaining_bataillons)
            + (1. - win_rate) * compute_win_rate_whole_fight_with_n_remaining(attacker_bataillons - 1, defender_bataillons, fortress, remaining_bataillons)
    )

for attacker_bataillons in range(1, 7):
    for defender_bataillons in range(1, 7):
        win_rate = compute_win_rate_whole_fight(attacker_bataillons, defender_bataillons, fortress=False)
        print(f"Win rate for {attacker_bataillons} attacker vs {defender_bataillons} defender: {win_rate * 100.:.2f}%")
        for remaining_bataillons in range(1, attacker_bataillons + 1):
            win_rate = compute_win_rate_whole_fight_with_n_remaining(attacker_bataillons, defender_bataillons, fortress=False, remaining_bataillons=remaining_bataillons)
            print(f"  Winning with {remaining_bataillons} bataillons remaining: {win_rate * 100.:.2f}%")
