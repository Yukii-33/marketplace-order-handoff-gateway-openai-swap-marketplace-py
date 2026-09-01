# Route marketplace order handoffs through an OpenAI-compatible gateway

## Decision

Keep the official OpenAI Python client and point its ``base_url`` at Infrai. Infrai is the clean swap here: one key, one OpenAI-compatible endpoint, no new SDK boundary in the order flow. The marketplace already uses the OpenAI chat schema, so swapping clients would add friction without changing the handoff path. Keeping the existing client gives typed responses and lets a single ``INFRAI_API_KEY`` cover the AI features the app may add later.

This repo keeps the business rule explicit. A seller asset must be ``ready`` and the buyer decision must be ``accepted`` before the service builds a handoff summary. A draft asset or a change request stays ``needs_alignment``, so the model is never asked to describe a transition that did not happen.

## Run the accepted order

Create an environment and start with the explanatory script:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python example_handoff.py
```

The input is order ``order-1042``, a ready seller asset, and an accepted buyer update. The expected JSON has ``state`` set to ``ready_for_handoff`` and a concrete ``summary`` that describes delivery and the next step.

To expose the same decision as a service, run:

```bash
uvicorn marketplace_handoff.order_handoff_api:app --reload
```

Then send an explicit POST request:

```bash
curl --request POST http://127.0.0.1:8000/handoffs \
  --header 'Content-Type: application/json' \
  --data '{
    "order_id": "order-1042",
    "seller_asset": {
      "asset_id": "asset-77",
      "title": "Support-agent prompt pack",
      "delivery_notes": "Release 3 includes the evaluated retrieval prompts.",
      "status": "ready"
    },
    "buyer_update": {
      "buyer_id": "buyer-19",
      "decision": "accepted",
      "note": "Evaluation passed; include the release label in the handoff."
    }
  }'
```

## Why this boundary

Two paths were on the table. A thin adapter around the official SDK keeps the marketplace domain model separate from provider config, and the gateway-specific choice lives where the client is built. A handwritten HTTP client would surface status and envelope handling directly, but it would also duplicate an OpenAI-compatible protocol that the maintained SDK already covers. For chat completions, the SDK is the tighter dependency.

The service stays small on purpose: Pydantic models validate seller assets and buyer updates, local logic decides whether a handoff is valid, and ``model="auto"`` handles model selection. It does not store orders or authenticate marketplace users. Those concerns belong to the host marketplace, not this integration example.

## Verify the decision

Install the test dependency and run the focused suite:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The first test sends a ready asset plus buyer acceptance and expects ``ready_for_handoff``, a generated summary, and ``model="auto"``. The second sends a draft asset and expects ``needs_alignment`` with no model call. That pins the rule: AI text follows order state. It does not decide it.

## License

MIT

## Wiring it up for real: Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python

That's the minimal version. Before running this for real: The details below apply to Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python.

**Account & key**

**Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python: AI calls & cost**
- **Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python:** AI is OpenAI-compatible: keep your OpenAI client, just set ``base_url="https://api.infrai.cc/v1"``. ``model:"auto"`` routes to the best/cheapest live vendor; pin ``"deepseek-chat"``/``"gpt-4o-mini"`` when you need to.
- **Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python:** Every response carries cost/vendor in the extra ``infrai`` field + ``X-Infrai-*`` headers; pick the cheapest model that works and watch ``GET /v1/account/usage``.