# ============================================================
# 1. 导入依赖库
# ============================================================

import asyncio
# asyncio: Python 内置的异步 IO 库，提供事件循环、sleep 等核心异步功能
# 相当于"异步工具箱"，让你能写 async/await 代码

from fastapi import FastAPI, Request
# FastAPI: 现代 Python Web 框架，用于构建 API
# Request: 代表客户端的 HTTP 请求对象，包含请求头、参数、客户端信息等
# 通过 Request 我们可以检测客户端是否断连 (request.is_disconnected())

# 实际只需要保留一个。sse_starlette 是更通用的选择（兼容所有 FastAPI 版本）
from sse_starlette import EventSourceResponse, ServerSentEvent  # 独立包，兼容性更好

# ============================================================
# 2. 创建 FastAPI 应用实例
# ============================================================

app = FastAPI()


# app 是整个应用的核心对象，所有路由、中间件、事件处理器都注册在它上面
# 后面 @app.get("/task/stream") 就是向这个 app 注册一个 GET 路由

# ============================================================
# 3. 核心：异步生成器（流式数据生产线）
# ============================================================

async def task_pipeline(request: Request, task_name: str):
    """
    这是一个异步生成器函数（async def + yield）

    作用：模拟一个多阶段任务流水线，每个阶段完成后，将进度实时推送（yield）给客户端

    参数：
        request: 客户端的 HTTP 请求对象，用于检测连接状态
        task_name: 任务名称（从 URL 参数 ?task=xxx 传入）

    返回值：无（但 yield 会不断向外产出 ServerSentEvent 对象）
    """

    # ===== 阶段 0：连接预热（立刻发送心跳，稳住连接） =====

    # 第一个 yield 必须足够早！不能在它之前有任何 await 操作
    # 因为如果服务器 0.5 秒后才开始发数据，部分客户端（如 curl）可能超时断开
    yield ServerSentEvent(
        comment="流水线启动",  # 注释类事件：前端 onmessage 不会触发，仅用于调试/心跳
        retry=3000  # 告诉浏览器：如果连接断了，等待 3000 毫秒（3 秒）后重连
    )
    # 这个 yield 执行后，客户端立刻收到数据，连接被"焊死"，不会超时断开了

    # 现在连接已经稳定，可以做耗时操作了
    await asyncio.sleep(0.5)  # 模拟"权限验证"阶段的耗时

    # ===== 断连检测（生产级代码必备） =====
    # 检查客户端是否还在线（是否刷新了页面、关闭了浏览器、网络断开了）
    # 如果客户端跑了，立刻 return 终止生成器，节省服务器 CPU 资源
    #TODO 为什么这个if语句要用await，return换成break行吗
    if await request.is_disconnected():
        print("⚠️ 客户端在鉴权阶段跑了")
        return  # 提前结束生成器，不再继续执行后面的代码

    # ===== 阶段 1：权限验证通过 =====
    yield ServerSentEvent(
        data="✅ 阶段 1/3：权限验证通过",  # 事件携带的数据（自动 JSON 编码）
        event="stage"  # 事件类型名，前端可用 addEventListener('stage', ...) 监听
    )
    # 这个 yield 执行后，前端会收到一个 event 类型为 "stage" 的消息
    # 前端可以专门为 stage 事件写不同的渲染逻辑（如更新进度条）

    # ===== 阶段 2：模拟查询数据库 =====
    #TODO是不是应该先检测断连再模拟查询 Answer：应该加
    await asyncio.sleep(1.0)  # 模拟数据库查询耗时（1秒）

    # 再次检测断连（高并发场景下，用户在等待过程中可能关掉页面）
    if await request.is_disconnected():
        print("⚠️ 客户端在查询阶段跑了")
        return

    # 产出阶段 2 的进度信息
    yield ServerSentEvent(
        data=f"📦 阶段 2/3：数据加载完成 (任务: {task_name})",
        event="stage"
    )

    # ===== 阶段 3：模拟逐字生成报告（核心流式输出） =====
    report_text = f"【最终报告】针对 '{task_name}' 的分析结果：一切正常。"
    #TODO enumerate什么东西
    # enumerate 会同时返回索引 (idx) 和字符 (char)
    for idx, char in enumerate(report_text):
        # 🛡️ 每次生成前都检测断连（重要！）
        # 因为生成过程可能持续数秒，用户可能在中间关掉页面
        # 如果不检测，服务器会白白计算大量字符然后丢弃
        if await request.is_disconnected():
            print(f"⚠️ 客户端在生成第 {idx} 个字时跑了")
            return

        # 模拟 AI 模型逐字生成延迟（真实场景中是等待 GPU 推理返回下一个 token）
        await asyncio.sleep(0.1)  # 0.1 秒一个字，模拟打字机效果

        # 🔥 核心：把每个字符作为一个独立的 SSE 事件发送出去
        # data=char: 发送单个字符（比如 "【"、"最"、"终"）
        # event="token": 事件类型为 token，前端可用 addEventListener('token', ...) 逐字渲染
        # id=str(idx): 给每个字符编号，如果网络断了，浏览器重连时会在请求头中携带 last-event-id
        #               服务器可以根据这个 id 决定是否断点续传
        yield ServerSentEvent(
            data=char,
            event="token",
            id=str(idx)
        )
        # 前端每收到一个 token 事件，就把字符追加到页面上
        # 这就是 "ChatGPT 逐字打印" 效果的实现原理！

    # ===== 最终结束信号 =====
    # 告诉前端：所有数据发送完毕，可以关闭连接或显示"完成"状态
    yield ServerSentEvent(
        data="🎉 全部任务完成",
        event="done"
    )


