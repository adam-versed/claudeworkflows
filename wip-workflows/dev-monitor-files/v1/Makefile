# ==========================================
# DEVELOPMENT WORKFLOW FOR TURBOREPO
# ==========================================
# CRITICAL: Claude should NEVER run 'make dev'
# Always ask user to start development services
# ==========================================

.PHONY: dev tail-log lint test format clean status stop help

# Start all development services (USER ONLY - NEVER AUTOMATED)
dev:
	@echo "🚀 Starting Turborepo development environment..."
	@echo "📱 Services will start with auto-reload enabled"
	@echo "📝 Logs will be written to dev.log"
	@rm -f dev.log
	@touch dev.log
	@echo "$$(date): Development services starting" >> dev.log
	shoreman Procfile

# Access unified development logs (Claude can use this)
tail-log:
	@if [ -f dev.log ]; then \
		echo "📋 Development logs (use Ctrl+C to exit):"; \
		tail -f dev.log; \
	else \
		echo "❌ No development logs found. Run 'make dev' first."; \
	fi

# Show current service status
status:
	@if [ -f shoreman.pid ]; then \
		echo "✅ Development services are running (PID: $$(cat shoreman.pid))"; \
		echo "📝 Log file: dev.log"; \
		echo "🔍 Use 'make tail-log' to view logs"; \
	else \
		echo "❌ Development services are not running"; \
		echo "🚀 Run 'make dev' to start services"; \
	fi

# Stop all services (USER ONLY)
stop:
	@if [ -f shoreman.pid ]; then \
		echo "🛑 Stopping development services..."; \
		kill $$(cat shoreman.pid) 2>/dev/null || true; \
		rm -f shoreman.pid; \
		echo "✅ Services stopped"; \
	else \
		echo "ℹ️  No services running"; \
	fi

# Code quality and testing
lint:
	@echo "🔍 Running linting across monorepo..."
	npx turbo lint

test:
	@echo "🧪 Running tests across monorepo..."
	npx turbo test

format:
	@echo "✨ Formatting code across monorepo..."
	npx turbo format

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	npx turbo clean
	@echo "🗑️  Removing log files..."
	rm -f dev.log shoreman.pid
	@echo "✅ Cleanup complete"

# Help
help:
	@echo "📚 Turborepo Development Commands:"
	@echo ""
	@echo "  make dev       Start all services (web, mobile, backend)"
	@echo "  make tail-log  View unified development logs"
	@echo "  make status    Check if services are running"
	@echo "  make stop      Stop all development services"
	@echo ""
	@echo "  make lint      Run code quality checks"
	@echo "  make test      Run test suites"
	@echo "  make format    Format all code"
	@echo "  make clean     Clean build artifacts and logs"
	@echo ""
	@echo "⚠️  Claude should NEVER run 'make dev' or 'make stop'"
	@echo "📋 Claude can use 'make tail-log' and 'make status'"
