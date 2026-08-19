# Free, Scriptable, Good-Quality Image Generation — Research Note

**Question:** Generate images programmatically at $0 cost, with generous limits and good-to-great quality.

**Context:** The user's earlier attempt at Google's Gemini image-generation *API* failed because image generation is paywalled there — free-tier API keys get `limit: 0` for the image model. Every option below is flagged **free / free-tier / paid** so you can tell them apart instantly.

**Method:** Claims below were checked against primary/official sources (provider docs, GitHub repos, model cards, Google support pages). A source URL is placed next to each number/claim. This was last verified **2026-08-17**; free tiers and rate limits change often, so re-check the linked page before relying on a limit.

---

## TL;DR — what you should actually do

1. **Read the Deal-Breakers section first.** Gemini image gen, OpenAI DALL‑E, Midjourney, Stability's paid API, Replicate, fal.ai, and RunPod all **require billing** for anything meaningful. Don't waste time on them.
2. **If you have a relatively modern GPU (≈6–8 GB VRAM) run it locally — it is the only truly free + unlimited + high-quality option.** Use **Diffusers** (Python) with **FLUX.1 schnell** (Apache-2.0, open) or **SDXL** (Open RAIL++‑M), or a GUI like **ComfyUI** (self-hosted is free; runs on your machine, no ongoing cost). Script snippet below.
3. **If you have no local GPU and want a zero-cost cloud API today**, **Pollinations' anonymous `image.pollinations.ai` endpoint is verified still free and key-less** (I fetched a real image from it while writing this — HTTP 200, JPEG). No billing card needed. Quality is high (FLUX/gptimage/zimage backends). Heavy/automated volume may be throttled.
4. **If you want monthly *hosted* free GPU compute to run FLUX/SDXL in the cloud**, **Modal's Starter plan gives every account $30/month of free credits** (plenty for hundreds of generations). Requires a free account, no card needed.
5. **For battery of simple fixed images (a "stick man", icons, diagrams), don't use AI at all** — use Pillow/SVG/matplotlib (free, unlimited, deterministic). Flagged below as procedural, not neural.

---

## Section 1 — Deal-breakers (PAID — do not attempt for $0)

These look "free" but block real API use behind billing or have no free tier. Listed so you don't repeat the Gemini experience.

| Service | Status | Why it's not free |
| --- | --- | --- |
| **Google Gemini image generation (API)** | **Paid** | Image generation via the Gemini API is only available on a **paid** plan; free-tier keys get `limit: 0` for the image model. This is exactly what the user hit. Source: https://ai.google.dev/gemini-api/docs/pricing (JS-rendered; confirmed by the user's first-hand `limit: 0` result). |
| **OpenAI DALL-E / gpt-image** | **Paid** | Image APIs are billed per image; no free tier. https://platform.openai.com/docs/guides/images/pricing |
| **Midjourney** | **Paid** | Subscription-only, and no official scriptable API. https://docs.midjourney.com/ |
| **Stability AI paid API** (platform.stability.ai) | **Paid** | Standard image generation costs credits; signup historically included a small one-time free credit, but sustained use is pay-per-image. Docs: https://platform.stability.ai/docs (JS-rendered; verify current credit terms). |
| **Replicate** | **Paid** | Pay-as-you-go per prediction; **no free tier** for the API. https://replicate.com/pricing |
| **fal.ai** | **Paid** | Requires pre-purchased credits; no free API tier. https://fal.ai/pricing/ |
| **RunPod** | **Paid** | Pay-per-hour GPU; no free tier. https://runpod.io/pricing |
| **Hugging Face Inference (image models)** | **~Paid** | Free users get only **$0.10/month** of credits; image models run on paid GPU providers once credit is spent. $0.10 isn't enough for meaningful image work. https://huggingface.co/docs/inference-providers/en/pricing |
| **Comfy Cloud** | **Paid** | Cloud version is a **monthly subscription**; the *self-hosted local* version is free (see below). Docs explicitly list Cost: "Free" (local) vs "Monthly Subscription" (cloud). https://docs.comfy.org/get_started/ |

