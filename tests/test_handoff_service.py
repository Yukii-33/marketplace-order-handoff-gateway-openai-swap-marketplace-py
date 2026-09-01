from types import SimpleNamespace

from marketplace_handoff.handoff_service import (
    HandoffRequest,
    HandoffService,
    HandoffState,
)


class RecordingCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        message = SimpleNamespace(content="Deliver asset-77 and record buyer acceptance.")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def request_with(status: str, decision: str) -> HandoffRequest:
    return HandoffRequest.model_validate(
        {
            "order_id": "order-1042",
            "seller_asset": {
                "asset_id": "asset-77",
                "title": "Support-agent prompt pack",
                "delivery_notes": "Release 3 is ready.",
                "status": status,
            },
            "buyer_update": {
                "buyer_id": "buyer-19",
                "decision": decision,
                "note": "Evaluation passed.",
            },
        }
    )


def test_accepted_ready_asset_becomes_a_handoff() -> None:
    completions = RecordingCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    service = HandoffService(client)  # type: ignore[arg-type]

    result = service.prepare(request_with("ready", "accepted"))

    assert result.state is HandoffState.READY_FOR_HANDOFF
    assert result.summary == "Deliver asset-77 and record buyer acceptance."
    assert completions.calls[0]["model"] == "auto"


def test_draft_asset_stays_in_alignment_without_an_ai_call() -> None:
    completions = RecordingCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    service = HandoffService(client)  # type: ignore[arg-type]

    result = service.prepare(request_with("draft", "accepted"))

    assert result.state is HandoffState.NEEDS_ALIGNMENT
    assert result.summary is None
    assert completions.calls == []

