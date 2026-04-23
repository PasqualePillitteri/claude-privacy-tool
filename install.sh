#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/.claude/privacy-tool"
VENV_DIR="${ROOT}/venv"
SCRIPTS_DIR="${ROOT}/scripts"
SETTINGS_FILE="${HOME}/.claude/settings.json"
REPO_URL="https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
say() { printf "${BLUE}[Claude Privacy Tool]${NC} %s\n" "$1"; }
ok()  { printf "${GREEN}[OK]${NC} %s\n" "$1"; }
warn(){ printf "${YELLOW}[!!]${NC} %s\n" "$1"; }
err() { printf "${RED}[ERR]${NC} %s\n" "$1"; exit 1; }

say "Checking prerequisites"
command -v python3 >/dev/null 2>&1 || err "Python 3.10+ required."
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
ok "Python ${PY_VER}"

command -v claude >/dev/null 2>&1 || warn "Claude Code CLI not found. Install from https://claude.ai/code"

say "Creating ${ROOT}"
mkdir -p "${ROOT}/mappings" "${SCRIPTS_DIR}"
chmod 700 "${ROOT}/mappings"

say "Creating isolated Python virtualenv"
python3 -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip >/dev/null

say "Installing transformers + torch (CPU) + safetensors + mcp"
pip install --quiet transformers torch safetensors "mcp>=1.0"

say "Downloading OpenAI Privacy Filter (~3 GB, one-time)"
python3 - <<'PY'
from transformers import AutoModelForTokenClassification, AutoTokenizer
AutoTokenizer.from_pretrained("openai/privacy-filter")
AutoModelForTokenClassification.from_pretrained("openai/privacy-filter")
print("Model ready")
PY

if [[ -f "./hook.py" && -f "./postresponse_hook.py" && -f "./mcp_server.py" ]]; then
    cp ./hook.py ./postresponse_hook.py ./mcp_server.py "${SCRIPTS_DIR}/"
else
    curl -fsSL "${REPO_URL}/hook.py" -o "${SCRIPTS_DIR}/hook.py"
    curl -fsSL "${REPO_URL}/postresponse_hook.py" -o "${SCRIPTS_DIR}/postresponse_hook.py"
    curl -fsSL "${REPO_URL}/mcp_server.py" -o "${SCRIPTS_DIR}/mcp_server.py"
fi
chmod +x "${SCRIPTS_DIR}/hook.py" "${SCRIPTS_DIR}/postresponse_hook.py" "${SCRIPTS_DIR}/mcp_server.py"
ok "Scripts installed in ${SCRIPTS_DIR}"

cat > "${SCRIPTS_DIR}/run-hook.sh" <<EOF
#!/usr/bin/env bash
source "${VENV_DIR}/bin/activate"
exec python "${SCRIPTS_DIR}/hook.py" "\$@"
EOF
cat > "${SCRIPTS_DIR}/run-postresponse.sh" <<EOF
#!/usr/bin/env bash
source "${VENV_DIR}/bin/activate"
exec python "${SCRIPTS_DIR}/postresponse_hook.py" "\$@"
EOF
cat > "${SCRIPTS_DIR}/run-mcp.sh" <<EOF
#!/usr/bin/env bash
source "${VENV_DIR}/bin/activate"
exec python "${SCRIPTS_DIR}/mcp_server.py" "\$@"
EOF
chmod +x "${SCRIPTS_DIR}/run-hook.sh" "${SCRIPTS_DIR}/run-postresponse.sh" "${SCRIPTS_DIR}/run-mcp.sh"

say "Registering Claude Code hooks in ${SETTINGS_FILE}"
mkdir -p "$(dirname "${SETTINGS_FILE}")"
[[ -f "${SETTINGS_FILE}" ]] || echo '{}' > "${SETTINGS_FILE}"
python3 - "${SETTINGS_FILE}" "${SCRIPTS_DIR}" <<'PY'
import json, sys
from pathlib import Path
settings_path = Path(sys.argv[1])
scripts_dir = sys.argv[2]
settings = {}
if settings_path.stat().st_size > 0:
    try: settings = json.loads(settings_path.read_text())
    except Exception: settings = {}
hooks = settings.setdefault("hooks", {})
def ensure(event_name, cmd):
    group = hooks.setdefault(event_name, [])
    for item in group:
        if any(h.get("command") == cmd for h in item.get("hooks", [])): return
    group.append({"matcher": "*", "hooks": [{"type":"command","command":cmd}]})
