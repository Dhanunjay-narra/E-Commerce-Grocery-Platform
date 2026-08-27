"""Warehouse Aisle/Rack/Bin Slotting and Cold Chain Sensor Compliance."""
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class StorageZoneType(str, Enum):
    AMBIENT = "AMBIENT"           # Room temperature: 20C - 28C (Rice, Flour, Oils, Snacks)
    COOL_PANTRY = "COOL_PANTRY"   # Cool ambient: 14C - 18C (Potatoes, Onions, Bananas, Bread)
    CHILLED = "CHILLED"           # Cold chain: 2C - 6C (Fresh Milk, Butter, Cheese, Paneer, Cut Fruits)
    FROZEN = "FROZEN"             # Frozen chain: -18C to -22C (Ice creams, Frozen peas, Meat)

class BinSlot(BaseModel):
    bin_code: str                 # e.g. "A01-R02-S03" (Aisle 1, Rack 2, Shelf 3)
    zone_type: StorageZoneType
    max_weight_capacity_kg: float = 250.0
    current_weight_kg: float = 0.0
    is_refrigerated: bool = False
    temperature_sensor_id: Optional[str] = None
    target_temperature_celsius: float = 24.0
    current_temperature_celsius: float = 24.0

class ColdChainTelemetry(BaseModel):
    sensor_id: str
    bin_code: str
    recorded_at: datetime
    temperature_celsius: float
    humidity_pct: float
    is_breach: bool = False
    breach_message: Optional[str] = None

class WarehouseSlottingEngine:
    """Assigns grocery inventory to optimal thermal zones and monitors HACCP cold-chain integrity."""
    
    TEMPERATURE_THRESHOLDS = {
        StorageZoneType.AMBIENT: (18.0, 30.0),
        StorageZoneType.COOL_PANTRY: (12.0, 20.0),
        StorageZoneType.CHILLED: (1.0, 8.0),
        StorageZoneType.FROZEN: (-25.0, -15.0),
    }

    @classmethod
    def evaluate_telemetry(cls, zone: StorageZoneType, telemetry: ColdChainTelemetry) -> ColdChainTelemetry:
        min_temp, max_temp = cls.TEMPERATURE_THRESHOLDS.get(zone, (15.0, 30.0))
        temp = telemetry.temperature_celsius
        
        if temp < min_temp:
            telemetry.is_breach = True
            telemetry.breach_message = f"Critical Low Temp Alert: {temp}C is below minimum safe threshold {min_temp}C"
        elif temp > max_temp:
            telemetry.is_breach = True
            telemetry.breach_message = f"Critical High Temp Alert: {temp}C exceeds maximum safe threshold {max_temp}C"
        else:
            telemetry.is_breach = False
            telemetry.breach_message = "Normal optimal operating temperature"
            
        return telemetry

    @classmethod
    def find_best_slot_for_product(cls, category_name: str, weight_kg: float, available_bins: List[BinSlot]) -> Optional[BinSlot]:
        category_lower = category_name.lower()
        
        if any(w in category_lower for w in ["milk", "butter", "cheese", "paneer", "dairy", "yogurt"]):
            target_zone = StorageZoneType.CHILLED
        elif any(w in category_lower for w in ["ice cream", "frozen", "meat"]):
            target_zone = StorageZoneType.FROZEN
        elif any(w in category_lower for w in ["onion", "potato", "apple", "banana", "bread"]):
            target_zone = StorageZoneType.COOL_PANTRY
        else:
            target_zone = StorageZoneType.AMBIENT
            
        matching_bins = [b for b in available_bins if b.zone_type == target_zone and (b.current_weight_kg + weight_kg) <= b.max_weight_capacity_kg]
        if not matching_bins:
            return None
            
        # Select bin with least weight for balanced loading
        matching_bins.sort(key=lambda x: x.current_weight_kg)
        return matching_bins[0]
