"""
Page 1: 生理基座与身体年龄看板
Physiological Dashboard

功能:
- 上传华为手表导出的JSON数据
- 计算身体准备度指数(RS)和心率恢复力(HRR)
- 展示多维生理状态雷达图
- Before/After历史对比
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.multi_agent import HPUMultiAgent
from src.agent.state import AgentRole

# 页面配置
st.set_page_config(
    page_title="生理看板 | HPU健康智能体",
    page_icon="📊",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6C757D;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def load_sample_watch_data():
    """加载示例手表数据"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "steps": 12500,
        "exercise_minutes": 65,
        "calories_burned": 2850,
        "heart_rate_avg": 72,
        "heart_rate_rest": 58,
        "heart_rate_max": 165,
        "hrv_data": {
            "sdnn": 45,
            "rmssd": 38,
            "lf_hf_ratio": 1.2
        },
        "sleep_data": {
            "total_hours": 7.5,
            "deep_sleep_percent": 22,
            "rem_sleep_percent": 23,
            "light_sleep_percent": 55,
            "sleep_score": 85
        },
        "stress_level": 45,
        "blood_oxygen": 97,
        "temperature_celsius": 36.4
    }


def calculate_recovery_score(watch_data: dict) -> dict:
    """计算身体准备度指数"""
    hrv = watch_data.get("hrv_data", {})
    sleep = watch_data.get("sleep_data", {})
    
    # HRV评分 (基于SDNN)
    sdnn = hrv.get("sdnn", 30)
    hrv_score = min(100, sdnn * 2)  # SDNN越高越好
    
    # 睡眠评分
    sleep_score = sleep.get("sleep_score", 70)
    
    # 静息心率评分
    resting_hr = watch_data.get("heart_rate_rest", 70)
    hr_score = max(0, 100 - (resting_hr - 55) * 5)  # 55bpm为最佳
    
    # 综合恢复度
    recovery_score = (hrv_score * 0.4 + sleep_score * 0.35 + hr_score * 0.25)
    
    # 状态判断
    if recovery_score >= 80:
        status = "完全恢复 ✅"
        status_color = "#28A745"
    elif recovery_score >= 60:
        status = "轻度疲劳 ⚠️"
        status_color = "#FFC107"
    else:
        status = "需要休息 🔴"
        status_color = "#DC3545"
    
    return {
        "recovery_score": round(recovery_score, 1),
        "hrv_score": round(hrv_score, 1),
        "sleep_score": round(sleep_score, 1),
        "hr_score": round(hr_score, 1),
        "status": status,
        "status_color": status_color
    }


def calculate_hrr(watch_data: dict) -> dict:
    """计算心率恢复力"""
    hr_rest = watch_data.get("heart_rate_rest", 65)
    hr_avg = watch_data.get("heart_rate_avg", 120)
    hr_max = watch_data.get("heart_rate_max", 180)
    
    # HRR = 最大心率 - 恢复1分钟后心率 (简化计算)
    # 假设恢复后心率约为静息心率 + (平均心率-静息心率)*0.3
    hr_recovery_estimate = hr_rest + (hr_avg - hr_rest) * 0.3
    hrr = hr_avg - hr_recovery_estimate
    
    # 评估
    if hrr >= 30:
        hrr_level = "优秀 💪"
    elif hrr >= 20:
        hrr_level = "良好 👍"
    elif hrr >= 10:
        hrr_level = "一般 😐"
    else:
        hrr_level = "需提升 ⚠️"
    
    return {
        "hrr_value": round(hrr, 1),
        "hr_rest": hr_rest,
        "hr_avg": hr_avg,
        "level": hrr_level
    }