ensure("UserPromptSubmit", f"{scripts_dir}/run-hook.sh")
ensure("Stop", f"{scripts_dir}/run-postresponse.sh")
settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False))
print("settings.json updated")
PY
ok "Claude Code hooks registered"

say "Registering MCP server in Claude Desktop config"
if [[ "$(uname -s)" == "Darwin" ]]; then
    DESKTOP_CONFIG="${HOME}/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$(uname -s)" == "Linux" ]]; then
    DESKTOP_CONFIG="${HOME}/.config/Claude/claude_desktop_config.json"
else
    DESKTOP_CONFIG="${APPDATA:-${HOME}/AppData/Roaming}/Claude/claude_desktop_config.json"
fi
mkdir -p "$(dirname "${DESKTOP_CONFIG}")"
[[ -f "${DESKTOP_CONFIG}" ]] || echo '{}' > "${DESKTOP_CONFIG}"
python3 - "${DESKTOP_CONFIG}" "${SCRIPTS_DIR}/run-mcp.sh" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); cmd = sys.argv[2]
try: cfg = json.loads(p.read_text() or "{}")
except Exception: cfg = {}
cfg.setdefault("mcpServers", {})["claude-privacy-tool"] = {"command": cmd}
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
print(f"MCP server registered in {p}")
PY
ok "Claude Desktop MCP server registered"
warn "Restart Claude Desktop to load the claude-privacy-tool MCP server"

cat > "${ROOT}/uninstall.sh" <<'BASH'
#!/usr/bin/env bash
SETTINGS_FILE="${HOME}/.claude/settings.json"
ROOT="${HOME}/.claude/privacy-tool"
python3 - "${SETTINGS_FILE}" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists(): sys.exit(0)
s = json.loads(p.read_text() or "{}")
for event in list(s.get("hooks", {})):
    s["hooks"][event] = [g for g in s["hooks"][event]
        if not any("privacy-tool" in h.get("command","") for h in g.get("hooks", []))]
    if not s["hooks"][event]: del s["hooks"][event]
p.write_text(json.dumps(s, indent=2, ensure_ascii=False))
PY
if [[ "$(uname -s)" == "Darwin" ]]; then
    DESKTOP_CONFIG="${HOME}/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$(uname -s)" == "Linux" ]]; then
    DESKTOP_CONFIG="${HOME}/.config/Claude/claude_desktop_config.json"
else
    DESKTOP_CONFIG="${APPDATA:-${HOME}/AppData/Roaming}/Claude/claude_desktop_config.json"
fi
if [[ -f "${DESKTOP_CONFIG}" ]]; then
    python3 - "${DESKTOP_CONFIG}" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
try: cfg = json.loads(p.read_text() or "{}")
except Exception: sys.exit(0)
if "mcpServers" in cfg and "claude-privacy-tool" in cfg["mcpServers"]:
    del cfg["mcpServers"]["claude-privacy-tool"]
    if not cfg["mcpServers"]: del cfg["mcpServers"]
    p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print("MCP server removed from Claude Desktop")
PY
fi
read -p "Delete ${ROOT} including model cache and mappings? (y/N) " yn
case "$yn" in
    [yY]*) rm -rf "${ROOT}"; echo "Removed." ;;
    *) echo "Kept data. Hooks and MCP server disabled." ;;
esac
BASH
chmod +x "${ROOT}/uninstall.sh"

say "Running smoke test"
TEST_OUT=$(echo '{"prompt":"Il cliente Mario Rossi (mario@test.com) ha firmato il 12/03/2026","session_id":"test"}' \
    | "${SCRIPTS_DIR}/run-hook.sh")
if echo "$TEST_OUT" | grep -q "PRIVATE_"; then
    ok "Smoke test passed"
else
    warn "Smoke test returned: $TEST_OUT"
fi

printf "\n${GREEN}Claude Privacy Tool installed.${NC}\n\n"
printf "${BLUE}Claude Code CLI${NC}    hooks active, just run 'claude'\n"
printf "${BLUE}Claude Desktop${NC}     restart the app to load the MCP server\n\n"
printf "Logs:      ${ROOT}/hook.log\n"
printf "MCP log:   ${ROOT}/mcp.log\n"
printf "Mappings:  ${ROOT}/mappings/ (0600)\n"
printf "Uninstall: ${ROOT}/uninstall.sh\n"
