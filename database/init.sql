-- DEWETRON 数据采集器数据库初始化脚本
-- 支持批次管理 + 命令执行追踪

PRAGMA busy_timeout = 5000;

-- 测试批次表（一次完整测试，可能包含多次追加）
CREATE TABLE IF NOT EXISTS de_test_batch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_uid TEXT UNIQUE NOT NULL,  -- 唯一标识，如 'flicker_20260714_132524'
    test_type TEXT NOT NULL,         -- 'flicker' / 'harmonic' / 'dewetron'
    total_versions INTEGER DEFAULT 0, -- 该批次总共多少次追加
    start_time TEXT,                 -- 批次开始时间
    end_time TEXT,                   -- 批次结束时间
    save_path TEXT                   -- CSV 保存路径
);

-- 测试记录表（每次追加一条记录）
CREATE TABLE IF NOT EXISTS de_test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,       -- 关联 de_test_batch.id
    version INTEGER NOT NULL,        -- 在该批次内的版本号（第几次追加）
    start_time TEXT,
    end_time TEXT,
    total_rows INTEGER DEFAULT 0,
    csv_header TEXT,
    UNIQUE(batch_id, version)        -- 同批次+版本唯一
);

-- 命令表（每条测试命令）
CREATE TABLE IF NOT EXISTS de_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,         -- 关联 de_test_runs.id
    seq INTEGER NOT NULL,            -- 命令序号（从1开始）
    device TEXT NOT NULL,            -- 设备: 'AC' / 'DC1' / 'DC2' / 'DEWETRON' 等
    operation TEXT NOT NULL,         -- 操作: 'write' / 'query'
    command TEXT NOT NULL,           -- SCPI 命令
    param1 TEXT,                     -- 参数1（如等待时间）
    param2 TEXT,                     -- 参数2
    param3 TEXT,                     -- 参数3
    param4 TEXT,                     -- 参数4
    param5 TEXT,                     -- 参数5
    param6 TEXT,                     -- 参数6
    param7 TEXT,                     -- 参数7
    raw_row TEXT,                    -- 原始10列命令JSON（无损回放）
    wait_time INTEGER DEFAULT 0,     -- 等待时间（0.1秒单位，兼容旧记录）
    executed INTEGER DEFAULT 0,      -- 是否已执行: 0=未执行, 1=已执行
    execute_time TEXT,               -- 执行时间
    execute_result TEXT,             -- 执行结果
    FOREIGN KEY (run_id) REFERENCES de_test_runs(id)
);

-- 数据表（结构固定，通过 run_id 关联）
CREATE TABLE IF NOT EXISTS de_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,         -- 关联 de_test_runs.id
    seq INTEGER,                     -- 序号（第几条数据）
    time REAL,                       -- 相对时间（秒）
    channel_values TEXT,             -- JSON 数组: '[1.23, 4.56, ...]'
    FOREIGN KEY (run_id) REFERENCES de_test_runs(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_de_test_runs_batch_id ON de_test_runs(batch_id);
CREATE INDEX IF NOT EXISTS idx_de_data_run_id ON de_data(run_id);
CREATE INDEX IF NOT EXISTS idx_de_test_batch_uid ON de_test_batch(batch_uid);
CREATE INDEX IF NOT EXISTS idx_de_commands_run_id ON de_commands(run_id);
CREATE INDEX IF NOT EXISTS idx_de_commands_executed ON de_commands(executed);
