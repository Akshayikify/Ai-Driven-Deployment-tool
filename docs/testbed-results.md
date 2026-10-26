# Deployment testbed results

The testbed (`testbed/apps/*`, 16 tiny apps) is run two ways:

- **Locally, detection + generation only**: `cd backend; venv/Scripts/python -m pytest tests -q`
- **In CI, full ladder** (detect, Dockerfile, `docker build`, `docker run`, HTTP 2xx-3xx): the `Deployment testbed` workflow (`.github/workflows/testbed.yml`), run from the Actions tab. Its job summary has the table. Set `set_port_env=1` to pass `PORT=<EXPOSE>` as the deployer now does.

## Detection + generation (local)

| Run | Passing | Failures |
|---|---|---|
| Baseline (before fixes) | 12 / 16 | ruby-sinatra, rust-std, static-html (no `EXPOSE` / no template), trap-node-stray-files (detected as Ruby because of one `.rb` file) |
| After fixes | 16 / 16 | none |

## CI ladder (build, run, HTTP)

Not run yet: needs the branch pushed to GitHub. Fill the table from the workflow summary:

| App | Detect | Build | Runs | HTTP |
|---|---|---|---|---|
| (pending first CI run) | | | | |

## What changed

- Stray `.php`/`.rb`/`.swift` files no longer override a language found via a manifest.
- Entry-point files (`src/index.js`, `tests/main.py`) no longer create extra service roots when a manifest exists.
- Node: Vite/CRA/Vue SPAs are built and served by nginx; server apps run as the `node` user with `PORT` set; `@nestjs/core` detected; `npm ci` falls back to `npm install`; lint failures don't block.
- Gradle projects get a Gradle build; Ruby Rack apps run through `rackup`; Rust drops cargo-chef and the old 1.75 pin; Go tracks `golang:1`; static sites get an nginx template.
- Django no longer gets an empty `DJANGO_SETTINGS_MODULE`; Python pytest failures no longer block image publishing.
- Workflows trigger on `main` and `master`; `latest` is tagged on the repo's default branch.
- Clone falls back to the default branch if the requested one doesn't exist.
- The monitor follows the run for the commit that was pushed (`head_sha`), and a failed push now fails the task.
- Pods get a readiness probe and `PORT`; "Application Live" requires a real HTTP response through the tunnel; replicas default to 1.
- The crash-loop auto-fix call matches `analyze_build_failure`'s signature (it previously raised a swallowed `TypeError`).
- Private task fields (`_github_token`, `_workspace`) are no longer written to MongoDB; `analyze.py` imports `os`.

## Not done (needs a decision or a Minikube machine)

- `apply_auto_fix` still makes one commit per file (triggers racing runs).
- Mongo still overwrites per-repo history instead of appending attempts.
- The hardcoded GitHub IP / `curloptResolve` DNS workaround in `repository.py` is kept: it was added for a real DNS problem on the dev machines.
- `frontend/.env` stays tracked (public Vite variables used for the hosted build).
- Real GitHub push → GHCR → Minikube end-to-end is untested here (no Docker/Minikube on this machine).
