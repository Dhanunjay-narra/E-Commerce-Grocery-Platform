"""Real-time Surge Pricing and Rain/Peak-Hour Dynamic Multipliers."""
from datetime import datetime, time, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class SurgeFactors(BaseModel):
    zone_id: str
    active_orders_count: int
    available_drivers_count: int
    is_raining: bool = False
    is_peak_hours: bool = False
    traffic_congestion_factor: float = Field(default=1.0, ge=1.0, le=2.5)

class SurgeResult(BaseModel):
    base_delivery_fee: float
    surge_multiplier: float
    final_delivery_fee: float
    surge_reason: Optional[str] = None
    is_surge_applied: bool = False

class DynamicPricingEngine:
    """Calculates dynamic surge delivery fees based on supply-demand imbalance and weather."""
    
    PEAK_WINDOWS = [
        (time(7, 0), time(10, 30)),   # Morning breakfast & grocery rush
        (time(17, 30), time(21, 30)), # Evening dinner & daily replenishment rush
    ]

    @classmethod
    def is_current_time_peak(cls, current_dt: Optional[datetime] = None) -> bool:
        now = current_dt or datetime.now()
        cur_t = now.time()
        for start_t, end_t in cls.PEAK_WINDOWS:
            if start_t <= cur_t <= end_t:
                return True
        return False

    @classmethod
    def evaluate_surge(cls, base_fee: float, factors: SurgeFactors, current_dt: Optional[datetime] = None) -> SurgeResult:
        multiplier = 1.0
        reasons = []
        
        # 1. Supply-Demand Ratio
        if factors.available_drivers_count == 0:
            multiplier += 0.8
            reasons.append("High delivery demand in your area")
        else:
            ratio = factors.active_orders_count / max(1, factors.available_drivers_count)
            if ratio > 3.0:
                multiplier += 0.6
                reasons.append("Driver fleet capacity constrained")
            elif ratio > 1.5:
                multiplier += 0.3
                reasons.append("Elevated order volume")
                
        # 2. Weather Conditions
        if factors.is_raining:
            multiplier += 0.5
            reasons.append("Inclement weather surcharge (100% paid to driver)")
            
        # 3. Peak Hours
        if factors.is_peak_hours or cls.is_current_time_peak(current_dt):
            multiplier += 0.2
            reasons.append("Peak grocery rush window")
            
        # 4. Traffic Congestion
        if factors.traffic_congestion_factor > 1.3:
            multiplier += (factors.traffic_congestion_factor - 1.0) * 0.4
            reasons.append("Traffic transit delay compensation")
            
        # Cap max surge to 2.5x to preserve customer goodwill
        multiplier = min(2.5, round(multiplier, 2))
        is_surge = multiplier > 1.0
        final_fee = round(base_fee * multiplier, 2)
        
        return SurgeResult(
            base_delivery_fee=base_fee,
            surge_multiplier=multiplier,
            final_delivery_fee=final_fee,
            surge_reason="; ".join(reasons) if reasons else None,
            is_surge_applied=is_surge,
        )
