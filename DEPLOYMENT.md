# Andile Deployment Configuration

## Free Cloud Providers (No Cost)

### 1. Cloudflare Workers (Recommended)
- **Cost**: Free (100k requests/day)
- **Limit**: No CPU time limit, but worker must complete quickly
- **Deploy**: `wrangler deploy`
- **File**: `cloudflare_worker.js`

### 2. Railway
- **Cost**: 500 hours free/month
- **Deploy**: `railway up`
- **File**: `railway.json`

### 3. Fly.io
- **Cost**: 3 VMs free
- **Deploy**: `fly deploy`
- **File**: `fly.toml`

### 4. Render
- **Cost**: Free web service (sleeps after 15 min inactivity)
- **Deploy**: Connect GitHub repo
- **File**: `render.yaml`

### 5. Oracle Cloud (Always Free)
- **Cost**: 2 VMs, always free
- **Deploy**: OCI CLI or console
- **Best for**: 24/7 operation

---

## Quick Deploy Commands

```bash
# Option 1: Cloudflare Workers (Easiest)
npm install -g wrangler
wrangler login
wrangler deploy

# Option 2: Railway
npm install -g @railway/cli
railway login
railway up

# Option 3: Fly.io
curl -L https://fly.io/install.sh | sh
fly auth login
fly deploy
```

---

## Environment Variables

Set these in your cloud provider:

```
OLLAMA_HOST=http://localhost:11434
ANDILE_LOCATION=cloud
ANDILE_NAME=Andile Sizophila Mchunu
ANDILE_MONIKER=Skywalkingzulu
```

---

## For Full Andile (with LLM)

The Cloudflare worker above is lightweight. For full 120B model:

1. **Use Ollama API** - Set OLLAMA_HOST to external service
2. **Use OpenAI/Claude fallback** - Add API key
3. **Use local model** - Run Ollama on a free VM (Oracle Cloud)

---

## Recommended Setup for $0/24hr

1. **Main Instance**: Oracle Cloud (2 free VMs) - runs full Andile
2. **Backup/Lightweight**: Cloudflare Workers - health checks, API
3. **State Sync**: Use GitHub Gist or KV store

This gives you redundancy and 24/7 operation.
