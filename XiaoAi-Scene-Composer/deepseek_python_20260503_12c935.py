import argparse
import time

def mock_run(query):
    print(f"用户需求: {query}\n")
    print("🤖 多Agent场景编排系统启动...\n")
    steps = [
        ("需求解析Agent", "意图: 离家时关闭所有灯和空调，打开摄像头"),
        ("设备能力Agent", "发现设备: 客厅灯、卧室灯、客厅空调、门口摄像头"),
        ("场景编排Agent", "生成场景JSON..."),
        ("验证Agent", "冲突检测通过 ✓"),
        ("模拟执行Agent", "执行场景: 灯→关, 空调→关, 摄像头→开"),
        ("状态检查Agent", "所有设备状态符合预期 ✓"),
        ("最终输出", "场景“离家模式”创建成功，耗时28秒")
    ]
    for agent, msg in steps:
        print(f"[{agent}] {msg}")
        time.sleep(0.2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["real", "mock"], default="mock")
    parser.add_argument("--query", default="我离开家时关掉所有灯和空调，打开摄像头")
    args = parser.parse_args()

    if args.mode == "mock":
        mock_run(args.query)
    else:
        from orchestrator import SceneOrchestrator
        orch = SceneOrchestrator()
        final = orch.run(args.query)
        print("\n🎉 编排结果:")
        print(final)