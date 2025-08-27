import pandas as pd

from app.pipelines.models.actions_utils import convert_col_idx


class Table:
    def __init__(self, name: str, content: pd.DataFrame):
        self.name = name
        self.content = content

    def _to_html_with_idx(df):
        html = df.to_html(classes='df-table', index=False)
        
        header_html = ""
        for idx, col_id in enumerate(df.columns):
            if isinstance(df.columns, pd.MultiIndex):
                header_html += f"""<th data-columnidx="{df.columns[idx]}">{df.columns[idx][-1]}</th>\n"""
            else:
                header_html += f"""<th data-columnidx="{df.columns[idx]}">{df.columns[idx]}</th>\n"""

        header_start = html.find('<thead>')
        header_end = html.find('</thead>')
        header_rows = html[header_start:header_end]
        modified_header = header_rows.rsplit('<tr', 1)
        modified_header = f"{modified_header[0]}<tr>{header_html}</tr>"
        return html[:header_start] + modified_header + html[header_end:]
    
    def to_html(self, display_len, start=False, end=False):
        df = self.content.head(display_len)
        if start and end:
            df = self.content.iloc[start:end]
        return Table._to_html_with_idx(df)
    
    def get_col_info(self, column_idx: str):
        df = self.content
        column = df[eval(convert_col_idx(column_idx))]

        col_infos = {
            "dtype": str(column.dtype),
            "unique": str(column.nunique()),
            "null": str(column.isna().sum()),
            "count": str(len(column.index)),
            "is_numeric": column.dtype in ["float64", "int64"],
            "is_string": column.dtype == "object" or isinstance(column.dtype, pd.StringDtype),
            "top_values": column.value_counts().head(5).to_dict()
        }

        if col_infos["is_numeric"]:
            col_infos["is_numeric"] = True
            col_infos["mean"] = str(column.mean())
            col_infos["std"] = str(column.std())
            col_infos["min"] = str(column.min())
            col_infos["max"] = str(column.max())
            col_infos["25"] = str(column.quantile(0.25))
            col_infos["50"] = str(column.quantile(0.5))
            col_infos["75"] = str(column.quantile(0.75))
        
        if col_infos["is_string"]:
            col_infos["is_string"] = True
            string_lengths = column.str.len()
            col_infos["avg_length"] = str(string_lengths.mean())
            col_infos["min_length"] = str(string_lengths.min())
            col_infos["max_length"] = str(string_lengths.max())
            col_infos["empty_strings"] = str((column == "").sum())

        return col_infos
