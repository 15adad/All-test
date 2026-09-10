from typing import Optional

from fastapi import FastAPI, Query, Path

from pydantic import BaseModel, Field

app = FastAPI()

"""
根据商品 ID 查询商品详情（路径参数）

分页查询商品列表（查询参数）

新增商品（请求体）

返回不同格式的响应（响应类型）
"""


class Product(BaseModel):
    id: int
    name: str
    price: float = Field(..., ge=0, description="价格必须要 ≥ 0")
    stock: int = Field(..., ge=0, description="库存必须 ≥ 0")
    # 代表可以传字符串或者不传
    category: Optional[str] = None


class CreateProductRequest(BaseModel):
    """创建商品请求体"""
    # TODO 1: name 必填，长度 1-50
    name: str = Field(..., min_length=1, max_length=50)

    # TODO 2: price 必填，必须 ≥ 0
    price: float = Field(..., ge=0)

    # TODO 3: stock 必填，必须 ≥ 0
    stock: int = Field(..., ge=0)

    # TODO 4: category 可选，默认为 "未分类"
    category: str = "未分类"

products_db = [
    Product(id=1, name="iPhone 15", price=5999.00, stock=10, category="电子产品"),
    Product(id=2, name="机械键盘", price=299.00, stock=25),
    Product(id=3, name="咖啡杯", price=45.00, stock=100, category="家居用品"),
    Product(id=4, name="Python 教程", price=89.00, stock=50, category="图书"),
]


@app.get("/products/{product_id}")
async def get_id(product_id: int = Path(..., ge=1)):
    return (products_db[product_id - 1])


@app.get("/products")
async def get_products_list(page:int=Query(ge=1,le=2,description="共两页")):
    i:int =1
    return (
    #     一个循环从products_db里拿数据并展示
    )

@app.post("/products")
async def create_product(product: CreateProductRequest):

    new_id=len(products_db)
    new_product=Product(
        id=new_id,
        name=product.name,
        price=product.price,
        stock=product.stock,
        category=product.category,
    )
    products_db.append(new_product)
    return new_product

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("demo7:app", host="127.0.0.1", port=8000, reload=True)
