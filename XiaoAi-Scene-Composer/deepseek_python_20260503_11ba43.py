import time
import json

# 模拟家庭设备库
DEVICES = {
    "light.living": {"name": "客厅灯", "type": "light", "capabilities": ["on", "off", "brightness"]},
    "light.bedroom": {"name": "卧室灯", "type": "light", "capabilities": ["on", "off", "brightness"]},
    "ac.living": {"name": "客厅空调", "type": "air_conditioner", "capabilities": ["on", "off", "mode", "temperature"]},
    "curtain.living": {"name": "客厅窗帘", "type": "curtain", "capabilities": ["open", "close"]},
    "camera.gate": {"name": "门口摄像头", "type": "camera", "capabilities": ["on", "off", "record"]},
    "lock.door": {"name": "大门锁", "type": "lock", "capabilities": ["lock", "unlock"]},
    "sensor.motion": {"name": "人体传感器", "type": "sensor", "capabilities": ["motion_detect"]},
}

# 已存在场景（用于冲突检测）
EXISTING_SCENES = [
    {
        "name": "回家模式",
        "trigger": "lock.door.unlock",
        "actions": [{"device": "light.living", "command": "on"}, {"device": "ac.living", "command": "on"}]
    }
]

def get_all_devices() -> dict:
    """获取家庭所有设备及其能力"""
    return DEVICES

def get_device_state(device_id: str) -> dict:
    """查询单个设备当前状态（模拟）"""
    dev = DEVICES.get(device_id)
    if not dev:
        return {"error": "device not found"}
    if dev["type"] == "light":
        state = {"on": True, "brightness": 80}
    elif dev["type"] == "air_conditioner":
        state = {"on": False, "mode": "cool", "temperature": 26}
    elif dev["type"] == "curtain":
        state = {"open": True}
    elif dev["type"] == "camera":
        state = {"on": True, "record": False}
    elif dev["type"] == "lock":
        state = {"locked": True}
    elif dev["type"] == "sensor":
        state = {"motion_detected": False}
    else:
        state = {}
    return {"device_id": device_id, "name": dev["name"], "state": state}

def validate_scene(scene_json: str) -> dict:
    """验证场景定义的合法性并检测冲突"""
    try:
        scene = json.loads(scene_json)
    except:
        return {"valid": False, "reason": "JSON 格式错误"}
    
    required = ["name", "trigger", "actions"]
    for key in required:
        if key not in scene:
            return {"valid": False, "reason": f"缺少关键字段: {key}"}
    
    # 检测冲突：是否与已有场景形成死循环
    for existing in EXISTING_SCENES:
        # 简单检测：如果新场景的触发条件会激活旧场景的动作，且旧场景动作又会触发新场景，则为死循环
        if scene["trigger"] == existing["trigger"]:
            return {"valid": False, "reason": f"触发条件与已有场景'{existing['name']}'重复，可能冲突"}
        for action in scene["actions"]:
            if action["device"] == existing["trigger"].split(".")[0] and action["command"] == existing["trigger"].split(".")[-1]:
                return {"valid": False, "reason": f"动作可能触发已有场景'{existing['name']}'，形成循环"}
    
    # 检测设备是否存在
    for action in scene["actions"]:
        if action["device"] not in DEVICES:
            return {"valid": False, "reason": f"设备 {action['device']} 不存在"}
    
    # 检测能力是否匹配
    for action in scene["actions"]:
        dev = DEVICES[action["device"]]
        if action["command"] not in dev["capabilities"]:
            return {"valid": False, "reason": f"设备 {dev['name']} 不支持命令 {action['command']}"}
    
    return {"valid": True}

def simulate_scene(scene_json: str) -> dict:
    """模拟执行场景，返回执行前后设备状态变化"""
    scene = json.loads(scene_json)
    result = {"executed": True, "changes": []}
    for action in scene["actions"]:
        dev_id = action["device"]
        cmd = action["command"]
        before = get_device_state(dev_id)
        # 模拟状态改变
        time.sleep(0.1)
        after = get_device_state(dev_id)
        # 模拟实际状态更新
        if cmd == "on":
            after["state"]["on"] = True
        elif cmd == "off":
            after["state"]["on"] = False
        # 其他命令简化为状态变更
        result["changes"].append({
            "device": dev_id,
            "before": before["state"],
            "after": after["state"],
            "status": "ok" if device_reachable(dev_id) else "fail"
        })
    return result

def device_reachable(device_id: str) -> bool:
    """模拟设备在线检测（假设都在线）"""
    return True

TOOLS_MAP = {
    "get_all_devices": get_all_devices,
    "get_device_state": get_device_state,
    "validate_scene": validate_scene,
    "simulate_scene": simulate_scene
}