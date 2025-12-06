import pytest
import pandas as pd
import numpy as np

from app.pipelines.models.actions import (
    AddColumn, AddRow, DeleteRow, KeepRow, DropDuplicates, CreateTable,
    CustomAction, MergeTables, ConcatenateTables, GroupBy,
    DropColumn, ReplaceVals, RemoveUnderOver, NLargest, NSmallest,
    RenameColumn, CutValues, SortColumn, ChangeType, NormalizeColumn,
    HandleMissingValues, ApplyFunction, ColDiff, MathOperations,
    ReplaceInCell, FormatString
)
from tests import MOCK_PROJECT


@pytest.mark.asyncio
async def test_add_column_sq_action(temp_project_dir_fixture):
    action = AddColumn({
        "table_name": "test_table",
        "col_name": "new_col",
        "col_value": "c['A'] + c['B']",
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})}

    result = await action.execute(tables)

    assert "new_col" in result["test_table"].columns
    assert result["test_table"]["new_col"].tolist() == [5, 7, 9]


@pytest.mark.asyncio
async def test_add_column_python(temp_project_dir_fixture):
    action = AddColumn({
        "table_name": "test_table",
        "col_name": "new_col",
        "col_value": "tables['test_table']['A'] * 2",
        "value_type": "python"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3]})}

    result = await action.execute(tables)

    assert "new_col" in result["test_table"].columns
    assert result["test_table"]["new_col"].tolist() == [2, 4, 6]