---

## Section 2 — Best: Local / self-hosted (truly free, unlimited, high quality)

Running the model on your own machine has **zero API cost and no rate limit** — your only cost is electricity and VRAM.

### 2.1 Diffusers (Hugging Face) — recommended for scripting

A Python library for running open diffusion models (SDXL, FLUX, SD3, etc.) locally in a few lines. Totally free.

- **Is it free?** Yes (`pip install`, open source). https://huggingface.co/docs/diffusers/index
- **Quality:** High (with SDXL or FLUX).
- **VRAM:** SDXL ~ needs ~6–8 GB VRAM; FLUX dev ~ 16–24 GB (use `schnell` or quantization/cpu-offload for less). Model cards provide `enable_model_cpu_offload()` for low-VRAM (https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0).
- **Script** (official usage from the SDXL model card):
  ```python
  pip install diffusers transformers accelerate
  from diffusers import DiffusionPipeline
  import torch
  pipe = DiffusionPipeline.from_pretrained(
      "stabilityai/stable-diffusion-xl-base-1.0",
      torch_dtype=torch.float16, use_safetensors=True
  ).to("cuda")
  img = pipe("a stick man waving, minimal line art").images[0]
  img.save("out.png")
  ```
  Source: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

### 2.2 ComfyUI — best GUI + solid programmatic API

Node-graph workflow tool; self-hosted (local) is free and can be scripted via its API and a Python client.

- **Is it free?** Yes locally; Comfy Cloud (the hosted version) is a subscription. https://docs.comfy.org/get_started/
- **Quality:** High.
- **API shape:** Runs a JSON workflow graph via HTTP; there is an official Cloud API and a local developer workflow API. Docs: https://docs.comfy.org/development/cloud/overview (hosted/API) and local install system requirements: https://docs.comfy.org/installation/system_requirements.
- **VRAM:** same model-dependent needs as above.

### 2.3 Stable Diffusion WebUI (AUTOMATIC1111) — easy local GUI + API

A mature local web UI for Stable Diffusion with a built-in REST API (`/sdapi/v1/txt2img`).

- **Is it free?** Yes — AGPL-3.0, free. https://github.com/AUTOMATIC1111/stable-diffusion-webui
- **Quality:** High for SD-family models; supports SDXL and many community checkpoints.
- **Script:** `POST http://127.0.0.1:7860/sdapi/v1/txt2img` with JSON `{"prompt": "a stick man", "steps": 20}` returns base64 images.
- **VRAM:** advertises 4 GB support (and reports of 2 GB). https://github.com/AUTOMATIC1111/stable-diffusion-webui

### 2.4 Model licensing — FLUX & SDXL in a nutshell

- **FLUX.1 schnell — Apache-2.0** (open, including commercial use). Weights + license: https://github.com/black-forest-labs/flux (table of open-weight models), license file: https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell
- **FLUX.1 dev / Kontext / Fill / etc.** — **Non-commercial** FLUX dev license. Free to use personally; commercial use needs a paid license. https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-dev
- **SDXL base** — **CreativeML Open RAIL++-M** (free weights, permissive for most uses incl. research/personal). https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- **SD3 Medium** — Stability AI Community License; free for non-commercial/under-$1M-revenue; requires a license above that. Verify in the model card: https://huggingface.co/stabilityai/stable-diffusion-3-medium

**Bottom line for local:** stick to **FLUX.1 schnell** (Apache-2.0, genuinely open) or **SDXL** (Open RAIL++‑M) so you have no license surprise.

---

## Section 3 — Free cloud APIs (no local GPU needed)

### 3.1 Pollinations — verified free, key-less, high quality ⭐

