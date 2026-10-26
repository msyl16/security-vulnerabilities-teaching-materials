import pandas as pd
import os
import shutil


from sklearn.metrics import (
    confusion_matrix,
    precision_score, 
    recall_score,  
    accuracy_score,
    f1_score,
)


def left_join(df_1: pd.DataFrame, df_2: pd.DataFrame, cols:list) -> pd.DataFrame:
    """
    Joins two Dataframes on Basis auf two identical columns.
    
    Params:
        * df_1: DataFrame
        * df_2: DataFrame
        * cols: list of two strings
    
    Output:
        * Left joined DataFrame
    """
    
    return (
        df_1
        .merge(
            df_2,
            left_on=cols[0],
            right_on=cols[1],
            how="left"
        )
    )



def filter_sample_cols(
        n: int, 
        by_col: str, 
        id: str, 
        df_: pd.DataFrame, 
        random: int=7,
) -> list:

    return (
        df_
        .groupby(by_col, as_index=False)
        .sample(n=n, random_state=random)
        [id]
    ).to_list()



def expand_list_entries_to_different_columns(
    df: pd.DataFrame,
    columns: list[str],
    drop_original_columns: bool=True,
) -> pd.DataFrame:
    
    df_result = df.copy()

    for col in columns:
        if col not in df_result.columns:
            continue

        # Listen in neues DataFrame aufteilen
        expanded = pd.DataFrame(
            df_result[col]
            .apply(lambda x: x if isinstance(x, (list, tuple)) else [])
            .tolist(),
            index=df_result.index,
        )

        # Spalten durchnummerieren (col_1, col_2, ...)
        expanded.columns = [f"{col}_{i+1}" for i in range(expanded.shape[1])]

        if drop_original_columns:
            df_result = df_result.drop(columns=[col])

        # Neue Spalten anhängen (Original bleibt bestehen)
        df_result = pd.concat([df_result, expanded], axis=1)

    return df_result



def copy_and_rename_file(
        destination_dir: str,
        df: pd.DataFrame, 
        path_col: str="id_file",
        new_name: str = "document_id"
    ) -> None:
    """
    Kopiert die Dateien, verändert den Namen und kopiert diese in ein anderes Verzeichnis
    
    Quelle/Idee: 
    * https://www.geeksforgeeks.org/python/python-list-files-in-a-directory/ 
    * https://www.geeksforgeeks.org/python/copy-files-and-rename-in-python/ 
    
    """

    for src, new_name in zip(df[path_col], df[new_name]):
        dest_file = os.path.join(destination_dir, new_name)
        shutil.copy(src, dest_file)



def calculate_metrics_sklearn(y_true, y_pred):
    """Folgende Funktion orientiert sich an
    https://medium.com/data-science/understanding-data-science-classification-metrics-in-scikit-learn-in-python-3bc336865019

    """

    # Direkte Berechnung der Konfusion-Matrix (true-negative, false-positive, ...)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # Berechnung der Metriken
    precision = precision_score(y_true, y_pred, zero_division=0.)

    recall = recall_score(y_true, y_pred, zero_division=0.)

    f1 = f1_score(y_true, y_pred, zero_division=0.)
    
    accuracy = accuracy_score(y_true, y_pred)
    
    return {
        'TP': int(tp),
        'FP': int(fp), 
        'FN': int(fn), 
        'TN': int(tn), 
        'Precision': precision, 
        'Recall': recall, 
        'F1-Score': f1, 
        'Accuracy': accuracy
    }