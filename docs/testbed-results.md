# Deployment testbed results

The testbed (`testbed/apps/*`, 16 tiny apps) is run two ways:

- **Locally, detection + generation only**: `cd backend; venv/Scripts/python -m pytest tests -q`
- **In CI, full ladder** (detect, Dockerfile, `docker build`, `docker run`, HTTP 2xx-3xx): the `Deployment testbed` workflow (`.github/workflows/testbed.yml`), run from the Actions tab. Its job summary has the table. Set `set_port_env=1` to pass `PORT=<EXPOSE>` as the deployer now does.

## Detection + generation (local)

| Run | Passing | Failures |
|---|---|---|
| Baseline (before fixes) | 12 / 16 | ruby-sinatra, rust-std, static-html (no `EXPOSE` / no template), trap-node-stray-files (detected as Ruby because of one `.rb` file) |
| After fixes | 16 / 16 | none |

## End-to-end on a real cluster (theakashainapur, Minikube, 2026-10-26)

Each app lives in a public repo `theakashainapur/tb-<app>`. `testbed/e2e_run.py` drove the tool's own `analyze_repo_task`: clone, analyze, generate, push, wait for the GitHub Actions run of the pushed commit, image to GHCR, pull into Minikube, pod Running, real HTTP request through the tunnel. Only Clerk, MongoDB and the AI fallback were stubbed.

| App | Language | Tool status | CI green | HTTP | Minutes |
|---|---|---|---|---|---|
| go-http | Go | success | yes | 200 | 10 |
| java-gradle | Java | success | yes | 200 | 11 |
| java-maven | Java | success | yes | 200 | 10 |
| node-express | JavaScript/TypeScript | success | yes | 200 | 3 |
| node-nextjs | JavaScript/TypeScript | success | yes | 200 | 25 |
| node-port-env | JavaScript/TypeScript | success | yes | 200 | 4 |
| node-vite-react | JavaScript/TypeScript | success | yes | 200 | 9 |
| php-plain | PHP | success | yes | 200 | 8 |
| python-django | Python | success | yes | 200 | 23 |
| python-fastapi | Python | success | yes | 200 | 8 |
| python-flask | Python | success | yes | 200 | 12 |
| python-stdlib | Python | success | yes | 200 | 25 |
| ruby-sinatra | Ruby | success | yes | 200 | 27 |
| rust-std | Rust | success | yes | 200 | 27 |
| static-html | HTML/Static | success | yes | 200 | 3 |
| trap-node-stray-files | JavaScript/TypeScript | success | yes | 200 | 9 |

**16 / 16 fully deployed and answering HTTP.**

Notes on how to read this:
- Every app got one attempt with no AI auto-fix. `python-flask` was the first app run and needed several attempts only because that run exposed tool bugs, now fixed; the other apps ran afterwards with those fixes in place.
- `java-gradle` failed its first CI run (the Java workflow was Maven-only: `cache: maven` needs a `pom.xml`). After the fix and a clean re-test it deployed; the CI list in its result file shows the failed and the green run.
- Some runs were delayed (not failed) by GitHub's "too many repositories" limit on a new account; the runner now backs off and creates repos one at a time.
- One image pull from GHCR took 11 minutes on this network; deploy time is dominated by pull speed.
- Results per app: `testbed/e2e-results/<app>.json`.

## CI ladder (build, run, HTTP, no cluster)

The `Deployment testbed` workflow (`.github/workflows/testbed.yml`) does the same detect/build/run/HTTP ladder on GitHub's runners without a cluster. Not run yet; it needs this branch pushed to the tool's own repo.

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
- The monitor retries transient GitHub poll failures and fails the task if GitHub stays unreachable (a single timeout used to leave the task hanging).
- The Java workflow matches the build tool (Maven or Gradle).
- Private task fields (`_github_token`, `_workspace`) are no longer written to MongoDB; `analyze.py` imports `os`.

## Not done (needs a decision or a Minikube machine)

- `apply_auto_fix` still makes one commit per file (triggers racing runs).
- Mongo still overwrites per-repo history instead of appending attempts.
- The DNS workaround in `repository.py` is kept but now applies only when the system resolver fails (it broke `git clone` on a healthy network).
- `frontend/.env` stays tracked (public Vite variables used for the hosted build).
- The end-to-end table above covers one run per app on one machine; flakiness and network variance over repeated runs are not measured.
