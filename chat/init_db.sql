-- ============================================================
-- AI 对话助手数据库初始化脚本
-- 数据库：SQLite
-- ============================================================

-- 开启外键约束（SQLite 默认关闭，必须手动开）
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. 建表
-- ============================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 对话表
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- ============================================================
-- 2. 索引（加速常用查询）
-- ============================================================

-- username 唯一索引（登录时查）
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 查某个用户的所有对话
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- 查某个对话的所有消息
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- 按对话 + 时间排序（最常用）
CREATE INDEX IF NOT EXISTS idx_messages_conv_created ON messages(conversation_id, created_at);

-- ============================================================
-- 3. 插入测试数据
-- ============================================================

-- -------------------- 用户 --------------------
-- 注：这里的 hashed_password 是 "secret123" 的 bcrypt 哈希示例
-- 真实的哈希需要通过 passlib.hash.bcrypt 生成
INSERT INTO users (username, hashed_password) VALUES
('alice', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lqZ5mL5F6JfK'),
('bob',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lqZ5mL5F6JfK'),
('carol', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lqZ5mL5F6JfK');

-- -------------------- 对话 --------------------
-- alice 的两个对话
INSERT INTO conversations (user_id, title) VALUES
(1, '关于 Python 异步编程'),
(1, '周末去哪玩');

-- bob 的一个对话
INSERT INTO conversations (user_id, title) VALUES
(2, '学习 FastAPI');

-- carol 的两个对话
INSERT INTO conversations (user_id, title) VALUES
(3, 'AI 应用开发路线'),
(3, '如何准备面试');

-- -------------------- 消息 --------------------
-- 对话 1：alice 问 Python 异步
INSERT INTO messages (conversation_id, role, content) VALUES
(1, 'user',      '你好，我想学 Python 的异步编程'),
(1, 'assistant', '你好！很高兴见到你，有什么我可以帮你的吗？'),
(1, 'user',      'async/await 到底是怎么回事？'),
(1, 'assistant', 'async 标记函数为协程，await 让它在等待 I/O 时让出 CPU 给事件循环。');

-- 对话 2：alice 问天气
INSERT INTO messages (conversation_id, role, content) VALUES
(2, 'user',      '今天天气怎么样'),
(2, 'assistant', '今天天气不错，阳光明媚。不过我没有联网获取实时天气的能力。');

-- 对话 3：bob 学 FastAPI
INSERT INTO messages (conversation_id, role, content) VALUES
(3, 'user',      'FastAPI 和 Flask 有什么区别'),
(3, 'assistant', 'FastAPI 原生支持异步，性能更好，还有自动生成的 API 文档。');

-- 对话 4：carol 问路线
INSERT INTO messages (conversation_id, role, content) VALUES
(4, 'user',      'AI 应用开发需要学什么'),
(4, 'assistant', '我理解你的问题，作为演示版机器人，我的知识有限。');

-- 对话 5：carol 问面试
INSERT INTO messages (conversation_id, role, content) VALUES
(5, 'user',      '面试要准备什么'),
(5, 'assistant', '我理解你的问题，作为演示版机器人，我的知识有限。');