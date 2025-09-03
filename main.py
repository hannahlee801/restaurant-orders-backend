from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import get_db
from sqlalchemy import func
from models import Customer, MenuItem, Order, OrderItem, CustomerOrderLink
from schemas import CreateOrderRequest, CreateCustomerRequest, CreateMenuItemRequest, UpdateCustomerRequest, UpdateItemRequest, UpdateOrderRequest, GetBestSellingItemRequest, GetCustomersOrderRequest

app = FastAPI()

### GET ###

@app.get("/menuitems")
async def get_menu_items(db: Session = Depends(get_db)) -> list[MenuItem]:
    return db.exec(select(MenuItem)).all()

@app.get("/menuitems/{item_id}")
async def get_menu_item(item_id: int, db: Session = Depends(get_db)) -> MenuItem:
    item: MenuItem | None = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item_id} not found.")
    return item

@app.get("/customers")
async def get_customers(db: Session = Depends(get_db)) -> list[Customer]:
    return db.exec(select(Customer)).all()

@app.get("/customers/{id}")
async def get_customer(id: int, db: Session = Depends(get_db)) -> Customer:
    customer: Customer | None = db.get(Customer, id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {id} not found.")
    return customer

@app.get("/orders")
async def get_orders(db: Session = Depends(get_db)) -> list[dict]:
    statement = (
        select(Order, OrderItem, MenuItem, Customer)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(MenuItem, MenuItem.id == OrderItem.item_id)
        .join(Customer, Customer.id == Order.customer_id)
    )

    results = db.exec(statement).all()

    orders: dict[int, dict] = {}
    for order, item, menu, customer in results:
        if order.id not in orders:
            orders[order.id] = {
                "id": order.id,
                "customer": customer.name,
                "items": []
            }
        orders[order.id]["items"].append({
            "id":item.item_id,
            "quantity": item.quantity,
            "menu_item": {
                "id": menu.id,
                "name": menu.name,
                "price": menu.price,
            }
        })
    return list(orders.values())

# @app.get("/orders/{id}")
# async def get_order(id: int, db: Session = Depends(get_db)) -> dict:
#     statement = (
#         select(Order, OrderItem, MenuItem, Customer)
#         .join(OrderItem, OrderItem.order_id)
#     )

### POST ###

@app.post("/menuitems", status_code=status.HTTP_201_CREATED)
async def create_menu_item(create_menu_item_request: CreateMenuItemRequest, db: Session = Depends(get_db)) -> MenuItem:
    menu_item: MenuItem = MenuItem(**create_menu_item_request.model_dump())
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item

@app.post("/customers", status_code=status.HTTP_201_CREATED)
async def create_customer(create_customer_request: CreateCustomerRequest, db: Session = Depends(get_db)) -> Customer:
    customer: Customer = Customer(**create_customer_request.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

# @app.post("/orders", status_code=status.HTTP_201_CREATED)
# async def create_order(create_order_request: CreateOrderRequest, db: Session = Depends(get_db)) -> None:
#     items: list[OrderItem] = []
#     for item in create_order_request.items:
#         menu_item: MenuItem | None = db.get(MenuItem, item.item_id)
#         if menu_item is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item.item_id} not found.")
#         order_item: OrderItem = OrderItem(menu_item_id=item.item_id, quantity=item.total_item_quantity)
#         items.append(order_item)
#     customer: Customer | None = db.get(Customer, create_order_request.customer_id)
#     if customer is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {create_order_request.customer_id} not found.")
#     order: Order = Order(**create_order_request.model_dump())
#     db.add(order)
#     db.commit()
#     db.refresh(order)
#     return order.id

### PATCH ###

@app.patch("/customer/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_customer(id: int, updated_fields: UpdateCustomerRequest, db: Session = Depends(get_db)) -> None:
    customer: Customer | None = db.get(Customer, id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {id} not found.")
    
    for k, v in updated_fields.model_dump(exclude_unset=True).items():
        setattr(customer, k, v)

    db.commit()

@app.patch("/menuitems/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_item(item_id: int, updated_fields: UpdateItemRequest, db: Session = Depends(get_db)) -> None:
    item: MenuItem | None = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item_id} not found.")
    
    for k, v in updated_fields.model_dump(exclude_unset=True).items():
        setattr(item, k, v)

    db.commit()

### DELETE ###

@app.delete("/customers/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> None:
    customer: Customer | None = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {id} not found.")
    
    db.delete(customer)
    db.commit()

@app.delete("/menuitems/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(item_id: int, db: Session = Depends(get_db)) -> None:
    menu_item: MenuItem | None = db.get(MenuItem, item_id)
    if menu_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item_id} not found.")
    
    db.delete(menu_item)
    db.commit()

### REPORTS ###

# @app.get("/reports/best-selling")
# async def get_best_selling_item(db: Session = Depends(get_db)) -> GetBestSellingItemRequest:
#     statement = (
#         select(MenuItem.id, MenuItem.name, func.sum(OrderItem.quantity)).join(OrderItem, OrderItem.item_id == MenuItem.id).group_by(MenuItem.id, MenuItem.name).order_by(func.sum(OrderItem.quantity).desc()).limit(1)
#     )
#     response= db.exec(statement).all()
#     if not response:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Best selling item not found.")
#     return GetBestSellingItemRequest(item_id=response[0], name=response[1], quantity=response[2])

# @app.get("/reports/customer-orders")
# async def get_customer_orders(customer_id: int, db: Session = Depends(get_db)) -> GetCustomersOrderRequest:
#     statement= (
#         select(Customer.id, Customer.name, func.coalesce(func.sum(OrderItem.quantity), 0)).select_from(Customer).outerjoin(Order, Order.customer_id == Customer.id).outerjoin(OrderItem, OrderItem.order_id == Order.id).where(Customer.id == customer_id).group_by(Customer.id, Customer.name)
#     )
#     response= db.exec(statement).first()

#     if not response:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with id {customer_id} not found.")
#     return GetCustomersOrderRequest(customer_id=response[0], name=response[1], quantity=response[2])