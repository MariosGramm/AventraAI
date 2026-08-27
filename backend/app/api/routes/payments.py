
import logging
from datetime import UTC, datetime
from typing import Any

from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from app.enums import SubscriptionTier
from app.models import Message, User, UserPublicDTO
from app.utils import generate_subscription_cancellation_email, generate_subscription_email, send_email
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy import Engine, select
from sqlmodel import Session
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(tags=["payments"])

class ConfirmCheckoutSessionDTO(BaseModel):
    session_id: str

class CreateCheckoutSessionDTO(BaseModel):
    return_to: str | None = None

# Only these internal paths are allowed as the Stripe cancel-redirect target,
# to avoid turning return_to into an open redirect.
ALLOWED_RETURN_PATHS = {"/", "/profile"}

def _get_period_end(subscription: dict) -> datetime | None:
    """
    Extract the current period end from a Stripe Subscription dict.

    Newer Stripe API versions moved this field off the subscription's top
    level and onto each subscription item.
    """
    items = subscription.get("items", {}).get("data", [])
    if items and items[0].get("current_period_end"):
        return datetime.fromtimestamp(items[0]["current_period_end"], tz=UTC)
    return None

def _apply_paid_subscription(db: Session, user: User, customer_id: str | None, subscription_id: str | None) -> bool:
    """
    Sync a user's row to reflect an active Pro subscription.

    Shared by the webhook handler and the synchronous checkout-confirmation
    endpoint, since either one may be the first to observe the upgrade
    (webhooks are not deliverable to localhost without a forwarding tunnel).

    Returns:
        True if this call transitioned the user from FREE to PAID (i.e. a
        confirmation email should be sent), False if they were already PAID.
    """
    was_already_paid = user.subscription_tier == SubscriptionTier.PAID

    user.subscription_tier = SubscriptionTier.PAID
    user.stripe_customer_id = customer_id
    user.stripe_subscription_id = subscription_id
    user.subscription_cancel_at_period_end = False

    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id).to_dict()
            user.subscription_current_period_end = _get_period_end(subscription)
        except Exception:
            logger.exception("Failed to retrieve Stripe subscription %s", subscription_id)

    db.add(user)
    db.commit()
    db.refresh(user)

    return not was_already_paid

@router.post("/create-checkout-session")
def create_checkout_session(current_user: CurrentUserDep, session: SessionDep, body: CreateCheckoutSessionDTO | None = None) -> dict:
    """
    Create a Stripe checkout session for upgrading to paid tier.
    Returns a checkout URL for the frontend to redirect to.
    """
    if current_user.subscription_tier == SubscriptionTier.PAID:
        raise HTTPException(status_code=400, detail="User is already subscribed to the Pro plan.")

    return_to = body.return_to if body and body.return_to in ALLOWED_RETURN_PATHS else "/"

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": settings.STRIPE_PRICE_ID,  
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{settings.FRONTEND_HOST}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_HOST}{return_to}",
            customer_email=current_user.email,
            metadata={"user_id": str(current_user.id)}
        )

        return {"checkout_url": checkout_session.url}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm-checkout-session", response_model=UserPublicDTO)
def confirm_checkout_session(current_user: CurrentUserDep, session: SessionDep, body: ConfirmCheckoutSessionDTO) -> Any:
    """
    Synchronously confirm a completed Stripe checkout and upgrade the user.

    The `/webhook` route is the reliable, eventually-consistent path for
    this, but webhooks can't reach localhost without a forwarding tunnel
    (e.g. `stripe listen`) and can also lag in production. The frontend
    calls this right after the success redirect so the UI reflects the
    upgrade immediately, regardless of webhook delivery.
    """
    try:
        checkout_session = stripe.checkout.Session.retrieve(body.session_id).to_dict()
    except Exception as e:
        logger.error(f"Stripe checkout session retrieval error: {e}")
        raise HTTPException(status_code=400, detail="Could not verify checkout session.")

    if checkout_session.get("metadata", {}).get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="This checkout session does not belong to you.")

    if checkout_session.get("payment_status") != "paid":
        raise HTTPException(status_code=400, detail="Checkout session is not paid yet.")

    is_new_upgrade = _apply_paid_subscription(
        session,
        current_user,
        customer_id=checkout_session.get("customer"),
        subscription_id=checkout_session.get("subscription"),
    )

    if is_new_upgrade:
        if settings.emails_enabled:
            email_data = generate_subscription_email(email_to=current_user.email)
            try:
                send_email(
                    email_to=current_user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )
            except Exception:
                logger.exception("Subscription confirmation email failed for %s", current_user.email)
        else:
            logger.warning("Subscription confirmation email skipped: Resend is not configured")

    return current_user

@router.post("/cancel-subscription")
def cancel_subscription(current_user: CurrentUserDep, session: SessionDep) -> dict:
    """
    Cancel the user's Pro subscription at the end of the current billing
    period — the user keeps Pro access (and won't be charged again) until
    then, instead of being downgraded immediately.
    """
    if current_user.subscription_tier != SubscriptionTier.PAID or not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active Pro subscription to cancel.")

    try:
        subscription = stripe.Subscription.modify(
            current_user.stripe_subscription_id,
            cancel_at_period_end=True,
        ).to_dict()
    except Exception as e:
        logger.error(f"Stripe cancel error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    current_user.subscription_cancel_at_period_end = True
    current_user.subscription_current_period_end = _get_period_end(subscription)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    if settings.emails_enabled:
        email_data = generate_subscription_cancellation_email(
            email_to=current_user.email,
            current_period_end=current_user.subscription_current_period_end,
        )
        try:
            send_email(
                email_to=current_user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        except Exception:
            logger.exception("Cancellation confirmation email failed for %s", current_user.email)
    else:
        logger.warning("Cancellation confirmation email skipped: Resend is not configured")

    return {
        "message": "Your Pro plan will remain active until the end of the billing period.",
        "current_period_end": current_user.subscription_current_period_end,
    }

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
                    is_new_upgrade = _apply_paid_subscription(
                        db,
                        user,
                        customer_id=session_data.get("customer"),
                        subscription_id=session_data.get("subscription"),
                    )

                    if is_new_upgrade:
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

    elif event["type"] == "customer.subscription.updated":
        subscription_data = event["data"]["object"].to_dict()
        customer_id       = subscription_data.get("customer")

        if customer_id:
            from sqlmodel import Session
            from app.core.db import engine
            with Session(engine) as db:
                user = db.exec(select(User).where(User.stripe_customer_id == customer_id)).first()
                if user:
                    user.subscription_cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)
                    period_end = _get_period_end(subscription_data)
                    if period_end:
                        user.subscription_current_period_end = period_end
                    db.add(user)
                    db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"].to_dict()
        customer_id       = subscription_data.get("customer")

        if customer_id:
            from sqlmodel import Session
            from app.core.db import engine
            with Session(engine) as db:
                user = db.exec(select(User).where(User.stripe_customer_id == customer_id)).first()
                if user:
                    user.subscription_tier = SubscriptionTier.FREE
                    user.monthly_searches_used = 0
                    user.stripe_subscription_id = None
                    user.subscription_cancel_at_period_end = False
                    user.subscription_current_period_end = None
                    db.add(user)
                    db.commit()

    return Message(message="Webhook received and processed successfully.")
                