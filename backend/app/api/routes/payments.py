
from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from fastapi import APIRouter, HTTPException
import stripe


router = APIRouter(tags=["payments"])

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
        raise HTTPException(status_code=400, detail=str(e))
