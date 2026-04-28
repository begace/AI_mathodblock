# MB: cli_tool_basic

TITLE: CLI Tool Basic Workflow
USE WHEN: Local automation commands, File conversion utilities, Developer workflow helpers.
AVOID: Long-running network services, Interactive full-screen terminal apps.
FORBID: Credential harvesting, Security bypass, Platform abuse.

FLOW:
define_command_names_arguments_and_exit_codes -> separate_command_parsing_from_core_business_logic -> implement_pure_functions_for_the_core_operation -> convert_exceptions_into_clear_cli_error_messages -> return_nonzero_exit_codes_for_invalid_input_or_failed_operations -> add_tests_for_command_output_and_exit_codes

CONTRACTS:
parse_args(argv: list[string]) -> object
run_command(args: object) -> int
main(argv: list[string]) -> int

FAIL:
Missing required argument | Invalid path | Permission denied | Ambiguous command output

VERIFY:
Help text renders | Valid command exits zero | Invalid command exits nonzero | Error message is actionable
