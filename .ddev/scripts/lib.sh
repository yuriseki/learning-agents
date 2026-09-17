# Shared definitions for the learning-agents DDEV commands. Sourced, not executed.

PROJECT_ROOT=/var/www/html
PYTHON_VERSION=3.12

# Always the system uv from web-build/Dockerfile.uv. crewai installs its own `uv` into the
# shared venv, which is on PATH in interactive shells; `uv venv --clear` would then run the
# venv's copy and delete it out from under the very next command.
UV=/usr/local/bin/uv

# Container venvs live under .ddev/ because the host venvs (.venv, src/ag2_agents/.venv)
# point at host interpreter paths and can't be reused inside the container.
VENV_MAIN="$PROJECT_ROOT/.ddev/.venv"
VENV_AG2="$PROJECT_ROOT/.ddev/.venv-ag2"

# uv keeps its Python builds and package cache in DDEV's global cache volume so
# they survive `ddev restart` and `ddev delete`. Fall back to uv's defaults if
# the volume isn't writable for some reason.
for _var in UV_PYTHON_INSTALL_DIR UV_CACHE_DIR; do
  _dir="${!_var:-}"
  if [[ -n "$_dir" ]] && ! mkdir -p "$_dir" 2>/dev/null; then
    echo "warning: $_dir not writable, falling back to uv default for $_var" >&2
    unset "$_var"
  fi
done
unset _var _dir

# List framework packages: every src/<pkg>/ with a main.py.
frameworks() {
  local f
  for f in "$PROJECT_ROOT"/src/*/main.py; do
    basename "$(dirname "$f")"
  done
}

# Map "strands" or "strands_agents" -> strands_agents. Fails with a list of options.
resolve_framework() {
  local name="$1" candidate
  for candidate in "$name" "${name}_agents"; do
    if [[ -f "$PROJECT_ROOT/src/$candidate/main.py" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  echo "Unknown framework '$name'. Available: $(frameworks | tr '\n' ' ')" >&2
  return 1
}

# AG2 needs its own venv (dependency conflicts); everything else shares one.
venv_for() {
  if [[ "$1" == ag2_agents ]]; then
    echo "$VENV_AG2"
  else
    echo "$VENV_MAIN"
  fi
}