Pollinations is an open-source generative-AI platform that has long offered **anonymous, free, no-API-key image generation** via a simple GET URL.

- **Is it free?** **Yes for the classic endpoint — verified live.** While writing this I fetched
  `https://image.pollinations.ai/prompt/a%20simple%20red%20circle?nologo=true` and received **HTTP 200, `image/jpeg`** with **no API key**. Historically free and key-less for reasonable personal use (rate-limited / best-effort).
- **Quality:** High — backends include FLUX, gptimage, and others.
- **How to call from a script:**
  ```python
  import urllib.request
  url = "https://image.pollinations.ai/prompt/a%20stick%20man%20waving"
  urllib.request.urlretrieve(url, "stickman.jpg")
  ```
  ```
  curl "https://image.pollinations.ai/prompt/a%20stick%20man%20waving?width=1024&height=1024&seed=42" -o stickman.jpg
  ```
- **⚠️ Watch this:** The platform is migrating to a **unified `gen.pollinations.ai` API that uses an account + "Pollen" credits** ($1 ≈ 1 Pollen, pay-as-you-go) for key-authenticated usage. The key-less `image.pollinations.ai` GET route still works today but heavy/automated usage may be throttled, and the free policy could change. Sources: platform README + API docs:
  - https://github.com/pollinations/pollinations
  - https://gen.pollinations.ai/docs (and APIDOCS.md in the same repo)
  - A note on credits: the README says "Pollen credits — simple pay-as-you-go system ($1 ≈ 1 Pollen)". https://github.com/pollinations/pollinations

### 3.2 Modal — $30/month free compute (hosted, high quality)

Modal is a serverless GPU platform. The **Starter plan is $0/month and includes $30/month of free compute credits** — enough for hundreds of FLUX/SDXL generations.

- **Is it free?** **Free-tier (ongoing, monthly)** — Starter: "$0 + compute / month", "$30 / month free credits", no credit card / "Get started with $30 / month free credit". High-end GPUs billed per-second *only after* free credits exhaust. https://modal.com/pricing
- **Quality:** High — you run FLUX/SDXL/diffusers yourself.
- **How to call from a script:** write a Modal `@app.function(gpu="A100")` that calls `DiffusionPipeline`; Modal runs it and returns the image. Official example (diffusers finetune) is in their library: https://modal.com/docs; image-generation example: https://modal.com/docs/examples/diffusers_lora_finetune
- **Caveat:** Free credits recur monthly (not one-time), making this a genuine recurring free tier, but CPU/GPU concurrency on the Starter plan is limited ("100 containers + 10 GPU concurrency").

### 3.3 Google Colab — free GPUs, but throttled

Free tier grants access to Google-hosted VMs **including GPUs and TPUs**, usable to run diffusers/ComfyUI code in a notebook.

- **Is it free?** **Free-tier, but heavily restricted.** Google: "Colab is free of charge to use" and includes "access to computing resources, including GPUs and TPUs". BUT: resources "are not guaranteed and not unlimited"; free-tier runs cap at **~12 hours**; and users who abuse free GPUs for web-UI content generation get runtimes terminated. https://research.google.com/colaboratory/faq.html
- **Quality:** High (you run FLUX/SDXL yourself).
- **How to call from a script:** a notebook cell that runs the diffusers snippet above; download the PNG at the end.
- **Caveat:** Reliability is poor for heavy automated generation — Google explicitly terminates free-tier runtimes that drive web-UI-style generation. Fine for occasional batch runs, not a pipeline.

### 3.4 Stability — free demo (not a usable API for free)

