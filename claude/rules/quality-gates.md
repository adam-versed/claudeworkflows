# Quality Gates

## Requirements
- All tests must pass
- Lint checks must pass
- Type checking must pass
- Build must succeed
- No security issues

## Commands
- test: `npm test` or `python -m pytest`
- lint: `npm run lint` or `flake8`
- type: `npm run typecheck` or `mypy`
- build: `npm run build` or `python setup.py build`

## Failure Handling
- Report all failures
- Fix underlying issues
- Never bypass with comments
- Never skip tests