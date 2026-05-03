import json
from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from tools import TOOLS_MAP

SYSTEM_PROMPT = """你是小爱场景智能编排系统，由4个专用Agent协作完成用户需求：

1. 需求解析Agent：理解用户自然语言，提取意图（触发条件、期望动作、涉及设备）
2. 设备能力Agent：调用 get_all_devices 获取家庭设备列表，调用 get_device_state 查询状态
3. 场景编排Agent：生成符合小米规则引擎的场景JSON，调用 validate_scene 验证合法性
4. 闭环验证Agent：调用 simulate_scene 模拟执行，检查设备状态变化是否达到预期
   若验证失败，回溯到编排Agent修正JSON后重试，直到成功或给出失败原因

你必须遵循长链推理流程：解析需求 → 查询设备 → 生成场景 → 验证冲突 → 模拟执行 → 检查结果 → 修正重试。
每次只调用一个工具，观察结果后再决定下一步。最终输出完整场景JSON和自然语言说明。"""

class SceneOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def run(self, user_query: str) -> str:
        self.messages.append({"role": "user", "content": user_query})
        
        for iteration in range(15):
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
                    print(f"\n🔧 [第{iteration+1}轮] 调用工具: {func_name}")
                    print(f"   参数: {json.dumps(args, ensure_ascii=False)}")
                    
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
                    print(f"📦 返回: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                final = msg.content
                self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                return final
        
        return "❌ 场景编排超时，请尝试简化您的需求。"

    def _tool_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_all_devices",
                    "description": "获取家庭中所有智能设备及其能力和类型",
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
                            "device_id": {"type": "string", "description": "设备ID，如 light.living"}
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_scene",
                    "description": "验证场景JSON定义的合法性，检测与已有场景的冲突和死循环",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scene_json": {"type": "string", "description": "场景定义的JSON字符串"}
                        },
                        "required": ["scene_json"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "simulate_scene",
                    "description": "在模拟环境中执行场景，返回设备状态变化",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scene_json": {"type": "string", "description": "场景定义的JSON字符串"}
                        },
                        "required": ["scene_json"]
                    }
                }
            }
        ]