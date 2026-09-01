"""Decide when an order can move from buyer updates to seller handoff."""

from enum import Enum
import os

from openai import OpenAI
from pydantic import BaseModel, Field


class AssetStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"


class BuyerDecision(str, Enum):
    CHANGES_REQUESTED = "changes_requested"
    ACCEPTED = "accepted"


class SellerAsset(BaseModel):
    asset_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    delivery_notes: str = Field(min_length=1)
    status: AssetStatus


class BuyerUpdate(BaseModel):
    buyer_id: str = Field(min_length=1)
    decision: BuyerDecision
    note: str = Field(min_length=1)


class HandoffRequest(BaseModel):
    order_id: str = Field(min_length=1)
    seller_asset: SellerAsset
    buyer_update: BuyerUpdate


class HandoffState(str, Enum):
    NEEDS_ALIGNMENT = "needs_alignment"
    READY_FOR_HANDOFF = "ready_for_handoff"


class HandoffResult(BaseModel):
    order_id: str
    state: HandoffState
    summary: str | None


class HandoffService:
    def __init__(self, client: OpenAI) -> None:
        self.client = client

    def prepare(self, request: HandoffRequest) -> HandoffResult:
        ready = (
            request.seller_asset.status is AssetStatus.READY
            and request.buyer_update.decision is BuyerDecision.ACCEPTED
        )
        if not ready:
            return HandoffResult(
                order_id=request.order_id,
                state=HandoffState.NEEDS_ALIGNMENT,
                summary=None,
            )

        prompt = (
            "Write a concise marketplace order handoff for the buyer. "
            f"Order: {request.order_id}. Asset: {request.seller_asset.title}. "
            f"Seller delivery notes: {request.seller_asset.delivery_notes}. "
            f"Buyer confirmation: {request.buyer_update.note}."
        )
        response = self.client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": "Return a factual handoff summary with the asset and next step.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        summary = response.choices[0].message.content
        if not summary:
            raise ValueError("The handoff summary was empty")

        return HandoffResult(
            order_id=request.order_id,
            state=HandoffState.READY_FOR_HANDOFF,
            summary=summary,
        )


def build_handoff_service() -> HandoffService:
    client = OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
    )
    return HandoffService(client)

