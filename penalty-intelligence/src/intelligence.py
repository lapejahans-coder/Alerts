import pandas as pd
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from scipy import stats
try:
    from scipy.stats import binomtest
except ImportError:
    # Fallback for older scipy
    from scipy.stats import binom_test as binomtest

from scipy.stats import gaussian_kde

class KeeperArchetype(Enum):
    REACTION_KEEPER = "Reaction Keeper"
    GAMBLER = "Gambler"
    HYBRID = "Hybrid"
    UNKNOWN = "Unknown"

class PressureProfile(Enum):
    CLUTCH = "Clutch"
    CHOKER = "Choker"
    STEADY = "Steady"
    UNKNOWN = "Unknown"

@dataclass
class ZoneVulnerability:
    zone_name: str
    total_shots: int
    goals_conceded: int
    saves: int
    missed: int
    concession_rate: float
    save_rate: float
    confidence_interval: Tuple[float, float]
    sample_size_rating: str
    statistical_significance: bool

@dataclass
class KeeperProfile:
    name: str
    total_penalties: int
    goals_conceded: int
    saves: int
    missed: int
    overall_save_rate: float
    archetype: KeeperArchetype
    pressure_profile: PressureProfile
    zones: Dict[str, ZoneVulnerability]
    primary_weakness: Optional[str]
    secondary_weakness: Optional[str]
    strength_zone: Optional[str]
    trend_direction: str
    recommendation_confidence: float

