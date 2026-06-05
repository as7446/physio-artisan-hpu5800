"""
设置页面: API配置 + 用户管理 + Agent AI绑定
"""

import streamlit as st
import sys
import os
import hashlib
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 页面配置
st.set_page_config(
    page_title="设置 | HPU健康智能体",
    page_icon="⚙️",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .config-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    .status-ok { color: #28A745; font-weight: bold; }
    .status-warn { color: #FFC107; font-weight: bold; }
    .status-error { color: #DC3545; font-weight: bold; }
    .api-key-input input { font-family: monospace; }
</style>
""", unsafe_allow_html=True)


def get_ai_config():
    """获取AI配置"""
    try:
        from src.ai.provider_manager import get_ai_manager
        return get_ai_manager()
    except:
        return None


def get_api_config():
    """获取API配置"""
    return {
        'openai': {
            'name': 'OpenAI API',
            'key': os.getenv('OPENAI_API_KEY', ''),
            'endpoint': os.getenv('OPENAI_ENDPOINT', 'https://api.openai.com/v1'),
            'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o'],
            'status': '✅ 已配置' if os.getenv('OPENAI_API_KEY') else '⚠️ 未配置'
        },
        'zhipu': {
            'name': '智谱AI (GLM)',
            'key': os.getenv('ZHIPU_API_KEY', ''),
            'endpoint': 'https://open.bigmodel.cn/api/paas/v4',
            'models': ['glm-4', 'glm-4-plus', 'glm-4v', 'glm-3-turbo'],
            'status': '✅ 已配置' if os.getenv('ZHIPU_API_KEY') else '⚠️ 未配置'
        },
        'anthropic': {
            'name': 'Anthropic (Claude)',
            'key': os.getenv('ANTHROPIC_API_KEY', ''),
            'endpoint': 'https://api.anthropic.com/v1',
            'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            'status': '✅ 已配置' if os.getenv('ANTHROPIC_API_KEY') else '⚠️ 未配置'
        },
        'azure': {
            'name': 'Azure OpenAI',
            'key': os.getenv('AZURE_API_KEY', ''),
            'endpoint': os.getenv('AZURE_ENDPOINT', ''),
            'models': ['gpt-4', 'gpt-35-turbo'],
            'status': '✅ 已配置' if os.getenv('AZURE_API_KEY') else '⚠️ 未配置'
        },
        'usda': {
            'name': 'USDA FoodData Central',
            'key': os.getenv('USDA_API_KEY', ''),
            'endpoint': 'https://api.nal.usda.gov/fdc/v1',
            'models': [],
            'status': '✅ 已配置' if os.getenv('USDA_API_KEY') else '⚠️ 未配置 (可选)'
        }
    }


def get_custom_apis():
    """获取自定义API配置"""
    custom = []
    for i in range(5):  # 支持5个自定义API
        prefix = f'CUSTOM_{i+1}'
        name = os.getenv(f'{prefix}_NAME')
        if name:
            custom.append({
                'index': i + 1,
                'name': name,
                'key': os.getenv(f'{prefix}_API_KEY', ''),
                'endpoint': os.getenv(f'{prefix}_ENDPOINT', ''),
                'models': os.getenv(f'{prefix}_MODELS', '').split(',') if os.getenv(f'{prefix}_MODELS') else [],
                'status': '✅ 已配置' if os.getenv(f'{prefix}_API_KEY') else '⚠️ 未配置'
            })
    return custom


def save_custom_api(index, name, api_key, endpoint, models):
    """保存自定义API"""
    prefix = f'CUSTOM_{index}'
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

    # 读取现有配置
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value

    # 更新配置
    config[f'{prefix}_NAME'] = name
    config[f'{prefix}_API_KEY'] = api_key
    config[f'{prefix}_ENDPOINT'] = endpoint
    config[f'{prefix}_MODELS'] = ','.join(models) if models else ''

    # 写回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")


def save_api_key(provider, api_key):
    """保存API密钥到.env文件"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    # 读取现有配置
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value
    
    # 更新配置
    env_vars = {
        'openai': 'OPENAI_API_KEY',
        'zhipu': 'ZHIPU_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'azure': 'AZURE_API_KEY',
        'usda': 'USDA_API_KEY'
    }
    
    if provider in env_vars:
        config[env_vars[provider]] = api_key
        os.environ[env_vars[provider]] = api_key
    
    # 写回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")


def get_users():
    """获取所有用户"""
    try:
        from src.database.models import get_session, User
        session = get_session()
        users = session.query(User).all()
        session.close()
        return users
    except Exception as e:
        st.error(f"获取用户失败: {e}")
        return []


def delete_user(user_id):
    """删除用户"""
    try:
        from src.database.models import get_session, User
        session = get_session()
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            session.delete(user)
            session.commit()
            session.close()
            return True
        session.close()
        return False
    except Exception as e:
        st.error(f"删除用户失败: {e}")
        return False


def save_agent_config(agent_name: str, provider: str, model: str):
    """保存Agent配置"""
    try:
        from src.ai.provider_manager import get_ai_manager
        manager = get_ai_manager()
        manager.set_agent_provider(agent_name, provider)
        manager.set_agent_model(agent_name, model)
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False


def main():
    st.markdown("## ⚙️ 设置中心")
    st.markdown("*管理API配置、Agent模型绑定和用户账户*")

    # 标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agent模型绑定", "🔌 API配置", "👥 用户管理", "📋 系统信息"])

    with tab1:
        st.markdown("### 🤖 Agent AI模型绑定")
        st.info("💡 为每个Agent分配不同的AI模型和Provider，实现多模型协同工作")

        # Agent角色说明
        with st.expander("📖 Agent角色说明", expanded=False):
            st.markdown("""
            | Agent | 角色 | 建议模型 |
            |-------|------|---------|
            | **HPUAssistant** | 主对话助手，综合协调 | GPT-4 / Claude |
            | **StateEvaluator** | 状态评估，计算BMI/BMR | GPT-4-Turbo / GLM-4 |
            | **ExerciseCoach** | 训练教练，动作分析 | GPT-4-Vision / GLM-4V |
            | **NutritionPlanner** | 营养规划师，饮食建议 | GPT-4 / GLM-4 |
            | **GuardrailAuditor** | 安全审计，内容审核 | Claude (更严格) |
            """)

        ai_manager = get_ai_config()
        if ai_manager:
            agents = ['HPUAssistant', 'StateEvaluator', 'ExerciseCoach', 'NutritionPlanner', 'GuardrailAuditor']
            agent_names = {
                'HPUAssistant': '🏠 主助手',
                'StateEvaluator': '📊 状态评估',
                'ExerciseCoach': '💪 训练教练',
                'NutritionPlanner': '🍽️ 营养规划',
                'GuardrailAuditor': '🛡️ 安全审计'
            }

            # 当前配置
            config = ai_manager.get_agent_config()

            for agent in agents:
                agent_config = config.get(agent, {})
                available_models = agent_config.get('available_models', [])

                with st.container():
                    st.markdown(f"""
                    <div class="agent-card">
                        <h4>{agent_names.get(agent, agent)}</h4>
                        <p style="opacity:0.8;font-size:0.9rem;">{agent}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_provider, col_model, col_status, col_save = st.columns([2, 2, 1, 1])

                    with col_provider:
                        # 获取自定义API列表
                        custom_apis = get_custom_apis()
                        custom_options = [f"custom_{c['index']}" for c in custom_apis]

                        provider_options = ['openai', 'zhipu', 'anthropic', 'azure', 'mock'] + custom_options
                        provider_labels = {
                            'openai': '🤖 OpenAI',
                            'zhipu': '🧠 智谱AI',
                            'anthropic': '🧩 Claude',
                            'azure': '☁️ Azure',
                            'mock': '🎭 模拟'
                        }
                        # 添加自定义API标签
                        for c in custom_apis:
                            provider_labels[f"custom_{c['index']}"] = f"🔧 {c['name']}"

                        selected_provider = st.selectbox(
                            "Provider",
                            options=provider_options,
                            format_func=lambda x: provider_labels.get(x, x),
                            key=f"provider_{agent}"
                        )

                    with col_model:
                        # 根据provider获取可用模型
                        model_options_map = {
                            'openai': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o'],
                            'zhipu': ['glm-4', 'glm-4-plus', 'glm-4v', 'glm-3-turbo'],
                            'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
                            'azure': ['gpt-4', 'gpt-35-turbo'],
                            'mock': ['mock-gpt']
                        }
                        # 添加自定义API的模型
                        for c in custom_apis:
                            model_options_map[f"custom_{c['index']}"] = c['models'] if c['models'] else ['custom-model']

                        model_options = model_options_map.get(selected_provider, ['mock-gpt'])

                        selected_model = st.selectbox(
                            "模型",
                            options=model_options if model_options else ['custom-model'],
                            key=f"model_{agent}"
                        )

                    with col_status:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if agent_config.get('provider_available'):
                            st.markdown('<span class="status-ok">✅ 就绪</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="status-warn">⚠️ 未配置密钥</span>', unsafe_allow_html=True)

                    with col_save:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("💾 保存", key=f"save_agent_{agent}"):
                            if save_agent_config(agent, selected_provider, selected_model):
                                st.session_state[f"saved_{agent}"] = True

                    if st.session_state.get(f"saved_{agent}"):
                        st.success("✅ 已保存!")
                        del st.session_state[f"saved_{agent}"]

                    st.divider()

            # 当前绑定总览
            st.markdown("### 🔗 当前绑定总览")
            overview_data = []
            for agent in agents:
                cfg = config.get(agent, {})
                overview_data.append({
                    "Agent": agent_names.get(agent, agent),
                    "Provider": cfg.get('provider', 'N/A'),
                    "模型": cfg.get('model', 'N/A'),
                    "状态": "✅" if cfg.get('provider_available') else "⚠️"
                })

            st.dataframe(overview_data, use_container_width=True)
        else:
            st.error("无法加载AI配置管理器，请检查是否正确安装依赖")

    with tab2:
        
        config = get_api_config()
        
        # API配置卡片
        for provider, info in config.items():
            with st.container():
                st.markdown('<div class="config-card">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"#### {info['name']}")
                    st.markdown(f"**状态:** {info['status']}")
                    if 'endpoint' in info and info['endpoint']:
                        st.caption(f"端点: {info['endpoint']}")
                
                with col2:
                    new_key = st.text_input(
                        "输入API密钥",
                        type="password",
                        placeholder="sk-...",
                        key=f"api_key_{provider}"
                    )
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 保存", key=f"save_api_{provider}"):
                        if new_key:
                            save_api_key(provider, new_key)
                            st.session_state[f"saved_api_{provider}"] = True
                        else:
                            st.warning("请输入密钥")

                if st.session_state.get(f"saved_api_{provider}"):
                    st.success(f"✅ {info['name']} 密钥已保存!")
                    del st.session_state[f"saved_api_{provider}"]
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()
        
        # 代理设置
        st.markdown("### 🌐 代理设置")
        with st.container():
            st.markdown('<div class="config-card">', unsafe_allow_html=True)

            use_proxy = st.checkbox("启用代理", value=bool(os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')))

            if use_proxy:
                col_proxy1, col_proxy2 = st.columns(2)
                with col_proxy1:
                    http_proxy = st.text_input(
                        "HTTP 代理",
                        value=os.getenv('HTTP_PROXY', ''),
                        placeholder="http://127.0.0.1:7890",
                        key="settings_http_proxy"
                    )
                with col_proxy2:
                    https_proxy = st.text_input(
                        "HTTPS 代理",
                        value=os.getenv('HTTPS_PROXY', ''),
                        placeholder="http://127.0.0.1:7890",
                        key="settings_https_proxy"
                    )

                if st.button("💾 保存代理设置"):
                    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
                    with open(env_path, 'a', encoding='utf-8') as f:
                        f.write(f"\nHTTP_PROXY={http_proxy}\n")
                        f.write(f"HTTPS_PROXY={https_proxy}\n")
                    st.session_state.proxy_saved = True

            if st.session_state.get("proxy_saved"):
                st.success("✅ 代理设置已保存!")
                del st.session_state["proxy_saved"]
            else:
                st.info("未启用代理。如需访问海外API，请配置代理。")

            st.markdown('</div>', unsafe_allow_html=True)

        # 自定义API设置
        st.markdown("### 🔧 自定义AI API")
        st.info("💡 添加您自己的AI API服务，支持任何兼容OpenAI格式的API（如硅基流动、OneAPI等）")

        custom_apis = get_custom_apis()

        for i in range(5):
            with st.container():
                st.markdown('<div class="config-card">', unsafe_allow_html=True)

                # 获取现有配置或默认
                existing = next((c for c in custom_apis if c['index'] == i + 1), None)
                default_name = existing['name'] if existing else ''
                default_key = existing['key'] if existing else ''
                default_endpoint = existing['endpoint'] if existing else ''
                default_models = existing['models'] if existing else []

                col_name, col_key = st.columns([2, 3])
                with col_name:
                    name = st.text_input(
                        f"API名称 #{i+1}",
                        value=default_name,
                        placeholder=f"我的API {i+1}",
                        key=f"settings_custom_name_{i}"
                    )
                with col_key:
                    api_key = st.text_input(
                        "API密钥",
                        value=default_key,
                        type="password",
                        placeholder="sk-...",
                        key=f"settings_custom_key_{i}"
                    )

                col_endpoint, col_models = st.columns([3, 2])
                with col_endpoint:
                    endpoint = st.text_input(
                        "API端点",
                        value=default_endpoint,
                        placeholder="https://api.example.com/v1",
                        key=f"settings_custom_endpoint_{i}"
                    )
                with col_models:
                    models = st.text_input(
                        "模型列表",
                        value=','.join(default_models) if default_models else '',
                        placeholder="model1,model2",
                        help="多个模型用逗号分隔",
                        key=f"settings_custom_models_{i}"
                    )

                if st.button(f"💾 保存 #{i+1}", key=f"save_custom_{i}"):
                    if name and api_key and endpoint:
                        model_list = [m.strip() for m in models.split(',') if m.strip()]
                        save_custom_api(i + 1, name, api_key, endpoint, model_list)
                        st.session_state[f"custom_saved_{i}"] = True
                    else:
                        st.warning("请填写名称、密钥和端点")

                if st.session_state.get(f"custom_saved_{i}"):
                    st.success(f"✅ 自定义API #{i+1} 已保存!")
                    del st.session_state[f"custom_saved_{i}"]

                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

    with tab3:
        st.markdown("### 用户管理")
        
        # 显示用户列表
        users = get_users()
        
        if users:
            st.write(f"**共 {len(users)} 个用户**")
            
            for user in users:
                with st.container():
                    col_user1, col_user2, col_user3, col_user4 = st.columns([2, 1, 1, 1])
                    
                    with col_user1:
                        gender_icon = "♂️" if user.gender == 'male' else "♀️"
                        st.markdown(f"**{user.name}** {gender_icon}")
                        st.caption(f"ID: {user.id} | {user.age or '?'}岁")
                    
                    with col_user2:
                        goal_map = {'lose_weight': '减脂', 'maintain': '维持', 'gain_muscle': '增肌'}
                        st.write(f"目标: {goal_map.get(user.goal, '未知')}")
                    
                    with col_user3:
                        st.write(f"身高: {user.height_cm or '?'}cm")
                        st.write(f"体重: {user.weight_kg or '?'}kg")
                    
                    with col_user4:
                        if st.button("🗑️ 删除", key=f"del_user_{user.id}"):
                            if delete_user(user.id):
                                st.session_state.deleted_user = user.name
                            else:
                                st.error("删除失败")

                    if st.session_state.get("deleted_user") == user.name:
                        st.success(f"用户 {user.name} 已删除")
                        del st.session_state["deleted_user"]
                    
                    st.divider()
        else:
            st.info("暂无用户，请从首页创建新用户")
        
        # 用户统计
        st.markdown("### 📊 用户统计")
        if users:
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("总用户数", len(users))
            
            with stat_col2:
                males = len([u for u in users if u.gender == 'male'])
                st.metric("男性", males)
            
            with stat_col3:
                females = len([u for u in users if u.gender == 'female'])
                st.metric("女性", females)
            
            with stat_col4:
                avg_age = sum([u.age or 0 for u in users]) / len(users) if users else 0
                st.metric("平均年龄", f"{avg_age:.0f}岁")
    
    with tab3:
        st.markdown("### 系统信息")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("#### 📁 项目结构")
            st.code("""
HPU/
├── app.py              # 主入口
├── pages/               # 页面模块
│   ├── 1_physiological_dashboard.py
│   ├── 2_vision_lab.py
│   ├── 3_agent_arena.py
│   └── 4_chat_agent.py
├── src/
│   ├── agent/          # AI Agent模块
│   ├── database/       # 数据库模块
│   ├── multimodal/    # 多模态模块
│   └── upload/        # 文件上传模块
├── sql/               # SQL脚本
└── .env              # 环境配置
            """)
        
        with info_col2:
            st.markdown("#### 🔧 技术栈")
            st.json({
                "前端": "Streamlit",
                "编排": "LangGraph",
                "视觉": "MediaPipe",
                "语音": "Edge-TTS",
                "数据库": "PostgreSQL",
                "AI": "支持多API (OpenAI/智谱/Claude)"
            })
        
        # 环境变量状态
        st.markdown("### 📋 环境变量状态")
        env_status = {
            'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'ZHIPU_API_KEY': bool(os.getenv('ZHIPU_API_KEY')),
            'USDA_API_KEY': bool(os.getenv('USDA_API_KEY')),
            'HTTP_PROXY': bool(os.getenv('HTTP_PROXY')),
        }
        
        for key, is_set in env_status.items():
            status = "✅ 已配置" if is_set else "⚪ 未配置"
            status_class = "status-ok" if is_set else "status-warn"
            st.markdown(f"- **{key}**: <span class='{status_class}'>{status}</span>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
