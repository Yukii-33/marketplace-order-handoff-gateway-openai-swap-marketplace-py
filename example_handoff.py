"""Run one accepted marketplace order through the handoff decision."""

from marketplace_handoff.handoff_service import HandoffRequest, build_handoff_service


def main() -> None:
    request = HandoffRequest.model_validate(
        {
            "order_id": "order-1042",
            "seller_asset": {
                "asset_id": "asset-77",
                "title": "Support-agent prompt pack",
                "delivery_notes": "Release 3 includes the evaluated retrieval prompts.",
                "status": "ready",
            },
            "buyer_update": {
                "buyer_id": "buyer-19",
                "decision": "accepted",
                "note": "Evaluation passed; include the release label in the handoff.",
            },
        }
    )
    result = build_handoff_service().prepare(request)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