def create_radar_chart(metrics: dict, title: str = "多维生理状态") -> str:
    """创建雷达图"""
    categories = ['心肺功能', '恢复状态', '睡眠质量', '运动表现', '压力水平', '整体健康']
    
    # 归一化到0-100
    values = [
        min(100, metrics.get('cardio', 70)),
        min(100, metrics.get('recovery', 75)),
        min(100, metrics.get('sleep', 80)),
        min(100, metrics.get('exercise', 70)),
        min(100, 100 - metrics.get('stress', 50)),  # 压力取反
        min(100, metrics.get('overall', 75))
    ]
    
    # 补全到6个
    while len(values) < 6:
        values.append(70)
    values += values[:1]  # 闭合
    
    # 角度
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB')
    ax.fill(angles, values, alpha=0.25, color='#2E86AB')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    os.makedirs("output/charts", exist_ok=True)
    path = f"output/charts/radar_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return path


def create_before_after_chart(before: dict, after: dict) -> str:
    """创建Before/After对比图"""
    metrics = ['身体年龄\n(岁)', 'BMI', '恢复度\n(%)', '睡眠\n评分']
    
    before_values = [
        before.get('body_age', 35),
        before.get('bmi', 25),
        100 - before.get('recovery_score', 50),
        before.get('sleep_score', 70)
    ]
    
    after_values = [
        after.get('body_age', 32),
        after.get('bmi', 23),
        100 - after.get('recovery_score', 70),
        after.get('sleep_score', 85)
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - width/2, before_values, width, label='干预前', color='#DC3545', alpha=0.7)
    bars2 = ax.bar(x + width/2, after_values, width, label='干预后', color='#28A745', alpha=0.7)
    
    ax.set_ylabel('数值')
    ax.set_title('身体指标 Before vs After 对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend()
    ax.set_ylim(0, 100)
    
    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}',
               ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}',
               ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    os.makedirs("output/charts", exist_ok=True)
    path = f"output/charts/comparison_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return path


