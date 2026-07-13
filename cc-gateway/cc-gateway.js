const http = require('http');
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ── 配置 ──────────────────────────────────────────────
const PORT = parseInt(process.env.CC_PORT || '48763', 10);
const TOKEN_FILE = path.join(__dirname, 'cc-token.txt');
const TOKEN = process.env.CC_TOKEN || readOrCreateToken();
const TIMEOUT_MS = parseInt(process.env.CC_TIMEOUT || '300000', 10);
const IS_WIN = process.platform === 'win32';

// ── 查找 Claude CLI ──────────────────────────────────
function findClaudePath() {
  // 1. 环境变量优先
  if (process.env.CC_CLAUDE_PATH) return process.env.CC_CLAUDE_PATH;

  // 2. 按优先级查找
  const commands = IS_WIN
    ? ['claude-haha.cmd', 'claude.cmd', 'claude-haha', 'claude']
    : ['claude', 'claude-haha'];

  for (const cmd of commands) {
    try {
      const result = execSync(
        IS_WIN ? `where ${cmd} 2>nul` : `which ${cmd} 2>/dev/null`,
        { encoding: 'utf8', timeout: 5000, shell: true }
      ).trim();
      const lines = result.split(/\r?\n/).filter(Boolean);
      if (lines.length > 0) return lines[0];
    } catch (_) {}
  }

  // 3. Windows 常见路径兜底
  if (IS_WIN) {
    const localBin = path.join(process.env.LOCALAPPDATA || '', '..', '..', '.local', 'bin', 'claude-haha.cmd');
    const roamingNpm = path.join(process.env.APPDATA || '', 'npm', 'claude.cmd');
    if (fs.existsSync(localBin)) return localBin;
    if (fs.existsSync(roamingNpm)) return roamingNpm;
  }

  return null;
}

const CLAUDE_PATH = findClaudePath();

// ── Token 管理 ────────────────────────────────────────
function readOrCreateToken() {
  if (fs.existsSync(TOKEN_FILE)) {
    return fs.readFileSync(TOKEN_FILE, 'utf8').trim();
  }
  const token = 'cc-' + crypto.randomBytes(32).toString('hex');
  fs.writeFileSync(TOKEN_FILE, token, 'utf8');
  console.log('  [new token generated]');
  return token;
}

// ── Bearer Token 验证 ─────────────────────────────────
function extractToken(req) {
  const auth = req.headers['authorization'];
  if (!auth) return null;
  const m = auth.match(/^Bearer\s+(.+)$/i);
  return m ? m[1] : null;
}

// ── CORS 头 ───────────────────────────────────────────
function setCORS(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Max-Age', '86400');
}

// ── JSON 响应 ─────────────────────────────────────────
function reply(res, status, body) {
  const json = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(json)
  });
  res.end(json);
}

// ── 解析请求体 ────────────────────────────────────────
function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
      catch { reject(new Error('Invalid JSON')); }
    });
    req.on('error', reject);
  });
}

