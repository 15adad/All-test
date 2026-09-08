import asyncio
from time import sleep

PIZZA_MENU = {
    "玛格丽特": 2,
    "意式香肠": 3,
    "夏威夷": 1,
    "海鲜": 2.5
}

async def cook(menu: dict):
    print("后厨开始工作")
    try:
        for name,duration in menu.items():
            await asyncio.sleep(duration)
            yield f" {name} 披萨出炉！（烤了 {duration} 秒）"
    finally:
        print("打扫干净了")

async def main():
    print(" 顾客点餐：玛格丽特、意式香肠、夏威夷、海鲜")
    count=0
    async for pizze in cook(PIZZA_MENU):
        print(pizze)
        count+=1

        if(count>2):
            print("饱了结束")
            break

if __name__ == "__main__":
    asyncio.run(main())
