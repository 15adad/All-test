import asyncio
import sys

#设计异步生成器
async def search_pages(query: str,total_pages: int):
    print(f"开始搜索 '{query}',共{total_pages}页")

    try:
        for page in range(1,total_pages+1):
            await asyncio.sleep(0.5)

            for i in range(1,3):
                yield f"【第{page}页】结果 {i}: 关于 {query} 的文档..."
    finally:
        print("正在释放网络连接...")

async def main():
    item=("[第]")
    print("程序启动")

    async for item in search_pages("Python异步",3):


if __name__ == "__main__":
    asyncio.run(main())