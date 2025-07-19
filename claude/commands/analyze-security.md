# analyze-security v0.2

**Mindset**: "What could go wrong?" - Combine automated scanning with contextual threat assessment.

## Behavior

Comprehensive security analysis using OWASP Top 10 framework with automated script integration and contextual threat assessment.

### Automated Security Checks (OWASP Top 10 Coverage)

Execute security analysis scripts via Bash tool for measurable vulnerability detection:

**Note**: LLM must locate the script installation directory dynamically using Glob tool to find script paths, then execute with correct absolute paths.

```bash
# Example execution format (LLM will determine actual paths):
python [SCRIPT_PATH]/detect_secrets.py . --output-format json
python [SCRIPT_PATH]/scan_vulnerabilities.py . --output-format json  
python [SCRIPT_PATH]/check_auth.py . --output-format json
python [SCRIPT_PATH]/validate_inputs.py . --output-format json
```

**Script Location Process:**
1. Use Glob tool to find script paths: `**/scripts/analyze/security/*.py`
2. Verify script availability and determine correct absolute paths
3. Execute scripts with resolved paths

## Script Capabilities (OWASP Top 10 Coverage)

- **scan_vulnerabilities.py**: Detects OWASP A01 (Injection - SQL, Command, LDAP, XPath) and A03 (XSS - Reflected, Stored)
- **validate_inputs.py**: Comprehensive injection detection covering SQL, NoSQL, Command, Path Traversal, and LDAP injection patterns
- **check_auth.py**: Covers OWASP A07 (Authentication Failures) including weak passwords, session fixation, missing CSRF
- **detect_secrets.py**: Identifies hardcoded credentials and API keys (supports OWASP A02 - Cryptographic Failures)

### Contextual Security Assessment

- **Business Logic Security**: Evaluate authorization rules for privilege escalation risks
- **Architecture Security Review**: Assess defense-in-depth implementation and control effectiveness
- **Risk Assessment**: Identify assets, threats, vulnerabilities in business context
- **Data Flow Security**: Analyze security between components and external interfaces

### Security Coverage Gap Assessment & Autonomous Action

- **Script vs. Codebase Reality Assessment**: Analyze script outputs against actual codebase architecture, technology stack, and implementation patterns to identify coverage gaps
- **Technology-Specific Security Analysis**: Identify framework-specific security requirements not covered by generic scripts (e.g., Django CSRF middleware, React XSS protections, Express.js security headers, JWT implementation patterns)
- **Business Logic Security Deep Dive**: Examine authorization flows, data access patterns, and privilege escalation paths that scripts cannot detect
- **Infrastructure & Deployment Security**: Assess configuration files, environment variables, container security, and deployment patterns for security misconfigurations
- **Autonomous Complementary Actions**: Perform additional security analysis tasks identified during gap assessment, including:
  - Custom vulnerability pattern searches based on identified technology stack
  - Configuration security validation for detected frameworks
  - Data flow security analysis for identified sensitive data paths
  - Authorization matrix validation for detected user roles and permissions

## Analysis Process

1. **Run scripts** to identify measurable security issues
2. **Analyze outputs** in context of business requirements
3. **Security Coverage Gap Assessment & Autonomous Action** - Assess script effectiveness against codebase reality and perform complementary security analysis
4. **Evaluate risks** through architectural review
5. **Prioritize findings** by business impact and exploitability
6. **Generate report** combining automated + contextual + autonomous analysis

### Gap Assessment Instructions

The LLM must autonomously:

**Phase 3A: Coverage Gap Identification**

- **Systematically review each OWASP Top 10 category against codebase reality:**
  - A01: Broken Access Control - Check authorization, privilege escalation
  - A02: Cryptographic Failures - Check secrets, SSL/TLS, encryption
  - A03: Injection - Check SQL, NoSQL, Command, Code injection patterns
  - A04: Insecure Design - Check architecture, business logic flaws
  - A05: Security Misconfiguration - Check framework settings, defaults
  - A06: Vulnerable Components - Check dependencies, libraries
  - A07: Authentication Failures - Check auth implementation, session management
  - A08: Software Integrity Failures - Check unsigned code, CI/CD security
  - A09: Logging Failures - Check security event logging, monitoring
  - A10: Server-Side Request Forgery - Check SSRF patterns, URL validation
- Compare script detection against each OWASP category systematically
- Document specific gaps between script objectives and codebase security reality

**Phase 3B: Autonomous Security Actions**

- Perform targeted Grep searches for technology-specific vulnerability patterns not covered by scripts
- Analyze configuration files for security misconfigurations (docker, nginx, package.json, requirements.txt)
- Examine environment variable usage and secret management patterns
- Validate authorization and authentication implementation patterns against best practices
- Search for business logic vulnerabilities in identified critical data flows
- Assess API security implementations (rate limiting, input validation, output encoding)

### Required Autonomous Search Patterns

**OWASP Top 10 Systematic Searches:**