- **Clipdrop SDXL** is a **free hosted SDXL** "demo/tool" (Stability's model card links to it: "Clipdrop provides free SDXL inference"). It's a UI, not a paywalled API — limited/watermarked and not scriptable in a headless way. https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- Stability also exposes a public **Availability API** that returns pre-generated images for known Object IDs without auth (designed for specific use cases, not for arbitrary prompts). Verify in their docs (JS-rendered): https://platform.stability.ai/docs
- Otherwise, stability's scriptable image generation is paid (see Deal-breakers).

### 3.5 Hugging Face Inference Providers — barely free for images

Free accounts get **$0.10/month** of Inference Providers credits (PRO $2/month). Image models are GPU-based and billed per-second on providers; $0.10 will cover only a handful of very small jobs, then it's pay-as-you-go. **Practically paid for images.** https://huggingface.co/docs/inference-providers/en/pricing

---

## Section 4 — Free, non-AI procedural generation (best for simple/fixed images)

For "a stick man", icons, logos, charts, and deterministic scenes, neural inference is overkill. These are free, unlimited, and scriptable — but **procedural, not AI** (no understanding of arbitrary prompts).

- **Pillow (PIL)** — draw shapes/text lines into a PNG. Free (BSD). `pip install Pillow`. https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
- **SVG + rasterization** — author `*.svg` by hand, rasterize with **resvg** (Rust) or **cairosvg** (Python). Free. https://github.com/RazrFalcon/resvg · https://cairosvg.org/
- **matplotlib** — programmatic charts/plots to PNG/PDF. Free. https://matplotlib.org/stable/api/pyplot_summary.html
- **Graphviz** — diagrams/graphs to PNG/SVG from a text spec. Free. https://graphviz.org/documentation/

---

## Section 5 — Model quality tiers (quick reference)

| Option | Free? | Quality | Scriptable? | One-liner |
| --- | --- | --- | --- | --- |
| Diffusers + FLUX schnell / SDXL (local) | Yes | **High** | Yes (Python) | `pipe(prompt).images[0]` |
| ComfyUI (local) | Yes | **High** | Yes (API/graph) | HTTP JSON workflow |
| Stable Diffusion WebUI (local) | Yes | High | Yes (REST) | `POST /sdapi/v1/txt2img` |
| Pollinations `image.pollinations.ai` | **Yes (verified)** | High | Yes (`GET /prompt/{text}`) | one `curl` |
| Modal Starter | **Free-tier ($30/mo)** | High | Yes (Python/@app) | diffusers on `@app.function` |
| Google Colab free | Free-tier (throttled) | High | Yes (notebook) | notebook cell |
| Stability paid API / Replicate / fal.ai / RunPod / Gemini img / DALL-E / Midjourney | **Paid** | High | Yes | ❌ avoid for $0 |
| Pillow / SVG / matplotlib | Yes | Medium (non-AI) | Yes | draw commands |

---

## Primary source index

- Diffusers: https://huggingface.co/docs/diffusers/index
- SDXL model card + Open RAIL++‑M license + usage snippet: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- FLUX open-weight models & licenses (schnell = Apache-2.0, dev = non-commercial): https://github.com/black-forest-labs/flux (licenses: `model_licenses/LICENSE-FLUX1-schnell`, `model_licenses/LICENSE-FLUX1-dev`)
- ComfyUI (local free vs cloud subscription): https://docs.comfy.org/get_started/
- Stable Diffusion WebUI (AGPL-3.0, free, API): https://github.com/AUTOMATIC1111/stable-diffusion-webui
- Pollinations platform + credits + API: https://github.com/pollinations/pollinations · https://gen.pollinations.ai/docs · https://pollinations.ai/
- Modal pricing (Starter $30/mo free credits): https://modal.com/pricing
- Google Colab FAQ (free GPUs, throttling, 12h cap): https://research.google.com/colaboratory/faq.html
- Hugging Face Inference Providers pricing ($0.10/mo free): https://huggingface.co/docs/inference-providers/en/pricing
- Replicate pricing (no free tier): https://replicate.com/pricing
- RunPod pricing (no free tier): https://runpod.io/pricing

*Re-verify limits before shipping — free tiers drift.*