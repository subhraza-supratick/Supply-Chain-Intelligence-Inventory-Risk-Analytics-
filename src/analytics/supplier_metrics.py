"""
Supplier Performance Metrics & Scorecard Module.
Calculates key procurement and vendor performance metrics:
- On-Time Delivery Rate (%)
- Average Delay (Days)
- Order Fill Rate (%)
- Defect / Damage Rate (%)
- Supplier Risk Score (0-100)
"""

import pandas as pd
import numpy as np

def calculate_supplier_scorecard(fact_deliveries, fact_purchase_orders, dim_supplier):
    """
    Computes a comprehensive scorecard for every supplier.
    """
    print("Calculating Supplier Performance Scorecards...")
    
    # 1. Delivery level metrics
    deliv_agg = fact_deliveries.groupby("supplier_id").agg(
        total_deliveries=("delivery_id", "count"),
        on_time_deliveries=("is_on_time", "sum"),
        avg_transit_days=("transit_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        total_qty_ordered=("quantity_ordered", "sum"),
        total_qty_received=("quantity_received", "sum"),
        total_damaged_qty=("damaged_quantity", "sum")
    ).reset_index()
    
    # Calculate percentages
    deliv_agg["on_time_delivery_rate_pct"] = round(
        (deliv_agg["on_time_deliveries"] / deliv_agg["total_deliveries"]) * 100, 2
    )
    deliv_agg["fill_rate_pct"] = round(
        (deliv_agg["total_qty_received"] / np.maximum(1, deliv_agg["total_qty_ordered"])) * 100, 2
    )
    deliv_agg["defect_rate_pct"] = round(
        (deliv_agg["total_damaged_qty"] / np.maximum(1, deliv_agg["total_qty_received"])) * 100, 2
    )
    deliv_agg["avg_delay_days"] = round(deliv_agg["avg_delay_days"], 2)
    
    # 2. PO level spend
    po_agg = fact_purchase_orders.groupby("supplier_id").agg(
        total_pos_issued=("po_id", "count"),
        total_procurement_spend=("total_po_cost", "sum")
    ).reset_index()
    
    scorecard = pd.merge(dim_supplier, deliv_agg, on="supplier_id", how="left").fillna(0)
    scorecard = pd.merge(scorecard, po_agg, on="supplier_id", how="left").fillna(0)
    
    # 3. Composite Supplier Risk Score (0 to 100)
    # Factors:
    # - Late delivery penalty: (100 - OTD%) * 0.40
    # - Delay magnitude penalty: min(100, avg_delay_days * 12) * 0.30
    # - Defect penalty: min(100, defect_rate_pct * 15) * 0.20
    # - Underfill penalty: (100 - Fill_Rate%) * 0.10
    
    late_penalty = (100.0 - scorecard["on_time_delivery_rate_pct"]).clip(lower=0) * 0.40
    delay_penalty = np.clip(scorecard["avg_delay_days"] * 12.0, 0, 100) * 0.30
    defect_penalty = np.clip(scorecard["defect_rate_pct"] * 15.0, 0, 100) * 0.20
    fill_penalty = (100.0 - scorecard["fill_rate_pct"]).clip(lower=0) * 0.10
    
    scorecard["supplier_risk_score"] = round(late_penalty + delay_penalty + defect_penalty + fill_penalty, 1)
    
    # Supplier Tier / Rating
    def get_supplier_rating(score):
        if score < 20:
            return "Preferred / Tier 1 (Stellar)"
        elif score < 45:
            return "Standard / Tier 2 (Reliable)"
        elif score < 70:
            return "Under Watch / Tier 3 (Moderate Risk)"
        else:
            return "High Risk / Critical Review Required"
            
    scorecard["supplier_rating"] = scorecard["supplier_risk_score"].apply(get_supplier_rating)
    
    return scorecard