```bash
# A01: Broken Access Control
rg "if.*user.*==.*admin|bypass.*auth|privilege.*escalat" --type py

# A02: Cryptographic Failures  
rg "verify\s*=\s*False|ssl.*CERT_NONE|md5\(|sha1\(" --type py
rg "password|secret|key" --type yaml --type json --type env

# A03: Injection
rg "eval\(|exec\(|__import__\(|compile\(" --type py
rg "f[\"'].*SELECT.*\{|\.format.*SELECT|%.*SELECT" --type py
rg "os\.system\(|subprocess\..*shell\s*=\s*True|popen\(" --type py

# A04: Insecure Design
rg "if.*role.*==.*\"|authorize.*skip|validation.*bypass" --type py

# A05: Security Misconfiguration
rg "DEBUG\s*=\s*True|ALLOWED_HOSTS.*\*|CORS_ALLOW_ALL" --type py
rg "default.*password|admin.*admin" --type py

# A06: Vulnerable Components
rg "import.*requests|import.*urllib|from.*ssl|import.*hashlib" --type py

# A07: Authentication Failures
rg "session.*fixation|auth.*bypass|login.*attempt" --type py

# A08: Software Integrity Failures
rg "pickle\.load|yaml\.load|eval.*input" --type py

# A09: Logging Failures
rg "print.*password|log.*secret|except.*pass" --type py

# A10: Server-Side Request Forgery
rg "requests\.get\(.*input|urllib.*open.*user|fetch.*url.*param" --type py
```

**Phase 3C: Enhanced Finding Generation**

- Generate additional security findings from autonomous analysis
- Correlate script findings with autonomous analysis results
- Identify compound security risks not detectable by individual script analysis
- Document technology-specific security recommendations

### Verbose Mode (--verbose flag)

When --verbose is specified:

- Show detailed breakdown of script findings vs gap analysis findings
- Include comprehensive gap analysis table with specific code examples
- Display full script outputs and autonomous analysis results
- Provide detailed vulnerability descriptions and locations without implementation guidance

Default mode (no --verbose):

- Show amalgamated security findings by severity as single-line items
- Present unified findings without source attribution (script vs LLM)
- **Hide gap analysis table completely** (only show in --verbose mode)
- **No executive summary section** - skip directly to findings breakdown
- Include only phased remediation roadmap with vulnerability descriptions and locations
- Focus on actionable findings and remediation steps

## Optional Flags

--c7: Use when you need to verify your security implementations against current OWASP Top 10 guidelines and framework-specific security patterns (e.g., Django CSRF middleware configuration, Express.js helmet security headers)
--seq: Use for comprehensive security audits - systematically breaks down the analysis into OWASP Top 10 categories with specific steps like 'A01: scan for injection vulnerabilities', 'A02: check authentication failures', 'A03: validate data exposure'
--verbose: Show detailed breakdown of script findings vs gap analysis findings, comprehensive gap analysis table, and full script outputs with detailed remediation guidance

## Risk Assessment Levels

- **CRITICAL**: Data breach, system compromise, compliance violation
- **HIGH**: Privilege escalation, injection, auth bypass
- **MEDIUM**: Information disclosure, DoS, config issues
- **LOW**: Hardening opportunities, defense gaps

## Output Requirements

### Default Mode

- **Security Score**: Overall risk assessment (0-100)
- **Findings by Severity**: Amalgamated findings grouped by severity level, each item on new line
  - Format: `[SEVERITY] Short Description - Location`
  - Example: `[CRITICAL] Code injection vulnerability - app.py:33`
  - **No executive summary section**
  - **Skip directly to findings breakdown**
- **Remediation Roadmap**: Single phased roadmap with high priority items first
  - Include brief description of each vulnerability that needs addressing
  - Include specific location in codebase for each item (e.g., app.py:33)
  - **No code examples or implementation guidance** - focus on issue identification only
  - Group by phases (Phase 1: Critical, Phase 2: High Priority, Phase 3: Security Hardening)
  - **No separate Priority Actions section**
  - Use format from original security-review-log.md as template

### Verbose Mode (--verbose)

- **Detailed Script Outputs**: Full JSON results from all security scripts
- **Gap Analysis Table**: Comprehensive comparison of script vs. actual findings
- **Script vs LLM Breakdown**: Attribution of findings to specific detection methods
- **Autonomous Analysis Results**: LLM-identified vulnerabilities with code examples
- **Technology-Specific Findings**: Framework and library security recommendations
- **Complete Remediation Roadmap**: Detailed vulnerability descriptions and locations without implementation guidance

## Symbol Legend

- 🤖 Automated script analysis
- 🧠 LLM contextual analysis
- 🔍 LLM autonomous gap assessment and action
- 🚨 Critical security flaw requiring immediate attention
- ⚠️ Security concern requiring assessment and remediation
- ✅ Security control properly implemented
- 📋 Coverage gap identified requiring complementary analysis

$ARGUMENTS
