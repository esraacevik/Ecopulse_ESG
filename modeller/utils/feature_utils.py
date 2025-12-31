"""
Feature Engineering Utilities
=============================

Feature oluşturma ve dönüştürme fonksiyonları
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Union
from datetime import datetime


def create_time_features(
    df: pd.DataFrame,
    date_column: str,
    features: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Tarih kolonundan zaman özellikleri oluştur
    
    Args:
        df: DataFrame
        date_column: Tarih kolonu
        features: Oluşturulacak özellikler (None ise tümü)
    
    Returns:
        Özellikler eklenmiş DataFrame
    """
    df = df.copy()
    
    # Ensure datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    all_features = ["hour", "day_of_week", "day_of_month", "month", "quarter", 
                   "year", "is_weekend", "is_month_start", "is_month_end",
                   "week_of_year", "season"]
    
    if features is None:
        features = all_features
    
    dt = df[date_column].dt
    
    if "hour" in features:
        df["hour"] = dt.hour
    
    if "day_of_week" in features:
        df["day_of_week"] = dt.dayofweek
    
    if "day_of_month" in features:
        df["day_of_month"] = dt.day
    
    if "month" in features:
        df["month"] = dt.month
    
    if "quarter" in features:
        df["quarter"] = dt.quarter
    
    if "year" in features:
        df["year"] = dt.year
    
    if "is_weekend" in features:
        df["is_weekend"] = (dt.dayofweek >= 5).astype(int)
    
    if "is_month_start" in features:
        df["is_month_start"] = dt.is_month_start.astype(int)
    
    if "is_month_end" in features:
        df["is_month_end"] = dt.is_month_end.astype(int)
    
    if "week_of_year" in features:
        df["week_of_year"] = dt.isocalendar().week.astype(int)
    
    if "season" in features:
        # Northern hemisphere seasons
        df["season"] = df["month"].apply(lambda x: 
            0 if x in [12, 1, 2] else  # Winter
            1 if x in [3, 4, 5] else   # Spring
            2 if x in [6, 7, 8] else   # Summer
            3                           # Fall
        )
    
    return df


