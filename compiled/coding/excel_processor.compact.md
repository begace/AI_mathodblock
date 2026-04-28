# MB: excel_processor_basic

TITLE: Excel Processor Basic Workflow
USE WHEN: Excel inventory cleanup, Duplicate SKU merge, Column name normalization, Spreadsheet report generation.
AVOID: Realtime collaborative editing, Distributed big data processing.
FORBID: Unauthorized data access, Privacy scraping, Security bypass.

FLOW:
inspect_the_input_file_format_and_sheet_names -> define_the_required_columns -> normalize_column_headers -> convert_rows_into_internal_records -> validate_missing_values_duplicates_and_type_errors -> transform_rows_according_to_the_task -> export_the_result_workbook -> test_with_representative_sample_files

CONTRACTS:
load_workbook_data(path: string) -> list[dict]
normalize_columns(rows: list[dict]) -> list[dict]
validate_rows(rows: list[dict]) -> dict
export_workbook(rows: list[dict], output_path: string) -> bool

FAIL:
Unexpected headers | Numeric values stored as strings | Empty rows mixed with data | Destination file locked by another program

VERIFY:
Normal sample file | Empty file | Missing required column | Duplicate row sample
