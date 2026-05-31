# HuggingMes - 專為 Hugging Face Spaces 設計的 Hermes AI Agent 網關

🪽 **HuggingMes** 是一個在 Hugging Face Spaces 上運行的 [Nous Research Hermes Agent](https://github.com/NousResearch/hermes-agent) 網關。它為你提供了一個 24/7 全天候在線的個人 AI 助理，配備管理儀表板、持久化的 HF Dataset 備份功能，以及自動修復連線問題的機制。

---

## ✨ 核心功能

- 🧠 **Hermes 核心**：執行 Hermes Agent，支援多輪對話、工具呼叫、記憶管理與 Agent 工作流。
- 🔐 **安全防護**：預設使用 `GATEWAY_TOKEN` 保護儀表板與 API。
- 🌐 **內建連線優化**：支援 Cloudflare Worker 代理，解決 Telegram 或其他 API 的出站流量封鎖問題。
- 📊 **管理儀表板**：在 `/` 路徑提供實時狀態監控（運行時間、同步健康度、模型資訊等）。
- 💾 **持久化備份**：自動將對話、配置與會話資料同步至私人的 HF Dataset。
- ⏰ **保持在線 (Keep-Alive)**：支援透過 Cloudflare Worker 定時觸發，防止免費版 Space 進入休眠。
- 💻 **內建終端機**：提供 JupyterLab 終端機 (`/terminal/`)，方便直接進行 Shell 操作與除錯。
- 🔄 **自癒能力**：自動監控並重啟意外結束的關鍵服務。
- 📦 **軟體包持久化**：在終端機安裝的 `apt`/`pip`/`npm` 軟體包會被記錄並在重啟時自動重新安裝。

---

## 🚀 快速開始 (Hugging Face Spaces 部署)

### 第一步：複製此 Space
前往專案頁面並點擊 **"Duplicate this Space"**。

### 第二步：新增 Secrets
在 Space 的 **Settings → Variables and secrets** 中，新增以下 **Secrets**：

| 名稱 | 說明 |
| :--- | :--- |
| `LLM_API_KEY` | 您的 LLM 供應商 API Key (如 OpenRouter, OpenAI, Anthropic 等)。 |
| `LLM_MODEL` | 模型 ID，例如 `openrouter/anthropic/claude-3.5-sonnet` 或 `openai/gpt-4o`。 |
| `GATEWAY_TOKEN` | 用於保護儀表板與終端機的強大金鑰 (建議產生 32 位元隨機字串)。 |
| `HF_TOKEN` | 具備 **Write** 權限的 Hugging Face Token (用於資料備份)。 |
| `TELEGRAM_BOT_TOKEN` | (選填) Telegram Bot Token。 |
| `TELEGRAM_ALLOWED_USERS` | (選填) 允許使用機器人的 Telegram 用戶 ID (逗號分隔)。 |
| `CLOUDFLARE_WORKERS_TOKEN`| (選填) 用於自動配置 Cloudflare 代理與 Keep-alive。 |

### 第三步：啟動與使用
完成設定後，Space 會自動構建並啟動。您可以存取儀表板並點擊 **"Open Hermes UI"** 開始與您的 AI 助理對話。

---

## 💾 備份與持久化
設定 `HF_TOKEN` 後，HuggingMes 會預設每 600 秒將 `workspace` 資料同步至名為 `huggingmes-backup` 的私人 Dataset 中。

---

## 💻 本地開發
如果您想在本地環境執行，請確保已安裝 Docker：

```bash
docker compose up --build
# 儀表板：http://localhost:7861
# Hermes 應用：http://localhost:7861/app/
```

---

## 🏗️ 系統架構
- **儀表板 (`/`)**：管理與監控中心。
- **Hermes App (`/app/`)**：受保護的 Agent 互動介面。
- **終端機 (`/terminal/`)**：JupyterLab 終端機。
- **同步引擎**：背景執行的 Python 任務，負責資料備份。

---
*由 [@somratpro](https://github.com/somratpro) 開發，由 Jules 提供繁體中文支持 ❤️*
