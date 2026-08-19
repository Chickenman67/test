# Free Vision (Image→Text) for a Text-Only Model — Research Note

**Question:** Give a text-only chat model (OpenCode running `omniroute/OpenCODE FREE`) the ability to "see" images the user pastes in, at **$0 cost** — i.e. a free backend that reads an image and returns a text description the text model can then use to reproduce it.

**Context:** The user's earlier attempt at image *generation* via the Gemini API failed because generation is paywalled there. But vision (image *input / understanding*) is a different, much more permissive feature — see Section 1.

**Key finding up front:** OpenCode **already natively accepts images** — official docs: *"Drag and drop images into the terminal to add them to the prompt. OpenCode can scan any images you give it and add them to the prompt."* So the image is already attached to the message; the **only blocker is the model chosen for that turn**. This makes the fix a **config change**, not a custom build. Source: https://opencode.ai/docs/

**Method:** Claims below were checked against primary/official sources (provider pricing pages, rate-limit docs, GitHub, model libraries). A source URL is placed next to each number/claim. Last verified **2026-08-18**; free tiers and rate limits change often, so re-check the linked page before relying on a limit. Claims marked **UNVERIFIED** could not be confirmed from a primary source.

---

## TL;DR — what you should actually do

1. **Best (zero install, genuinely free, largest limits):** Add **Google Gemini API on the Free tier** as the model for image turns. Image *understanding* input is **"free of charge"** on the free tier for the flash/flash-lite line (`gemini-3.5-flash-lite`, `gemini-2.5-flash`, `gemini-3.6-flash`) — with no spend cap and multi-million-token/day request quotas. It's free because you're doing vision/*understanding*, not *generation*. Just change the agent (or a sub-agent) model to a Gemini flash model in OpenCode's config; the pasted image passes straight through.
2. **Runner-up (no card needed, OpenAI-compatible):** **Groq Free plan, `qwen/qwen3.6-27b`** — a hosted 27B vision model, vision + JSON + tool use, with a first-party OpenCode integration. Free-plan limits: **30 RPM / 1K RPD / 8K TPM / 200K TPD**, **20 MB** max image, **5 images** per request. No credit card required to create a key.
3. **Best for private/unlimited/local (no ongoing cost, needs a GPU):** **Ollama `qwen3.6:27b`** (~17 GB, 256K context, vision) — fully local and unlimited, with an official `ollama launch opencode --model qwen3.6` integration so OpenCode can use it directly. Cost is just a one-time download + ~16–17 GB VRAM (or smaller/quantized models for ~8–12 GB).

---

## Section 1 — Free cloud vision APIs (free / free-tier)

| Provider | Vision model | Status | Limits (exact, current) | Citation |
|---|---|---|---|---|
| **Google Gemini API** | `gemini-3.5-flash-lite`, `gemini-2.5-flash`, `gemini-3.6-flash`, `gemini-3.7-flash` (all multimodal: image+text) | **free-tier** | Input & output **"Free of charge"** on the Standard free tier; per-model free-tier RPM/TPM/RPD are dynamic and only shown in Google AI Studio. Free tier spend limit = **N/A**. Exact free RPM values **UNVERIFIED** (Google only exposes them in AI Studio). | https://ai.google.dev/gemini-api/docs/pricing, https://ai.google.dev/gemini-api/docs/rate-limits |
| **Groq** | `qwen/qwen3.6-27b` (27B, vision, thinking, tool use, JSON mode) | **free-tier** | Free plan: **30 RPM / 1K RPD / 8K TPM / 200K TPD**; **20 MB** max image, **5 images** per request. ⚠️ Groq's models page lists a paid price ($0.60 in / $3.00 out per 1M) and Developer-plan limits; whether Free-plan usage is actually $0 vs metered is **UNVERIFIED** — confirm on your console/limits page. | https://console.groq.com/docs/rate-limits, https://console.groq.com/docs/models |
| **Hugging Face Inference Providers** | 200+ hosted models incl. vision | **free-tier (tiny)** | Free users get **$0.10 / month** of credits (PRO $2.00). Billing is compute-time × GPU $/sec (e.g. $0.00012/s). $0.10 ≈ only a handful of cheap vision calls — fine to test, not a real free tier. | https://huggingface.co/docs/inference-providers/en/pricing |

**Direct answers:**
- **Gemini free tier + vision? YES.** Image *understanding* (input) is "free of charge" on the free tier for the flash/flash-lite line. The earlier paywall was for image **generation**, a separate paid-only feature — **not** for image input. Above the free tier, input is explicitly priced for "text / image / video / audio," confirming image is a standard billable-but-free-on-free-tier modality.
- **Groq free vision? YES** — `qwen/qwen3.6-27b` appears in the Free Plan rate-limit table, so it's reachable on a free key (see UNVERIFIED nuance above).

---

## Section 2 — Free local vision (unlimited, private; cost is a GPU)

| Option | Status | Requirement | Citation |
|---|---|---|---|
| **Ollama `qwen3.6:27b`** | **free** | ~**17 GB** (27B) download; 256K ctx; vision. First-party OpenCode integration: `ollama launch opencode --model qwen3.6` | https://ollama.com/library/qwen3.6 |
| **Ollama other vision models** | **free** | Ollama's "Vision" filter now lists e.g. `gemma4`, `kimi-k3`, `nemotron3`, `minimax-m3`; older small options (`llava`, `llama3.2-vision`, `gemma3`, and smaller `qwen3.6` quants) run on ~8–16 GB VRAM depending on size/quantization | https://ollama.com/models |
| **Python `transformers` pipeline (local)** | **free** | Runs any open vision model (e.g. Qwen2.5-VL) on GPU; same VRAM trade-offs as Ollama | https://huggingface.co/docs |

Local = never monetized / unlimited, but requires hardware + a one-time model download. On Windows you may need WSL for GPU acceleration.

---

## Section 3 — Routing / architecture (how to wire it into a text-only harness)

- **OpenCode handles images natively** — so the pasted image is already in the prompt; pick a vision-capable model and it works. Source: https://opencode.ai/docs/
- **Two wiring options:**
  1. **Switch the model** for image turns to Gemini free tier / Groq free / local Ollama. Simplest — pure config.
  2. **Keep `omniroute/OpenCODE FREE` as the main agent** but route image-bearing turns to a vision-capable **sub-agent**, OR use a small script / MCP tool that calls a free vision endpoint (Groq base64 or Gemini) on the attached image and pastes the returned description as text the text-only model reads. Fully scriptable — Groq's vision docs show base64 `data:image/...` usage.
- **Groq↔OpenCode is first-party:** official page documents `/connect` → Groq → API key; "OpenCode supports all models available through Groq's API." Source: https://console.groq.com/docs/coding-with-groq/opencode
- **Ollama↔OpenCode is first-party:** `ollama launch opencode --model qwen3.6`. Source: https://ollama.com/library/qwen3.6

---

## Section 4 — Non-LLM OCR (flag — NOT visual understanding)

- **Tesseract OCR** — free, local, unlimited, but extracts **only text that appears in images** (screenshots/forms). Cannot describe a photo, UI layout, or diagram. Use only if images are always text-containing screenshots; otherwise it won't satisfy "describe and reproduce the image." Source: https://github.com/tesseract-ocr/tesseract

---

## Deal-breakers (looks free, isn't / has gotchas)

| Option | Reality |
|---|---|
| **Gemini "vision, free" trap** | Understanding is free; image **generation** (e.g. Nano Banana) is **still paid-only** — that's the paywall the user hit before. Don't confuse the two modalities. |
| **Hugging Face $0.10/month** | Effectively a demo credit (~a handful of calls). Not a real free tier for sustained vision. |
| **Groq free vision** | Reachable on the Free plan at 30 RPM/1K RPD, but Groq meters `qwen3.6-27b` on paid plans — confirm Free-plan usage is $0 in your console (UNVERIFIED). |
| **Ollama** | Free & unlimited but needs ~16–17 GB VRAM for the 27B vision model (smaller/quant ⇢ ~8–12 GB) plus a large download; not viable without a local GPU. |

---

## Bottom line

**Switch to Gemini free-tier flash for image turns (or Groq free / local Ollama) — no code, no cost.** OpenCode already attaches pasted images to the prompt; the only thing standing between a text-only model and "seeing" the image is choosing a vision-capable model for that turn.