#!/usr/bin/env python3
"""
Vulnerability Scanning Script
Analyzes code for OWASP Top 10 vulnerabilities and common security issues.
"""

import os
import sys
import re
import json
import time
from typing import Dict, List, Any
from collections import defaultdict

# Add utils to path for cross-platform and output_formatter imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

try:
    from cross_platform import PlatformDetector, PathUtils
    from output_formatter import ResultFormatter, AnalysisResult, AnalysisType, Finding, Severity
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class VulnerabilityScanner:
    """Scans for OWASP Top 10 and common security vulnerabilities."""
    
    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()
        
        # OWASP Top 10 vulnerability patterns
        self.injection_patterns = {
            'sql_injection': {
                'indicators': [
                    r'query\s*=\s*[\'"].*%.*[\'"]',
                    r'execute\s*\(\s*[\'"].*%.*[\'"]',
                    r'cursor\.execute.*%',
                    r'SELECT.*\+.*user',
                    r'INSERT.*\+.*request',
                    r'UPDATE.*\+.*input'
                ],
                'severity': 'critical',
                'description': 'Potential SQL injection vulnerability'
            },
            'command_injection': {
                'indicators': [
                    r'os\.system\s*\(.*\+',
                    r'subprocess\.(call|run|Popen).*\+',
                    r'exec\s*\(.*user',
                    r'eval\s*\(.*request',
                    r'shell=True.*\+',
                    r'system\(.*\$'
                ],
                'severity': 'critical',
                'description': 'Potential command injection vulnerability'
            },
            'ldap_injection': {
                'indicators': [
                    r'ldap.*search.*\+',
                    r'ldap.*filter.*user',
                    r'distinguished.*name.*\+',
                    r'ldap.*query.*request'
                ],
                'severity': 'high',
                'description': 'Potential LDAP injection vulnerability'
            },
            'xpath_injection': {
                'indicators': [
                    r'xpath.*\+.*user',
                    r'xml.*query.*\+',
                    r'xpath.*request',
                    r'xml.*search.*input'
                ],
                'severity': 'high',
                'description': 'Potential XPath injection vulnerability'
            }
        }
        
        self.xss_patterns = {
            'reflected_xss': {
                'indicators': [
                    r'innerHTML\s*=.*request',
                    r'document\.write.*user',
                    r'response.*write.*request',
                    r'render.*\+.*input',
                    r'html.*\+.*user.*input'
                ],
                'severity': 'high',
                'description': 'Potential reflected XSS vulnerability'
            },
            'stored_xss': {
                'indicators': [
                    r'save.*user.*input.*(?!.*escape)',
                    r'store.*user.*data.*(?!.*sanitize)',
                    r'database.*insert.*user.*(?!.*clean)',
                    r'persist.*user.*content'
                ],
                'severity': 'high',
                'description': 'Potential stored XSS vulnerability'
            },
            'dom_xss': {
                'indicators': [
                    r'innerHTML.*location',
                    r'document\.write.*window',
                    r'innerHTML.*hash',
                    r'outerHTML.*search'
                ],
                'severity': 'medium',
                'description': 'Potential DOM-based XSS vulnerability'
            }
        }
        
        self.security_misconfiguration = {
            'debug_enabled': {
                'indicators': [
                    r'DEBUG\s*=\s*True',
                    r'debug\s*=\s*true',
                    r'development.*mode',
                    r'console\.log.*password',
                    r'print.*secret'
                ],
                'severity': 'medium',
                'description': 'Debug mode enabled or sensitive info logging'
            },
            'weak_crypto': {
                'indicators': [
                    r'md5\(',
                    r'sha1\(',
                    r'DES\(',
                    r'RC4\(',
                    r'algorithm.*md5',
                    r'cipher.*des'
                ],
                'severity': 'high',
                'description': 'Use of weak cryptographic algorithms'
            },
            'insecure_randomness': {
                'indicators': [
                    r'random\.random\(\)',
                    r'Math\.random\(\)',
                    r'rand\(\)',
                    r'srand\(',
                    r'predictable.*random'
                ],
                'severity': 'medium',
                'description': 'Use of insecure random number generation'
            },
            'missing_security_headers': {
                'indicators': [
                    r'response\.headers.*(?!.*security)',
                    r'Content-Security-Policy.*none',
                    r'X-Frame-Options.*(?!DENY|SAMEORIGIN)',
                    r'Strict-Transport-Security.*(?!max-age)'
                ],
                'severity': 'medium',
                'description': 'Missing or weak security headers'
            }
        }
        
        self.sensitive_data_exposure = {
            'unencrypted_storage': {
                'indicators': [
                    r'password.*=.*plain',
                    r'store.*sensitive.*(?!encrypt)',
                    r'save.*credit.*card.*(?!encrypt)',
                    r'database.*personal.*(?!encrypt)'
                ],
                'severity': 'high',
                'description': 'Sensitive data stored without encryption'
            },
            'logs_exposure': {
                'indicators': [
                    r'log.*password',
                    r'console.*secret',
                    r'print.*token',
                    r'debug.*sensitive',
                    r'trace.*personal'
                ],
                'severity': 'medium',
                'description': 'Sensitive data exposed in logs'
            },
            'error_disclosure': {
                'indicators': [
                    r'Exception.*stack.*trace',
                    r'error.*full.*path',
                    r'debug.*info.*production',
                    r'traceback.*user'
                ],
                'severity': 'medium',
                'description': 'Information disclosure through error messages'
            }
        }
        
        self.xxe_patterns = {
            'xml_external_entity': {
                'indicators': [
                    r'XMLParser.*resolve.*external',
                    r'SAXParser.*external.*true',
                    r'DocumentBuilder.*entity.*true',
                    r'xml.*external.*entity',
                    r'<!ENTITY.*SYSTEM'
                ],
                'severity': 'high',
                'description': 'Potential XML External Entity (XXE) vulnerability'
            }
        }
        
        self.deserialization_patterns = {
            'unsafe_deserialization': {
                'indicators': [
                    r'pickle\.loads\(',
                    r'cPickle\.loads\(',
                    r'marshal\.loads\(',
                    r'eval\(.*request',
                    r'exec\(.*user',
                    r'yaml\.load\(.*(?!Loader=yaml\.SafeLoader)'
                ],
                'severity': 'critical',
                'description': 'Unsafe deserialization vulnerability'
            }
        }

    def scan_vulnerabilities(self, target_path: str, min_severity: str = "low") -> Dict[str, Any]:
        """Scan for vulnerabilities in the target path."""
        
        start_time = time.time()
        result = ResultFormatter.create_security_result("scan_vulnerabilities.py", target_path)
        
        if not os.path.exists(target_path):
            result.set_error(f"Path does not exist: {target_path}")
            result.set_execution_time(start_time)
            return result.to_dict()
        
        vulnerability_summary = defaultdict(int)
        file_count = 0
        
        try:
            # Walk through all files
            for root, dirs, files in os.walk(target_path):
                # Skip common build/dependency directories
                dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]
                
                for file in files:
                    if self._should_analyze_file(file):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, target_path)
                        
                        try:
                            file_findings = self._analyze_file_vulnerabilities(file_path, relative_path)
                            file_count += 1
                            
                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"VULN_{vulnerability_summary[finding_data['vuln_type']] + 1:03d}",
                                    title=finding_data['vuln_type'].replace('_', ' ').title(),
                                    description=finding_data['message'],
                                    severity=finding_data['severity'],
                                    file_path=finding_data['file'],
                                    line_number=finding_data['line'],
                                    recommendation=self._get_vulnerability_recommendation(finding_data['vuln_type']),
                                    evidence={
                                        'context': finding_data.get('context', ''),
                                        'category': finding_data.get('category', 'vulnerability'),
                                        'owasp_category': finding_data.get('owasp_category', 'unknown')
                                    }
                                )
                                result.add_finding(finding)
                                vulnerability_summary[finding_data['vuln_type']] += 1
                                
                        except Exception as e:
                            error_finding = ResultFormatter.create_finding(
                                finding_id=f"ERROR_{file_count:03d}",
                                title="Analysis Error",
                                description=f"Error analyzing file: {str(e)}",
                                severity="low",
                                file_path=relative_path,
                                line_number=0
                            )
                            result.add_finding(error_finding)
            
            # Generate analysis summary
            analysis_summary = self._generate_vulnerability_summary(vulnerability_summary, file_count)
            result.metadata = analysis_summary
            
            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)
            
        except Exception as e:
            result.set_error(f"Vulnerability scanning failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_vulnerabilities(self, file_path: str, relative_path: str) -> List[Dict[str, Any]]:
        """Analyze vulnerabilities in a single file."""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check injection vulnerabilities
            findings.extend(self._check_vulnerability_patterns(
                content, lines, relative_path, self.injection_patterns, 'injection', 'A03:2021 – Injection'
            ))
            
            # Check XSS vulnerabilities
            findings.extend(self._check_vulnerability_patterns(
                content, lines, relative_path, self.xss_patterns, 'xss', 'A03:2021 – Injection'
            ))
            
            # Check security misconfiguration
            findings.extend(self._check_vulnerability_patterns(
                content, lines, relative_path, self.security_misconfiguration, 'misconfiguration', 'A05:2021 – Security Misconfiguration'
            ))
            
            # Check sensitive data exposure
            findings.extend(self._check_vulnerability_patterns(
                content, lines, relative_path, self.sensitive_data_exposure, 'data_exposure', 'A02:2021 – Cryptographic Failures'
            ))
            
            # Check XXE vulnerabilities
            findings.extend(self._check_vulnerability_patterns(
                content, lines, relative_path, self.xxe_patterns, 'xxe', 'A05:2021 – Security Misconfiguration'
            ))
            
            # Check deserialization vulnerabilities
            findings.extend(self._check_vulnerability_patterns(
                content, lines, relative_path, self.deserialization_patterns, 'deserialization', 'A08:2021 – Software and Data Integrity Failures'
            ))
            
        except Exception as e:
            findings.append({
                'file': relative_path,
                'line': 0,
                'vuln_type': 'file_error',
                'severity': 'low',
                'message': f"Could not analyze file: {str(e)}",
                'category': 'analysis',
                'owasp_category': 'N/A'
            })
        
        return findings

    def _check_vulnerability_patterns(self, content: str, lines: List[str], file_path: str,
                                    pattern_dict: Dict, category: str, owasp_category: str) -> List[Dict[str, Any]]:
        """Check for specific vulnerability patterns in file content."""
        findings = []
        
        for pattern_name, pattern_info in pattern_dict.items():
            for indicator in pattern_info['indicators']:
                matches = re.finditer(indicator, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    findings.append({
                        'file': file_path,
                        'line': line_num,
                        'vuln_type': f"{category}_{pattern_name}",
                        'severity': pattern_info['severity'],
                        'message': f"{pattern_info['description']} ({pattern_name})",
                        'context': lines[line_num - 1].strip() if line_num <= len(lines) else "",
                        'category': category,
                        'owasp_category': owasp_category
                    })
        
        return findings

    def _get_vulnerability_recommendation(self, vuln_type: str) -> str:
        """Get specific recommendations for vulnerabilities."""
        recommendations = {
            'injection_sql_injection': 'Use parameterized queries or prepared statements',
            'injection_command_injection': 'Validate input and avoid system calls with user data',
            'injection_ldap_injection': 'Use parameterized LDAP queries and input validation',
            'injection_xpath_injection': 'Use parameterized XPath queries and input sanitization',
            'xss_reflected_xss': 'Sanitize and encode user input before rendering',
            'xss_stored_xss': 'Validate, sanitize, and encode data before storage and display',
            'xss_dom_xss': 'Use safe DOM manipulation methods and validate client-side input',
            'misconfiguration_debug_enabled': 'Disable debug mode in production environments',
            'misconfiguration_weak_crypto': 'Use strong cryptographic algorithms (AES, SHA-256+)',
            'misconfiguration_insecure_randomness': 'Use cryptographically secure random generators',
            'misconfiguration_missing_security_headers': 'Implement security headers (CSP, HSTS, X-Frame-Options)',
            'data_exposure_unencrypted_storage': 'Encrypt sensitive data at rest',
            'data_exposure_logs_exposure': 'Remove sensitive data from logs and debug output',
            'data_exposure_error_disclosure': 'Use generic error messages in production',
            'xxe_xml_external_entity': 'Disable XML external entity processing',
            'deserialization_unsafe_deserialization': 'Validate serialized data and use safe deserialization methods'
        }
        return recommendations.get(vuln_type, 'Review code for security best practices')

    def _generate_vulnerability_summary(self, vulnerability_summary: Dict, file_count: int) -> Dict[str, Any]:
        """Generate summary of vulnerability scanning."""
        
        # Categorize vulnerabilities by OWASP Top 10
        owasp_categories = {
            'A01:2021 – Broken Access Control': ['missing_authorization', 'privilege_escalation'],
            'A02:2021 – Cryptographic Failures': ['weak_crypto', 'unencrypted_storage'],
            'A03:2021 – Injection': ['sql_injection', 'command_injection', 'ldap_injection', 'xpath_injection', 'reflected_xss', 'stored_xss', 'dom_xss'],
            'A04:2021 – Insecure Design': ['insecure_randomness'],
            'A05:2021 – Security Misconfiguration': ['debug_enabled', 'missing_security_headers', 'xml_external_entity'],
            'A06:2021 – Vulnerable Components': [],
            'A07:2021 – Identity and Authentication Failures': [],
            'A08:2021 – Software and Data Integrity Failures': ['unsafe_deserialization'],
            'A09:2021 – Security Logging and Monitoring Failures': ['logs_exposure', 'error_disclosure'],
            'A10:2021 – Server-Side Request Forgery': []
        }
        
        total_issues = sum(vulnerability_summary.values())
        severity_counts = self._count_by_severity(vulnerability_summary)
        
        return {
            'total_files_analyzed': file_count,
            'total_vulnerabilities': total_issues,
            'vulnerabilities_by_owasp_category': {
                category: {
                    'count': sum(vulnerability_summary.get(f"{cat}_{vuln}", 0) for cat in ['injection', 'xss', 'misconfiguration', 'data_exposure', 'xxe', 'deserialization'] for vuln in vulns),
                    'vulnerabilities': {vuln: vulnerability_summary.get(f"{cat}_{vuln}", 0) 
                                     for cat in ['injection', 'xss', 'misconfiguration', 'data_exposure', 'xxe', 'deserialization'] 
                                     for vuln in vulns 
                                     if vulnerability_summary.get(f"{cat}_{vuln}", 0) > 0}
                }
                for category, vulns in owasp_categories.items()
            },
            'severity_breakdown': severity_counts,
            'security_score': self._calculate_security_score(total_issues, file_count),
            'critical_vulnerabilities': self._get_critical_vulnerabilities(vulnerability_summary),
            'recommendations': self._generate_priority_recommendations(vulnerability_summary)
        }

    def _count_by_severity(self, vulnerability_summary: Dict) -> Dict[str, int]:
        """Count vulnerabilities by severity level."""
        severity_mapping = {
            'critical': ['sql_injection', 'command_injection', 'unsafe_deserialization'],
            'high': ['ldap_injection', 'xpath_injection', 'reflected_xss', 'stored_xss', 'weak_crypto', 'unencrypted_storage', 'xml_external_entity'],
            'medium': ['dom_xss', 'debug_enabled', 'insecure_randomness', 'missing_security_headers', 'logs_exposure', 'error_disclosure'],
            'low': ['file_error']
        }
        
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for vuln, count in vulnerability_summary.items():
            vuln_name = vuln.split('_', 1)[-1]  # Remove category prefix
            for severity, patterns in severity_mapping.items():
                if vuln_name in patterns:
                    counts[severity] += count
                    break
        
        return counts

    def _calculate_security_score(self, total_issues: int, file_count: int) -> float:
        """Calculate a security score (0-100, higher is better)."""
        if file_count == 0:
            return 100.0
        
        issue_density = total_issues / file_count
        # Score decreases with issue density, with critical issues having heavy impact
        score = max(0, 100 - (issue_density * 20))
        return round(score, 1)

    def _get_critical_vulnerabilities(self, vulnerability_summary: Dict) -> List[Dict[str, Any]]:
        """Get critical vulnerabilities requiring immediate attention."""
        critical_patterns = ['sql_injection', 'command_injection', 'unsafe_deserialization']
        critical_vulns = []
        
        for vuln, count in vulnerability_summary.items():
            vuln_name = vuln.split('_', 1)[-1]
            if vuln_name in critical_patterns and count > 0:
                critical_vulns.append({
                    'vulnerability': vuln.replace('_', ' ').title(),
                    'count': count,
                    'severity': 'critical'
                })
        
        return critical_vulns

    def _generate_priority_recommendations(self, vulnerability_summary: Dict) -> List[str]:
        """Generate priority recommendations based on findings."""
        recommendations = []
        
        # Critical vulnerabilities first
        if any('sql_injection' in k for k in vulnerability_summary.keys()):
            recommendations.append("CRITICAL: Fix SQL injection vulnerabilities with parameterized queries")
        if any('command_injection' in k for k in vulnerability_summary.keys()):
            recommendations.append("CRITICAL: Fix command injection by validating input and avoiding system calls")
        if any('unsafe_deserialization' in k for k in vulnerability_summary.keys()):
            recommendations.append("CRITICAL: Replace unsafe deserialization with safe alternatives")
        
        # High priority vulnerabilities
        if any('xss' in k for k in vulnerability_summary.keys()):
            recommendations.append("HIGH: Implement proper input sanitization to prevent XSS")
        if any('weak_crypto' in k for k in vulnerability_summary.keys()):
            recommendations.append("HIGH: Replace weak cryptographic algorithms with strong alternatives")
        
        # General recommendations
        total_issues = sum(vulnerability_summary.values())
        if total_issues > 20:
            recommendations.append("Consider comprehensive security audit and code review")
        
        return recommendations[:5]

    def _should_skip_directory(self, directory: str) -> bool:
        """Check if directory should be skipped."""
        skip_dirs = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'build', 'dist', '.next', '.nuxt', 'coverage',
            'venv', 'env', '.env', 'vendor', 'logs'
        }
        return directory in skip_dirs or directory.startswith('.')

    def _should_analyze_file(self, filename: str) -> bool:
        """Check if file should be analyzed."""
        analyze_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cs',
            '.cpp', '.c', '.h', '.hpp', '.go', '.rs', '.php',
            '.rb', '.swift', '.kt', '.scala', '.xml', '.html'
        }
        return any(filename.endswith(ext) for ext in analyze_extensions)


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan for OWASP Top 10 vulnerabilities in codebase')
    parser.add_argument('target_path', help='Path to analyze')
    parser.add_argument('--min-severity', choices=['low', 'medium', 'high', 'critical'],
                       default='low', help='Minimum severity level to report')
    parser.add_argument('--output-format', choices=['json', 'console'], 
                       default='json', help='Output format')
    
    args = parser.parse_args()
    
    scanner = VulnerabilityScanner()
    result = scanner.scan_vulnerabilities(args.target_path, args.min_severity)
    
    if args.output_format == 'console':
        # Simple console output
        if result.get('success', False):
            print(f"Vulnerability Scan Results for: {args.target_path}")
            print(f"Analysis Type: {result.get('analysis_type', 'unknown')}")
            print(f"Execution Time: {result.get('execution_time', 0)}s")
            print(f"\nFindings: {len(result.get('findings', []))}")
            for finding in result.get('findings', []):
                file_path = finding.get('file_path', 'unknown')
                line = finding.get('line_number', 0)
                desc = finding.get('description', 'No description')
                severity = finding.get('severity', 'unknown')
                print(f"  {file_path}:{line} - {desc} [{severity}]")
        else:
            error_msg = result.get('error_message', 'Unknown error')
            print(f"Error: {error_msg}")
    else:  # json (default)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()