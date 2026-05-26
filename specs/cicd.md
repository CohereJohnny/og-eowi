# EOWI Demo CI/CD Specification

## Overview

This document defines what the EOWI demo repository requires for local quality gates, pull-request validation, dependency updates, and main branch protection.

The goal is to keep the demo merge-ready without slowing down local iteration on data ingestion and UI polish.

## Requirements

### Functional Requirements

- FR-1: The repository must run automated checks before code reaches `main`.
- FR-2: Local hooks must catch formatting issues, syntax issues, obvious secrets, large files, and merge conflicts.
- FR-3: Pull-request CI must validate backend Python, frontend TypeScript/Next.js, Docker Compose configuration, and the mock-corpus eval harness.
- FR-4: Local environment files and credentials must not be committed.
- FR-5: Dependency update PRs must be opened automatically for pnpm, uv, and GitHub Actions.

### Non-Functional Requirements

- NFR-1: Pre-commit must remain fast enough for normal development.
- NFR-2: Slower checks must run on pre-push and CI rather than every commit.
- NFR-3: CI must not require live Cohere API calls or the Databricks Volve export.
- NFR-4: CI must run entirely against the bundled mock corpus.

## Local Quality Gates

### Commit-Time Requirements

- Trim trailing whitespace.
- Ensure newline at end of file.
- Validate YAML, JSON, and TOML.
- Detect merge conflict markers.
- Detect private keys.
- Block files larger than 10 MB.
- Run Ruff check and Ruff format on Python files.
- Prevent staging local secret/key files:
  - `.env`
  - `.env.local`
  - `*.pem`
  - `*.key`

### Push-Time Requirements

- Frontend type checking must pass.
- Backend unit tests must pass.

## Pull Request CI

CI must run on:

- Pull requests targeting `main`
- Pushes to `main`

### Backend Validation

- Python linting must pass for backend and ingestion/eval scripts.
- Python formatting must be validated.
- Backend tests must pass.
- Mock-corpus eval smoke tests must pass.

### Frontend Validation

- Frontend dependencies must install from the lockfile.
- TypeScript type checking must pass.
- Production build must pass.

### Configuration and Security Validation

- Docker Compose configuration must be valid.
- Tracked files must not contain obvious Cohere API key patterns.
- Tracked files must not contain private keys.
- Secret scanning must run in CI.

## Dependency Updates

Automated dependency update PRs must be opened weekly for:

- `pnpm` dependencies in `frontend/`
- `uv` dependencies in the Python workspace
- GitHub Actions in `.github/workflows/`

## Branch Protection

Enable branch protection for `main` after the first CI run exists.

Recommended settings:

- Require pull request before merging.
- Require status checks to pass.
- Require branches to be up to date before merging.
- Require conversation resolution.
- Block force pushes.
- Block branch deletion.
- Require linear history if the repo owner wants squash/rebase-only history.

Optional settings:

- Require one approval if another reviewer is available.
- Require signed commits only if the org already enforces signing.

## Required Checks

The following CI categories must be required before merging to `main`:

- Backend validation
- Frontend validation
- Configuration and security validation

## Release Flow

1. Work on a sprint branch.
2. Keep `sprints/sprint_N/sprint_N_tasks.md` updated.
3. Open PR to `main`.
4. Wait for CI checks.
5. Perform browser smoke test on `http://localhost:3001`.
6. Merge after checks pass.
7. Tag demo milestones, for example `eowi-demo-v1`, once the repo reaches a release-ready state.

## Secrets Policy

- Local environment files are for developer secrets only and must be ignored by git.
- CI must not require `COHERE_API_KEY` for mock-corpus validation.
- Live Cohere/Databricks checks belong in manual release validation, not PR CI.

## Acceptance Criteria

- [ ] AC-1: Local commit hooks catch whitespace, syntax, merge conflict, large-file, and obvious secret issues.
- [ ] AC-2: Local push hooks catch frontend type errors and backend test failures.
- [ ] AC-3: Pull requests to `main` run backend, frontend, configuration, and security checks.
- [ ] AC-4: Dependency update PRs are opened automatically for frontend, backend, and workflow dependencies.
- [ ] AC-5: Main branch protection requires CI to pass before merge.
- [ ] AC-6: The CI path runs without live external data or model credentials.

## Related Implementation Artifacts

- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `.github/dependabot.yml`
- `pyproject.toml`
- `frontend/package.json`

## Known Limitations

- The eval harness is currently a smoke test over the mock corpus. It should expand once real Volve data is indexed.
- Gitleaks may need organization-level GitHub permissions depending on repository visibility and org settings.
- Full Docker image build is not required in CI yet; `docker compose config` validates configuration only.
