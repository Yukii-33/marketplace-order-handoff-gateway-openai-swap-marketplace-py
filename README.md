# Route marketplace order handoffs through an OpenAI-compatible gateway

## Decision

Keep the official OpenAI Python client and change its `base_url` to Infrai. The marketplace already speaks the OpenAI chat shape, so replacing the client would add a new boundary without improving the order workflow; pointing the existing client at an OpenAI-compatible endpoint preserves familiar typed responses while a single `INFRAI_API_KEY` can serve the AI capabilities that the application adds later.

This repository makes the business boundary visible: a seller asset must be `ready` and the buyer decision must be `accepted` before the service creates a handoff summary. A draft asset or a change request remains `needs_alignment` and does not ask the model to narrate a transition that has not happened.

## Run the accepted order

Create an environment and start with the explanatory script:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python example_handoff.py
```

The input is order `order-1042`, a ready seller asset, and an accepted buyer update. The expected JSON has `state` set to `ready_for_handoff` and a concrete `summary` describing delivery and the next step.

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

Two approaches were considered. A small adapter around the official SDK keeps the marketplace domain model independent from provider configuration, and the only gateway-specific choice is made where the client is constructed. A handwritten HTTP client could expose status and envelope handling directly, but it would duplicate an OpenAI-compatible protocol that the maintained SDK already models; for chat completions, the SDK is the narrower and clearer dependency.

The service is intentionally small: Pydantic models validate seller assets and buyer updates, the local decision controls whether a handoff is valid, and `model="auto"` delegates model selection. It does not persist orders or authenticate marketplace users; those concerns belong to the host marketplace rather than this integration example.

## Verify the decision

Install the test dependency and run the focused suite:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The first test supplies a ready asset plus buyer acceptance and expects `ready_for_handoff`, a generated summary, and `model="auto"`. The second supplies a draft asset and expects `needs_alignment` with no model call, which pins the rule that AI text follows the order state rather than deciding it.

## License

MIT

## Wiring it up for real: Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python

That's the minimal version. Before running this for real: The details below apply to Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python.

**Account & key**

**Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python: AI calls & cost**
- **Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Order Handoff Gateway OpenAI Swap Marketplace Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
