# Hardened Harvey deployment (opt-in)
This branch adds a Compose override. **It does not change the normal deployment**.

## Security objective
The stock compose mounts the *host user's* ~/.claude into Harvey, writable.
The override adds a **dedicated** authentication directory, and disables
privilege escalation / Linux capabilities. Claude CLI refreshes auth tokens,
so making the directory read-only would break authentication.

## Prepare
1. Create a separate authentication directory, on the host, owned by the
   container's UID 1000. Keep it outside any other Claude profile.
2. Authenticate Claude for Harvey alone in that directory. Never copy an
   existing primary profile or commit credentials.
3. Set HARVEY_CLAUDE_AUTH_DIR to the **absolute** dedicated directory path.
4. Inspect the final resolved compose configuration (including merged volume
   entries) before starting: `docker compose -f docker-compose.yml -f docker-compose.security.yml config`.
5. Start only in a disposable/staging environment:
   `docker compose -f docker-compose.yml -f docker-compose.security.yml up -d --build`.

## Caveats
- Compose volume merges are path-dependent; verify that ~/.claude from the
  base file is not mounted. If it survives, do not start.
- The dedicated profile still contains secrets accessible to the container.
- The Chromium sandbox and /tmp requirements may vary; smoke-test browser
  functions, Claude login, token refresh and restart on the target host.
- This does not eliminate SSRF, prompt injection, insecure email sending or
  other application-layer vulnerabilities. No production approval implied.
- Do not publish dashboard ports or Docker socket access. Keep email sending
  disabled pending review.
