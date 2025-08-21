import pandas as pd

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_to_html_with_idx():
    """
    Test that to_html_with_idx correctly adds data-columnidx attributes to table headers.
    """
    from app.tables.routers.tables import to_html_with_idx
    
    # Test case 1: Simple DataFrame with single-level columns
    df1 = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })
    html1 = to_html_with_idx(df1)
    
    assert 'df-table' in html1
    assert 'data-columnidx="A"' in html1
    assert 'data-columnidx="B"' in html1
    assert '>A<' in html1
    assert '>B<' in html1
    
    # Test case 2: DataFrame with MultiIndex columns
    columns = pd.MultiIndex.from_tuples([('Group1', 'A'), ('Group1', 'B'), ('Group2', 'C')])
    df2 = pd.DataFrame([[1, 'a', 4], [2, 'b', 5], [3, 'c', 6]], columns=columns)
    html2 = to_html_with_idx(df2)
    
    assert 'df-table' in html2
    for col_tuple in df2.columns:
        col_str = str(col_tuple)
        assert f'data-columnidx="{col_str}"' in html2
    for _, col_name in df2.columns:
        assert f">{col_name}<" in html2
