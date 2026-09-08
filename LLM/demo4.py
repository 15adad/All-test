import asyncio

# 定义异步生成器
async def wrap(level):
    print("启动曲速引擎充能程序...")
    try:
        for i in range(1, level + 1):
            await asyncio.sleep(1)
            yield f"引擎充能中{i}/{level}"
    finally:
        print("引擎冷却系统已激活，资源释放完毕")


async def main():
    count = 0
    print("舰长下令：准备曲速跳跃！")
    async for i in wrap(5):
        print(i)
        count += 1
        if count > 3:
            print("不等了")
            break


if __name__ == "__main__":
    asyncio.run(main())