def main():
    # 标题
    st.markdown('<p class="main-header">📊 生理基座与身体年龄看板</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Physiological Dashboard | 实时监测 · 智能评估</p>', unsafe_allow_html=True)
    
    # 侧边栏 - 数据输入
    with st.sidebar:
        st.header("📱 数据输入")
        
        uploaded_file = st.file_uploader(
            "上传华为手表JSON数据",
            type=['json'],
            help="上传从华为运动健康App导出的JSON格式数据"
        )
        
        if st.button("加载示例数据"):
            uploaded_file = None
        
        st.divider()
        
        # 用户切换
        st.subheader("👤 用户切换")
        
        # 尝试从数据库加载用户列表
        try:
            from src.database.models import get_session, User
            session = get_session()
            users = session.query(User).all()
            session.close()
            
            user_options = {u.id: f"{u.name} ({u.gender}, {u.age}岁)" for u in users}
        except Exception as e:
            # 如果数据库连接失败，使用默认用户
            user_options = {
                1: "张三 (男, 28岁)",
                2: "李四 (女, 25岁)",
                3: "王五 (男, 35岁)"
            }
        
        # 用户选择器
        selected_user_id = st.selectbox(
            "选择用户",
            options=list(user_options.keys()),
            format_func=lambda x: user_options[x],
            index=0
        )
        
        # 保存到session state
        st.session_state['selected_user_id'] = selected_user_id
        st.session_state['user_options'] = user_options
        
        # 获取当前用户信息
        try:
            from src.database.models import get_session, User
            session = get_session()
            current_user = session.query(User).filter(User.id == selected_user_id).first()
            session.close()
            
            if current_user:
                user_data = {
                    "name": current_user.name,
                    "age": current_user.age,
                    "gender": current_user.gender,
                    "height_cm": current_user.height_cm,
                    "weight_kg": current_user.weight_kg
                }
            else:
                user_data = {"name": "未知用户", "age": 30, "gender": "男", "height_cm": 170, "weight_kg": 70}
        except:
            # 默认用户数据
            default_users = {
                1: {"name": "张三", "age": 28, "gender": "男", "height_cm": 175, "weight_kg": 72},
                2: {"name": "李四", "age": 25, "gender": "女", "height_cm": 162, "weight_kg": 55},
                3: {"name": "王五", "age": 35, "gender": "男", "height_cm": 180, "weight_kg": 80}
            }
            user_data = default_users.get(selected_user_id, default_users[1])
        
        st.json(user_data)
    
    # 主内容区
    col1, col2, col3 = st.columns(3)
    
    # 读取数据
    if uploaded_file is not None:
        try:
            watch_data = json.load(uploaded_file)
        except:
            st.error("文件格式错误，请上传有效的JSON文件")
            watch_data = load_sample_watch_data()
    else:
        watch_data = load_sample_watch_data()
    
    # 计算指标
    recovery = calculate_recovery_score(watch_data)
    hrr = calculate_hrr(watch_data)
    
    # 计算其他指标
    bmi = 72 / (1.75 ** 2)
    bmi_category = "正常" if 18.5 <= bmi < 24 else "超重"
    
    # 身体年龄计算
    base_age = 30
    age_adjustment = 0
    age_adjustment += (65 - watch_data.get("heart_rate_rest", 65)) * -0.3  # 心率越低越年轻
    age_adjustment += (watch_data.get("sleep_data", {}).get("sleep_score", 75) - 75) * 0.1
    age_adjustment += (100 - recovery["recovery_score"]) * 0.05
    body_age = int(base_age + age_adjustment)
    
    # 显示关键指标卡片
    with col1:
        st.metric(
            label="🎯 身体准备度指数 (RS)",
            value=f"{recovery['recovery_score']}/100",
            delta="+5.2 vs 昨日"
        )
        st.markdown(f"**状态**: <span style='color:{recovery['status_color']}'>{recovery['status']}</span>", unsafe_allow_html=True)
    
    with col2:
        st.metric(
            label="💓 心率恢复力 (HRR)",
            value=f"{hrr['hrr_value']} bpm",
            delta="+3.1 vs 上周"
        )
        st.markdown(f"**等级**: {hrr['level']}")
    
    with col3:
        st.metric(
            label="⏳ 估算身体年龄",
            value=f"{body_age} 岁",
            delta=f"{body_age - 30:+d} vs 基准",
            delta_color="off"
        )
        st.markdown(f"**BMI**: {bmi:.1f} ({bmi_category})")
    
    st.divider()
    
    # 详细指标
    st.subheader("📈 详细生理指标")
    
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown("#### 🏃 运动数据")
        st.write(f"- 步数: {watch_data.get('steps', 0):,} 步")
        st.write(f"- 运动时长: {watch_data.get('exercise_minutes', 0)} 分钟")
        st.write(f"- 消耗热量: {watch_data.get('calories_burned', 0):,} kcal")
        st.write(f"- 平均心率: {watch_data.get('heart_rate_avg', 0)} bpm")
        st.write(f"- 最大心率: {watch_data.get('heart_rate_max', 0)} bpm")
    
    with detail_col2:
        st.markdown("#### 😴 睡眠数据")
        sleep = watch_data.get("sleep_data", {})
        st.write(f"- 总时长: {sleep.get('total_hours', 0)} 小时")
        st.write(f"- 深睡比例: {sleep.get('deep_sleep_percent', 0)}%")
        st.write(f"- REM睡眠: {sleep.get('rem_sleep_percent', 0)}%")
        st.write(f"- 睡眠评分: {sleep.get('sleep_score', 0)}/100")
    
    # HRV数据
    hrv = watch_data.get("hrv_data", {})
    if hrv:
        st.markdown("#### 📉 心率变异性 (HRV)")
        hrv_col1, hrv_col2, hrv_col3 = st.columns(3)
        with hrv_col1:
            st.metric("SDNN", f"{hrv.get('sdnn', 0)} ms")
        with hrv_col2:
            st.metric("RMSSD", f"{hrv.get('rmssd', 0)} ms")
        with hrv_col3:
            st.metric("LF/HF", f"{hrv.get('lf_hf_ratio', 0):.2f}")
    
    st.divider()
    
    # 可视化区域
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.markdown("#### 🕸️ 多维生理状态雷达图")
        
        # 生成雷达图数据
        radar_metrics = {
            'cardio': min(100, (watch_data.get('heart_rate_avg', 120) - 60) / 1.5),
            'recovery': recovery['recovery_score'],
            'sleep': watch_data.get('sleep_data', {}).get('sleep_score', 75),
            'exercise': min(100, watch_data.get('exercise_minutes', 30) * 1.5),
            'stress': watch_data.get('stress_level', 50),
            'overall': (recovery['recovery_score'] + watch_data.get('sleep_data', {}).get('sleep_score', 75)) / 2
        }
        
        radar_path = create_radar_chart(radar_metrics)
        st.image(radar_path, use_container_width=True)
    
    with viz_col2:
        st.markdown("#### 📊 Before vs After 对比")
        
        # 模拟干预前后数据
        before_data = {
            'body_age': 35.0,
            'bmi': 25.2,
            'recovery_score': 55,
            'sleep_score': 68
        }
        after_data = {
            'body_age': body_age,
            'bmi': bmi,
            'recovery_score': recovery['recovery_score'],
            'sleep_score': watch_data.get('sleep_data', {}).get('sleep_score', 75)
        }
        
        comparison_path = create_before_after_chart(before_data, after_data)
        st.image(comparison_path, use_container_width=True)
        
        st.markdown("""
        <div class="success-box">
        ✅ <b>干预效果</b>: 身体年龄从 <b>35.0</b> 岁降至 <b>{:.1f}</b> 岁<br>
        睡眠质量回升 <b>+17</b> 分，恢复度提升 <b>+{:.1f}</b>
        </div>
        """.format(after_data['body_age'], after_data['recovery_score'] - before_data['recovery_score']), 
        unsafe_allow_html=True)
    
    # 运行Agent分析
    st.divider()
    st.subheader("🧠 Agent智能分析")
    
    if st.button("🚀 启动多Agent分析", type="primary", use_container_width=True):
        with st.spinner("Agent正在分析..."):
            # 准备状态
            from src.agent.state import AgentState
            initial_state: AgentState = {
                "user_id": "demo_user",
                "session_id": "session_001",
                "timestamp": datetime.now().isoformat(),
                "watch_data": watch_data,
                "exercise_video": None,
                "food_image": None,
                "health_metrics": None,
                "exercise_analysis": None,
                "nutrition_analysis": None,
                "current_agent": None,
                "decision_history": [],
                "reasoning_chain": [],
                "safety_result": None,
                "guardrail_active": False,
                "recommendations": [],
                "training_plan": None,
                "meal_plan": None,
                "speech_report": None,
                "step": 0,
                "max_steps": 10,
                "error": None,
                "status": "running"
            }
            
            # 运行Agent
            agent = HPUMultiAgent()
            result_state = agent.run(initial_state)
            
            # 显示思考链
            st.markdown("#### 🔄 Agent决策链 (Chain of Thought)")
            
            thinking_col1, thinking_col2 = st.columns([2, 1])
            
            with thinking_col1:
                for i, thought in enumerate(result_state.get("reasoning_chain", [])):
                    with st.expander(f"步骤 {i+1}: {thought[:50]}...", expanded=i<3):
                        st.code(thought, language=None)
            
            with thinking_col2:
                st.markdown("#### 📋 决策节点")
                for decision in result_state.get("decision_history", []):
                    st.write(f"**{decision['agent']}**")
                    st.caption(f"调用工具: {', '.join(decision.get('tools_used', []))}")
            
            # 显示健康指标
            if result_state.get("health_metrics"):
                metrics = result_state["health_metrics"]
                st.markdown("#### 📊 Agent计算的健康指标")
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                with metrics_col1:
                    st.metric("BMI", f"{metrics.bmi:.1f}")
                with metrics_col2:
                    st.metric("BMR", f"{metrics.bmr} kcal")
                with metrics_col3:
                    st.metric("TDEE", f"{metrics.tdee} kcal")
                with metrics_col4:
                    st.metric("身体年龄", f"{metrics.body_age} 岁")
    
    # 页脚
    st.divider()
    st.caption("HPU健康智能体 | 期末项目演示 | 数据仅供参考，不构成医疗建议")


if __name__ == "__main__":
    main()
