# MB: desktop_macro_safe

TITLE: Safe Desktop Macro Workflow
USE WHEN: Repetitive local UI workflows, Data entry with visible confirmation, Screenshot-guided desktop steps.
AVOID: Hidden background account actions, High-risk irreversible operations.
FORBID: Capturing credentials, Bypassing access controls, Evading platform rules, Online game cheating, Anti-cheat bypass, Security control bypass.

FLOW:
confirm_the_user_s_intended_target_application_and_task -> inspect_visible_ui_state_before_acting -> prefer_stable_accessibility_selectors_over_coordinates -> perform_one_reversible_action_at_a_time -> re_check_state_after_each_action -> stop_and_report_when_the_visible_state_does_not_match_expectatio

CONTRACTS:
inspect_state(app_name: string) -> dict
perform_action(state: dict, action: dict) -> dict
verify_state(expected: dict, actual: dict) -> bool

FAIL:
Target window not focused | UI state changed between steps | Button disabled | Action would be irreversible

VERIFY:
Dry-run plan is visible | State check happens before action | Macro stops on mismatch