@pytest.mark.asyncio
async def test_add_row(temp_project_dir_fixture):
    action = AddRow({
        "table_name": "test_table",
        "new_rows": "[{'A': 4, 'B': 5}, {'A': 6, 'B': 7}]"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2], "B": [3, 4]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 4
    assert result["test_table"]["A"].tolist() == [1, 2, 4, 6]


@pytest.mark.asyncio
async def test_delete_row(temp_project_dir_fixture):
    action = DeleteRow({
        "table_name": "test_table",
        "delete_domain": "A > 2"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["A"].tolist() == [1, 2]


@pytest.mark.asyncio
async def test_keep_row(temp_project_dir_fixture):
    action = KeepRow({
        "table_name": "test_table",
        "keep_domain": "A <= 2"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["A"].tolist() == [1, 2]


@pytest.mark.asyncio
async def test_drop_duplicates_first(temp_project_dir_fixture):
    action = DropDuplicates({
        "table_name": "test_table",
        "subset": "['A']",
        "keep": "first"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 1, 2], "B": [3, 4, 5]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["B"].tolist() == [3, 5]


@pytest.mark.asyncio
async def test_drop_duplicates_last(temp_project_dir_fixture):
    action = DropDuplicates({
        "table_name": "test_table",
        "subset": "['A']",
        "keep": "last"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 1, 2], "B": [3, 4, 5]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["B"].tolist() == [4, 5]


@pytest.mark.asyncio
async def test_drop_duplicates_false(temp_project_dir_fixture):
    action = DropDuplicates({
        "table_name": "test_table",
        "subset": "['A']",
        "keep": "false"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 1, 2], "B": [3, 4, 5]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 1
    assert result["test_table"]["A"].tolist() == [2]


@pytest.mark.asyncio
async def test_create_table_from_data_source(temp_project_dir_fixture):
    action = CreateTable({
        "table_name": "new_table",
        "project_dir": MOCK_PROJECT,
        "source_creation_type": "data_source",
        "data_source_dir": "Csv_ordered",
        "table_df": ""
    })
    tables = {}

    result = await action.execute(tables)

    assert "new_table" in result
    assert isinstance(result["new_table"], pd.DataFrame)


@pytest.mark.asyncio
async def test_create_table_from_other_tables(temp_project_dir_fixture):
    action = CreateTable({
        "table_name": "new_table",
        "project_dir": MOCK_PROJECT,
        "source_creation_type": "other_tables",
        "data_source_dir": "",
        "table_df": "existing_table"
    })
    tables = {"existing_table": pd.DataFrame({"A": [1, 2, 3]})}

    result = await action.execute(tables)

    assert "new_table" in result
    assert result["new_table"]["A"].tolist() == [1, 2, 3]


@pytest.mark.asyncio
async def test_custom_action(temp_project_dir_fixture):
    action = CustomAction({
        "custom_action_code": "tables['test_table']['C'] = c['A'] + c['B']",
        "custom_action_name": "test_custom",
        "table_name": "test_table"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2], "B": [3, 4]})}

    result = await action.execute(tables)

    assert "C" in result["test_table"].columns
    assert result["test_table"]["C"].tolist() == [4, 6]


@pytest.mark.asyncio
async def test_merge_tables_inner(temp_project_dir_fixture):
    action = MergeTables({
        "table_name": "table1",
        "table2": "table2",
        "on": "key",
        "how": "inner"
    })
    tables = {
        "table1": pd.DataFrame({"key": [1, 2, 3], "val1": ["a", "b", "c"]}),
        "table2": pd.DataFrame({"key": [2, 3, 4], "val2": ["x", "y", "z"]})
    }

    result = await action.execute(tables)

    assert len(result["table1"]) == 2
    assert result["table1"]["key"].tolist() == [2, 3]


@pytest.mark.asyncio
async def test_merge_tables_outer(temp_project_dir_fixture):
    action = MergeTables({
        "table_name": "table1",
        "table2": "table2",
        "on": "key",
        "how": "outer"
    })
    tables = {
        "table1": pd.DataFrame({"key": [1, 2], "val1": ["a", "b"]}),
        "table2": pd.DataFrame({"key": [2, 3], "val2": ["x", "y"]})
    }

    result = await action.execute(tables)

    assert len(result["table1"]) == 3


@pytest.mark.asyncio
async def test_merge_tables_left(temp_project_dir_fixture):
    action = MergeTables({
        "table_name": "table1",
        "table2": "table2",
        "on": "key",
        "how": "left"
    })
    tables = {
        "table1": pd.DataFrame({"key": [1, 2, 3], "val1": ["a", "b", "c"]}),
        "table2": pd.DataFrame({"key": [2, 3], "val2": ["x", "y"]})
    }

    result = await action.execute(tables)

    assert len(result["table1"]) == 3
    assert result["table1"]["key"].tolist() == [1, 2, 3]


@pytest.mark.asyncio
async def test_merge_tables_right(temp_project_dir_fixture):
    action = MergeTables({
        "table_name": "table1",
        "table2": "table2",
        "on": "key",
        "how": "right"
    })
    tables = {
        "table1": pd.DataFrame({"key": [1, 2], "val1": ["a", "b"]}),
        "table2": pd.DataFrame({"key": [2, 3, 4], "val2": ["x", "y", "z"]})
    }

    result = await action.execute(tables)

    assert len(result["table1"]) == 3
    assert result["table1"]["key"].tolist() == [2, 3, 4]


@pytest.mark.asyncio
async def test_concatenate_tables(temp_project_dir_fixture):
    action = ConcatenateTables({
        "table_name": "table1",
        "table": "table2"
    })
    tables = {
        "table1": pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
        "table2": pd.DataFrame({"A": [5, 6], "B": [7, 8]})
    }

    result = await action.execute(tables)

    assert len(result["table1"]) == 4
    assert result["table1"]["A"].tolist() == [1, 2, 5, 6]


@pytest.mark.asyncio
async def test_group_by(temp_project_dir_fixture):
    action = GroupBy({
        "table_name": "test_table",
        "groupby": "category",
        "agg": "{'value': 'sum'}"
    })
    tables = {
        "test_table": pd.DataFrame({
            "category": ["A", "A", "B", "B"],
            "value": [1, 2, 3, 4]
        })
    }

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["value"].tolist() == [3, 7]


@pytest.mark.asyncio
async def test_drop_column(temp_project_dir_fixture):
    action = DropColumn({
        "table_name": "test_table",
        "col_name": "B",
        "col_idx": "B",
        "col_dtype": "int64"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2], "B": [3, 4]})}

    result = await action.execute(tables)

    assert "B" not in result["test_table"].columns
    assert "A" in result["test_table"].columns


@pytest.mark.asyncio
async def test_replace_vals_string(temp_project_dir_fixture):
    action = ReplaceVals({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "col_dtype": "object",
        "replace_vals": "{'old': 'new', 'foo': 'bar'}"
    })
    tables = {"test_table": pd.DataFrame({"A": ["old", "foo", "other"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["new", "bar", "other"]


@pytest.mark.asyncio
async def test_replace_vals_int(temp_project_dir_fixture):
    action = ReplaceVals({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "col_dtype": "int64",
        "replace_vals": "{'1': '100', '2': '200'}"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [100, 200, 3]


@pytest.mark.asyncio
async def test_replace_vals_bool(temp_project_dir_fixture):
    action = ReplaceVals({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "col_dtype": "bool",
        "replace_vals": "{'True': 'False', 'False': 'True'}"
    })
    tables = {"test_table": pd.DataFrame({"A": [True, False, True]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [False, True, False]


@pytest.mark.asyncio
async def test_remove_under_over(temp_project_dir_fixture):
    action = RemoveUnderOver({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "lower_bound": "2",
        "upper_bound": "4"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3, 4, 5]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 3
    assert result["test_table"]["A"].tolist() == [2, 3, 4]


@pytest.mark.asyncio
async def test_nlargest_first(temp_project_dir_fixture):
    action = NLargest({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "n": "2",
        "keep": "first"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 5, 3, 5, 2]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["A"].tolist() == [5, 5]


@pytest.mark.asyncio
async def test_nlargest_all(temp_project_dir_fixture):
    action = NLargest({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "n": "2",
        "keep": "all"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 5, 3, 5, 2]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["A"].tolist() == [5, 5]


@pytest.mark.asyncio
async def test_nsmallest_first(temp_project_dir_fixture):
    action = NSmallest({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "n": "2",
        "keep": "first"
    })
    tables = {"test_table": pd.DataFrame({"A": [5, 1, 3, 1, 4]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2
    assert result["test_table"]["A"].tolist() == [1, 1]


@pytest.mark.asyncio
async def test_nsmallest_last(temp_project_dir_fixture):
    action = NSmallest({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "n": "3",
        "keep": "last"
    })
    tables = {"test_table": pd.DataFrame({"A": [5, 1, 3, 1, 4]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 3


@pytest.mark.asyncio
async def test_rename_column(temp_project_dir_fixture):
    action = RenameColumn({
        "table_name": "test_table",
        "col_name": "old_name",
        "col_idx": "old_name",
        "new_col_name": "new_name"
    })
    tables = {"test_table": pd.DataFrame({"old_name": [1, 2, 3]})}

    result = await action.execute(tables)

    assert "new_name" in result["test_table"].columns
    assert "old_name" not in result["test_table"].columns


@pytest.mark.asyncio
async def test_cut_values(temp_project_dir_fixture):
    action = CutValues({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "cut_values": "0,10,20,30",
        "cut_labels": "low,medium,high"
    })
    tables = {"test_table": pd.DataFrame({"A": [5, 15, 25]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["low", "medium", "high"]


@pytest.mark.asyncio
async def test_sort_column_ascending(temp_project_dir_fixture):
    action = SortColumn({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "sort_order": "ascending",
        "sort_key": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [3, 1, 2]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [1, 2, 3]


@pytest.mark.asyncio
async def test_sort_column_descending(temp_project_dir_fixture):
    action = SortColumn({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "sort_order": "descending",
        "sort_key": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [3, 1, 2]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [3, 2, 1]


@pytest.mark.asyncio
async def test_sort_column_custom(temp_project_dir_fixture):
    action = SortColumn({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "sort_order": "custom",
        "sort_key": "x.str.len()"
    })
    tables = {"test_table": pd.DataFrame({"A": ["abc", "a", "ab"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["a", "ab", "abc"]


@pytest.mark.asyncio
async def test_change_type_int(temp_project_dir_fixture):
    action = ChangeType({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "new_type": "int"
    })
    tables = {"test_table": pd.DataFrame({"A": ["1", "2", "3"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].dtype == "int32"


@pytest.mark.asyncio
async def test_change_type_float(temp_project_dir_fixture):
    action = ChangeType({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "new_type": "float"
    })
    tables = {"test_table": pd.DataFrame({"A": ["1.5", "2.5", "3.5"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].dtype == "float64"


@pytest.mark.asyncio
async def test_change_type_string(temp_project_dir_fixture):
    action = ChangeType({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "new_type": "string"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].dtype == "string"


@pytest.mark.asyncio
async def test_change_type_datetime(temp_project_dir_fixture):
    action = ChangeType({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "new_type": "datetime"
    })
    tables = {"test_table": pd.DataFrame({"A": ["2023-01-01", "2023-01-02"]})}

    result = await action.execute(tables)

    assert pd.api.types.is_datetime64_any_dtype(result["test_table"]["A"])


@pytest.mark.asyncio
async def test_normalize_column_min_max(temp_project_dir_fixture):
    action = NormalizeColumn({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "method": "min_max"
    })
    tables = {"test_table": pd.DataFrame({"A": [0, 5, 10]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [0.0, 0.5, 1.0]


@pytest.mark.asyncio
async def test_normalize_column_z_score(temp_project_dir_fixture):
    action = NormalizeColumn({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "method": "z_score"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3, 4, 5]})}

    result = await action.execute(tables)

    assert abs(result["test_table"]["A"].mean()) < 1e-10
    assert abs(result["test_table"]["A"].std() - 1.0) < 1e-10


@pytest.mark.asyncio
async def test_handle_missing_values_delete(temp_project_dir_fixture):
    action = HandleMissingValues({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "action": "delete",
        "replace_value": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [1, None, 3]})}

    result = await action.execute(tables)

    assert len(result["test_table"]) == 2


@pytest.mark.asyncio
async def test_handle_missing_values_replace(temp_project_dir_fixture):
    action = HandleMissingValues({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "action": "replace",
        "replace_value": "0"
    })
    tables = {"test_table": pd.DataFrame({"A": [1.0, None, 3.0]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [1.0, 0.0, 3.0]


@pytest.mark.asyncio
async def test_handle_missing_values_interpolate(temp_project_dir_fixture):
    action = HandleMissingValues({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "action": "interpolate",
        "replace_value": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [1.0, None, 3.0]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [1.0, 2.0, 3.0]


@pytest.mark.asyncio
async def test_apply_function(temp_project_dir_fixture):
    action = ApplyFunction({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "function": "row['A'] * 2"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 2, 3]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [2, 4, 6]


@pytest.mark.asyncio
async def test_col_diff(temp_project_dir_fixture):
    action = ColDiff({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "periods": "1"
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 3, 6, 10]})}

    result = await action.execute(tables)

    assert "A-diff" in result["test_table"].columns
    assert result["test_table"]["A-diff"].tolist()[1:] == [2.0, 3.0, 4.0]


@pytest.mark.asyncio
async def test_math_operations_log(temp_project_dir_fixture):
    action = MathOperations({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "log",
        "decimals": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [1, np.e, np.e**2]})}

    result = await action.execute(tables)

    expected = [0.0, 1.0, 2.0]
    for i, val in enumerate(result["test_table"]["A"].tolist()):
        assert abs(val - expected[i]) < 1e-10


@pytest.mark.asyncio
async def test_math_operations_sqrt(temp_project_dir_fixture):
    action = MathOperations({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "sqrt",
        "decimals": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [1, 4, 9]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [1.0, 2.0, 3.0]


@pytest.mark.asyncio
async def test_math_operations_abs(temp_project_dir_fixture):
    action = MathOperations({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "abs",
        "decimals": ""
    })
    tables = {"test_table": pd.DataFrame({"A": [-1, 2, -3]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [1, 2, 3]


@pytest.mark.asyncio
async def test_math_operations_round(temp_project_dir_fixture):
    action = MathOperations({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "round",
        "decimals": "2"
    })
    tables = {"test_table": pd.DataFrame({"A": [1.2345, 2.6789]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == [1.23, 2.68]


@pytest.mark.asyncio
async def test_replace_in_cell_whitespace(temp_project_dir_fixture):
    action = ReplaceInCell({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "action": "whitespace",
        "regex": "",
        "replacement": "_"
    })
    tables = {"test_table": pd.DataFrame({"A": ["hello world", "foo  bar"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["hello_world", "foo_bar"]


@pytest.mark.asyncio
async def test_replace_in_cell_regex(temp_project_dir_fixture):
    action = ReplaceInCell({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "action": "regex",
        "regex": r"\d+",
        "replacement": "X"
    })
    tables = {"test_table": pd.DataFrame({"A": ["abc123", "def456"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["abcX", "defX"]


@pytest.mark.asyncio
async def test_format_string_upper(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "upper"
    })
    tables = {"test_table": pd.DataFrame({"A": ["hello", "world"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["HELLO", "WORLD"]


@pytest.mark.asyncio
async def test_format_string_lower(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "lower"
    })
    tables = {"test_table": pd.DataFrame({"A": ["HELLO", "WORLD"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["hello", "world"]


@pytest.mark.asyncio
async def test_format_string_title(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "title"
    })
    tables = {"test_table": pd.DataFrame({"A": ["hello world", "foo bar"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["Hello World", "Foo Bar"]


@pytest.mark.asyncio
async def test_format_string_capitalize(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "capitalize"
    })
    tables = {"test_table": pd.DataFrame({"A": ["hello world", "foo bar"]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["Hello world", "Foo bar"]


@pytest.mark.asyncio
async def test_format_string_strip(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "strip"
    })
    tables = {"test_table": pd.DataFrame({"A": ["  hello  ", "  world  "]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["hello", "world"]


@pytest.mark.asyncio
async def test_format_string_lstrip(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "lstrip"
    })
    tables = {"test_table": pd.DataFrame({"A": ["  hello  ", "  world  "]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["hello  ", "world  "]


@pytest.mark.asyncio
async def test_format_string_rstrip(temp_project_dir_fixture):
    action = FormatString({
        "table_name": "test_table",
        "col_name": "A",
        "col_idx": "A",
        "operation": "rstrip"
    })
    tables = {"test_table": pd.DataFrame({"A": ["  hello  ", "  world  "]})}

    result = await action.execute(tables)

    assert result["test_table"]["A"].tolist() == ["  hello", "  world"]
