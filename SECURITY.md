# Security Policy

MethodBlock Registry stores reusable procedural knowledge. That can be useful for safe development workflows, but it can also be misused if MethodBlocks describe harmful automation.

## Disallowed Content

Do not contribute MethodBlocks that enable:

- Credential theft, phishing, or secret extraction
- Unauthorized data access or privacy scraping
- Access control bypass or payment bypass
- Malware creation, deployment, persistence, or evasion
- DRM, anti-cheat, platform rule, or rate-limit evasion
- Fraud, impersonation, or deceptive automation

## Required Safety Metadata

Every MethodBlock should include `forbidden_for` entries that make misuse boundaries explicit.

Automation-related MethodBlocks should also:

- Require visible user intent
- Prefer reversible actions
- Stop when state checks fail
- Avoid capturing or replaying secrets

## Reporting

If you find a MethodBlock that may enable misuse, open an issue or contact the maintainers privately before publishing exploit details.
