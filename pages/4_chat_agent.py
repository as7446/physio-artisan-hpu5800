"""
Page 4: AI对话智能体
支持多模态输入，实时展示Agent调用链

功能:
- 文本/图片/视频上传
- 实时Agent调用链可视化
- 语音报告播放
- 显示各Agent使用的AI模型
"""

import streamlit as st
import sys
import os
import time
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 页面配置
st.set_page_config(
    page_title="AI对话 | HPU健康智能体",
    page_icon="💬",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background: white;
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .tool-call {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .agent-node {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        display: inline-block;
        margin: 0.3rem;
    }
    .upload-zone {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
    }
    .model-badge {
        background: #e9ecef;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.75rem;
        color: #666;
    }
    .model-badge-openai { background: #10a37f; color: white; }
    .model-badge-zhipu { background: #7c3aed; color: white; }
    .model-badge-anthropic { background: #d97706; color: white; }
    .model-badge-azure { background: #0078d4; color: white; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent_chain' not in st.session_state:
        st.session_state.agent_chain = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}


def add_user_message(content, files=None):
    """添加用户消息"""
    message = {
        'role': 'user',
        'content': content,
        'files': files,
        'timestamp': datetime.now().strftime("%H:%M")
    }
    st.session_state.messages.append(message)


def add_assistant_message(content, tool_calls=None, agent=None, provider=None, model=None):
    """添加助手消息"""
    message = {
        'role': 'assistant',
        'content': content,
        'tool_calls': tool_calls or [],
        'agent': agent,
        'provider': provider,
        'model': model,
        'timestamp': datetime.now().strftime("%H:%M")
    }
    st.session_state.messages.append(message)


def add_tool_call(tool_name, args, result):
    """添加工具调用记录"""
    st.session_state.agent_chain.append({
        'tool': tool_name,
        'args': args,
        'result': result,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })


def get_model_badge(provider: str, model: str) -> str:
    """获取模型徽章"""
    badges = {
        'openai': f'<span class="model-badge model-badge-openai">🤖 {model}</span>',
        'zhipu': f'<span class="model-badge model-badge-zhipu">🧠 {model}</span>',
        'anthropic': f'<span class="model-badge model-badge-anthropic">🧩 {model}</span>',
        'azure': f'<span class="model-badge model-badge-azure">☁️ {model}</span>',
    }
    return badges.get(provider, f'<span class="model-badge">🎭 {model}</span>')


def simulate_agent_response(user_input, files=None):
    """模拟Agent响应，使用AI管理器"""
    
    # 获取AI配置
    try:
        from src.ai.provider_manager import get_ai_manager
        ai_manager = get_ai_manager()
        agent_config = ai_manager.get_agent_config()
    except:
        agent_config = {}
    
    # 模拟不同类型的响应
    responses = {
        '训练': {
            'content': """根据您上传的数据，我为您制定了以下训练计划：

**今日训练: 下肢力量**

1. **深蹲** 4组 x 12次 (组间休息60秒)
2. **硬拉** 3组 x 10次
3. **腿举** 3组 x 15次
4. **保加利亚蹲** 3组 x 10次/侧

⚠️ 注意保持核心收紧，避免塌腰""",
            'tools': [
                {'name': 'calculate_TDEE', 'args': {'age': 28, 'weight': 72, 'height': 175}, 'result': '2450 kcal'},
                {'name': 'get_exercise_library', 'args': {'type': 'legs'}, 'result': '5 exercises'},
            ],
            'agent': 'ExerciseCoach',
            'provider': 'openai',
            'model': 'gpt-4-turbo'
        },
        '饮食': {
            'content': """基于您的目标和活动量，我推荐以下饮食方案：

**每日摄入: 2000 kcal**

**宏量营养素分配:**
- 🥩 蛋白质: 160g (640 kcal)
- 🍚 碳水: 200g (800 kcal)  
- 🫒 脂肪: 65g (585 kcal)

**餐次安排:**
- 早餐: 400 kcal (鸡蛋、全麦面包)
- 午餐: 600 kcal (鸡胸肉、糙米)
- 加餐: 200 kcal (蛋白粉、香蕉)
- 晚餐: 500 kcal (鱼、蔬菜)
- 训练后: 300 kcal (碳水+蛋白)""",
            'tools': [
                {'name': 'query_USDA', 'args': {'food': 'chicken breast'}, 'result': '165 kcal/100g'},
                {'name': 'calculate_macros', 'args': {'protein': 160, 'carbs': 200}, 'result': '2000 kcal'},
            ],
            'agent': 'NutritionPlanner',
            'provider': 'zhipu',
            'model': 'glm-4-plus'
        },
        '睡眠': {
            'content': """根据您的手表数据分析：

**睡眠质量评估: 良好 (78分)**

- 🌙 总睡眠: 7小时30分钟
- 😴 深睡眠: 1小时45分钟 (23%)
- 💤 浅睡眠: 5小时15分钟 (70%)
- ⏰ 快速眼动: 30分钟 (7%)

**建议:**
1. 建议睡前1小时停止使用电子设备
2. 保持卧室温度在18-20°C
3. 今晚可提前30分钟入睡""",
            'tools': [
                {'name': 'analyze_sleep_data', 'args': {'hrv': 38, 'resting_hr': 58}, 'result': 'sleep_score: 78'},
            ],
            'agent': 'StateEvaluator',
            'provider': 'zhipu',
            'model': 'glm-4'
        }
    }
    
    # 根据输入内容匹配响应
    user_lower = user_input.lower()
    for key, response in responses.items():
        if key in user_lower:
            # 获取实际的Agent配置
            agent_name = response['agent']
            if agent_config:
                cfg = agent_config.get(agent_name, {})
                provider = cfg.get('provider', response['provider'])
                model = cfg.get('model', response['model'])
            else:
                provider = response['provider']
                model = response['model']
            
            # 添加工具调用
            for tool in response['tools']:
                add_tool_call(tool['name'], tool['args'], tool['result'])
            
            add_assistant_message(
                response['content'], 
                response['tools'], 
                agent_name,
                provider,
                model
            )
            return
    
    # 默认响应
    default_response = """我理解您的需求。作为HPU健康智能体，我可以帮助您：

🔹 **分析您的健康数据** - 上传手表JSON查看身体状态
🔹 **制定训练计划** - 基于您的目标和体能
🔹 **规划饮食方案** - 计算卡路里和营养素
🔹 **评估运动动作** - 上传视频分析深蹲等动作

请告诉我您需要哪方面的帮助？"""

    # 使用主助手的模型
    if agent_config:
        cfg = agent_config.get('HPUAssistant', {})
        provider = cfg.get('provider', 'mock')
        model = cfg.get('model', 'mock-gpt')
    else:
        provider = 'mock'
        model = 'mock-gpt'

    add_assistant_message(default_response, [], 'HPUAssistant', provider, model)


def render_message(message):
    """渲染单条消息"""
    if message['role'] == 'user':
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 您</strong> <span style="opacity:0.7;font-size:0.8rem">{message['timestamp']}</span>
            <p>{message['content']}</p>
            {f"<small>📎 附件: {len(message.get('files', []))} 个文件</small>" if message.get('files') else ""}
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.container():
            # Agent和模型信息
            agent_html = f'<span class="agent-node">{message.get("agent", "HPUAssistant")}</span>'
            if message.get('provider') and message.get('model'):
                agent_html += get_model_badge(message.get('provider'), message.get('model'))
            
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 HPU智能体</strong> {agent_html}
                <span style="opacity:0.7;font-size:0.8rem">{message['timestamp']}</span>
                <p>{message['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示工具调用
            if message.get('tool_calls'):
                st.markdown("**🔧 工具调用:**")
                for tool in message['tool_calls']:
                    st.markdown(f"""
                    <div class="tool-call">
                        <strong>⚡ {tool['name']}</strong><br>
                        <small>参数: {json.dumps(tool['args'], ensure_ascii=False)}</small><br>
                        <small>结果: {tool['result']}</small>
                    </div>
                    """, unsafe_allow_html=True)


def render_agent_chain():
    """渲染Agent调用链"""
    if not st.session_state.agent_chain:
        return
    
    st.markdown("### 🔄 Agent调用链")
    
    chain_html = """
    <div style="display:flex;flex-wrap:wrap;align-items:center;gap:5px;padding:1rem;background:#f8f9fa;border-radius:10px;">
    """
    
    for i, call in enumerate(st.session_state.agent_chain):
        chain_html += f"""
        <div class="agent-node">{call['tool']}</div>
        """
        if i < len(st.session_state.agent_chain) - 1:
            chain_html += '<span style="font-size:1.5rem;color:#667eea;">→</span>'
    
    chain_html += """
    </div>
    """
    st.markdown(chain_html, unsafe_allow_html=True)
    
    # 详细日志
    with st.expander("📋 查看详细调用日志"):
        for call in st.session_state.agent_chain:
            st.json({
                'time': call['timestamp'],
                'tool': call['tool'],
                'args': call['args'],
                'result': call['result']
            })


def main():
    init_session_state()
    
    # 页面标题
    st.markdown("## 💬 AI对话智能体")
    st.markdown("*上传数据，智能体自动分析并生成建议*")
    
    # 布局: 左侧对话，右侧上传和调用链
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # 对话区域
        st.markdown("### 对话记录")
        
        # 消息容器
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                render_message(msg)
        
        # 清空按钮
        if st.session_state.messages and st.button("🗑️ 清空对话"):
            st.session_state.messages = []
            st.session_state.agent_chain = []
            st.session_state.clear_chat = True
    
    # Handle clear after render
    if st.session_state.get("clear_chat"):
        del st.session_state["clear_chat"]
    
    with col_right:
        # 文件上传区
        st.markdown("### 📎 附件上传")
        
        with st.expander("上传文件", expanded=True):
            uploaded_video = st.file_uploader(
                "运动视频 (MP4)", 
                type=['mp4', 'avi'],
                help="上传运动视频进行动作分析"
            )
            
            uploaded_image = st.file_uploader(
                "图片 (JPG/PNG)", 
                type=['jpg', 'jpeg', 'png'],
                help="上传食物图片进行营养识别"
            )
            
            uploaded_json = st.file_uploader(
                "手表数据 (JSON)", 
                type=['json'],
                help="上传华为手表导出的数据"
            )
            
            if uploaded_video or uploaded_image or uploaded_json:
                st.success("✅ 文件已上传，将在对话中自动分析")
        
        # 调用链可视化
        st.divider()
        render_agent_chain()
        
        # 快捷输入
        st.markdown("### ⚡ 快捷问题")
        quick_questions = [
            "分析我的训练计划",
            "制定今天的饮食方案", 
            "评估我的睡眠质量",
            "深蹲动作有什么问题"
        ]
        
        for q in quick_questions:
            if st.button(q, use_container_width=True, key=f"quick_{q}"):
                add_user_message(q)
                with st.spinner("🤔 智能体正在思考..."):
                    time.sleep(1)
                    simulate_agent_response(q)
                st.session_state.quick_sent = True

    # Handle quick sent
    if st.session_state.get("quick_sent"):
        del st.session_state["quick_sent"]
    
    # 输入区域
    st.divider()
    
    # 创建输入表单
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        
        with col_input:
            user_input = st.text_area(
                "输入您的问题:",
                placeholder="例如: 帮我分析今天的深蹲动作，或者推荐今天的饮食方案...",
                height=80,
                label_visibility="collapsed"
            )
        
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 发送", use_container_width=True)
        
        if submitted and user_input:
            add_user_message(user_input)
            
            with st.spinner("🤔 智能体正在分析..."):
                time.sleep(1.5)
                simulate_agent_response(user_input)
            # st.rerun()
            st.session_state.message_sent = True

    if st.session_state.get("message_sent"):
        del st.session_state["message_sent"]
    
    # 使用说明
    with st.expander("ℹ️ 使用说明"):
        st.markdown("""
        **如何使用AI对话:**
        
        1. 在下方输入您的问题或需求
        2. 可以上传运动视频、图片或手表数据作为附件
        3. 智能体将自动分析并调用相关工具
        4. 右侧可实时查看Agent调用链
        
        **支持的查询:**
        - 训练相关: "分析训练计划"、"推荐动作"
        - 饮食相关: "制定饮食方案"、"计算热量"
        - 睡眠相关: "评估睡眠质量"、"改善建议"
        """)


if __name__ == "__main__":
    main()