# ============================================================
# 4. 路由定义（API 入口）
# ============================================================

@app.get("/task/stream")
# ↑ 装饰器：注册一个 GET 请求的路由，路径为 /task/stream
# 访问 http://127.0.0.1:8000/task/stream?task=测试 时，这个函数会被调用

async def stream_task(request: Request, task: str = "默认任务"):
    """
    这是 API 入口函数（路由处理函数）

    参数：
        request: FastAPI 自动注入的请求对象
        task: 从 URL 查询参数 ?task=xxx 获取，如果没传则使用默认值 "默认任务"

    返回：
        EventSourceResponse: 专门用于 SSE 流式响应的对象
    """

    # 创建并返回 SSE 响应对象 #TODO这个对象是干嘛的谁创建的给谁用
    return EventSourceResponse(
        # 第一个参数：异步生成器对象（实际的数据生产者）
        # 注意：这里传入的是 task_pipeline(request, task) 的执行结果（生成器对象），
        #       而不是函数本身。EventSourceResponse 会循环调用这个生成器的 __anext__()
        task_pipeline(request, task),

        # headers: 额外响应头（生产环境必备）
        # X-Accel-Buffering: no 是告诉 Nginx 反向代理：
        #   "不要缓存我的响应数据，来一点就转发给客户端一点"
        #   如果不加这行，Nginx 默认会攒满 4KB 才发送，导致流式失效（失去逐字效果）#TODO前提服务器这里采用了Nginx技术是吧
        headers={"X-Accel-Buffering": "no"}
    )


# ============================================================
# 5. 启动入口
# ============================================================

if __name__ == "__main__":
    # 如果直接运行这个文件（而不是被 import），则启动 uvicorn 服务器
    import uvicorn

    # uvicorn.run() 会启动一个 ASGI 服务器
    # 参数：
    #   app: 要运行的应用实例（就是上面的 FastAPI 对象）
    #   host: 监听所有网络接口（0.0.0.0 表示允许外部机器访问，127.0.0.1 只允许本机访问）
    #   port: 监听端口 8000
    #   reload: 这里没加，加上 --reload 参数可以热重载（改代码自动重启）
    uvicorn.run(app, host="127.0.0.1", port=8000)