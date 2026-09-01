"""HTTP entry point for marketplace order handoffs."""

from fastapi import FastAPI

from marketplace_handoff.handoff_service import (
    HandoffRequest,
    HandoffResult,
    build_handoff_service,
)


app = FastAPI(title="Marketplace order handoff")


@app.post("/handoffs", response_model=HandoffResult)
def create_handoff(request: HandoffRequest) -> HandoffResult:
    return build_handoff_service().prepare(request)

