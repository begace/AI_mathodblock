# MB: crud_web_app_basic

TITLE: CRUD Web App Basic Workflow
USE WHEN: Admin data entry tools, Small internal dashboards, Form-backed resource management.
AVOID: High-frequency realtime collaboration, Complex distributed transactions.
FORBID: Authentication bypass, Access control bypass, Data exfiltration.

FLOW:
define_the_resource_fields_and_validation_rules -> choose_the_storage_model_and_persistence_boundary -> implement_create_and_read_flows_first -> implement_update_and_delete_flows_with_explicit_confirmation_whe -> add_server_side_validation_and_clear_error_responses -> add_ui_states_for_loading_empty_error_and_success -> test_the_happy_path_and_validation_failures

CONTRACTS:
create_record(payload: dict) -> dict
list_records(filters: dict) -> list[dict]
update_record(record_id: string, payload: dict) -> dict
delete_record(record_id: string) -> bool

FAIL:
Missing required fields | Duplicate unique field | Stale update payload | Delete called on a missing record

VERIFY:
Create valid record | Reject invalid payload | Update existing record | Delete existing record
