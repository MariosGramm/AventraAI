
import logging

from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from app.enums import SubscriptionTier
from app.models import Message, User
from app.utils import generate_subscription_email, send_email
from fastapi import APIRouter, HTTPException, Header, Request
from sqlalchemy import Engine, select
from sqlmodel import Session
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(tags=["payments"])

@router.post("/create-checkout-session")
def create_checkout_session(current_user: CurrentUserDep, session: SessionDep) -> dict:
    """
    Create a Stripe checkout session for upgrading to paid tier.
    Returns a checkout URL for the frontend to redirect to.
    """
    if current_user.subscription_tier == SubscriptionTier.PAID:
        raise HTTPException(status_code=400, detail="User is already subscribed to the Pro plan.")

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
async def stripe_webhook(request: Request, session: SessionDep,stripe_signature: str = Header(None, alias="stripe-signature")) -> Message:
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
        session_data = event["data"]["object"].to_dict()
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

                    if settings.emails_enabled:
                        email_data = generate_subscription_email(email_to=user.email)
                        try:
                            send_email(
                                email_to=user.email,
                                subject=email_data.subject,
                                html_content=email_data.html_content,
                            )
                        except Exception:
                            logger.exception(
                                "Subscription confirmation email failed for %s",
                                user.email,
                            )
                    else:
                        logger.warning(
                            "Subscription confirmation email skipped: Resend is not configured"
                        )
                else:
                    logger.warning("Stripe checkout completed for unknown user id %s", user_id)
        else:
            logger.warning(
                "checkout.session.completed event %s has no user_id in metadata",
                event.get("id"),
            )

    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"].to_dict()
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
                