// ── 解析 .cmd 文件，提取实际 exe 路径和参数 ──────────
function resolveCmdFile(cmdPath) {
  if (!IS_WIN || !cmdPath.endsWith('.cmd')) return { exe: cmdPath, args: [] };

  try {
    const content = fs.readFileSync(cmdPath, 'utf8');
    const locals = {}; // 解析 set 定义的本地变量

    for (const raw of content.split(/\r?\n/)) {
      // 匹配 set "VAR=value"
      const sm = raw.match(/^set\s+"(\w+)=(.+)"$/i);
      if (sm) locals[sm[1]] = sm[2];
    }

    // 找最后一行实际调用，替换 %VAR% 引用
    for (let i = content.split(/\r?\n/).length - 1; i >= 0; i--) {
      const line = content.split(/\r?\n/)[i].replace(/%\*/g, '').trim();
      const m = line.match(/"([^"]+)"\s+(.+)/);
      if (m) {
        const exe = m[1].replace(/%(\w+)%/g, (_, k) => locals[k] || process.env[k] || `%${k}%`);
        const args = (m[2].match(/(?:[^\s"]+|"[^"]*")+/g) || [])
          .map(a => {
            // 去掉外围引号，替掉 %VAR%
            const unquoted = a.replace(/^"(.*)"$/, '$1');
            return unquoted.replace(/%(\w+)%/g, (_, k) => locals[k] || process.env[k] || `%${k}%`);
          });
        return { exe, args };
      }
    }
  } catch (_) {}

  return { exe: cmdPath, args: [] };
}

// ── 调用 Claude CLI ───────────────────────────────────
function callClaude(prompt) {
  return new Promise((resolve, reject) => {
    if (!CLAUDE_PATH) {
      return reject(new Error('Claude CLI not found'));
    }

    // 解析 .cmd 文件 → 拿到真正的 exe + 固定参数
    const { exe, args } = resolveCmdFile(CLAUDE_PATH);
    const spawnArgs = [...args, '-p', prompt];

    // DEBUG: 打印实际 spawn 的命令，方便排查编码问题
    if (process.env.CC_DEBUG) {
      console.log('[spawn]', JSON.stringify({ exe, args: spawnArgs.map(a => a.length > 50 ? a.slice(0, 50) + '...' : a) }));
    }

    // 直接 spawn exe（非 cmd.exe），传 prompt 作为命令行参数。
    // spawn 通过 Windows CreateProcessW 传 Unicode 参数，无编码问题。
    const child = spawn(exe, spawnArgs, {
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
      timeout: TIMEOUT_MS
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', d => { stdout += d.toString(); });
    child.stderr.on('data', d => { stderr += d.toString(); });

    child.on('close', code => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(new Error(stderr.trim() || stdout.trim() || `CLI exited with code ${code}`));
      }
    });

    child.on('error', err => {
      reject(new Error(`Failed to spawn CLI: ${err.message}`));
    });
  });
}

// ── 路由 ──────────────────────────────────────────────
async function handleRequest(req, res) {
  setCORS(res);

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }

  const token = extractToken(req);

  // GET /health — 无需 token 也能查看状态
  if (req.method === 'GET' && req.url === '/health') {
    return reply(res, 200, {
      status: 'ok',
      claude: CLAUDE_PATH ? 'available' : 'missing',
      timestamp: new Date().toISOString()
    });
  }

  // 其余接口需要 Bearer Token
  if (!token || token !== TOKEN) {
    return reply(res, 401, { error: 'Unauthorized' });
  }

  // POST /api/chat
  if (req.method === 'POST' && req.url === '/api/chat') {
    try {
      const body = await readBody(req);
      if (!body.prompt || typeof body.prompt !== 'string') {
        return reply(res, 400, { error: 'Missing or invalid "prompt" field' });
      }
      const response = await callClaude(body.prompt);
      reply(res, 200, { response });
    } catch (err) {
      reply(res, 500, { error: err.message });
    }
    return;
  }

  reply(res, 404, { error: 'Not found' });
}

// ── 启动 ──────────────────────────────────────────────
const server = http.createServer(handleRequest);

server.listen(PORT, '127.0.0.1', () => {
  console.log('');
  console.log('═══════════════════════════════════════════');
  console.log('  Claude Code HTTP Gateway');
  console.log('═══════════════════════════════════════════');
  console.log(`  Port:    ${PORT}`);
  console.log(`  Token:   ${TOKEN.substring(0, 12)}...`);
  console.log(`  Claude:  ${CLAUDE_PATH ? 'available' : 'MISSING'}`);
  if (CLAUDE_PATH) console.log(`  Path:    ${CLAUDE_PATH}`);
  console.log(`  URL:     http://127.0.0.1:${PORT}`);
  console.log('═══════════════════════════════════════════');
  console.log('');
  console.log('Ready. Press Ctrl+C to stop.');
});