class PenaltyIntelligenceEngine:
    @staticmethod
    def classify_zone(goal_y: float, goal_z: float) -> str:
        # y: [-4.0, -1.33), [-1.33, 1.33), [1.33, 4.0]
        # z: [1.78, 2.67], [0.89, 1.78], [0.0, 0.89]
        if goal_z >= 1.78: row = "T"
        elif goal_z >= 0.89: row = "M"
        else: row = "B"

        if goal_y < -1.33: col = "L"
        elif goal_y < 1.33: col = "C"
        else: col = "R"

        return f"{row}{col}"

    def analyze_goalkeeper(self, df: pd.DataFrame, keeper_name: str) -> KeeperProfile:
        keeper_df = df[df['goalkeeper'] == keeper_name].copy()

        total_penalties = len(keeper_df)
        goals_conceded = len(keeper_df[keeper_df['outcome'] == 'Goal'])
        saves = len(keeper_df[keeper_df['outcome'] == 'Saved'])
        missed = len(keeper_df[keeper_df['outcome'] == 'Missed'])

        total_faced = saves + goals_conceded
        overall_save_rate = saves / total_faced if total_faced > 0 else 0.0
        overall_concession_rate = goals_conceded / total_faced if total_faced > 0 else 0.0

        keeper_df['zone'] = keeper_df.apply(lambda row: self.classify_zone(row['goal_y'], row['goal_z']), axis=1)

        zone_data = {}
        all_zones = ['TL', 'TC', 'TR', 'ML', 'MC', 'MR', 'BL', 'BC', 'BR']

        for zone in all_zones:
            z_df = keeper_df[keeper_df['zone'] == zone]
            z_total = len(z_df)
            z_goals = len(z_df[z_df['outcome'] == 'Goal'])
            z_saves = len(z_df[z_df['outcome'] == 'Saved'])
            z_missed = len(z_df[z_df['outcome'] == 'Missed'])

            z_faced = z_goals + z_saves
            z_concession_rate = z_goals / z_faced if z_faced > 0 else 0.0
            z_save_rate = z_saves / z_faced if z_faced > 0 else 0.0

            ci_low, ci_high = self._calculate_wilson_ci(z_goals, z_faced)

            if z_total < 5: rating = "poor"
            elif z_total < 15: rating = "fair"
            elif z_total < 30: rating = "good"
            else: rating = "excellent"

            if z_faced > 0:
                # Use binomtest (handles both old and new scipy if aliased)
                try:
                    res = binomtest(z_goals, n=z_faced, p=overall_concession_rate, alternative='greater')
                    p_val = getattr(res, 'pvalue', res) # handle if binom_test returns float
                except:
                    p_val = binomtest(z_goals, z_faced, overall_concession_rate, alternative='greater')
                sig = p_val < 0.05
            else:
                sig = False

            zone_data[zone] = ZoneVulnerability(
                zone_name=zone, total_shots=z_total, goals_conceded=z_goals,
                saves=z_saves, missed=z_missed, concession_rate=z_concession_rate,
                save_rate=z_save_rate, confidence_interval=(ci_low, ci_high),
                sample_size_rating=rating, statistical_significance=sig
            )

        valid_zones = [z for z in zone_data.values() if z.total_shots >= 2]
        sorted_weakness = sorted(valid_zones, key=lambda x: x.concession_rate, reverse=True)
        primary_weakness = sorted_weakness[0].zone_name if sorted_weakness else None
        secondary_weakness = sorted_weakness[1].zone_name if len(sorted_weakness) > 1 else None

        decent_sample_zones = [z for z in zone_data.values() if z.total_shots >= 3]
        sorted_strength = sorted(decent_sample_zones, key=lambda x: x.concession_rate)
        strength_zone = sorted_strength[0].zone_name if sorted_strength else None

        archetype = self._detect_archetype(keeper_df)
        pressure = self._detect_pressure_profile(keeper_df)
        trend = self._calculate_trend(keeper_df)
        rec_conf = min(total_penalties / 50.0, 1.0)

        return KeeperProfile(
            name=keeper_name, total_penalties=total_penalties, goals_conceded=goals_conceded,
            saves=saves, missed=missed, overall_save_rate=overall_save_rate,
            archetype=archetype, pressure_profile=pressure, zones=zone_data,
            primary_weakness=primary_weakness, secondary_weakness=secondary_weakness,
            strength_zone=strength_zone, trend_direction=trend, recommendation_confidence=rec_conf
        )

    def _calculate_wilson_ci(self, count: int, nobs: int, confidence: float = 0.95) -> Tuple[float, float]:
        if nobs == 0: return 0.0, 1.0
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        p = count / nobs
        denominator = 1 + z**2/nobs
        centre_adj_p = p + z**2 / (2 * nobs)
        adj_p_delta = z * np.sqrt((p * (1 - p) + z**2 / (4 * nobs)) / nobs)
        lower = (centre_adj_p - adj_p_delta) / denominator
        upper = (centre_adj_p + adj_p_delta) / denominator
        return max(0, lower), min(1, upper)

    def _detect_archetype(self, df: pd.DataFrame) -> KeeperArchetype:
        saves_df = df[df['outcome'] == 'Saved']
        if len(saves_df) < 5:
            return KeeperArchetype.UNKNOWN

        # Reaction Keeper: central saves > 35%, average height > 1.2 yards
        central_saves = len(saves_df[abs(saves_df['goal_y']) < 1.33])
        central_ratio = central_saves / len(saves_df)
        avg_height = saves_df['goal_z'].mean()

        if central_ratio > 0.35 and avg_height > 1.2:
            return KeeperArchetype.REACTION_KEEPER

        # Gambler: saves clustered on one side (high lateral skew, low std)
        if abs(saves_df['goal_y'].mean()) > 1.0 and saves_df['goal_y'].std() < 1.5:
            return KeeperArchetype.GAMBLER

        return KeeperArchetype.HYBRID

    def _detect_pressure_profile(self, df: pd.DataFrame) -> PressureProfile:
        if 'pressure_context' not in df.columns:
            return PressureProfile.UNKNOWN

        high_p = df[df['pressure_context'] == 'high']
        norm_p = df[df['pressure_context'] == 'normal']

        if len(high_p) < 3 or len(norm_p) < 3:
            return PressureProfile.UNKNOWN

        def get_rate(sub_df):
            faced = sub_df[sub_df['outcome'].isin(['Goal', 'Saved'])]
            if len(faced) == 0: return 0.0
            return len(faced[faced['outcome'] == 'Saved']) / len(faced)

        high_rate = get_rate(high_p)
        norm_rate = get_rate(norm_p)

        diff = high_rate - norm_rate
        if diff > 0.15: return PressureProfile.CLUTCH
        if diff < -0.15: return PressureProfile.CHOKER
        return PressureProfile.STEADY

    def _calculate_trend(self, df: pd.DataFrame) -> str:
        if len(df) < 10:
            return "unknown"

        df = df.sort_values('match_date')
        mid = len(df) // 2
        first_half = df.iloc[:mid]
        second_half = df.iloc[mid:]

        def get_save_rate(sub_df):
            faced = sub_df[sub_df['outcome'].isin(['Goal', 'Saved'])]
            if len(faced) == 0: return 0
            return len(faced[faced['outcome'] == 'Saved']) / len(faced)

        r1 = get_save_rate(first_half)
        r2 = get_save_rate(second_half)

        if r2 > r1 + 0.05: return "improving"
        if r2 < r1 - 0.05: return "declining"
        return "stable"

    def generate_shooter_strategy(self, profile: KeeperProfile, shooter_foot: str, pressure_context: str) -> dict:
        primary = profile.primary_weakness
        secondary = profile.secondary_weakness

        is_natural = False
        if primary:
            # Simple heuristic: R footer natural is Goal Right (Y > 0), L footer is Goal Left (Y < 0)
            if shooter_foot == "Right" and "R" in primary: is_natural = True
            if shooter_foot == "Left" and "L" in primary: is_natural = True

        side_pref = "natural" if is_natural else "across-body"

        tactics = []
        if profile.archetype == KeeperArchetype.GAMBLER:
            tactics.append("Wait for keeper movement; they commit early.")
        elif profile.archetype == KeeperArchetype.REACTION_KEEPER:
            tactics.append("Prioritize power and corners; keeper relies on reflexes.")

        if profile.pressure_profile == PressureProfile.CHOKER and pressure_context != "normal":
            tactics.append("Keeper's performance drops in high-pressure; stay calm.")

        return {
            "primary_target": primary,
            "secondary_target": secondary,
            "side_guidance": f"{side_pref} side",
            "tactics": tactics,
            "confidence": profile.recommendation_confidence,
            "sample_size_warning": "Small sample size - use caution." if profile.total_penalties < 15 else None
        }

    def generate_pre_match_briefing(self, profile: KeeperProfile) -> str:
        report = f"PRE-MATCH BRIEFING: {profile.name.upper()}\n"
        report += "="*30 + "\n"
        report += f"Archetype: {profile.archetype.value}\n"
        report += f"Overall Save Rate: {profile.overall_save_rate:.1%}\n"
        report += f"Pressure Profile: {profile.pressure_profile.value}\n"
        report += f"Recent Trend: {profile.trend_direction}\n\n"
        report += f"VULNERABILITY ANALYSIS:\n"
        if profile.primary_weakness:
            z = profile.zones[profile.primary_weakness]
            report += f"- PRIMARY TARGET: {profile.primary_weakness} zone ({z.concession_rate:.1%} concession rate).\n"
        if profile.secondary_weakness:
            report += f"- SECONDARY TARGET: {profile.secondary_weakness} zone.\n"
        if profile.strength_zone:
            report += f"- AVOID: {profile.strength_zone} zone (Keeper's strongest area).\n"
        report += f"\nTACTICAL RECOMMENDATION:\n"
        if profile.archetype == KeeperArchetype.GAMBLER:
            report += "- The keeper tends to gamble on a side. Hold your shot as late as possible.\n"
        elif profile.archetype == KeeperArchetype.REACTION_KEEPER:
            report += "- Exceptional reflexes. Ensure high power and aim for the absolute corners.\n"
        report += f"- Focus on the {profile.primary_weakness} zone where the keeper is statistically most vulnerable.\n"
        return report

    def compare_keepers(self, df: pd.DataFrame, keeper_names: List[str]) -> pd.DataFrame:
        results = []
        for name in keeper_names:
            profile = self.analyze_goalkeeper(df, name)
            results.append({
                "Keeper": name,
                "Penalties": profile.total_penalties,
                "Save Rate": f"{profile.overall_save_rate:.1%}",
                "Archetype": profile.archetype.value,
                "Weakness": profile.primary_weakness,
                "Trend": profile.trend_direction,
                "Confidence": f"{profile.recommendation_confidence:.0%}"
            })
        return pd.DataFrame(results)

    def generate_demo_dataset(self) -> pd.DataFrame:
        np.random.seed(42)
        keepers = [
            ("Alisson", KeeperArchetype.REACTION_KEEPER, "BL", "CLUTCH"),
            ("Ederson", KeeperArchetype.GAMBLER, "TR", "STEADY"),
            ("Courtois", KeeperArchetype.REACTION_KEEPER, "BR", "CLUTCH"),
            ("ter Stegen", KeeperArchetype.HYBRID, "ML", "STEADY"),
            ("Neuer", KeeperArchetype.REACTION_KEEPER, "TL", "STEADY"),
            ("Oblak", KeeperArchetype.HYBRID, "MR", "CHOKER"),
            ("Donnarumma", KeeperArchetype.GAMBLER, "TC", "CHOKER"),
            ("Martinez", KeeperArchetype.GAMBLER, "BC", "CLUTCH")
        ]

        data = []
        for name, arch, weakness, pressure in keepers:
            n = np.random.randint(30, 60)
            for i in range(n):
                date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=np.random.randint(0, 365))
                if np.random.random() < 0.35: zone = weakness
                else: zone = np.random.choice(['TL', 'TC', 'TR', 'ML', 'MC', 'MR', 'BL', 'BC', 'BR'])
                y, z = self._zone_to_coords(zone)
                ctx = "high" if np.random.random() < 0.3 else "normal"

                save_prob = 0.22
                if zone == weakness: save_prob -= 0.15
                if arch == KeeperArchetype.REACTION_KEEPER and z > 1.2: save_prob += 0.08
                if arch == KeeperArchetype.GAMBLER and abs(y) > 2.0: save_prob += 0.1

                if ctx == "high":
                    if pressure == "CLUTCH": save_prob += 0.12
                    if pressure == "CHOKER": save_prob -= 0.12

                save_prob = max(0.04, min(0.5, save_prob))
                rand = np.random.random()
                if rand < save_prob: outcome = "Saved"
                elif rand < 0.94: outcome = "Goal"
                else: outcome = "Missed"

                data.append({
                    "goalkeeper": name, "goal_y": y, "goal_z": z, "outcome": outcome,
                    "match_date": date, "pressure_context": ctx, "competition": "Champions League",
                    "shooter": f"Shooter {np.random.randint(1, 200)}", "shooter_foot": np.random.choice(["Right", "Left"])
                })
        return pd.DataFrame(data)

    def _zone_to_coords(self, zone: str) -> Tuple[float, float]:
        mapping = {
            'TL': ((-4.0, -1.33), (1.78, 2.67)), 'TC': ((-1.33, 1.33), (1.78, 2.67)), 'TR': ((1.33, 4.0), (1.78, 2.67)),
            'ML': ((-4.0, -1.33), (0.89, 1.78)), 'MC': ((-1.33, 1.33), (0.89, 1.78)), 'MR': ((1.33, 4.0), (0.89, 1.78)),
            'BL': ((-4.0, -1.33), (0.0, 0.89)), 'BC': ((-1.33, 1.33), (0.0, 0.89)), 'BR': ((1.33, 4.0), (0.0, 0.89)),
        }
        y_range, z_range = mapping[zone]
        y = np.random.uniform(y_range[0], y_range[1])
        z = np.random.uniform(z_range[0], z_range[1])
        return y, z
