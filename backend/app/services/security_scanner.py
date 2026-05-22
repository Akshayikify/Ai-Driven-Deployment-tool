"""
security_scanner.py
-------------------
Three-layer secret detection engine for the AI-Driven Deployment Tool.

Detection layers (applied in order):
  Layer 1 — Dangerous file names (.env, id_rsa, *.pem, credentials.json …)
  Layer 2 — Regex pattern matching (AWS keys, OpenAI tokens, Stripe, DB URLs …)
  Layer 3 — Shannon entropy (catches custom/unknown high-entropy secrets)

Design decisions:
  - Reuses the file_index already built by AnalysisEngine (no extra filesystem walk).
  - The raw secret value is NEVER stored or logged; only a redacted snippet is kept.
  - Zero external dependencies — pure stdlib (re, math, os, time).
  - CRITICAL findings block the pipeline; HIGH/MEDIUM/LOW produce warnings only.
"""

from __future__ import annotations

import math
import os
import re
import time
from typing import Dict, List, Optional, Tuple

from loguru import logger

from app.schemas.security import SecurityFinding, SecurityReport

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories to skip when walking the workspace (same as AnalysisEngine)
SKIP_DIRS: frozenset = frozenset({
    ".git", "node_modules", "venv", "__pycache__",
    "aienv", ".venv", "dist", "build", "target",
})

# File extensions that are binary or lock-files (lock files contain legit long hashes)
SKIP_EXTENSIONS: frozenset = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".mp3", ".wav", ".ogg",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".bin", ".exe", ".so", ".dll", ".dylib", ".class", ".jar",
    ".pyc", ".pyo",
    # Lock files: contain long content-hash strings that trigger false entropy alarms
    ".lock",                  # Pipfile.lock, yarn.lock
    # Also skip compiled/minified JS
    ".min.js", ".map",
})

# Skip files larger than 1 MB (binary blobs, datasets, etc.)
MAX_FILE_SIZE_BYTES: int = 1_000_000

# ---------------------------------------------------------------------------
# Layer 1 — Dangerous file name patterns
# ---------------------------------------------------------------------------

# Each entry: (glob_suffix_or_exact_name, severity, rule_id, description, recommendation)
DANGEROUS_FILE_RULES: List[Tuple[str, str, str, str, str]] = [
    # .env files
    (".env",              "CRITICAL", "ENV_FILE",        ".env file committed to repository",
     "Add .env to .gitignore and use environment variables / secrets manager instead."),
    (".env.local",        "CRITICAL", "ENV_FILE_LOCAL",  ".env.local file committed to repository",
     "Remove this file from version control and rotate any exposed secrets."),
    (".env.production",   "CRITICAL", "ENV_FILE_PROD",   ".env.production file committed",
     "Production secrets must never be committed. Use CI/CD secret stores."),
    (".env.development",  "HIGH",     "ENV_FILE_DEV",    ".env.development file committed",
     "Development secrets may still contain real credentials. Remove from VCS."),
    (".env.staging",      "HIGH",     "ENV_FILE_STAGING", ".env.staging file committed",
     "Remove from version control and use environment variables in CI/CD."),
    (".env.test",         "MEDIUM",   "ENV_FILE_TEST",   ".env.test file committed",
     "Verify this file does not contain real credentials."),

    # Private keys / certificates
    ("id_rsa",            "CRITICAL", "SSH_PRIVATE_KEY", "SSH private key (id_rsa) found",
     "Delete immediately, revoke the key pair, generate a new one, and NEVER commit keys."),
    ("id_dsa",            "CRITICAL", "SSH_PRIVATE_KEY", "SSH private key (id_dsa) found",
     "Delete immediately and revoke the key pair."),
    ("id_ecdsa",          "CRITICAL", "SSH_PRIVATE_KEY", "SSH private key (id_ecdsa) found",
     "Delete immediately and revoke the key pair."),
    ("id_ed25519",        "CRITICAL", "SSH_PRIVATE_KEY", "SSH private key (id_ed25519) found",
     "Delete immediately and revoke the key pair."),

    # Cloud credential files
    ("credentials.json",  "CRITICAL", "GCP_CREDENTIALS",
     "Google Cloud / Firebase service account credentials file detected",
     "Remove immediately. Revoke the service account key and use Workload Identity / Secret Manager."),
    ("service-account.json", "CRITICAL", "GCP_SERVICE_ACCOUNT",
     "GCP service account JSON key file detected",
     "Revoke this service account key and use environment variables or GCP Workload Identity."),

    # AWS
    ("credentials",       "CRITICAL", "AWS_CREDENTIALS", "AWS credentials file detected",
     "Remove from repo. Use IAM roles or environment variables (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)."),

    # Terraform secrets
    ("terraform.tfvars",  "HIGH",     "TERRAFORM_TFVARS",
     "Terraform .tfvars file may contain infrastructure secrets",
     "Add *.tfvars to .gitignore and use Terraform Cloud / Vault for secrets."),

    # npm tokens
    (".npmrc",            "HIGH",     "NPMRC_FILE",
     ".npmrc file may contain npm auth tokens",
     "Remove from VCS; store tokens in CI/CD environment variables."),

    # Java keystores
    (".jks",              "HIGH",     "JAVA_KEYSTORE",  "Java KeyStore file committed",
     "Remove the keystore from VCS. Never commit certificate stores."),
    (".p12",              "HIGH",     "PKCS12_KEYSTORE", "PKCS12 keystore/certificate bundle found",
     "Remove from VCS and store securely."),
    (".pfx",              "HIGH",     "PFX_CERT",       "PFX certificate file found",
     "Remove from VCS and store securely."),

    # Docker
    (".docker/config.json", "HIGH",   "DOCKER_CONFIG",  "Docker config with auth tokens found",
     "Remove from VCS; use docker credential helpers."),

    # Django settings — commonly contains hardcoded SECRET_KEY and DB passwords
    ("settings.py",         "MEDIUM", "DJANGO_SETTINGS",
     "Django settings.py file detected — verify SECRET_KEY and database credentials are not hardcoded",
     "Ensure SECRET_KEY is loaded from environment variables. Use python-decouple or django-environ."),
]

