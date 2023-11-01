from fastapi import APIRouter, status, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import session


orders_router = APIRouter(prefix="/orders", tags=["orders"])


@orders_router.get("/")
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"message": "Hello world"}


@orders_router.post("/order")
async def place_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
    )

    new_order.user = user
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status,
    }

    return jsonable_encoder(response)


@orders_router.get('/orders')
async def list_all_orders(Authorize: AuthJWT = Depends()):
    """
        ## List all orders
        This lists all  orders made. It can be accessed by superusers
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
                            )

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()

        return jsonable_encoder(orders)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not a superuser"
                        )


@orders_router.get('/orders/{id}')
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    """
        ## Get an order by its ID
        This gets an order by its ID and is only accessed by a superuser
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()

        return jsonable_encoder(order)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not allowed to carry out request"
    )


@orders_router.get('/user/orders')
async def get_users_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    return jsonable_encoder(current_user.orders)


@orders_router.get('/user/order/{id}')
async def get_users_orders(id:int, Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    orders = current_user.orders
    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No order with such id"
    )


@orders_router.put('/order/update/{id}')
async def update_order(id, order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    order_to_update = session.query(Order).filter(Order.id == id).first()

    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    session.commit()

    response = {
        "id": order_to_update.id,
        "quantity": order_to_update.quantity,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status,
    }

    return jsonable_encoder(order_to_update)


@orders_router.patch('/order/status/{id}')
async def update_order_status(id: int,
                              order: OrderStatusModel,
                              Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()

        order_to_update.order_status = order.order_status

        session.commit()

        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status": order_to_update.order_status,
        }

        return jsonable_encoder(order_to_update)


@orders_router.delete('/delete/{id}')
async def delete_order(id: int,
                       Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order_to_delete = session.query(Order).filter(Order.id == id).first()
        session.delete(order_to_delete)
        session.commit()

        return order_to_delete
