
import logging

from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from app.enums import SubscriptionTier
from app.models import Message, User
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import Engine, select
from sqlmodel import Session
import stripe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(tags=["payments"])

@router.post("/create-checkout-session")
def create_checkout_session(current_user: CurrentUserDep, session: SessionDep) -> dict:
    """
    Create a Stripe checkout session for upgrading to paid tier.
    Returns a checkout URL for the frontend to redirect to.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": settings.STRIPE_PRICE_ID,  
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{settings.FRONTEND_HOST}/dashboard?upgraded=true",
            cancel_url=f"{settings.FRONTEND_HOST}/pricing",
            customer_email=current_user.email,
            metadata={"user_id": str(current_user.id)}
        )

        return {"checkout_url": checkout_session.url}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, session: SessionDep) -> Message:
    """
    Handle Stripe webhook events.
    Verifies webhook signature and updates user subscription tier.
    """
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload = payload,
            sig_header = stripe_signature,
            secret = settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e :
        raise HTTPException(status_code= 400, detail=f"Webhook signature verification failed: {str(e)}")

    # Event handling logic
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        user_id      = session_data.get("metadata", {}).get("user_id")

        if user_id:
            from sqlmodel import Session
            from app.core.db import engine
            with Session(engine) as db:
                user = db.get(User, user_id)
                if user:
                    user.subscription_tier = SubscriptionTier.PAID
                    db.add(user)
                    db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"]
        customer_email    = subscription_data.get("customer_email")

        if customer_email:
            from sqlmodel import Session
            from app.core.db import engine
            with Session(engine) as db:
                user = db.exec(select(User).where(User.email == customer_email)).first()
                if user:
                    user.subscription_tier = SubscriptionTier.FREE
                    user.monthly_searches_used = 0
                    db.add(user)
                    db.commit()

    return Message(message="Webhook received and processed successfully.")
                