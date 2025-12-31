"""
Data Utilities
==============

Veri okuma, temizleme ve dönüştürme fonksiyonları
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Union, Generator
import warnings


def load_csv(
    path: Union[str, Path],
    chunks: bool = False,
    chunk_size: int = 100000,
    **kwargs
) -> Union[pd.DataFrame, Generator]:
    """
    CSV dosyasını yükle
    
    Args:
        path: Dosya yolu
        chunks: Büyük dosyalar için chunk'lar halinde oku
        chunk_size: Chunk boyutu
        **kwargs: pd.read_csv parametreleri
    
    Returns:
        DataFrame veya chunk generator
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if chunks:
        return pd.read_csv(path, chunksize=chunk_size, **kwargs)
    
    return pd.read_csv(path, **kwargs)


def load_excel(
    path: Union[str, Path],
    sheet: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Excel dosyasını yükle
    
    Args:
        path: Dosya yolu
        sheet: Sheet adı (None ise ilk sheet)
        **kwargs: pd.read_excel parametreleri
    
    Returns:
        DataFrame
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if sheet:
        return pd.read_excel(path, sheet_name=sheet, **kwargs)
    
    return pd.read_excel(path, **kwargs)


def clean_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    columns: Optional[List[str]] = None,
    fill_value: Optional[float] = None
) -> pd.DataFrame:
    """
    Eksik değerleri temizle
    
    Args:
        df: DataFrame
        strategy: "drop", "mean", "median", "mode", "ffill", "bfill", "value"
        columns: İşlenecek kolonlar (None ise tümü)
        fill_value: strategy="value" için dolgu değeri
    
    Returns:
        Temizlenmiş DataFrame
    """
    df = df.copy()
    
    if columns is None:
        columns = df.columns.tolist()
    
    if strategy == "drop":
        df = df.dropna(subset=columns)
    
    elif strategy == "mean":
        for col in columns:
            if df[col].dtype in [np.float64, np.int64, float, int]:
                df[col] = df[col].fillna(df[col].mean())
    
    elif strategy == "median":
        for col in columns:
            if df[col].dtype in [np.float64, np.int64, float, int]:
                df[col] = df[col].fillna(df[col].median())
    
    elif strategy == "mode":
        for col in columns:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
    
    elif strategy == "ffill":
        df[columns] = df[columns].ffill()
    
    elif strategy == "bfill":
        df[columns] = df[columns].bfill()
    
    elif strategy == "value":
        if fill_value is None:
            raise ValueError("fill_value required for strategy='value'")
        df[columns] = df[columns].fillna(fill_value)
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return df


def normalize_columns(
    df: pd.DataFrame,
    columns: List[str],
    method: str = "minmax"
) -> pd.DataFrame:
    """
    Kolonları normalize et
    
    Args:
        df: DataFrame
        columns: Normalize edilecek kolonlar
        method: "minmax" veya "zscore"
    
    Returns:
        Normalize edilmiş DataFrame
    """
    df = df.copy()
    
    for col in columns:
        if col not in df.columns:
            warnings.warn(f"Column not found: {col}")
            continue
        
        if method == "minmax":
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df[col] = (df[col] - min_val) / (max_val - min_val)
        
        elif method == "zscore":
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                df[col] = (df[col] - mean_val) / std_val
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    return df


def detect_outliers(
    df: pd.DataFrame,
    column: str,
    method: str = "iqr",
    threshold: float = 1.5
) -> pd.Series:
    """
    Outlier tespiti
    
    Args:
        df: DataFrame
        column: Kontrol edilecek kolon
        method: "iqr" veya "zscore"
        threshold: Eşik değeri (IQR için 1.5, Z-score için 3)
    
    Returns:
        Boolean series (True = outlier)
    """
    values = df[column]
    
    if method == "iqr":
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return (values < lower) | (values > upper)
    
    elif method == "zscore":
        z_scores = (values - values.mean()) / values.std()
        return np.abs(z_scores) > threshold
    
    else:
        raise ValueError(f"Unknown method: {method}")


def resample_timeseries(
    df: pd.DataFrame,
    date_column: str,
    freq: str = "H",
    agg_func: str = "mean"
) -> pd.DataFrame:
    """
    Zaman serisini yeniden örnekle
    
    Args:
        df: DataFrame
        date_column: Tarih kolonu
        freq: Örnekleme frekansı ("H", "D", "W", "M", vb.)
        agg_func: Aggregation fonksiyonu ("mean", "sum", "max", "min")
    
    Returns:
        Yeniden örneklenmiş DataFrame
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.set_index(date_column)
    
    if agg_func == "mean":
        return df.resample(freq).mean().reset_index()
    elif agg_func == "sum":
        return df.resample(freq).sum().reset_index()
    elif agg_func == "max":
        return df.resample(freq).max().reset_index()
    elif agg_func == "min":
        return df.resample(freq).min().reset_index()
    else:
        raise ValueError(f"Unknown agg_func: {agg_func}")


def merge_datasets(
    dfs: List[pd.DataFrame],
    on: Union[str, List[str]],
    how: str = "inner"
) -> pd.DataFrame:
    """
    Birden fazla DataFrame'i birleştir
    
    Args:
        dfs: DataFrame listesi
        on: Birleştirme kolonları
        how: Birleştirme tipi
    
    Returns:
        Birleştirilmiş DataFrame
    """
    if len(dfs) < 2:
        raise ValueError("At least 2 DataFrames required")
    
    result = dfs[0]
    for df in dfs[1:]:
        result = result.merge(df, on=on, how=how)
    
    return result


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    DataFrame özet bilgisi
    
    Args:
        df: DataFrame
    
    Returns:
        Özet dictionary
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "memory_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
    }

