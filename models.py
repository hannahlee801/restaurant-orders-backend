from sqlmodel import Relationship, Field, SQLModel

class CustomerOrderLink(SQLModel, table=True):
    orderitem_id: int | None = Field(foreign_key="orderitem.item_id", primary_key=True)
    order_id: int | None = Field(foreign_key="order.id", primary_key=True)

# Menu Items

class MenuItem(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str
    price: float
    calories: int

# Customers

class Customer(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str
    orders: list["Order"] = Relationship(back_populates="customer")

# Orders

class OrderItem(SQLModel, table=True):
    item_id: int | None = Field(primary_key=True)
    menu_item_id: int = Field(foreign_key="menuitem.id")
    menu_item: MenuItem = Relationship()
    quantity: int = 1
    order_id: int | None = Field(foreign_key="order.id")
    orders: list["Order"] = Relationship(back_populates="items", link_model=CustomerOrderLink)

class Order(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    items: list["OrderItem"] = Relationship(back_populates="orders", link_model=CustomerOrderLink)
    customer_id: int | None = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="orders")

