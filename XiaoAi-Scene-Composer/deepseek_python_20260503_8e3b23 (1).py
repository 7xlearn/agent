import json
from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from tools import TOOLS_MAP

SYSTEM_PROMPT = """你是小爱场景智能编排系统，由4个专用 Agent 协作：
1. 解析用户需求，提取意图
2. 调用设备查询工具获取家庭设备信息
3. 生成场景 JSON 并验证冲突
4. 模拟执行并观察结果，若失败则修正后重试

你必须严格遵循长链推理：获得需求 → 查询设备 → 生成场景 → 验证 → 模拟 → 检查结果 → 修正直到成功。
使用提供的工具函数完成每一步，最终输出用户可直接使用的场景 JSON 和自然语言说明。
工具函数：
- get_all_devices() 获取所有设备
- get_device_state(device_id) 获取设备状态
- validate_scene(scene_json) 验证场景合法性
- simulate_scene(scene_json) 模拟执行场景
"""

class SceneOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def run(self, user_query: str) -> str:
        self.messages.append({"role": "user", "content": user_query})
        
        for _ in range(15):  # 最多15轮
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=self.messages,
                tools=self._tool_schema(),
                tool_choice="auto",
                temperature=0.2
            )
            msg = response.choices[0].message
            self.messages.append(msg)
            
            if msg.tool_calls:
                for tool in msg.tool_calls:
                    func_name = tool.function.name
                    args = json.loads(tool.function.arguments)
                    print(f"🔧 Agent调用工具: {func_name}")
                    func = TOOLS_MAP[func_name]
                    if args:
                        result = func(**args)
                    else:
                        result = func()
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                    print(f"📦 工具返回: {result}")
            else:
                # 最终答案
                final = msg.content
                self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                return final
        return "场景编排超时，请简化需求。"

    def _tool_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_all_devices",
                    "description": "获取家庭中所有智能设备及其能力",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_device_state",
                    "description": "查询指定设备的当前状态",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string", "description": "设备ID"}
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_scene",
                    "description": "验证场景JSON定义是否合法、是否有冲突",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scene_json": {"type": "string", "description": "场景的JSON字符串"}
                        },
                        "required": ["scene_json"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "simulate_scene",
                    "description": "模拟执行场景，查看设备变化",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scene_json": {"type": "string", "description": "场景的JSON字符串"}
                        },
                        "required": ["scene_json"]
                    }
                }
            }
        ]