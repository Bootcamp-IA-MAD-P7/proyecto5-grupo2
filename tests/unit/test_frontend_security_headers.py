from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NGINX_CONFIG = PROJECT_ROOT / "app" / "frontend" / "nginx.conf"


def test_nginx_disables_version_tokens_and_adds_security_headers() -> None:
    config = NGINX_CONFIG.read_text(encoding="utf-8")

    assert "server_tokens off;" in config
    assert 'add_header Strict-Transport-Security "max-age=31536000" always;' in config
    assert 'add_header X-Content-Type-Options "nosniff" always;' in config
    assert 'add_header X-Frame-Options "DENY" always;' in config
    assert 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;' in config
    assert (
        'add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;'
        in config
    )
