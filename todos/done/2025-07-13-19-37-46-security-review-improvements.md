# review security-review-log to improve analyze-security workflow and report output

**Status:** Done
**Started:** 2025-07-13T19:37:46
**Agent PID:** 28752

## Description
Review and improve the analyze-security workflow based on issues identified in the security-review-log. The current implementation has three main problems: (1) script argument errors causing command failures, (2) verbose and confusing report output layout that obscures key findings, and (3) missed opportunities to enhance automated scripts based on LLM gap analysis. This task will fix the script argument format in the workflow, streamline the report output to show only amalgamated findings (script + LLM) with severity counts and critical details, and identify script improvements based on LLM-identified gaps.

## Implementation Plan
- [x] Review current script argument formats to determine standard convention (analyze-security.md:10-16)
- [x] Update script command format to use consistent --[command-label-with-hyphens] pattern (analyze-security.md:10-16)
- [x] Verify actual script argument expectations match workflow instructions (check script help output)
- [x] Add --verbose flag handling with clear breakdown: script findings vs gap analysis table (analyze-security.md:71)
- [x] Update default output requirements to show amalgamated findings by severity with single-line format: severity → short descriptive label → codebase location (analyze-security.md:82-89)
- [x] Add required autonomous search patterns for critical gaps (analyze-security.md:65)
- [x] Update optional flags section to include --verbose flag with specific breakdown description (analyze-security.md:72-74)
- [x] Check actual argument format accepted by each security script (detect_secrets.py, scan_vulnerabilities.py, check_auth.py, validate_inputs.py)
- [x] Ensure workflow commands match script expectations exactly
- [x] Document correct hyphenated argument format for consistency
- [x] Update workflow instructions to align with actual script interfaces
- [x] Define single-line finding format: `[SEVERITY] Short Description - Location`
- [x] Specify amalgamated findings table structure (severity grouping with individual items)
- [x] Clarify that --verbose shows detailed script attribution and gap analysis breakdown
- [x] Ensure default mode hides source attribution (script vs LLM) but shows all findings
- [x] Review scan_vulnerabilities.py for code injection and SSL bypass pattern additions
- [x] Review validate_inputs.py for f-string injection detection enhancement  
- [x] Document specific pattern additions based on LLM gap findings

## Script Enhancement Recommendations

**scan_vulnerabilities.py missing patterns:**
```python
# Add to injection_patterns:
'code_injection': {
    'indicators': [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'compile\s*\('
    ],
    'severity': 'critical',
    'description': 'Code injection vulnerability detected'
},
'ssl_bypass': {
    'indicators': [
        r'verify\s*=\s*False',
        r'ssl\._create_unverified_context',
        r'CERT_NONE',
        r'check_hostname\s*=\s*False'
    ],
    'severity': 'critical', 
    'description': 'SSL/TLS verification bypass detected'
}
```

**validate_inputs.py missing patterns:**
```python
# Add f-string injection detection:
'format_injection': {
    'indicators': [
        r'f["\'].*\{.*user.*\}',
        r'f["\'].*\{.*input.*\}',
        r'\.format\(.*user.*\)',
        r'%.*%.*user'
    ],
    'severity': 'high',
    'description': 'Format string injection vulnerability'
}
```
- [x] Automated test: Verify corrected script commands execute without errors using consistent argument format
- [x] Automated test: Test --verbose flag produces script breakdown and gap analysis table
- [x] Automated test: Confirm default mode shows severity-grouped findings with single-line format
- [x] Fix relative path issue by implementing dynamic script path resolution using Glob tool
- [x] Fix install script unbound variable error in update mode
- [x] Update default output format to hide gap analysis table unless --verbose
- [x] Remove executive summary requirement and skip directly to findings breakdown
- [x] Restructure remediation roadmap to match original security-review-log.md format
- [x] Add detailed location requirements for roadmap items 
- [x] Remove code examples and implementation guidance - focus on issue identification only
- [x] Remove separate Priority Actions section requirement
- [x] Add systematic OWASP Top 10 coverage for deterministic gap identification
- [x] Replace ad-hoc pattern searches with structured OWASP category searches
- [x] User test: Run /analyze-security on test_codebase with corrected consistent script commands
- [x] User test: Verify default output shows amalgamated findings by severity as single-line items
- [x] User test: Confirm --verbose flag displays script findings breakdown and gap analysis table

## Notes
Fixed the relative path issue by updating the workflow to:
1. Use dynamic script path resolution via Glob tool pattern `**/scripts/analyze/security/*.py`
2. Require LLM to locate and verify script paths before execution
3. Execute scripts with resolved absolute paths rather than static relative paths
4. This approach works regardless of execution directory or installation location

Fixed install script unbound variable error:
- Protected array access in update mode by checking array length before iteration
- Prevents "unbound variable" error when custom_commands array is empty
- Now safely handles both empty and populated custom command arrays

## Original Todo
- review security-review-log to review our analyze-security workflow and report output to make improvements, including:

1. several script failure calls with incorrect arguments
2. confusing report output layout, it should be found items counts broken down by severity, short detail on each critical issue - these found items are an amalgamation of items found by scripts and items found by LLM automation to cover identified gaps, we dont need to outline which script found what and we dont need a table or information on the gaps covered by the LLM unless a --verbose switch is used. This should be followed by a recommended roadmap of phased changes ordered by priority and immediate risk.
3. Review the gaps the LLM identified and see if we can improve or add to our automated security scripts to close gaps.