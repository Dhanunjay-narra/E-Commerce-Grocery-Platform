"""GST/VAT Tax Slab calculations and HSN code classification."""
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
    """Calculates itemized and composite GST across multi-state shipping."""
    
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
