# Create setup-dev-monitoring Command
**Status:** Done
**Agent PID:** 40202

## Original Todo
take the approach and learnings from setup_make_dev.py script and create a new command file setup-dev-monitoring that uses the programmatic-prompt-commandfile approach to constructing its prompt to consist of:

1. LLM to call a python script that checks for and installs dependencies (copy sections of the setup_make_dev.py into new small scripts with specific goals)
2. LLM analysis and awarenss of the monorepo and what apps and packages are installed and what to label them
3. Use that awareness to pass arguments to create an appropriate make file with all necessary commands
4. Use that awareness to pass argument to create an appropriate profile with necessary commands
5. Creates an appropriate or adds to a Claude.md file in the project level .claude (should make it if missing)
   We need to also review if there are any other things it should do that I havent considered based on the setup_make_dev.py script

## Description
Create a new `setup-dev-monitoring` command file that uses the programmatic-prompt-commandfile structure to establish comprehensive development monitoring capabilities for any project structure. The command will be **source project pattern agnostic** - leveraging Claude's analytical capabilities to explore and understand any given project structure (monorepo, single-repo, multi-language, framework-specific, etc.) and intelligently determine what monitoring assets need to be created to meet the objective.

The command combines LLM-driven project analysis with targeted Python automation scripts to install monitoring dependencies, generate appropriate build/process management files (Makefiles, Procfiles, or alternatives), and create tailored development monitoring infrastructure including performance tracking, error monitoring, log aggregation, and health checking capabilities that adapt to the discovered project patterns.

## Implementation Plan
- [x] Create setup-dev-monitoring.md command file with fully LLM-driven workflow phases (claude/commands/setup-dev-monitoring.md)
- [x] Create cross-platform dependency checking script (claude/scripts/utils/check_system_dependencies.py)
- [x] Create cross-platform monitoring tool installation script (claude/scripts/utils/install_monitoring_tools.py) 
- [x] Create monitoring file template generation script (claude/scripts/utils/generate_monitoring_templates.py)
- [x] Test utility scripts work on current platform
- [x] Improve command structure based on user feedback:
  - LLM-driven project component discovery (no hardcoded types)
  - Script-based dependency check/install, Makefile, and Procfile generation
  - LLM determines watch patterns based on analysis
  - Remove templates from command, integrate into scripts
  - Validation as final phase
  - Remove framework-specific flags
- [x] Streamline Phase 3 to run dry-run silently before single STOP point
- [x] User test: Run setup-dev-monitoring command on actual project and verify monitoring setup works

## Notes
[Implementation notes]