def create_lag_features(
    df: pd.DataFrame,
    column: str,
    lags: List[int],
    group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Lag özellikleri oluştur
    
    Args:
        df: DataFrame
        column: Lag oluşturulacak kolon
        lags: Lag sayıları listesi [1, 24, 168] gibi
        group_by: Gruplama kolonu (opsiyonel)
    
    Returns:
        Lag özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    
    for lag in lags:
        col_name = f"{column}_lag_{lag}"
        
        if group_by:
            df[col_name] = df.groupby(group_by)[column].shift(lag)
        else:
            df[col_name] = df[column].shift(lag)
    
    return df


def create_rolling_features(
    df: pd.DataFrame,
    column: str,
    windows: List[int],
    functions: Optional[List[str]] = None,
    group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Rolling window özellikleri oluştur
    
    Args:
        df: DataFrame
        column: Rolling oluşturulacak kolon
        windows: Window boyutları [24, 168] gibi
        functions: Uygulanacak fonksiyonlar ["mean", "std", "min", "max"]
        group_by: Gruplama kolonu (opsiyonel)
    
    Returns:
        Rolling özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    
    if functions is None:
        functions = ["mean", "std"]
    
    for window in windows:
        for func in functions:
            col_name = f"{column}_rolling_{func}_{window}"
            
            if group_by:
                grouped = df.groupby(group_by)[column]
                if func == "mean":
                    df[col_name] = grouped.transform(lambda x: x.rolling(window).mean())
                elif func == "std":
                    df[col_name] = grouped.transform(lambda x: x.rolling(window).std())
                elif func == "min":
                    df[col_name] = grouped.transform(lambda x: x.rolling(window).min())
                elif func == "max":
                    df[col_name] = grouped.transform(lambda x: x.rolling(window).max())
            else:
                if func == "mean":
                    df[col_name] = df[column].rolling(window).mean()
                elif func == "std":
                    df[col_name] = df[column].rolling(window).std()
                elif func == "min":
                    df[col_name] = df[column].rolling(window).min()
                elif func == "max":
                    df[col_name] = df[column].rolling(window).max()
    
    return df


def create_diff_features(
    df: pd.DataFrame,
    column: str,
    periods: List[int] = [1],
    group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Fark özellikleri oluştur
    
    Args:
        df: DataFrame
        column: Fark oluşturulacak kolon
        periods: Periyot sayıları
        group_by: Gruplama kolonu
    
    Returns:
        Fark özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    
    for period in periods:
        col_name = f"{column}_diff_{period}"
        
        if group_by:
            df[col_name] = df.groupby(group_by)[column].diff(period)
        else:
            df[col_name] = df[column].diff(period)
    
    return df


def create_pct_change_features(
    df: pd.DataFrame,
    column: str,
    periods: List[int] = [1],
    group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Yüzde değişim özellikleri oluştur
    
    Args:
        df: DataFrame
        column: Yüzde değişim oluşturulacak kolon
        periods: Periyot sayıları
        group_by: Gruplama kolonu
    
    Returns:
        Yüzde değişim özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    
    for period in periods:
        col_name = f"{column}_pct_change_{period}"
        
        if group_by:
            df[col_name] = df.groupby(group_by)[column].pct_change(period)
        else:
            df[col_name] = df[column].pct_change(period)
    
    return df


def create_cyclical_features(
    df: pd.DataFrame,
    column: str,
    max_value: int
) -> pd.DataFrame:
    """
    Döngüsel özellikleri sin/cos olarak kodla
    
    Args:
        df: DataFrame
        column: Kodlanacak kolon (hour, month, day_of_week, vb.)
        max_value: Maksimum değer (hour: 24, month: 12, dow: 7)
    
    Returns:
        Sin/cos özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    
    df[f"{column}_sin"] = np.sin(2 * np.pi * df[column] / max_value)
    df[f"{column}_cos"] = np.cos(2 * np.pi * df[column] / max_value)
    
    return df


def create_weather_features(
    df: pd.DataFrame,
    weather_df: pd.DataFrame,
    date_column: str,
    location_column: Optional[str] = None,
    weather_date_column: str = "date",
    weather_location_column: str = "location"
) -> pd.DataFrame:
    """
    Hava durumu özelliklerini ekle
    
    Args:
        df: Ana DataFrame
        weather_df: Hava durumu DataFrame
        date_column: Ana DataFrame tarih kolonu
        location_column: Ana DataFrame lokasyon kolonu
        weather_date_column: Weather tarih kolonu
        weather_location_column: Weather lokasyon kolonu
    
    Returns:
        Weather özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    weather_df = weather_df.copy()
    
    # Ensure datetime
    df[date_column] = pd.to_datetime(df[date_column])
    weather_df[weather_date_column] = pd.to_datetime(weather_df[weather_date_column])
    
    # Extract date for merge
    df["_merge_date"] = df[date_column].dt.date
    weather_df["_merge_date"] = weather_df[weather_date_column].dt.date
    
    # Merge based on date (and optionally location)
    if location_column and weather_location_column:
        merge_cols = ["_merge_date", location_column]
        weather_df = weather_df.rename(columns={weather_location_column: location_column})
        merge_on = merge_cols
    else:
        merge_on = "_merge_date"
    
    # Select weather columns
    weather_cols = [c for c in weather_df.columns if c not in 
                   [weather_date_column, weather_location_column, "_merge_date"]]
    
    df = df.merge(
        weather_df[["_merge_date"] + weather_cols].drop_duplicates(),
        on="_merge_date",
        how="left"
    )
    
    # Clean up
    df = df.drop(columns=["_merge_date"])
    
    return df


def create_degree_days(
    df: pd.DataFrame,
    temperature_column: str,
    base_temp_heating: float = 18.0,
    base_temp_cooling: float = 24.0
) -> pd.DataFrame:
    """
    Heating/Cooling Degree Days oluştur
    
    Args:
        df: DataFrame
        temperature_column: Sıcaklık kolonu
        base_temp_heating: HDD baz sıcaklığı (Celsius)
        base_temp_cooling: CDD baz sıcaklığı (Celsius)
    
    Returns:
        HDD/CDD eklenmiş DataFrame
    """
    df = df.copy()
    
    # Heating Degree Days (ne kadar ısıtma gerekli)
    df["hdd"] = np.maximum(0, base_temp_heating - df[temperature_column])
    
    # Cooling Degree Days (ne kadar soğutma gerekli)
    df["cdd"] = np.maximum(0, df[temperature_column] - base_temp_cooling)
    
    return df


def create_interaction_features(
    df: pd.DataFrame,
    column_pairs: List[tuple],
    operations: List[str] = ["multiply"]
) -> pd.DataFrame:
    """
    Etkileşim özellikleri oluştur
    
    Args:
        df: DataFrame
        column_pairs: Kolon çiftleri [(col1, col2), ...]
        operations: Uygulanacak işlemler ["multiply", "divide", "add", "subtract"]
    
    Returns:
        Etkileşim özellikleri eklenmiş DataFrame
    """
    df = df.copy()
    
    for col1, col2 in column_pairs:
        for op in operations:
            if op == "multiply":
                df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
            elif op == "divide":
                df[f"{col1}_div_{col2}"] = df[col1] / (df[col2] + 1e-10)
            elif op == "add":
                df[f"{col1}_plus_{col2}"] = df[col1] + df[col2]
            elif op == "subtract":
                df[f"{col1}_minus_{col2}"] = df[col1] - df[col2]
    
    return df


def select_features_by_importance(
    df: pd.DataFrame,
    target_column: str,
    n_features: int = 20,
    method: str = "mutual_info"
) -> List[str]:
    """
    Önem skoruna göre özellik seç
    
    Args:
        df: DataFrame
        target_column: Hedef kolon
        n_features: Seçilecek özellik sayısı
        method: "mutual_info" veya "correlation"
    
    Returns:
        Seçilen özellik isimleri
    """
    from sklearn.feature_selection import mutual_info_regression
    
    feature_columns = [c for c in df.columns if c != target_column]
    X = df[feature_columns].select_dtypes(include=[np.number])
    y = df[target_column]
    
    # Drop NaN
    mask = X.notna().all(axis=1) & y.notna()
    X = X[mask]
    y = y[mask]
    
    if method == "mutual_info":
        scores = mutual_info_regression(X, y)
        importance = pd.Series(scores, index=X.columns)
    
    elif method == "correlation":
        importance = X.apply(lambda x: abs(x.corr(y)))
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    top_features = importance.nlargest(n_features).index.tolist()
    return top_features

