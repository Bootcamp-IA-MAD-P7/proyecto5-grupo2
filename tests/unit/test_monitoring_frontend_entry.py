from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "app" / "frontend"


def test_monitoring_dashboard_has_a_separate_production_entrypoint() -> None:
    monitoring_html = (FRONTEND / "monitoring.html").read_text(encoding="utf-8")
    vite_config = (FRONTEND / "vite.config.js").read_text(encoding="utf-8")
    nginx_config = (FRONTEND / "nginx.conf").read_text(encoding="utf-8")
    dockerfile = (FRONTEND / "Dockerfile").read_text(encoding="utf-8")

    assert 'src="/src/monitoring/main.jsx"' in monitoring_html
    assert 'monitoring: `${rootDirectory}monitoring.html`' in vite_config
    assert "location = /monitoring" in nginx_config
    assert "try_files /monitoring.html =404" in nginx_config
    assert "COPY index.html monitoring.html vite.config.js ./" in dockerfile


def test_monitoring_dashboard_uses_real_experiment_evidence() -> None:
    service = (FRONTEND / "src" / "monitoring" / "monitoringService.js").read_text(
        encoding="utf-8"
    )
    dashboard = (
        FRONTEND / "src" / "monitoring" / "MonitoringDashboard.jsx"
    ).read_text(encoding="utf-8")

    assert 'settle("experiments", "/monitoring/experiments")' in service
    assert "experiments.neural_network" in dashboard
    assert "experiments.ab_testing" in dashboard
    assert "experiments.conditional_promotion" in dashboard
    assert "Sin experimento registrado" not in dashboard
