#!/bin/bash

# Test script to verify command workflows work with migrated scripts
# Tests actual script execution with standardized arguments against test_codebase

set -e  # Exit on any error

echo "=== Testing Command Workflows Against test_codebase ==="
echo "This simulates real workflow usage with the migrated scripts"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"

    echo -e "${YELLOW}Testing: $test_name${NC}"
    echo "Command: $command"

    TESTS_RUN=$((TESTS_RUN + 1))

    if eval "$command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "Sample output:"
        head -3 /tmp/test_output.log | sed 's/^/  /'
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "Error output:"
        head -5 /tmp/test_output.log | sed 's/^/  /'
    fi
    echo
}

echo "=== Security Analysis Workflow ==="

# Test security scripts (analyze-security.md workflow)
run_test "Detect hardcoded secrets" \
    "python3 claude/scripts/analyze/security/detect_secrets.py test_codebase --output-format json"

run_test "Scan for vulnerabilities" \
    "python3 claude/scripts/analyze/security/scan_vulnerabilities.py test_codebase --output-format json"

run_test "Check authentication security" \
    "python3 claude/scripts/analyze/security/check_auth.py test_codebase --output-format json"

run_test "Validate input handling" \
    "python3 claude/scripts/analyze/security/validate_inputs.py test_codebase --output-format json"

echo "=== Code Quality Analysis Workflow ==="

# Test code quality scripts (analyze-code-quality.md workflow)
run_test "Analyze code complexity with Lizard" \
    "python3 claude/scripts/analyze/code_quality/complexity_lizard.py test_codebase --output-format json"

run_test "Generate complexity metrics" \
    "python3 claude/scripts/analyze/code_quality/complexity_metrics.py test_codebase --output-format json --summary"

run_test "Test coverage analysis" \
    "python3 claude/scripts/analyze/code_quality/test_coverage_analysis.py test_codebase --output-format json"

echo "=== Architecture Analysis Workflow ==="

# Test architecture scripts (analyze-architecture.md workflow)
run_test "Evaluate design patterns" \
    "python3 claude/scripts/analyze/architecture/pattern_evaluation.py test_codebase --output-format json"

run_test "Check scalability bottlenecks" \
    "python3 claude/scripts/analyze/architecture/scalability_check.py test_codebase --output-format json"

run_test "Analyze code coupling" \
    "python3 claude/scripts/analyze/architecture/coupling_analysis.py test_codebase --output-format json --summary"

echo "=== Performance Analysis Workflow ==="

# Test performance scripts (analyze-performance.md workflow)
run_test "Check performance bottlenecks" \
    "python3 claude/scripts/analyze/performance/check_bottlenecks.py test_codebase --output-format json"

run_test "Analyze frontend performance" \
    "python3 claude/scripts/analyze/performance/analyze_frontend.py test_codebase --output-format json"

run_test "Profile database usage" \
    "python3 claude/scripts/analyze/performance/profile_database.py test_codebase --output-format json --summary"

run_test "Establish performance baseline" \
    "python3 claude/scripts/analyze/performance/performance_baseline.py test_codebase --output-format json"

echo "=== Root Cause Analysis Workflow ==="

# Test root cause scripts (analyze-root-cause.md workflow)
run_test "Trace execution patterns" \
    "python3 claude/scripts/analyze/root_cause/trace_execution.py test_codebase --output-format json"

run_test "Analyze recent code changes" \
    "python3 claude/scripts/analyze/root_cause/recent_changes.py test_codebase --output-format json"

run_test "Detect error patterns" \
    "python3 claude/scripts/analyze/root_cause/error_patterns.py test_codebase --output-format json"

run_test "Simple execution tracing" \
    "python3 claude/scripts/analyze/root_cause/simple_trace.py test_codebase --output-format json"

echo "=== Comprehensive Analysis Workflow ==="

# Test comprehensive analysis (plan-refactor.md workflow)
run_test "Run comprehensive analysis" \
    "python3 claude/scripts/run_all_analysis.py test_codebase --output-format json"

echo "=== Console Output Format Tests ==="

# Test console output format for user-friendly display
run_test "Security analysis (console output)" \
    "python3 claude/scripts/analyze/security/detect_secrets.py test_codebase --output-format console"

run_test "Code quality analysis (console output)" \
    "python3 claude/scripts/analyze/code_quality/complexity_metrics.py test_codebase --output-format console"

run_test "Architecture analysis (console output)" \
    "python3 claude/scripts/analyze/architecture/pattern_evaluation.py test_codebase --output-format console"

echo "=== High Severity Filtering Tests ==="

# Test severity filtering (useful for CI/CD pipelines)
run_test "Security issues (high severity only)" \
    "python3 claude/scripts/analyze/security/check_auth.py test_codebase --output-format json --min-severity high"

run_test "Code quality issues (critical severity only)" \
    "python3 claude/scripts/analyze/code_quality/complexity_metrics.py test_codebase --output-format json --min-severity critical"

echo "=== FINAL RESULTS ==="
echo "Tests run: $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$((TESTS_RUN - TESTS_PASSED))${NC}"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo -e "${GREEN}🎉 ALL WORKFLOW TESTS PASSED!${NC}"
    echo "All command workflows are working correctly with migrated scripts."
    exit 0
else
    echo -e "${RED}❌ Some workflow tests failed.${NC}"
    echo "Check the output above for details."
    exit 1
fi
