# Changelog

All notable changes to this project will be documented in this file.

This project follows an incremental delivery approach. Versions and tags will be created for relevant project milestones.

## [Unreleased]

### Added

- Unit tests for the optimized Random Forest challenger tuning, including selected hyperparameters, minimum validation F1 and overfitting rule checks.
- Champion Random Forest integration in the FastAPI backend.
- Champion metadata loading from `models/champion/champion_metadata.json`.
- Champion Random Forest diagnostic figures for confusion matrix, ROC curve and feature importance.
- Technical presentation support note for the final metrics and overfitting review.
- Feedback logging endpoint `POST /feedback`.
- Feedback summary endpoint `GET /feedback/summary`.
- CSV feedback persistence under `data/feedback/prediction_feedback.csv`.
- Feedback ingestion utility for future retraining datasets.
- End-to-end smoke test covering health, model info, prediction, feedback and feedback summary.
- Docker validation with backend, frontend, Champion inference and feedback endpoints.
- Manual app validation report in `reports/manual_app_validation.md`.

### Changed

- Updated SPEC tasks, technical SPEC and README to mark `T-3.3 Optimizar hiperparametros` as completed after the optimized challenger was integrated and verified.
- Updated API contract, SPEC tasks, technical SPEC and README to reflect `random_forest_champion_v0.1.0` as the model served by the API.
- Updated SPEC tasks, technical SPEC and README to mark feedback, new-data collection, Docker validation and smoke flow as completed.
- Updated README, roadmap and model report to reflect the Champion Random Forest as the model loaded by the API.
- Updated Champion metadata and diagnostics text with final validation metrics, cross-validation and overfitting evidence.

### Pending

- Cloud deployment decision.
- Frontend UX review or alternative beta flow.

## [v0.4.0-essential-mvp] - 2026-07-09

### Added

- Dataset status details in `.specify/2_spec.md`, including confirmed CSV path, row count, column count and target distribution.
- Initial API contract in `docs/api_contract.md`.
- Initial FastAPI backend structure in `app/backend`.
- `GET /health` endpoint for backend availability checks.
- `POST /predict` endpoint with response contract compatible with the current frontend.
- Backend dependencies in `requirements.txt`: `fastapi`, `pydantic` and `uvicorn`.
- Backend API smoke tests for `GET /health`, `POST /predict` and invalid payload validation.
- GitHub Actions workflow for backend API tests.
- GitHub Actions workflow for frontend build checks.
- Explicit `httpx` dependency for FastAPI `TestClient` in CI.
- Docker setup for backend, frontend and local compose orchestration.
- `GET /model/info` endpoint for model status and future Champion Model metadata.
- Backend model service layer to isolate model inference from API routes.
- Additional API contract tests for model info and model version consistency.
- Real baseline inference in `POST /predict` using `models/baseline/logistic_regression_baseline.pkl`.
- Arrival date fields in the API and frontend prediction payload to match the trained model feature contract.
- Model diagnostics script for baseline coefficient importance and validation error analysis.

### Changed

- Replaced remaining Trello references with Jira in SPEC and agent prompt documentation.
- Updated dataset-related SPEC notes now that the CSV is already available in `data/raw/`.
- Updated SPEC status to reflect the merged backend API base.
- Updated `README.md` with delivery-level progress against the project briefing.
- Defined F1-score of the `Canceled` class as the primary model metric in SPEC, roadmap and README.
- Updated API contract and README with model info endpoint.
- Updated API contract, SPEC tasks and README to reflect real baseline inference instead of mock backend prediction.
- Updated `reports/model_report.md` with feature importance, error analysis, limitations and next-step interpretation.

### Fixed

- Removed obsolete dataset TODOs from `.specify/2_spec.md`.

### Verified

- Essential level covered: functional classification model, EDA, overfitting under 5%, productivized API solution and technical model report.
- Local test suite verified with `python -m pytest`.
- Frontend build verified with `pnpm build`.

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

### v0.5.0-api

Next API/product increment:

- Manual validation evidence.
- Frontend UX evidence.
- Optional cloud deployment preparation.

### v0.6.0-champion

Champion model:

- Champion validation evidence.
- Docker validation with Champion inference.
- Model report and README final alignment.

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