# Filenames that must match exactly (case-insensitive) vs. suffix match
_EXACT_MATCH_DANGEROUS = frozenset(
    rule[0] for rule in DANGEROUS_FILE_RULES
    if not rule[0].startswith("*") and "." not in rule[0].lstrip(".")
)

# ---------------------------------------------------------------------------
# Layer 2 — Regex secret patterns
# ---------------------------------------------------------------------------

# Each entry: (rule_id, severity, description, compiled_pattern, recommendation)
_RAW_SECRET_PATTERNS: List[Tuple[str, str, str, str, str]] = [
    # --- AWS ---
    ("AWS_ACCESS_KEY_ID", "CRITICAL",
     "AWS Access Key ID detected",
     r"AKIA[0-9A-Z]{16}",
     "Rotate this key immediately in AWS IAM. Use IAM roles or environment variables."),

    ("AWS_SECRET_KEY", "CRITICAL",
     "AWS Secret Access Key detected",
     r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9+/]{40}['\"]?",
     "Rotate this key immediately in AWS IAM."),

    # --- Google ---
    ("GOOGLE_API_KEY", "CRITICAL",
     "Google API Key (AIza...) detected",
     r"AIza[0-9A-Za-z\-_]{35}",
     "Restrict and rotate this key in Google Cloud Console. Use Secret Manager."),

    ("GCP_SERVICE_ACCOUNT_EMAIL", "HIGH",
     "Google service account JSON key content detected",
     r"\"type\"\s*:\s*\"service_account\"",
     "Revoke the service account key and remove this file from version control."),

    # --- OpenAI / AI providers ---
    ("OPENAI_API_KEY", "CRITICAL",
     "OpenAI API Key detected",
     r"sk-[a-zA-Z0-9]{48}",
     "Revoke this key at platform.openai.com and use environment variables."),

    ("OPENAI_PROJECT_KEY", "CRITICAL",
     "OpenAI Project API Key detected",
     r"sk-proj-[a-zA-Z0-9_\-]{90,}",
     "Revoke this key at platform.openai.com and use environment variables."),

    ("ANTHROPIC_API_KEY", "CRITICAL",
     "Anthropic (Claude) API Key detected",
     r"sk-ant-[a-zA-Z0-9\-_]{90,}",
     "Revoke this key at console.anthropic.com and use environment variables."),

    ("GROQ_API_KEY", "CRITICAL",
     "Groq API Key detected",
     r"gsk_[a-zA-Z0-9]{52}",
     "Revoke this key at console.groq.com and use environment variables."),

    # --- GitHub ---
    ("GITHUB_TOKEN", "CRITICAL",
     "GitHub Personal Access Token or App token detected",
     r"gh[pousr]_[A-Za-z0-9_]{36,}",
     "Revoke this token at github.com/settings/tokens immediately."),

    # --- Stripe ---
    ("STRIPE_KEY", "CRITICAL",
     "Stripe API Key (live or test) detected",
     r"(?:r|s)k_(?:live|test)_[0-9a-zA-Z]{24}",
     "Revoke at dashboard.stripe.com. Live keys especially must be rotated immediately."),

    # --- Twilio ---
    ("TWILIO_AUTH_TOKEN", "HIGH",
     "Twilio Auth Token / Account SID pattern detected",
     r"AC[a-fA-F0-9]{32}|SK[a-fA-F0-9]{32}",
     "Rotate this token in your Twilio console."),

    # --- Slack ---
    ("SLACK_WEBHOOK", "HIGH",
     "Slack Incoming Webhook URL detected",
     r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
     "Revoke and regenerate this webhook in your Slack app settings."),

    ("SLACK_TOKEN", "CRITICAL",
     "Slack Bot/OAuth token detected",
     r"xox[baprs]-[0-9A-Za-z\-]{10,}",
     "Revoke at api.slack.com/apps and use environment variables."),

    # --- SendGrid ---
    ("SENDGRID_API_KEY", "CRITICAL",
     "SendGrid API Key detected",
     r"SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}",
     "Revoke at app.sendgrid.com and use environment variables."),

    # --- Firebase ---
    ("FIREBASE_SERVER_KEY", "CRITICAL",
     "Firebase Cloud Messaging Server Key detected",
     r"AAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140}",
     "Revoke in Firebase Console under Project Settings > Cloud Messaging."),

    # --- Heroku ---
    ("HEROKU_API_KEY", "HIGH",
     "Heroku API Key detected",
     r"(?i)heroku[_\-]?api[_\-]?key\s*[:=]\s*['\"]?[0-9a-f\-]{36}['\"]?",
     "Revoke at heroku.com/account and use Heroku config vars."),

    # --- JWT ---
    ("JWT_TOKEN", "HIGH",
     "Hardcoded JSON Web Token (JWT) detected",
     r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
     "Never hardcode JWTs. Generate them at runtime using a secret key stored in env vars."),

    # --- Private keys (file content) ---
    ("RSA_PRIVATE_KEY", "CRITICAL",
     "RSA/EC Private Key block found in file content",
     r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
     "Remove this private key immediately. Never commit private keys to version control."),

    ("PGP_PRIVATE_KEY", "CRITICAL",
     "PGP Private Key block found in file content",
     r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
     "Remove this PGP private key immediately and revoke it."),

    # --- Database connection strings with embedded passwords ---
    ("POSTGRES_CONN_STRING", "CRITICAL",
     "PostgreSQL connection string with embedded password",
     r"postgres(?:ql)?://[^:\s]+:[^@\s]{3,}@",
     "Use DATABASE_URL as an environment variable. Never embed passwords in connection strings."),

    ("MYSQL_CONN_STRING", "CRITICAL",
     "MySQL connection string with embedded password",
     r"mysql(?:2)?://[^:\s]+:[^@\s]{3,}@",
     "Store credentials in environment variables, not connection strings."),

    ("MONGODB_CONN_STRING", "CRITICAL",
     "MongoDB connection string with embedded password",
     r"mongodb(?:\+srv)?://[^:\s]+:[^@\s]{3,}@",
     "Use MONGODB_URI as an environment variable."),

    ("REDIS_CONN_STRING", "HIGH",
     "Redis connection string with embedded password",
     r"redis://:[^@\s]{3,}@",
     "Use REDIS_URL as an environment variable."),

    # --- Django SECRET_KEY (hardcoded insecure key) ---
    ("DJANGO_SECRET_KEY", "CRITICAL",
     "Hardcoded Django SECRET_KEY detected — django-insecure prefix confirms it is not loaded from env",
     r"(?i)SECRET_KEY\s*=\s*['\"]django-insecure-[^'\"]{20,}['\"]",
     "Remove the hardcoded SECRET_KEY. Set it via an environment variable: "
     "SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') and add python-decouple or django-environ."),

    # --- Django SECRET_KEY (any hardcoded string, even without insecure prefix) ---
    ("DJANGO_SECRET_KEY_GENERIC", "HIGH",
     "Hardcoded Django SECRET_KEY detected in settings file",
     r"(?i)SECRET_KEY\s*=\s*['\"][^'\"]{20,}['\"]",
     "Never hardcode SECRET_KEY. Use an environment variable: "
     "SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') and rotate the exposed value."),

    # --- Generic hardcoded assignments (high-confidence heuristic) ---
    # Matches patterns like: password = '...', api_key = '...', client_secret = '...'
    # Also catches variable names that END with _key, _secret, _token, _password, _pwd
    ("HARDCODED_SECRET", "HIGH",
     "Hardcoded secret/password in variable assignment",
     r"(?i)(?:password|passwd|pwd|secret|api_key|apikey|auth_token|access_token|client_secret"
     r"|[a-z_]*_(?:key|secret|token|password|pwd))\s*[:=]\s*['\"](?!\s*\$\{)(?!['\"])[^'\"]{8,}['\"]",
     "Replace hardcoded values with environment variable references (e.g. os.getenv('SECRET'))."),

    # --- Mailgun ---
    ("MAILGUN_API_KEY", "HIGH",
     "Mailgun API Key detected",
     r"key-[0-9a-zA-Z]{32}",
     "Revoke at app.mailgun.com and use environment variables."),
]

