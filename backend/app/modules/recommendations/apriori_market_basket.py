"""Market Basket Analysis and Apriori Association Mining for Grocery Upsell and Cross-Sell."""
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from pydantic import BaseModel

class AssociationRule(BaseModel):
    antecedents: List[str]
    consequents: List[str]
    support: float
    confidence: float
    lift: float

class MarketBasketAnalyzer:
    """Calculates live Support, Confidence, and Lift for frequently co-purchased grocery items."""

    @classmethod
    def mine_rules(
        cls,
        transactions: List[List[str]],
        min_support: float = 0.05,
        min_confidence: float = 0.4,
    ) -> List[AssociationRule]:
        num_trans = len(transactions)
        if num_trans == 0:
            return []

        item_counts = defaultdict(int)
        pair_counts = defaultdict(int)

        for trans in transactions:
            unique_items = sorted(list(set(trans)))
            for item in unique_items:
                item_counts[item] += 1
            for i in range(len(unique_items)):
                for j in range(i + 1, len(unique_items)):
                    pair = (unique_items[i], unique_items[j])
                    pair_counts[pair] += 1

        rules = []
        for (item_a, item_b), count in pair_counts.items():
            pair_support = count / num_trans
            if pair_support < min_support:
                continue

            supp_a = item_counts[item_a] / num_trans
            supp_b = item_counts[item_b] / num_trans

            conf_a_to_b = pair_support / supp_a
            lift_a_to_b = conf_a_to_b / supp_b

            if conf_a_to_b >= min_confidence:
                rules.append(AssociationRule(
                    antecedents=[item_a],
                    consequents=[item_b],
                    support=round(pair_support, 4),
                    confidence=round(conf_a_to_b, 4),
                    lift=round(lift_a_to_b, 3),
                ))

            conf_b_to_a = pair_support / supp_b
            lift_b_to_a = conf_b_to_a / supp_a

            if conf_b_to_a >= min_confidence:
                rules.append(AssociationRule(
                    antecedents=[item_b],
                    consequents=[item_a],
                    support=round(pair_support, 4),
                    confidence=round(conf_b_to_a, 4),
                    lift=round(lift_b_to_a, 3),
                ))

        rules.sort(key=lambda r: (r.lift, r.confidence), reverse=True)
        return rules
