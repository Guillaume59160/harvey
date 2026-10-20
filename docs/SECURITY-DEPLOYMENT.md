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

## Mandatory P0 gates before production
1. Run all pytest and Docker smoke tests. GitHub Actions currently has no
   reported workflow runs; code review is not a substitute for a passing CI.
2. Run the resolved Compose preflight:
   `docker compose -f docker-compose.yml -f docker-compose.security.yml config --format json | python scripts/check_security_compose.py`
   Set HARVEY_CLAUDE_AUTH_DIR to a dedicated *absolute* path first.
3. Block container egress to Docker bridge and host networks, all RFC1918,
   loopback, link-local, cloud metadata (169.254.169.254), multicast, and
   IPv6 private/link-local ranges **at the host or network gateway**.
   Verify this with harmless connectivity tests from staging, including DNS
   rebinding scenarios. The Python pre-request DNS check is not atomic with
   connect and does not by itself prevent DNS rebinding. Do not treat a simple
   Docker container network as a private-address firewall.
4. Keep outbound email disabled and test with a fake provider. Native delivery
   and Instantly are distinct paths; Instantly now refuses deployment whenever
   human approval is required. An external Instantly campaign already active
   cannot be recalled by Harvey's local kill switch: pause it at the provider.
5. Revalidate all collectors and outbound integrations for SSRF; the profile
   guard is only a first coverage area.
6. The host must not expose SSH, Docker or admin APIs to Harvey's egress.

## Étape préliminaire : test du réseau Docker jetable

Sur le runner Ubuntu GitHub, le job `docker-network-smoke` exécute
`bash scripts/smoke_docker_network_none.sh`. Il lance une image Python
éphémère, non privilégiée, en `--network none`, sans identifiants ni volumes
professionnels, puis vérifie l'absence de connexions sortantes. **Il ne
lance pas Harvey** et ne valide donc ni la politique réseau de la véritable
instance ni son accès éventuel à des services sur le VPS.

Le véritable Harvey a besoin d'un accès réseau pour découvrir les entreprises,
profilage et fournisseurs : `--network none` convient uniquement aux essais
hors ligne. Avant les essais avec réseau, imposer et tester des règles egress
sur un environnement de staging distinct, bloquer les réseaux privés et
métadonnées, prévoir la résolution DNS contrôlée et les exceptions strictement
nécessaires. Ne jamais appliquer une règle globale sans auditer l'impact sur
Hermes, EspoCRM et les autres conteneurs.