# Compile all patterns once at module load time
SECRET_PATTERNS: List[Tuple[str, str, str, re.Pattern, str]] = [
    (rule_id, severity, description, re.compile(pattern), recommendation)
    for rule_id, severity, description, pattern, recommendation in _RAW_SECRET_PATTERNS
]

# ---------------------------------------------------------------------------
# Layer 3 — Shannon entropy constants
# ---------------------------------------------------------------------------

# Thresholds for entropy-based secret detection
ENTROPY_THRESHOLD: float = 3.5        # bits per character
ENTROPY_MIN_LENGTH: int = 20          # ignore short values (too many false positives)
ENTROPY_MAX_LENGTH: int = 500         # ignore very long values (paragraphs of text)

# Pattern to extract assignment values for entropy check.
# The character class is intentionally broad to capture Django-style keys that contain
# special characters such as #, ^, *, !, (, ), %, @, &, ~, etc.
_ASSIGNMENT_RE = re.compile(
    r"(?i)(?:key|token|secret|password|passwd|pwd|api|auth|credential|private)"
    r"[_\-\s\w]*[:=]\s*['\"]?([A-Za-z0-9+/=_\-!@#$%^&*()~]{20,})['\"]?"
)

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_ORDER: Dict[str, int] = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def _severity_rank(s: str) -> int:
    return _SEVERITY_ORDER.get(s, 0)


