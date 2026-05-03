"""
小爱场景智能编排与自愈 Agent
用法：
  python main.py --mode mock
  python main.py --mode real --query "我离开家时关掉所有灯和空调，打开摄像头"
"""

import argparse
import time

def mock_run(query):
    print("=" * 60)
    print("  小爱场景智能编排与自愈 Agent (模拟模式)")
    print("=" * 60)
    print(f"\n📝 用户需求: {query}\n")
    
    steps = [
        ("需求解析Agent", "提取意图 → 触发条件: 用户离家, 动作: 关灯/关空调/开摄像头"),
        ("设备能力Agent", "查询家庭设备 → 发现: 客厅灯、卧室灯、客厅空调、门口摄像头"),
        ("场景编排Agent", "生成场景JSON → 4个动作, 触发条件: lock.door.lock"),
        ("验证Agent", "冲突检测 → 无死循环 ✓, 设备能力匹配 ✓"),
        ("模拟执行Agent", "执行场景 → 灯关 ✓, 空调关 ✓, 摄像头开 ✓"),
        ("状态检查Agent", "设备状态验证 → 全部符合预期 ✓"),
        ("最终输出", "✅ 场景'离家模式'创建成功, 耗时28秒"),
    ]
    
    for agent, msg in steps:
        print(f"  [{agent}] {msg}")
        time.sleep(0.3)
    
    print("\n" + "=" * 60)
    print("  场景JSON定义:")
    print("=" * 60)
    scene = {
        "name": "离家模式",
        "trigger": "lock.door.lock",
        "actions": [
            {"device": "light.living", "command": "off"},
            {"device": "light.bedroom", "command": "off"},
            {"device": "ac.living", "command": "off"},
            {"device": "camera.gate", "command": "on"}
        ]
    }
    import json
    print(json.dumps(scene, ensure_ascii=False, indent=2))
    print("\n  Token消耗: ~18,500 | 推理轮次: 7 | 状态: 成功 ✅")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小爱场景智能编排Agent")
    parser.add_argument("--mode", choices=["real", "mock"], default="mock",
                       help="mock=模拟演示, real=调用真实LLM")
    parser.add_argument("--query", type=str, 
                       default="我离开家时关掉所有灯和空调，打开摄像头",
                       help="自然语言场景需求")
    args = parser.parse_args()

    if args.mode == "mock":
        mock_run(args.query)
    else:
        from orchestrator import SceneOrchestrator
        print("=" * 60)
        print("  小爱场景智能编排与自愈 Agent (真实模式)")
        print("  模型:", __import__('config').LLM_MODEL)
        print("=" * 60)
        print(f"\n📝 用户需求: {args.query}\n")
        
        orch = SceneOrchestrator()
        final = orch.run(args.query)
        
        print("\n" + "=" * 60)
        print("  🎉 最终编排结果:")
        print("=" * 60)
        print(final)