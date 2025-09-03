from pydantic import BaseModel

class CreateMenuItemRequest(BaseModel):
    name: str
    price: float
    calories: int

class CreateCustomerRequest(BaseModel):
    name: str

class CreateOrderItemRequest(BaseModel):
    total_item_quantity: int
    menu_item_id: int

class CreateOrderRequest(BaseModel):
    customer_id: int
    items: list[CreateOrderItemRequest]

class UpdateItemRequest(BaseModel):
    name: str
    price: float
    calories: int

class UpdateCustomerRequest(BaseModel):
    name: str

class UpdateOrderRequest(BaseModel):
    items: list[CreateOrderItemRequest]
    customer_id: int

class GetCustomersOrderRequest(BaseModel):
    customer_id: int
    name: str
    quantity: int

class GetBestSellingItemRequest(BaseModel):
    menu_item_id: int
    name: str
    quantity: int

class GetDailyRevenueRequest(BaseModel):
    date: str
    revenue: float