# ---------------------------------------------------------------------------
# Main SecurityScanner class
# ---------------------------------------------------------------------------

class SecurityScanner:
    """
    Scans a cloned repository workspace for hardcoded secrets.

    Usage:
        report = security_scanner.scan(workspace_path, file_index)
        if report.blocked:
            # halt pipeline
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self, workspace_path: str, file_index: dict) -> SecurityReport:
        """
        Run a full three-layer security scan on the workspace.

        Parameters
        ----------
        workspace_path : str
            Absolute path to the cloned repository on disk.
        file_index : dict
            The file index already built by AnalysisEngine.analyze_directory().
            Keys used: ``all_files`` (list of relative paths).

        Returns
        -------
        SecurityReport
            Complete scan result. If ``report.blocked`` is True the caller
            must halt the deployment pipeline.
        """
        t_start = time.monotonic()
        all_files: List[str] = file_index.get("all_files", [])

        findings: List[SecurityFinding] = []
        scanned = 0

        for rel_path in all_files:
            # --- Skip noise ---
            if self._should_skip(rel_path):
                continue

            abs_path = os.path.join(workspace_path, rel_path)
            if not os.path.isfile(abs_path):
                continue

            try:
                file_size = os.path.getsize(abs_path)
            except OSError:
                continue

            if file_size > MAX_FILE_SIZE_BYTES:
                logger.debug(f"Security scan: skipping large file {rel_path} ({file_size} bytes)")
                continue

            # --- Layer 1: file name check ---
            layer1 = self._check_filename(rel_path)
            if layer1:
                findings.append(layer1)
                # Still scan content — there could be more secrets inside

            # --- Layers 2 & 3: content scan ---
            try:
                content_findings = self._scan_file_content(abs_path, rel_path)
                findings.extend(content_findings)
                scanned += 1
            except Exception as exc:
                logger.warning(f"Security scan: could not read {rel_path}: {exc}")

        elapsed_ms = int((time.monotonic() - t_start) * 1000)
        return self._build_report(findings, scanned, elapsed_ms)

    # ------------------------------------------------------------------
    # Layer 1 — Dangerous file name
    # ------------------------------------------------------------------

    def _check_filename(self, rel_path: str) -> Optional[SecurityFinding]:
        """Return a finding if the file name matches a dangerous-file rule."""
        filename = os.path.basename(rel_path).lower()
        # Normalize rel_path separators
        norm_path = rel_path.replace("\\", "/").lower()

        for pattern, severity, rule_id, description, recommendation in DANGEROUS_FILE_RULES:
            pattern_lower = pattern.lower()

            # Exact match on the bare filename
            if filename == pattern_lower:
                return SecurityFinding(
                    severity=severity,
                    rule_id=rule_id,
                    description=description,
                    file_path=rel_path,
                    line_number=0,
                    redacted_snippet=f"File: {rel_path}",
                    recommendation=recommendation,
                )

            # Suffix match (e.g. ".jks", ".p12")
            if pattern_lower.startswith(".") and filename.endswith(pattern_lower):
                return SecurityFinding(
                    severity=severity,
                    rule_id=rule_id,
                    description=description,
                    file_path=rel_path,
                    line_number=0,
                    redacted_snippet=f"File: {rel_path}",
                    recommendation=recommendation,
                )

            # Path-suffix match (e.g. ".aws/credentials", ".docker/config.json")
            if norm_path.endswith(pattern_lower):
                return SecurityFinding(
                    severity=severity,
                    rule_id=rule_id,
                    description=description,
                    file_path=rel_path,
                    line_number=0,
                    redacted_snippet=f"File: {rel_path}",
                    recommendation=recommendation,
                )

        return None

    # ------------------------------------------------------------------
    # Layers 2 & 3 — File content scan
    # ------------------------------------------------------------------

    def _scan_file_content(self, abs_path: str, rel_path: str) -> List[SecurityFinding]:
        """Read a file and apply regex + entropy checks line by line."""
        findings: List[SecurityFinding] = []
        seen_rules_on_line: set = set()  # avoid duplicate findings for the same line+rule

        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as fh:
                for line_no, raw_line in enumerate(fh, start=1):
                    line = raw_line.rstrip("\n\r")

                    # Skip blank lines and comment-only lines (faster inner loop)
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                        continue

                    # Layer 2 — regex patterns
                    for rule_id, severity, description, pattern, recommendation in SECRET_PATTERNS:
                        cache_key = (line_no, rule_id)
                        if cache_key in seen_rules_on_line:
                            continue
                        match = pattern.search(line)
                        if match:
                            seen_rules_on_line.add(cache_key)
                            findings.append(SecurityFinding(
                                severity=severity,
                                rule_id=rule_id,
                                description=description,
                                file_path=rel_path,
                                line_number=line_no,
                                redacted_snippet=self._redact(line, match.start(), match.end()),
                                recommendation=recommendation,
                            ))

                    # Layer 3 — Shannon entropy
                    entropy_finding = self._entropy_check(line, rel_path, line_no)
                    if entropy_finding:
                        # Avoid re-reporting something already caught by regex
                        already_reported = any(
                            f.file_path == rel_path and f.line_number == line_no
                            for f in findings
                        )
                        if not already_reported:
                            findings.append(entropy_finding)

        except (UnicodeDecodeError, PermissionError) as exc:
            logger.debug(f"Security scan: skipping binary/unreadable file {rel_path}: {exc}")

        return findings

    # ------------------------------------------------------------------
    # Layer 3 helper — Shannon entropy
    # ------------------------------------------------------------------

    def _entropy_check(self, line: str, rel_path: str, line_no: int) -> Optional[SecurityFinding]:
        """
        Checks a line for high-entropy assignment values that look like secrets
        even if they don't match any known pattern.
        """
        matches = _ASSIGNMENT_RE.findall(line)
        for value in matches:
            length = len(value)
            if length < ENTROPY_MIN_LENGTH or length > ENTROPY_MAX_LENGTH:
                continue
            # Skip all-lowercase values — likely regular words, not encoded secrets
            if value == value.lower():
                continue

            entropy = _shannon_entropy(value)
            if entropy >= ENTROPY_THRESHOLD:
                snippet = self._redact(line, line.find(value), line.find(value) + length)
                return SecurityFinding(
                    severity="HIGH",
                    rule_id="HIGH_ENTROPY_SECRET",
                    description=f"High-entropy value detected in assignment (entropy={entropy:.2f} bits/char)",
                    file_path=rel_path,
                    line_number=line_no,
                    redacted_snippet=snippet,
                    recommendation=(
                        "This value looks like a secret (high randomness). "
                        "If it is a credential or key, move it to an environment variable."
                    ),
                )
        return None

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _should_skip(rel_path: str) -> bool:
        """Return True if this path should be completely excluded from scanning."""
        parts = rel_path.replace("\\", "/").split("/")
        # Skip if any directory component is in the skip list
        for part in parts[:-1]:
            if part in SKIP_DIRS:
                return True
        # Skip by extension
        filename = parts[-1]
        _, ext = os.path.splitext(filename)
        if ext.lower() in SKIP_EXTENSIONS:
            return True
        # Specifically catch .min.js (splitext only gives .js for 'foo.min.js')
        if filename.endswith(".min.js") or filename.endswith(".min.css"):
            return True
        # Skip the scanner's own source file to avoid the raw regex strings
        # triggering findings against themselves
        if filename == "security_scanner.py":
            return True
        return False

    @staticmethod
    def _redact(line: str, match_start: int, match_end: int) -> str:
        """
        Replace the matched secret portion with ***REDACTED*** in the snippet.
        The returned snippet is trimmed to 120 characters for display.
        """
        redacted = line[:match_start] + "***REDACTED***" + line[match_end:]
        return redacted.strip()[:120]

    @staticmethod
    def _build_report(
        findings: List[SecurityFinding],
        scanned_files: int,
        elapsed_ms: int,
    ) -> SecurityReport:
        """Aggregate individual findings into a final SecurityReport."""
        counts: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1

        blocked = counts["CRITICAL"] > 0
        is_clean = len(findings) == 0

        if is_clean:
            summary = "✅ No secrets detected. Repository is clean."
        elif blocked:
            summary = (
                f"🚨 {len(findings)} secret(s) detected "
                f"({counts['CRITICAL']} CRITICAL). Deployment blocked."
            )
        else:
            summary = (
                f"⚠️ {len(findings)} potential secret(s) found "
                f"(no CRITICAL issues). Review before deploying."
            )

        # Sort findings by severity (most severe first), then by file + line
        findings.sort(
            key=lambda f: (-_severity_rank(f.severity), f.file_path, f.line_number)
        )

        logger.info(
            f"Security scan complete in {elapsed_ms}ms — "
            f"scanned {scanned_files} files, "
            f"found {len(findings)} issue(s). Blocked={blocked}"
        )

        return SecurityReport(
            scanned_files=scanned_files,
            scan_duration_ms=elapsed_ms,
            findings=findings,
            severity_counts=counts,
            is_clean=is_clean,
            blocked=blocked,
            summary=summary,
        )


# ---------------------------------------------------------------------------
# Shannon entropy function
# ---------------------------------------------------------------------------

def _shannon_entropy(data: str) -> float:
    """Compute Shannon entropy in bits per character for the given string."""
    if not data:
        return 0.0
    length = len(data)
    freq = {}
    for ch in data:
        freq[ch] = freq.get(ch, 0) + 1
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


# ---------------------------------------------------------------------------
# Module-level singleton (matches existing service pattern in this project)
# ---------------------------------------------------------------------------

security_scanner = SecurityScanner()
