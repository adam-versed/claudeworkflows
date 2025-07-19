# Create Make-Based Development System
**Status:** InProgress
**Agent PID:** 40202

## Original Todo
we need to work out the best way to create a command(s) that will, for each project we run the command in, replicate the make system shown in wip-workflows/make-dev1.png. Essentially it uses a combination of make commands, procifles and watchexec tool to control server start, server automatic recompile on file change where not already supported and also a capture of component (frontend, backend) events to a central dev.log which you can access the tail from through another make command through any terminal instance running claude code within a given project (dev.log is per project). Supporting files in wip-workflows folder:
  video transcript - make-dev-notes.md (all commentary on this subject is in first 3rd of video)
  claude.md-make-commands.png
  logfile-terminal-output.png
  make-dev1.png
  procifle-example.png
  watchexec.png
  https://github.com/chrismytton/shoreman
  https://github.com/watchexec/watchexec

## Description
A make-based development command specifically for Turborepo monorepos with Next.js web apps, React Native mobile apps, and Convex backend. This creates a standardized development workflow that manages the web server, mobile development server, Convex backend, and unified logging across all three environments. The system uses make targets, Procfiles, and watchexec to provide Claude with reliable access to development logs with user controlled starting and stopping of services preventing the LLM from taking these actions.

## Implementation Plan
- [x] Create `claude/commands/setup-make-dev.md` command file with header comment and versioning
- [x] Add project structure detection for Turborepo monorepos (turbo.json, apps/web, apps/native, packages/backend)
- [x] Generate Makefile with standardized targets (dev, tail-log, lint, test, clean, format)
- [x] Create Procfile template for Turborepo setup (web: next dev, native: expo start, backend: convex dev)
- [x] Configure watchexec for multi-workspace file monitoring (.js, .ts, .tsx, .json, convex files)
- [x] Implement unified logging system writing to dev.log with service prefixes
- [x] Add CLAUDE.md documentation section explaining development commands and LLM restrictions
- [x] Automated test: Verify Makefile targets work correctly and Procfile processes start
- [x] User test: Run `make dev` to start all services, verify `make tail-log` shows unified logs, confirm Claude can read logs but cannot start/stop services
- [x] Create Python script for automated make-dev setup with dependency installation and file generation

## Notes
Added comprehensive Python setup script at `claude/scripts/setup_make_dev.py` that:
- Automatically detects Turborepo project structure
- Checks and installs required dependencies (make, node, npm, watchexec, shoreman)
- Generates Makefile and Procfile based on detected services
- Updates .gitignore and CLAUDE.md with development workflow documentation
- Runs validation tests to ensure everything works
- Supports dry-run mode and cross-platform installation