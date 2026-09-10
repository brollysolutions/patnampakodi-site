-- Disposable local credentials only. Provision deployment credentials separately.
CREATE ROLE pakodi_app LOGIN PASSWORD 'local-app-only' NOSUPERUSER NOBYPASSRLS;
