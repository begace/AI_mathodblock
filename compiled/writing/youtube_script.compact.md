# MB: youtube_script_basic

TITLE: YouTube Script Basic Workflow
USE WHEN: Educational video scripts, Product walkthrough scripts, Short documentary outlines.
AVOID: Fabricated news, Medical or legal advice without expert review.
FORBID: Defamation, Plagiarism, Misleading impersonation.

FLOW:
define_the_target_audience_and_viewer_promise -> write_a_one_sentence_premise -> outline_the_hook_context_main_beats_and_payoff -> mark_claims_that_need_sources_or_verification -> draft_narration_in_a_spoken_style -> add_visual_notes_only_where_they_clarify_the_script -> review_for_unsupported_claims_and_pacing_issues

CONTRACTS:
build_outline(premise: string, audience: string) -> list[dict]
draft_script(outline: list[dict]) -> string
fact_check_claims(script: string) -> dict

FAIL:
Weak hook | Unsupported factual claim | Overlong intro | Visual notes overwhelm narration

VERIFY:
Premise is clear | Claims are marked for review | Intro reaches the point quickly | Ending has a concise call to action
