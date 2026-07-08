# Changelog

All notable changes to this project will be documented in this file.

This project follows an incremental delivery approach. Versions and tags will be created for relevant project milestones.

## [Unreleased]

### Added

- No unreleased changes yet.

### Changed

- No unreleased changes yet.

### Fixed

- No unreleased changes yet.

## [v0.2.0-frontend-mock] - 2026-07-07

### Added

- React + Vite frontend in `app/frontend`.
- Hotel Insights visual prototype with boutique hospitality look and feel.
- Reservation form for cancellation-risk prediction inputs.
- Mock prediction service to validate UX/UI before backend integration.
- Result panel with probability, risk level, factors and recommendation.
- Frontend execution documented in `README.md`.

### Verified

- Frontend build verified with:

```bash
cd app/frontend
pnpm install
pnpm build
```

## [v0.1.0-docs-foundation] - 2026-07-07

### Added

- Project vision documentation.
- Git workflow documentation.
- SDD and AI agents workflow documentation.
- Delivery roadmap by project phase.
- Professional project README.
- SPEC 2 updated with React + Vite frontend, planned FastAPI backend and Jira board.
- Pull Request template for consistent reviews.
- Initial changelog structure.

### Verified

- Documentation merged through Pull Requests into `develop`.
- Local `develop` checked clean after merges.

## Planned Milestones

### v0.3.0-data-eda

Dataset and exploratory analysis:

- Dataset validation.
- Data dictionary.
- EDA visualizations.
- Target distribution.
- Initial feature analysis.

### v0.4.0-baseline

Essential ML baseline:

- Preprocessing pipeline.
- Baseline model.
- Required classification metrics.
- Overfitting check.

### v0.5.0-api

Backend inference API:

- FastAPI backend.
- `POST /predict`.
- Model loading.
- Frontend-backend integration.

### v0.6.0-champion

Champion model:

- Ensemble or selected final model.
- Cross-validation.
- Hyperparameter tuning.
- Champion metadata.
- Model report update.

### v0.7.0-operational

Operational layer:

- Tests.
- GitHub Actions.
- Docker.
- Feedback persistence.

### v1.0.0-final

Final delivery:

- Stable demo.
- Technical report.
- Business presentation.
- Technical presentation.
- Final checklist.
