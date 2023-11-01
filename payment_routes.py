import stripe
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from stripe.error import SignatureVerificationError, StripeError
from database import Session, engine
from models import Order, User
from models import DBPayment

pay_router = APIRouter(prefix="/payment", tags=["pay"])

session = Session(bind=engine)

stripe.api_key = "sk_test_51N0OMdLVhrgvo0Lj9XHxRUfZGiC7LIDFhw0QS7m14xyWGJM2KHVuB1RE4OP5jMzwEcBU1EufEvJXopmwzKd0DCRS00ss5y7gKd"


def calculate_amount(quantity, pizza_size):
    pizza_prices = {
        "SMALL": 10.0,
        "MEDIUM": 15.0,
        "LARGE": 20.0,
        "EXTRA-LARGE": 25.0,
    }

    if pizza_size not in pizza_prices:
        raise HTTPException(status_code=400, detail="Invalid pizza size")

    price_per_pizza = pizza_prices[pizza_size]
    total_amount = quantity * price_per_pizza
    return int(total_amount)


@pay_router.get("/payment-success/")
async def payment_success(request: Request):
    try:
        session_id = request.query_params.get("session_id")
        # Retrieve the session using Stripe
        stripe_session = stripe.checkout.Session.retrieve(session_id)

        # Check if the payment was successful
        if stripe_session.payment_status == "paid":
            # Mark payment as PAID
            payment = session.query(DBPayment).filter(DBPayment.session_id == session_id).first()
            order = session.query(Order).filter(Order.id == payment.order_id).first()
            if payment.status == "PAID":
                return {"message": "Payment already marked as PAID"}
            payment.status = "PAID"
            order.order_status = "DELIVERED"
            session.add(payment)
            session.commit()

            return {"message": "Payment marked as PAID and order status changed to DELIVERED"}

        return {"message": "Payment not paid"}

    except SignatureVerificationError:
        raise HTTPException(status_code=404)


@pay_router.get("/payment-cancel/")
async def payment_cancel():
    return {"message": "Payment canceled. You can pay later within 24 hours."}


@pay_router.post("/create-payment/{order_id}")
async def create_payment_intent(
    order_id: int,
    request: Request,
):
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        amount = calculate_amount(order.quantity, order.pizza_size)

        BASE_URL = "http://localhost:8000"  # Update this value for different environments
        success_url = f"{BASE_URL}/payment/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = request.url_for("payment_cancel")

        stripe_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Payment for order#{order.id}",
                        },
                        "unit_amount": int(amount) * 100,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        payment = DBPayment(
            status="PENDING",
            session_url=str(stripe_session.url),
            session_id=stripe_session.id,
            money_to_pay=amount,
            order_id=order_id,
        )
        order.order_status = "IN-TRANSIT"
        session.add(payment)
        session.commit()

        return jsonable_encoder({
            "order_id": payment.order_id,
            "money_to_pay": payment.money_to_pay,
            "url_to_pay": payment.session_url
        })
    except StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@pay_router.get('/payments')
async def list_all_payments(Authorize: AuthJWT = Depends()):
    """
        ## List all payments
        This lists all  payments made. It can be accessed by superusers
    """
    #
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
                            )

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        payments = session.query(DBPayment).all()

        return jsonable_encoder(payments)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not a superuser"
                        )