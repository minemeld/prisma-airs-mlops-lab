# Serving Architecture — Deep Dive

> This is supplemental depth for `/lab:explore`. The main flow teaches: why self-host, decoupled architecture, vLLM/endpoints/chat templates at a high level, and the request flow. This guide goes deeper on the implementation details.

## Additional Topics

### rawPredict and Model Naming
Vertex AI's `rawPredict` API forwards requests directly to the vLLM container without any interpretation — unlike the `predict` API which expects specific input/output schemas. This gives you full control over the request format but means you need to match exactly what vLLM expects.

The Vertex AI vLLM launcher overrides the served model name to `"openapi"` regardless of what your model is actually called. Every request must use `model: "openapi"` or it will be rejected. This is a Vertex AI-specific quirk — vanilla vLLM lets you set whatever model name you want.

**Explore:** Read `src/airs_mlops_lab/serving/inference_client.py` and find the rawPredict URL construction and the `model: "openapi"` field. What happens if you use the actual model name instead?

### Chat Template Construction
The Qwen2 model uses a specific chat format with `<|im_start|>` and `<|im_end|>` tokens. The app must construct this manually because Vertex AI's vLLM build only exposes `/v1/completions` (not `/v1/chat/completions`).

**Explore:** Read `src/airs_mlops_lab/serving/inference_client.py` lines 91-98. Trace how the chat history is formatted into a single prompt string with role markers.

**Why this matters:** If you use the wrong template format, the model will produce garbage output even though the endpoint is healthy. This is a common debugging trap — the model works but the output makes no sense because the prompt format is wrong.

### Why /v1/completions Only
Vertex AI's pre-built vLLM container exposes the OpenAI-compatible completions API but NOT the chat completions API. This is a Vertex AI constraint, not a vLLM limitation — vanilla vLLM supports both.

**Explore:** Compare the Vertex AI vLLM container configuration with a standard vLLM deployment. What features are missing? What does Vertex AI add (auth, scaling, monitoring)?

### vLLM Internals
vLLM (Very Large Language Model) is popular for production serving because of **PagedAttention** — a memory management technique that allows efficient batching of multiple concurrent requests on a single GPU. Traditional serving loads the full model attention cache per request, wasting GPU memory. PagedAttention treats attention memory like virtual memory pages, sharing common prefixes across requests.

**Explore:** Research PagedAttention and compare vLLM performance to other serving frameworks (TGI, Triton, TensorRT-LLM). What are the tradeoffs?

### Security Implications of Decoupling
The separation between model and app creates two independent security surfaces:
- **Model endpoint:** GPU infrastructure, model weights, inference API. Secured by IAM + VPC Service Controls.
- **Application:** CPU infrastructure, business logic, user-facing. Secured by Cloud Run IAM + optional auth.

**Explore:** Where would you insert an AIRS scan in this architecture? What artifacts would you scan? When would you scan them — at build time, deploy time, or runtime?

## Key Files
- `src/airs_mlops_lab/serving/inference_client.py` — rawPredict client, chat template
- `src/airs_mlops_lab/serving/server.py` — FastAPI app
- `Dockerfile` — thin container (no model, no GPU)

## Student Activities
- Trace the full rawPredict request from inference_client through to vLLM
- Modify the chat template to see how output quality changes
- Trace the authentication flow from Cloud Run SA → Vertex AI endpoint
- Compare container size (this app) vs. a container with an embedded model

## Customer Talking Point
"Decoupled serving means you can scan and gate the model independently from the application code. The model never touches the app container — it lives in a managed endpoint with its own access controls."
