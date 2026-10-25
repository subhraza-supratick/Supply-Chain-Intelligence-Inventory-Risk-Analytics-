"""
Master Pipeline Orchestration Script.
Executes the end-to-end Supply Chain Analytics & Machine Learning Pipeline:
1. Load Raw Datasets
2. Clean and Standardize Data
3. Run Data Quality & Validation Suite
4. Transform into Star Schema Data Warehouse
5. Compute Inventory KPIs & Pareto ABC Classification
6. Calculate Supplier Performance Scorecards
7. Engineer Features & Train Random Forest Demand Forecasting Model
8. Evaluate Model Metrics (MAE, RMSE, MAPE, R2)
9. Compute Composite Inventory Risk Scores & Actionable Business Recommendations
10. Export Analytics Datasets for SQL Data Warehouse and Power BI Dashboard Ingestion
"""

import os
import sys
import time
import pandas as pd

# Add repo root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.etl.load_data import load_raw_csvs, get_db_engine, save_to_db, PROCESSED_DATA_DIR
from src.etl.clean_data import clean_all_data
from src.etl.validate_data import validate_all_data
from src.etl.transform_data import transform_all_data
from src.analytics.inventory_kpis import calculate_inventory_kpis, perform_abc_analysis
from src.analytics.supplier_metrics import calculate_supplier_scorecard
from src.analytics.risk_scoring import calculate_inventory_risk_scores
from src.forecasting.feature_engineering import build_demand_features, split_chronological
from src.forecasting.train_model import train_demand_model, get_feature_importance
from src.forecasting.evaluate_model import evaluate_forecasts, generate_forecast_export

def run_end_to_end_pipeline():
    start_time = time.time()
    print("=" * 80)
    print("SUPPLY CHAIN INTELLIGENCE & INVENTORY RISK ANALYTICS PIPELINE")
    print("=" * 80)
    
    # 1. LOAD RAW DATA
    print("\n>>> STEP 1: LOADING RAW DATASETS")
    raw_data = load_raw_csvs()
    
    # 2. CLEAN DATA
    print("\n>>> STEP 2: CLEANING AND STANDARDIZING DATA")
    cleaned_data = clean_all_data(raw_data)
    
    # 3. DATA QUALITY & VALIDATION
    print("\n>>> STEP 3: AUTOMATED DATA QUALITY & INTEGRITY VALIDATION")
    dq_summary, is_valid = validate_all_data(cleaned_data)
    dq_summary.to_csv(os.path.join(PROCESSED_DATA_DIR, "data_quality_report.csv"), index=False)
    
    # 4. TRANSFORM & STAR SCHEMA DW
    print("\n>>> STEP 4: STAR SCHEMA DATA WAREHOUSE TRANSFORMATION")
    dw_tables = transform_all_data(cleaned_data)
    
    # 5. INVENTORY KPIS & ABC ANALYSIS
    print("\n>>> STEP 5: INVENTORY KPI ANALYSIS & ABC CLASSIFICATION")
    df_abc = perform_abc_analysis(dw_tables["fact_sales"], dw_tables["dim_product"])
    df_abc.to_csv(os.path.join(PROCESSED_DATA_DIR, "abc_inventory_analysis.csv"), index=False)
    
    kpi_df = calculate_inventory_kpis(dw_tables["fact_sales"], dw_tables["fact_inventory"], dw_tables["dim_product"])
    
    # 6. SUPPLIER SCORECARD
    print("\n>>> STEP 6: SUPPLIER PERFORMANCE SCORECARD")
    supplier_scorecard = calculate_supplier_scorecard(dw_tables["fact_deliveries"], dw_tables["fact_purchase_orders"], dw_tables["dim_supplier"])
    supplier_scorecard.to_csv(os.path.join(PROCESSED_DATA_DIR, "supplier_scorecard.csv"), index=False)
    
    # 7. DEMAND FORECASTING (ML)
    print("\n>>> STEP 7: DEMAND FORECASTING FEATURE ENGINEERING & MACHINE LEARNING")
    df_features = build_demand_features(dw_tables["fact_sales"])
    X_train, y_train, X_test, y_test, train_df, test_df, feature_cols = split_chronological(df_features, split_date="2024-10-01")
    
    model = train_demand_model(X_train, y_train, model_type="random_forest", n_estimators=100)
    
    # Feature Importances
    feat_imp = get_feature_importance(model, feature_cols)
    print("\nTop 5 Predictive Demand Features:")
    print(feat_imp.head(5).to_string(index=False))
    feat_imp.to_csv(os.path.join(PROCESSED_DATA_DIR, "feature_importances.csv"), index=False)
    
    # 8. EVALUATION & FORECAST EXPORT
    print("\n>>> STEP 8: MODEL EVALUATION & FORECAST EXPORT")
    y_pred = model.predict(X_test)
    eval_metrics = evaluate_forecasts(y_test, y_pred)
    
    test_eval_df, forecast_agg_df = generate_forecast_export(model, test_df, X_test, dw_tables["dim_product"])
    
    # 9. INVENTORY RISK SCORING & RECOMMENDATIONS
    print("\n>>> STEP 9: COMPOSITE INVENTORY RISK SCORING & RECOMMENDATIONS")
    risk_df = calculate_inventory_risk_scores(kpi_df, supplier_scorecard, forecast_agg_df, dw_tables["fact_sales"])
    # Merge ABC class
    risk_df = pd.merge(risk_df, df_abc[["product_id", "abc_class"]], on="product_id", how="left")
    risk_file = os.path.join(PROCESSED_DATA_DIR, "inventory_risk_scores.csv")
    risk_df.to_csv(risk_file, index=False)
    print(f" -> Saved complete Inventory Risk Scores to {risk_file}")
    
    # 10. SAVE FINAL ANALYTICS TABLES TO DW (SQLite / PostgreSQL)
    print("\n>>> STEP 10: SAVING ANALYTICS TABLES TO DATA WAREHOUSE")
    analytics_tables = {
        "analytics_inventory_risk": risk_df,
        "analytics_supplier_scorecard": supplier_scorecard,
        "analytics_abc_analysis": df_abc,
        "analytics_demand_forecasts": forecast_agg_df
    }
    engine = get_db_engine()
    save_to_db(analytics_tables, engine)
    
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"END-TO-END SUPPLY CHAIN PIPELINE EXECUTED SUCCESSFULLY IN {elapsed} SECONDS!")
    print("All processed datasets, SQL DW tables, ML forecasts, and risk scores are ready.")
    print("=" * 80)

if __name__ == "__main__":
    run_end_to_end_pipeline()
