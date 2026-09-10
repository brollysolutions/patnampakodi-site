-- Local development credentials only. Never use this bootstrap in production.
CREATE ROLE pakodi_reader LOGIN PASSWORD 'local-reader-only' NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT ON DATABASE pakodi TO pakodi_reader;
GRANT USAGE ON SCHEMA public TO pakodi_reader;
