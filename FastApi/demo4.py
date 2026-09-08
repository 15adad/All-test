import asyncio
import random
import json
from importlib import reload

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse

app = FastAPI()

# ============================================================
# 模拟股票数据
# ============================================================
stocks = {
    "AAPL": 175.50,
    "TSLA": 245.30,
    "NVDA": 890.20
}


# ============================================================
# 核心生成器：手拼 SSE 数据流
# ============================================================
async def stock_price_stream(request: Request):
    """
    使用 StreamingResponse + 手拼 SSE 格式字符串
    完全避免 sse-starlette 的兼容性问题
    """
    # ① 发送注释（心跳），让连接稳住
    yield ": 行情推送已连接\n\n"

    update_count = 0

    while True:
        # ② 检测客户端是否断开
        if await request.is_disconnected():
            print(f"⚠️ 客户端断开，共推送 {update_count} 次")
            break

        # ③ 随机选股票，模拟价格变动
        symbol = random.choice(list(stocks.keys()))
        old_price = stocks[symbol]
        change_percent = random.uniform(-0.05, 0.05)
        new_price = round(old_price * (1 + change_percent), 2)
        stocks[symbol] = new_price
        change = round(new_price - old_price, 2)

        update_count += 1

        # ④ 组装数据字典
        data = {
            "symbol": symbol,
            "price": new_price,
            "change": change,
            "change_percent": round(change_percent * 100, 2),
            "timestamp": asyncio.get_event_loop().time(),
            "update_id": update_count
        }

        # ⑤ 手动构建 SSE 事件块（关键！）
        # 格式：event: tick\nid: 1\ndata: {"symbol":"AAPL",...}\n\n
        event_block = (
            f"event: tick\n"
            f"id: {update_count}\n"
            f"data: {json.dumps(data)}\n\n"
        )
        yield event_block

        # ⑥ 随机等待 0.8~2.0 秒
        await asyncio.sleep(random.uniform(0.8, 2.0))

    # ⑦ 发送结束信号（如果需要）
    yield f"event: done\ndata: {json.dumps({'type': 'end', 'total': update_count})}\n\n"


# ============================================================
# SSE 路由（使用 StreamingResponse）
# ============================================================
@app.get("/stocks/stream")
async def stream_stocks(request: Request):
    return StreamingResponse(
        stock_price_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# ============================================================
# 前端页面（根目录）
# ============================================================
@app.get("/")
async def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>📈 实时股票看板</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #0d1117; color: #e6edf3; padding: 30px; max-width: 800px; margin: 0 auto; }
            h1 { text-align: center; color: #58a6ff; }
            .status { text-align: center; color: #8b949e; font-size: 14px; margin-bottom: 20px; }
            .board { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
            .card { background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; text-align: center; }
            .card .symbol { font-size: 20px; font-weight: bold; color: #58a6ff; }
            .card .price { font-size: 32px; font-weight: bold; margin: 10px 0; }
            .card .change { font-size: 16px; font-weight: 600; }
            .card .change.up { color: #3fb950; }
            .card .change.down { color: #f85149; }
            .card .change.flat { color: #8b949e; }
            .update-info { text-align: center; margin-top: 20px; color: #8b949e; font-size: 13px; }
        </style>
    </head>
    <body>
        <h1>📈 实时行情看板</h1>
        <div class="status" id="status">⏳ 连接中...</div>
        <div class="board" id="board"></div>
        <div class="update-info" id="info">等待数据...</div>
        <script>
            const board = document.getElementById('board');
            const statusDiv = document.getElementById('status');
            const infoDiv = document.getElementById('info');
            const symbols = ['AAPL', 'TSLA', 'NVDA'];
            const cardMap = {};
            symbols.forEach(sym => {
                const card = document.createElement('div');
                card.className = 'card';
                card.id = `card-${sym}`;
                card.innerHTML = `
                    <div class="symbol">${sym}</div>
                    <div class="price" id="price-${sym}">--</div>
                    <div class="change" id="change-${sym}">等待数据...</div>
                `;
                board.appendChild(card);
                cardMap[sym] = card;
            });

            const source = new EventSource('/stocks/stream');
            source.addEventListener('tick', function(e) {
                const data = JSON.parse(e.data);
                const priceEl = document.getElementById(`price-${data.symbol}`);
                const changeEl = document.getElementById(`change-${data.symbol}`);
                priceEl.textContent = `$${data.price.toFixed(2)}`;
                const changeText = `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)} (${data.change_percent >= 0 ? '+' : ''}${data.change_percent.toFixed(2)}%)`;
                changeEl.textContent = changeText;
                changeEl.className = 'change';
                if (data.change > 0) changeEl.classList.add('up');
                else if (data.change < 0) changeEl.classList.add('down');
                else changeEl.classList.add('flat');
                statusDiv.textContent = `🟢 已接收 ${data.update_id} 条更新`;
                infoDiv.textContent = `⏱️ 最新更新: ${data.symbol} @ $${data.price.toFixed(2)}`;
            });
            source.onopen = () => statusDiv.textContent = '🟢 连接已建立，等待行情数据...';
            source.onerror = () => {
                if (source.readyState === EventSource.CLOSED) statusDiv.textContent = '🔴 连接已关闭';
                else statusDiv.textContent = '🔄 连接中断，自动重连中...';
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)