"""Generates extended backend domain services, pricing engines, logistics algorithms, warehouse slotting, subscriptions, payouts, recipes, and catalog datasets."""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    ensure_dir(os.path.dirname(full_path))
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Wrote {rel_path} ({len(content.splitlines()):,} lines)")

def main():
    print("[*] Generating Backend Domain Engines...")

    # 1. Pricing Engine
    write_file("backend/app/modules/pricing/tax_slabs.py", """\"\"\"GST/VAT Tax Slab calculations and HSN code classification.\"\"\"
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class TaxCategory(str, Enum):
    EXEMPT = "EXEMPT"  # Fresh vegetables, fruits, unprocessed milk, eggs, loose grains (0%)
    FIVE_PERCENT = "5%"  # Packaged paneer, butter, edible oils, spices, tea (5%)
    TWELVE_PERCENT = "12%"  # Fruit juices, ghee, packaged dry fruits, namkeen (12%)
    EIGHTEEN_PERCENT = "18%"  # Chocolates, biscuits, pastries, detergents, cleaning (18%)
    TWENTY_EIGHT_PERCENT = "28%"  # Aerated sugary drinks, energy drinks (28%)

class HSNCodeMapping(BaseModel):
    hsn_code: str
    description: str
    tax_rate: float
    is_essential: bool = False
    cess_rate: float = 0.0

HSN_DIRECTORY: Dict[str, HSNCodeMapping] = {
    "0702": HSNCodeMapping(hsn_code="0702", description="Fresh Tomatoes (Organic/Hybrid)", tax_rate=0.0, is_essential=True),
    "0703": HSNCodeMapping(hsn_code="0703", description="Fresh Onions, Garlic & Leeks", tax_rate=0.0, is_essential=True),
    "0701": HSNCodeMapping(hsn_code="0701", description="Fresh Potatoes", tax_rate=0.0, is_essential=True),
    "0808": HSNCodeMapping(hsn_code="0808", description="Fresh Apples and Pears", tax_rate=0.0, is_essential=True),
    "0803": HSNCodeMapping(hsn_code="0803", description="Fresh Bananas", tax_rate=0.0, is_essential=True),
    "0401": HSNCodeMapping(hsn_code="0401", description="Fresh Pasteurized Milk (Unsweetened)", tax_rate=0.0, is_essential=True),
    "0402": HSNCodeMapping(hsn_code="0402", description="Milk Powder and Condensed Milk", tax_rate=5.0),
    "0405": HSNCodeMapping(hsn_code="0405", description="Butter and Dairy Spreads", tax_rate=5.0),
    "0406": HSNCodeMapping(hsn_code="0406", description="Cheese and Paneer (Packaged)", tax_rate=5.0),
    "1006": HSNCodeMapping(hsn_code="1006", description="Basmati and Non-Basmati Rice", tax_rate=0.0, is_essential=True),
    "1101": HSNCodeMapping(hsn_code="1101", description="Wheat Flour (Atta / Maida)", tax_rate=0.0, is_essential=True),
    "1508": HSNCodeMapping(hsn_code="1508", description="Groundnut Cooking Oil", tax_rate=5.0, is_essential=True),
    "1512": HSNCodeMapping(hsn_code="1512", description="Sunflower Cooking Oil", tax_rate=5.0, is_essential=True),
    "1515": HSNCodeMapping(hsn_code="1515", description="Sesame / Gingelly Oil", tax_rate=5.0),
    "0902": HSNCodeMapping(hsn_code="0902", description="Tea & Infusions", tax_rate=5.0),
    "0901": HSNCodeMapping(hsn_code="0901", description="Coffee Beans & Ground Coffee", tax_rate=5.0),
    "1905": HSNCodeMapping(hsn_code="1905", description="Bakery Bread, Biscuits & Cakes", tax_rate=5.0),
    "2009": HSNCodeMapping(hsn_code="2009", description="Packaged Fruit Juices & Purees", tax_rate=12.0),
    "2106": HSNCodeMapping(hsn_code="2106", description="Ready to Cook Food Mixes", tax_rate=12.0),
    "2202": HSNCodeMapping(hsn_code="2202", description="Aerated Soft Drinks", tax_rate=28.0, cess_rate=12.0),
    "3401": HSNCodeMapping(hsn_code="3401", description="Organic Soaps & Cleaners", tax_rate=18.0),
    "3402": HSNCodeMapping(hsn_code="3402", description="Detergents & Dishwashing Liquids", tax_rate=18.0),
}

class TaxBreakdownResult(BaseModel):
    item_id: str
    taxable_amount: float
    tax_rate: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    total_tax: float
    total_with_tax: float

class TaxEngine:
    \"\"\"Calculates itemized and composite GST across multi-state shipping.\"\"\"
    
    @staticmethod
    def calculate_tax(
        item_id: str,
        amount: float,
        hsn_code: Optional[str] = None,
        origin_state: str = "Telangana",
        destination_state: str = "Telangana",
    ) -> TaxBreakdownResult:
        mapping = HSN_DIRECTORY.get(hsn_code or "0702", HSNCodeMapping(hsn_code="9999", description="General Food", tax_rate=5.0))
        rate = mapping.tax_rate
        
        taxable = round(amount, 2)
        total_tax = round((taxable * rate) / 100.0, 2)
        
        is_intra_state = origin_state.strip().lower() == destination_state.strip().lower()
        
        if is_intra_state:
            cgst = round(total_tax / 2.0, 2)
            sgst = round(total_tax - cgst, 2)
            igst = 0.0
        else:
            cgst = 0.0
            sgst = 0.0
            igst = total_tax
            
        return TaxBreakdownResult(
            item_id=item_id,
            taxable_amount=taxable,
            tax_rate=rate,
            cgst_amount=cgst,
            sgst_amount=sgst,
            igst_amount=igst,
            total_tax=total_tax,
            total_with_tax=round(taxable + total_tax, 2),
        )

    @staticmethod
    def calculate_cart_tax_summary(items: List[Dict[str, Any]], origin_state: str = "Telangana", destination_state: str = "Telangana") -> Dict[str, Any]:
        total_taxable = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_tax = 0.0
        breakdowns = []
        
        for it in items:
            item_id = it.get("item_id", "unknown")
            amt = float(it.get("amount", 0.0))
            hsn = it.get("hsn_code", "0702")
            res = TaxEngine.calculate_tax(item_id, amt, hsn, origin_state, destination_state)
            
            total_taxable += res.taxable_amount
            total_cgst += res.cgst_amount
            total_sgst += res.sgst_amount
            total_igst += res.igst_amount
            total_tax += res.total_tax
            breakdowns.append(res.dict())
            
        return {
            "total_taxable_amount": round(total_taxable, 2),
            "total_cgst": round(total_cgst, 2),
            "total_sgst": round(total_sgst, 2),
            "total_igst": round(total_igst, 2),
            "total_tax": round(total_tax, 2),
            "grand_total": round(total_taxable + total_tax, 2),
            "item_breakdowns": breakdowns,
        }
""")

    # 2. Surge Pricing & Dynamic Discounting
    write_file("backend/app/modules/pricing/surge_pricing.py", """\"\"\"Real-time Surge Pricing and Rain/Peak-Hour Dynamic Multipliers.\"\"\"
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
    \"\"\"Calculates dynamic surge delivery fees based on supply-demand imbalance and weather.\"\"\"
    
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
""")

    # 3. Logistics & Fleet Routing
    write_file("backend/app/modules/logistics/routing_engine.py", """\"\"\"Last-Mile Route Optimization, Haversine Matrix, and Traveling Salesperson Heuristics.\"\"\"
import math
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel

class GeoLocation(BaseModel):
    latitude: float
    longitude: float
    label: str = ""
    order_id: str = ""
    estimated_drop_duration_mins: int = 5

class RouteSegment(BaseModel):
    from_point: GeoLocation
    to_point: GeoLocation
    distance_km: float
    transit_duration_mins: float

class OptimizedRoute(BaseModel):
    total_distance_km: float
    total_duration_mins: float
    waypoints_order: List[GeoLocation]
    segments: List[RouteSegment]

class FleetRoutingEngine:
    \"\"\"Solves multi-stop drop sequencing from dark store hub to customer doorsteps.\"\"\"
    
    EARTH_RADIUS_KM = 6371.0
    AVERAGE_URBAN_SPEED_KMPH = 24.0  # Urban electric scooter speed

    @classmethod
    def haversine_distance(cls, loc1: GeoLocation, loc2: GeoLocation) -> float:
        lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
        lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        
        return round(cls.EARTH_RADIUS_KM * c, 3)

    @classmethod
    def estimate_travel_time(cls, distance_km: float) -> float:
        # Distance / Speed in hours -> convert to minutes + traffic buffer
        hours = distance_km / cls.AVERAGE_URBAN_SPEED_KMPH
        mins = hours * 60.0
        return round(mins * 1.15, 1)  # 15% traffic buffer

    @classmethod
    def solve_nearest_neighbor(cls, origin: GeoLocation, destinations: List[GeoLocation]) -> OptimizedRoute:
        if not destinations:
            return OptimizedRoute(total_distance_km=0.0, total_duration_mins=0.0, waypoints_order=[origin], segments=[])
            
        unvisited = list(destinations)
        current = origin
        route_order = [origin]
        segments = []
        total_dist = 0.0
        total_time = 0.0
        
        while unvisited:
            nearest = None
            min_dist = float('inf')
            
            for candidate in unvisited:
                d = cls.haversine_distance(current, candidate)
                if d < min_dist:
                    min_dist = d
                    nearest = candidate
                    
            unvisited.remove(nearest)
            transit_time = cls.estimate_travel_time(min_dist)
            drop_time = nearest.estimated_drop_duration_mins
            
            segment = RouteSegment(
                from_point=current,
                to_point=nearest,
                distance_km=min_dist,
                transit_duration_mins=transit_time,
            )
            segments.append(segment)
            route_order.append(nearest)
            
            total_dist += min_dist
            total_time += transit_time + drop_time
            current = nearest
            
        return OptimizedRoute(
            total_distance_km=round(total_dist, 2),
            total_duration_mins=round(total_time, 1),
            waypoints_order=route_order,
            segments=segments,
        )
""")

    # 4. Cold Chain & Warehouse Bin Slotting
    write_file("backend/app/modules/warehouse/bin_slotting.py", """\"\"\"Warehouse Aisle/Rack/Bin Slotting and Cold Chain Sensor Compliance.\"\"\"
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
    \"\"\"Assigns grocery inventory to optimal thermal zones and monitors HACCP cold-chain integrity.\"\"\"
    
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
""")

    # 5. Subscriptions & Recurring Delivery
    write_file("backend/app/modules/subscriptions/recurring_billing.py", """\"\"\"Household Grocery Recurring Cadence and Subscription Billing Scheduler.\"\"\"
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta, timezone
from pydantic import BaseModel, Field

class CadenceType(str, Enum):
    DAILY = "DAILY"                 # Fresh milk, bread, coriander, eggs
    ALTERNATE_DAYS = "ALTERNATE_DAYS"
    WEEKLY = "WEEKLY"               # Vegetables, fruits, paneer
    BI_WEEKLY = "BI_WEEKLY"         # Snacks, beverages
    MONTHLY = "MONTHLY"             # Rice, Atta, Cooking oils, Ghee, Cleaning

class SubscriptionItem(BaseModel):
    product_id: str
    product_name: str
    quantity: float
    unit: str
    unit_price: float

class GrocerySubscription(BaseModel):
    id: str
    user_id: str
    household_id: Optional[str] = None
    items: List[SubscriptionItem]
    cadence: CadenceType
    preferred_slot_time: str = "07:00-09:00"
    is_paused: bool = False
    pause_until: Optional[date] = None
    next_delivery_date: date
    auto_pay_enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SubscriptionSchedulerEngine:
    \"\"\"Computes next recurring delivery triggers and handles skip/pause workflows.\"\"\"

    @staticmethod
    def calculate_next_date(current_date: date, cadence: CadenceType) -> date:
        if cadence == CadenceType.DAILY:
            return current_date + timedelta(days=1)
        elif cadence == CadenceType.ALTERNATE_DAYS:
            return current_date + timedelta(days=2)
        elif cadence == CadenceType.WEEKLY:
            return current_date + timedelta(days=7)
        elif cadence == CadenceType.BI_WEEKLY:
            return current_date + timedelta(days=14)
        elif cadence == CadenceType.MONTHLY:
            # Approximate 30-day month cadence
            return current_date + timedelta(days=30)
        return current_date + timedelta(days=7)

    @classmethod
    def generate_scheduled_orders(cls, subscriptions: List[GrocerySubscription], target_date: date) -> List[Dict[str, Any]]:
        orders_to_create = []
        
        for sub in subscriptions:
            if sub.is_paused:
                if sub.pause_until and target_date >= sub.pause_until:
                    sub.is_paused = False
                    sub.pause_until = None
                else:
                    continue
                    
            if sub.next_delivery_date == target_date:
                total_amt = sum(item.quantity * item.unit_price for item in sub.items)
                orders_to_create.append({
                    "subscription_id": sub.id,
                    "user_id": sub.user_id,
                    "household_id": sub.household_id,
                    "scheduled_date": str(target_date),
                    "delivery_slot": sub.preferred_slot_time,
                    "order_type": "SUBSCRIPTION_RECURRING",
                    "total_amount": round(total_amt, 2),
                    "items": [item.dict() for item in sub.items],
                })
                
        return orders_to_create
""")

    print("[*] Completed Core Backend Domain Engines Generation!")

if __name__ == "__main__":
    main()
