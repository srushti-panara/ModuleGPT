import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime, timedelta
import json
import os

# -------------------- CONFIG --------------------
genai.configure(api_key="your_api_key_here")  # Replace with your actual API key
MODEL_NAME = "gemini-2.0-flash"

st.set_page_config(
    page_title="🎓 ModuleGPT - AI Module & Roadmap Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------------- DATA PERSISTENCE FUNCTIONS --------------------
def load_user_data():
    """Load user data from JSON file"""
    try:
        if os.path.exists('user_data.json'):
            with open('user_data.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return {}


def save_user_data():
    """Save user data to JSON file"""
    try:
        data_to_save = {
            "saved_modules": st.session_state.saved_modules,
            "user_profile": st.session_state.user_profile,
            "learning_progress": st.session_state.learning_progress,
            "search_history": st.session_state.search_history,
            "dark_mode": st.session_state.dark_mode,
            "font_size": st.session_state.font_size
        }
        with open('user_data.json', 'w') as f:
            json.dump(data_to_save, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")


# -------------------- SESSION STATE INITIALIZATION --------------------
# Load existing data
saved_data = load_user_data()

if "saved_modules" not in st.session_state:
    st.session_state.saved_modules = saved_data.get("saved_modules", {})

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = saved_data.get("dark_mode", False)

if "user_profile" not in st.session_state:
    default_profile = {
        "name": "Demo",
        "email": "demo@gmail.com",
        "streak": saved_data.get("user_profile", {}).get("streak", 0),
        "progress": saved_data.get("user_profile", {}).get("progress", 0),
        "last_activity": saved_data.get("user_profile", {}).get("last_activity"),
        "completed_modules": saved_data.get("user_profile", {}).get("completed_modules", []),
        "badges": saved_data.get("user_profile", {}).get("badges", ["🎯 Starter"]),
        "total_modules": saved_data.get("user_profile", {}).get("total_modules", 0),
        "login_streak": saved_data.get("user_profile", {}).get("login_streak", 0),
        "last_login": saved_data.get("user_profile", {}).get("last_login"),
        "daily_goal": saved_data.get("user_profile", {}).get("daily_goal", 60),
        "expertise_level": saved_data.get("user_profile", {}).get("expertise_level", "Beginner"),
        "interests": saved_data.get("user_profile", {}).get("interests", []),
        "profile_visibility": saved_data.get("user_profile", {}).get("profile_visibility", "Public"),
        "join_date": saved_data.get("user_profile", {}).get("join_date", datetime.now().strftime("%Y-%m-%d")),
        "timezone": saved_data.get("user_profile", {}).get("timezone", "UTC"),
        "notifications": saved_data.get("user_profile", {}).get("notifications", True)
    }
    st.session_state.user_profile = default_profile

if "learning_progress" not in st.session_state:
    st.session_state.learning_progress = saved_data.get("learning_progress", {})
if "current_module" not in st.session_state:
    st.session_state.current_module = None
if "show_emoji_picker" not in st.session_state:
    st.session_state.show_emoji_picker = False
if "show_delete_dialog" not in st.session_state:
    st.session_state.show_delete_dialog = None
if "currently_viewing_module" not in st.session_state:
    st.session_state.currently_viewing_module = None
if "font_size" not in st.session_state:
    st.session_state.font_size = saved_data.get("font_size", "medium")
if "show_edit_profile" not in st.session_state:
    st.session_state.show_edit_profile = False
if "user_activity" not in st.session_state:
    st.session_state.user_activity = {}
if "search_history" not in st.session_state:
    st.session_state.search_history = saved_data.get("search_history", [])
if "currently_viewing_roadmap" not in st.session_state:
    st.session_state.currently_viewing_roadmap = None
if "current_roadmap" not in st.session_state:
    st.session_state.current_roadmap = None


# -------------------- BADGE SYSTEM --------------------
def check_badges():
    badges = st.session_state.user_profile["badges"].copy()
    streak = st.session_state.user_profile["streak"]
    completed = len(st.session_state.user_profile["completed_modules"])
    total_modules = st.session_state.user_profile["total_modules"]
    login_streak = st.session_state.user_profile["login_streak"]

    # Streak badges
    if streak >= 3 and "🔥 3-Day Streak" not in badges:
        badges.append("🔥 3-Day Streak")
    if streak >= 7 and "⚡ 7-Day Streak" not in badges:
        badges.append("⚡ 7-Day Streak")
    if streak >= 15 and "🚀 15-Day Streak" not in badges:
        badges.append("🚀 15-Day Streak")
    if streak >= 30 and "🏆 Monthly Master" not in badges:
        badges.append("🏆 Monthly Master")
    if streak >= 60 and "💎 Diamond Learner" not in badges:
        badges.append("💎 Diamond Learner")

    # Login streak badges
    if login_streak >= 5 and "📅 Consistent" not in badges:
        badges.append("📅 Consistent")
    if login_streak >= 15 and "🗓️ Dedicated" not in badges:
        badges.append("🗓️ Dedicated")
    if login_streak >= 30 and "📊 Committed" not in badges:
        badges.append("📊 Committed")

    # Completion badges
    if completed >= 1 and "🌱 First Step" not in badges:
        badges.append("🌱 First Step")
    if completed >= 3 and "📚 Quick Learner" not in badges:
        badges.append("📚 Quick Learner")
    if completed >= 5 and "🎯 Focused" not in badges:
        badges.append("🎯 Focused")
    if completed >= 10 and "🎓 Knowledge Seeker" not in badges:
        badges.append("🎓 Knowledge Seeker")
    if completed >= 15 and "🌟 Learning Star" not in badges:
        badges.append("🌟 Learning Star")
    if completed >= 25 and "🚀 Fast Tracker" not in badges:
        badges.append("🚀 Fast Tracker")
    if completed >= 50 and "🏅 Master Learner" not in badges:
        badges.append("🏅 Master Learner")

    # Level-based badges
    beginner_modules = [mod for mod in st.session_state.user_profile["completed_modules"]
                        if st.session_state.saved_modules.get(mod, {}).get("level") == "Beginner"]
    intermediate_modules = [mod for mod in st.session_state.user_profile["completed_modules"]
                            if st.session_state.saved_modules.get(mod, {}).get("level") == "Intermediate"]
    advanced_modules = [mod for mod in st.session_state.user_profile["completed_modules"]
                        if st.session_state.saved_modules.get(mod, {}).get("level") == "Advanced"]

    if len(beginner_modules) >= 3 and "🟢 Beginner Pro" not in badges:
        badges.append("🟢 Beginner Pro")
    if len(intermediate_modules) >= 3 and "🟡 Intermediate Pro" not in badges:
        badges.append("🟡 Intermediate Pro")
    if len(advanced_modules) >= 3 and "🔴 Advanced Pro" not in badges:
        badges.append("🔴 Advanced Pro")

    # Progress badges
    progress = st.session_state.user_profile["progress"]
    if progress >= 25 and "📈 Getting There" not in badges:
        badges.append("📈 Getting There")
    if progress >= 50 and "🎪 Halfway Hero" not in badges:
        badges.append("🎪 Halfway Hero")
    if progress >= 75 and "✨ Almost There" not in badges:
        badges.append("✨ Almost There")
    if progress >= 100 and "✅ Completionist" not in badges:
        badges.append("✅ Completionist")

    # Special badges
    if total_modules >= 10 and "🏗️ Module Builder" not in badges:
        badges.append("🏗️ Module Builder")
    if len(st.session_state.saved_modules) >= 5 and "📚 Collector" not in badges:
        badges.append("📚 Collector")
    if any("Expert" in mod for mod in st.session_state.user_profile["completed_modules"]) and "🧠 Expert" not in badges:
        badges.append("🧠 Expert")

    return list(set(badges))  # Remove duplicates


# -------------------- STREAK CALCULATION --------------------
def update_streak():
    today = datetime.now().date()
    last_activity = st.session_state.user_profile.get("last_activity")
    last_login = st.session_state.user_profile.get("last_login")

    # Learning streak (module generation/completion)
    if last_activity:
        last_date = datetime.strptime(last_activity, "%Y-%m-%d").date()
        if today == last_date + timedelta(days=1):
            # Consecutive day
            st.session_state.user_profile["streak"] += 1
        elif today > last_date + timedelta(days=1):
            # Streak broken
            st.session_state.user_profile["streak"] = 1
        # Same day - no change
    else:
        # First activity
        st.session_state.user_profile["streak"] = 1

    # Login streak (app usage)
    if last_login:
        last_login_date = datetime.strptime(last_login, "%Y-%m-%d").date()
        if today == last_login_date + timedelta(days=1):
            st.session_state.user_profile["login_streak"] += 1
        elif today > last_login_date + timedelta(days=1):
            st.session_state.user_profile["login_streak"] = 1
    else:
        st.session_state.user_profile["login_streak"] = 1

    st.session_state.user_profile["last_activity"] = today.strftime("%Y-%m-%d")
    st.session_state.user_profile["last_login"] = today.strftime("%Y-%m-%d")
    st.session_state.user_profile["badges"] = check_badges()
    save_user_data()


# -------------------- PROGRESS CALCULATION --------------------
def update_progress():
    completed = len(st.session_state.user_profile["completed_modules"])
    total = st.session_state.user_profile["total_modules"]

    if total > 0:
        progress = (completed / total) * 100
        st.session_state.user_profile["progress"] = min(100, round(progress))
    else:
        st.session_state.user_profile["progress"] = 0
    save_user_data()


# -------------------- INITIALIZE STREAK --------------------
# Initialize streak on first load
if not st.session_state.user_profile.get("last_login"):
    update_streak()


# -------------------- APPLY THEME AND FONT SIZE --------------------
def apply_theme_and_font():
    # Get current settings
    is_dark = st.session_state.dark_mode
    font_size = st.session_state.font_size

    # Define colors for light and dark themes
    if is_dark:
        # Dark theme colors
        bg_color = '#29498a'
        text_color = '#FAFAFA'
        sidebar_bg = '#29498a'
        card_bg = '#af9af5'
        border_color = '#d9d0f5'
        hover_glow = '0 0 20px rgba(247, 247, 245, 010.0)'
        shadow_color = 'rgba(19, 227, 235, 0.3)'
    else:
        # Light theme colors
        bg_color = '#eee6f7'
        text_color = '#1a1c1c'
        sidebar_bg = '#eee6f7'
        card_bg = '#c0bdff'
        border_color = '#E2E8F0'
        hover_glow = '0 0 20px rgba(99, 255, 252, 0.9)'
        shadow_color = 'rgba(5, 17, 245, 0.1)'

    # Define font sizes
    font_sizes = {
        'small': '14px',
        'medium': '16px',
        'large': '18px',
        'xlarge': '20px'
    }
    current_font_size = font_sizes.get(font_size, '16px')

    css = f"""
    <style>
    /* Main app background and text */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}

    /* Sidebar background */
    .css-1d391kg, .css-1lcbmhc {{
        background-color: {sidebar_bg} !important;
    }}

    /* Main content area */
    .main .block-container {{
        background-color: {bg_color};
        color: {text_color};
        font-size: {current_font_size};
    }}

    /* Headers and text */
    h1, h2, h3, h4, h5, h6, p, div, span {{
        color: {text_color} !important;
    }}

    /* Input fields - rounded with glow */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 2px solid {border_color} !important;
        border-radius: 20px !important;
        padding: 16px 19px !important;
        transition: all 0.5s ease !important;
    }}

    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{
        border-color: #64ebf5 !important;
        box-shadow: {hover_glow} !important;
        outline: #a773fa !important;
    }}

    /* Buttons - rounded with glow */
    .stButton button {{
        background-color: #6C63FF;
        color: white;
        border: none;
        border-radius: 15px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.5s ease;
        box-shadow: 0 4px 15px {shadow_color};
    }}

    .stButton button:hover {{
        background-color: #4A44C6;
        transform: translateY(-2px);
        box-shadow: {hover_glow};
    }}

    /* Tabs - rounded with glow */
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 3px solid {border_color} !important;
        border-radius: 12px 12px 12px 12px !important;
        margin: 5px 5px !important;
        transition: all 0.5s ease !important;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #6C63FF !important;
        color: white !important;
        border-color: #6C63FF !important;
        box-shadow: {hover_glow};
        transform: translateY(-2px);
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #6C63FF !important;
        color: white !important;
        border-color: #6C63FF !important;
        box-shadow: {hover_glow};
    }}

    /* Containers and boxes - rounded with glow */
    .stContainer, .element-container, .block-container {{
        border-radius: 20px !important;
    }}

    /* Sidebar containers */
    .css-1lcbmhc .css-1adrfps {{
        background-color: {card_bg} !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        border: 2px solid {border_color} !important;
        transition: all 0.3s ease !important;
    }}

    .css-1lcbmhc .css-1adrfps:hover {{
        box-shadow: {hover_glow};
        border-color: #6C63FF !important;
        transform: translateY(-2px);
    }}

    /* Expander widgets */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        border: 2px solid {border_color} !important;
        border-radius: 15px !important;
        margin: 5px 0 !important;
        transition: all 0.3s ease !important;
    }}

    .streamlit-expanderHeader:hover {{
        box-shadow: {hover_glow};
        border-color: #6C63FF !important;
        transform: translateY(-2px);
    }}

    /* Metric cards */
    [data-testid="metric-container"] {{
        background-color: {card_bg} !important;
        border: 2px solid {border_color} !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        transition: all 0.3s ease !important;
    }}

    [data-testid="metric-container"]:hover {{
        box-shadow: {hover_glow};
        border-color: #6C63FF !important;
        transform: translateY(-2px);
    }}

    /* Custom classes for our app */
    .main-title {{
        font-family: 'Arial', sans-serif;
        font-weight: 700;
        font-size: 3.5rem;
        text-align: center;
        background: linear-gradient(90deg, #6C63FF, #4A44C6, #FF6584);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;

        /* Minimal white glow */
        text-shadow: 
            0 0 1px rgba(255, 255, 255, 0.15);

        /* Hairline white stroke */
        -webkit-text-stroke: 0.1px rgba(255, 255, 255, 0.2);
        text-stroke: 0.1px rgba(255, 255, 255, 0.2);
    }}

    .welcome-text {{
        font-family: 'Bradley Hand', sans-serif;
        font-weight: 500;
        font-size: 2.5rem;
        text-align: center;
        color: #6C63FF;
        margin-bottom: 2rem;

        /* Minimal white glow */
        text-shadow: 
            0 0 1px rgba(255, 255, 255, 0.15);

        /* Hairline white stroke */
        -webkit-text-stroke: 0.1px rgba(255, 255, 255, 0.2);
        text-stroke: 0.1px rgba(255, 255, 255, 0.2);
    }}

    .user-profile {{
        position: fixed;
        top: 60px;
        right: 20px;
        display: flex;
        align-items: center;
        background: {card_bg};
        border-radius: 50px;
        padding: 8px 15px;
        box-shadow: 0 4px 15px {shadow_color};
        z-index: 999;
        border: 2px solid {border_color};
        font-family: 'Arial', sans-serif;
        transition: all 0.3s ease;
    }}

    .user-profile:hover {{
        box-shadow: {hover_glow};
        border-color: #6C63FF;
        transform: translateY(-2px);
    }}

    .user-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(45deg, #6C63FF, #FF6584);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-right: 10px;
    }}

    .badge-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
    }}

    .badge {{
        background: linear-gradient(45deg, #6C63FF, #FF6584);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }}

    .badge:hover {{
        transform: translateY(-2px);
        box-shadow: {hover_glow};
    }}

    .completion-section {{
        background: {card_bg};
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        border: 3px solid #6C63FF;
        text-align: center;
        transition: all 0.3s ease;
    }}

    .completion-section:hover {{
        box-shadow: {hover_glow};
        transform: translateY(-2px);
    }}

    /* History items */
    .history-item {{
        background: {card_bg};
        border: 2px solid {border_color};
        border-radius: 15px;
        padding: 15px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }}

    .history-item:hover {{
        box-shadow: {hover_glow};
        border-color: #6C63FF;
        transform: translateY(-2px);
    }}

    /* Completed module item */
    .completed-item {{
        background: linear-gradient(45deg, #10B981, #059669);
        color: white;
        border: 2px solid #10B981;
        border-radius: 15px;
        padding: 12px;
        margin: 6px 0;
        transition: all 0.3s ease;
    }}

    .completed-item:hover {{
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.6);
        transform: translateY(-2px);
    }}

    /* History delete buttons */
    .history-delete-btn {{
        background: linear-gradient(45deg, #EF4444, #DC2626) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
    }}

    .history-delete-btn:hover {{
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
    }}

    .history-regen-btn {{
        background: linear-gradient(45deg, #3B82F6, #1D4ED8) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
    }}

    .history-regen-btn:hover {{
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    }}

    /* Info and warning boxes */
    .stAlert {{
        border-radius: 20px !important;
        border: 2px solid {border_color} !important;
        transition: all 0.3s ease !important;
    }}

    .stAlert:hover {{
        box-shadow: {hover_glow} !important;
        border-color: #6C63FF !important;
        transform: translateY(-2px) !important;
    }}

    /* Success boxes */
    .stSuccess {{
        border-radius: 20px !important;
        border: 2px solid #10B981 !important;
    }}

    /* Error boxes */
    .stError {{
        border-radius: 20px !important;
        border: 2px solid #EF4444 !important;
    }}

    /* Warning boxes */
    .stWarning {{
        border-radius: 20px !important;
        border: 2px solid #F59E0B !important;
    }}

    /* Info boxes */
    .stInfo {{
        border-radius: 20px !important;
        border: 2px solid #6C63FF !important;
    }}

    /* Spinner */
    .stSpinner > div {{
        border-radius: 50% !important;
        box-shadow: 0 0 20px #6C63FF !important;
    }}

    /* Selectbox dropdown */
    .stSelectbox:focus-within {{
        border-radius: 15px !important;
        box-shadow: {hover_glow} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Apply theme and font size
apply_theme_and_font()

# -------------------- HEADER --------------------
st.markdown('<h1 class="main-title">🎓 ModuleGPT - AI Module & Roadmap Generator</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="welcome-text">Hello, {st.session_state.user_profile["name"]}!</p>', unsafe_allow_html=True)

# -------------------- USER PROFILE --------------------
st.markdown(
    f"""
    <div class="user-profile">
        <div class="user-avatar">
            {st.session_state.user_profile['name'][0].upper()}
        </div>
        <div class="user-details">
            <div class="user-name">{st.session_state.user_profile['name']}</div>
            <div class="user-stats">🔥 {st.session_state.user_profile['streak']} • 📈 {st.session_state.user_profile['progress']}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True
)

# -------------------- MODULE VIEWING PAGE --------------------
if st.session_state.get('currently_viewing_module'):
    module_name = st.session_state.currently_viewing_module

    # Clear the main page content
    st.empty()

    # Create right sidebar for module actions FIRST
    with st.sidebar:
        # Clear existing sidebar content
        st.markdown("## 🎯 Module Actions")
        st.markdown("---")

        # Go Back button
        if st.button("⬅️ Go Back", use_container_width=True):
            st.session_state.currently_viewing_module = None
            st.rerun()

        # Mark as Completed button
        if module_name not in st.session_state.user_profile["completed_modules"]:
            if st.button("✅ Mark as Completed", use_container_width=True):
                st.session_state.user_profile["completed_modules"].append(module_name)
                if module_name in st.session_state.saved_modules:
                    st.session_state.saved_modules[module_name]["completed"] = True
                update_progress()
                st.session_state.user_profile["badges"] = check_badges()
                save_user_data()
                st.success(f"🎊 Congratulations! You've completed '{module_name}'!")
                st.rerun()
        else:
            st.success("✅ Already Completed!")

        # Progress tracking
        st.markdown("---")
        st.markdown("### 📊 Update Progress")
        current_progress = st.session_state.learning_progress.get(module_name, "🔴")
        progress_options = ["🔴 Not Started", "🟡 In Progress", "🟢 Almost Done", "✅ Completed"]

        new_progress = st.selectbox(
            "Your Progress:",
            progress_options,
            index=["🔴", "🟡", "🟢", "✅"].index(current_progress),
            key=f"sidebar_progress_{module_name}"
        )
        if new_progress.split(" ")[0] != current_progress:
            st.session_state.learning_progress[module_name] = new_progress.split(" ")[0]
            save_user_data()
            st.rerun()

        # Go to Home tab
        st.markdown("---")
        if st.button("🏠 Go to Home Tab", use_container_width=True):
            st.session_state.currently_viewing_module = None
            st.rerun()

    # Now display the module content in main area
    # Check if it's a current module or saved module
    module_data = None

    # First check if it's the current module
    if st.session_state.current_module and st.session_state.current_module["topic"] == module_name:
        module_data = st.session_state.current_module
    # Then check if it's in saved modules
    elif module_name in st.session_state.saved_modules:
        module_data = st.session_state.saved_modules[module_name]

    if module_data:
        # Main content area for module
        st.subheader(f"📚 {module_name}")
        if "level" in module_data:
            st.markdown(f"**Level:** {module_data['level']}")
        if "timestamp" in module_data:
            st.markdown(f"**Saved on:** {module_data.get('timestamp', 'Recently')}")
        elif "generated_at" in module_data:
            st.markdown(f"**Generated on:** {module_data.get('generated_at', 'Recently')}")

        # Display module content
        st.markdown("---")
        st.markdown(module_data["content"])
    else:
        st.error("Module not found!")
        if st.button("Return to Home"):
            st.session_state.currently_viewing_module = None
            st.rerun()

# -------------------- ROADMAP VIEWING PAGE --------------------
elif st.session_state.get('currently_viewing_roadmap'):
    roadmap_data = st.session_state.currently_viewing_roadmap

    # Clear the main page content
    st.empty()

    # Create right sidebar for roadmap actions FIRST
    with st.sidebar:
        st.markdown("## 🗺️ Roadmap Actions")
        st.markdown("---")

        # Go Back button
        if st.button("⬅️ Go Back", use_container_width=True):
            st.session_state.currently_viewing_roadmap = None
            st.rerun()

        # Go to Home tab
        st.markdown("---")
        if st.button("🏠 Go to Home Tab", use_container_width=True):
            st.session_state.currently_viewing_roadmap = None
            st.rerun()

    # Main content area for roadmap
    st.subheader(f"🗺️ {roadmap_data['topic']}")
    st.markdown(f"**Generated on:** {roadmap_data.get('generated_at', 'Recently')}")

    # Display roadmap content
    st.markdown("---")
    st.markdown(roadmap_data["content"])

# -------------------- MAIN APP CONTENT (when not viewing specific content) --------------------
else:
    # -------------------- MAIN HORIZONTAL TABS --------------------
    main_tab = st.tabs(["🏠 Home", "📝 How to Use", "ℹ About", "🏆 Badges & Progress"])

    # -------------------- HOME TAB --------------------
    with main_tab[0]:
        home_sub_tab = st.tabs(["Generate Module", "Generate Roadmap"])

        # ----------- Generate Module ----------- #
        with home_sub_tab[0]:
            st.subheader("🎓 Generate AI Module")
            topic = st.text_input("🔍 Enter Topic for Module", "")
            module_level = st.selectbox("Select Module Level", ["Beginner", "Intermediate", "Advanced"])
            generate_module_btn = st.button("Generate Module", key="generate_module")

            # Handle module generation
            if generate_module_btn and topic.strip():
                with st.spinner("✨ Generating module..."):
                    try:
                        # Add to search history
                        search_entry = {
                            "topic": topic,
                            "type": "module",
                            "level": module_level,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.search_history.insert(0, search_entry)
                        save_user_data()

                        model = genai.GenerativeModel(MODEL_NAME)
                        prompt = f"""
                        Create a comprehensive learning module about: {topic}

                        Level: {module_level}

                        Please structure it as follows:

                        ## 📚 Module: {topic}

                        ### 🎯 Learning Objectives
                        - List 3-5 key learning objectives

                        ### 📖 Core Concepts
                        - Explain the main concepts in detail
                        - Provide clear examples
                        - Include diagrams or visual explanations where helpful

                        ### 🛠️ Practical Applications
                        - Real-world use cases
                        - Step-by-step implementations
                        - Best practices

                        ### 💡 Exercises & Practice
                        - 3-5 practice exercises with solutions
                        - Hands-on activities
                        - Challenge problems

                        ### 📋 Quick Reference
                        - Key formulas/commands
                        - Important tips
                        - Common pitfalls to avoid

                        ### 🎓 Knowledge Check
                        - Self-assessment questions
                        - Quiz to test understanding

                        Make it engaging, practical, and suitable for {module_level.lower()} level learners.
                        """
                        response = model.generate_content(prompt)
                        full_text = response.text

                        # Store the generated module in session state
                        st.session_state.current_module = {
                            "topic": topic,
                            "level": module_level,
                            "content": full_text,
                            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "completed": False
                        }

                        # Display the generated content
                        st.markdown(full_text)

                        # Update user activity for streak tracking
                        update_streak()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Show module actions if there's a current module
            if st.session_state.current_module:
                st.markdown("---")
                st.subheader("📋 Module Actions")

                # Display current module info
                current_topic = st.session_state.current_module["topic"]
                st.info(f"**Current Module:** {current_topic} | **Level:** {st.session_state.current_module['level']}")

                # Action buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("💾 Save This Module", key="save_module", use_container_width=True, type="primary"):
                        # Save the current module
                        st.session_state.saved_modules[current_topic] = {
                            "level": st.session_state.current_module["level"],
                            "content": st.session_state.current_module["content"],
                            "timestamp": st.session_state.current_module["generated_at"],
                            "completed": False
                        }
                        # Update total modules count
                        st.session_state.user_profile["total_modules"] = len(st.session_state.saved_modules)
                        update_progress()
                        save_user_data()
                        st.success(f"✅ Module '{current_topic}' saved successfully!")
                        st.balloons()

                with col2:
                    if st.button("📖 Open Full View", key="open_full_view", use_container_width=True):
                        st.session_state.currently_viewing_module = current_topic
                        st.rerun()

                with col3:
                    if st.button("🔄 Generate New", key="new_module", use_container_width=True):
                        st.session_state.current_module = None
                        st.rerun()

            # Show saved modules count
            if st.session_state.saved_modules:
                st.markdown("---")
                st.subheader("📚 Your Saved Modules")
                st.write(
                    f"You have **{len(st.session_state.saved_modules)}** saved modules. Check the sidebar to view them!")

        # ----------- Generate Roadmap ----------- #
        with home_sub_tab[1]:
            st.subheader("🗺 Generate Roadmap")
            roadmap_topic = st.text_input("🔍 Enter Topic for Roadmap", key="roadmap_topic")
            generate_roadmap_btn = st.button("Generate Roadmap", key="generate_roadmap")

            if generate_roadmap_btn:
                if roadmap_topic.strip() == "":
                    st.warning("Please enter a topic name for roadmap.")
                else:
                    with st.spinner("🧠 Generating roadmap..."):
                        try:
                            # Add to search history
                            search_entry = {
                                "topic": roadmap_topic,
                                "type": "roadmap",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state.search_history.insert(0, search_entry)
                            save_user_data()

                            model = genai.GenerativeModel(MODEL_NAME)
                            prompt = f"""
                            Create a complete learning roadmap for: {roadmap_topic}

                            Please include:

                            1. Provide a Mindmap/Flowchart first.
                        2. Then provide a detailed step-by-step roadmap for learning this topic.
                        Format the mindmap as text diagram and roadmap as steps.
                        
                            5. 🛠️ Projects & Practice
                            6. 🏆 Success Metrics

                            Make it practical with clear steps and achievable goals.
                            """
                            response = model.generate_content(prompt)
                            roadmap_text = response.text

                            # Store roadmap in session state
                            st.session_state.current_roadmap = {
                                "topic": roadmap_topic,
                                "content": roadmap_text,
                                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                            }

                            st.markdown(roadmap_text)

                            # Add viewing capability for roadmaps
                            st.markdown("---")
                            if st.button("🗺️ Open Roadmap in Full View", use_container_width=True,
                                         key="open_roadmap_view"):
                                st.session_state.currently_viewing_roadmap = st.session_state.current_roadmap
                                st.rerun()

                            # Update streak for roadmap generation too
                            update_streak()

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

    # -------------------- HOW TO USE TAB --------------------
    with main_tab[1]:
        st.title("📝 How to Use This App")
        st.markdown("""
        ### 🎓 Learning with AI Module Generator

        1. **Generate Modules**: Create AI-powered learning modules with exercises
        2. **Create Roadmaps**: Get structured learning paths with milestones
        3. **Track Progress**: Real-time streaks, badges, and completion tracking

        ### 🔥 Streak System
        - **Daily Learning**: Generate or complete modules daily
        - **Login Bonus**: Using the app daily increases login streak
        - **Don't Break**: Missing a day resets learning streak

        ### 🏆 Badge System
        Earn badges for:
        - Learning streaks (3, 7, 15, 30+ days)
        - Module completions (1, 3, 5, 10, 15+)
        - Progress milestones (25%, 50%, 75%, 100%)
        - Level mastery (Beginner, Intermediate, Advanced)
        - Special achievements
        """)

    # -------------------- ABOUT TAB --------------------
    with main_tab[2]:
        st.title("ℹ About This App")
        st.markdown("""
        **ModuleGPT - AI Module and Roadmap Generator** - Your personal AI learning companion

        ### 🚀 Features:
        - **Smart Module Generation**: Create detailed courses with exercises
        - **Learning Roadmaps**: Visualize your learning journey
        - **Progress Tracking**: Real streaks, badges, and completion system
        - **Customizable Interface**: Full theme and font size control

        *"Learn smarter. Stay motivated. Achieve more with AI guidance."*
        """)

    # -------------------- BADGES & PROGRESS TAB --------------------
    with main_tab[3]:
        st.title("🏆 Badges & Progress System")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Your Current Badges")
            if st.session_state.user_profile["badges"]:
                st.markdown('<div class="badge-container">', unsafe_allow_html=True)
                for badge in st.session_state.user_profile["badges"]:
                    st.markdown(f'<span class="badge">{badge}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Complete modules to earn your first badge!")

        with col2:
            st.subheader("📊 Your Progress")
            st.metric("Current Streak", f"{st.session_state.user_profile['streak']} days")
            st.metric("Login Streak", f"{st.session_state.user_profile['login_streak']} days")
            st.metric("Modules Completed", f"{len(st.session_state.user_profile['completed_modules'])}")
            st.metric("Overall Progress", f"{st.session_state.user_profile['progress']}%")

        st.subheader("🎖️ Available Badges")

        badge_categories = {
            "🔥 Streak Badges": [
                ("🔥 3-Day Streak", "Maintain 3-day learning streak"),
                ("⚡ 7-Day Streak", "Maintain 7-day learning streak"),
                ("🚀 15-Day Streak", "Maintain 15-day learning streak"),
                ("🏆 Monthly Master", "Maintain 30-day learning streak"),
                ("💎 Diamond Learner", "Maintain 60-day learning streak")
            ],
            "📅 Consistency Badges": [
                ("📅 Consistent", "5-day login streak"),
                ("🗓️ Dedicated", "15-day login streak"),
                ("📊 Committed", "30-day login streak")
            ],
            "🎓 Completion Badges": [
                ("🌱 First Step", "Complete your first module"),
                ("📚 Quick Learner", "Complete 3 modules"),
                ("🎯 Focused", "Complete 5 modules"),
                ("🎓 Knowledge Seeker", "Complete 10 modules"),
                ("🌟 Learning Star", "Complete 15 modules"),
                ("🚀 Fast Tracker", "Complete 25 modules"),
                ("🏅 Master Learner", "Complete 50 modules")
            ],
            "📈 Progress Badges": [
                ("📈 Getting There", "Reach 25% overall progress"),
                ("🎪 Halfway Hero", "Reach 50% overall progress"),
                ("✨ Almost There", "Reach 75% overall progress"),
                ("✅ Completionist", "Reach 100% overall progress")
            ],
            "🟢 Level Mastery": [
                ("🟢 Beginner Pro", "Complete 3 beginner modules"),
                ("🟡 Intermediate Pro", "Complete 3 intermediate modules"),
                ("🔴 Advanced Pro", "Complete 3 advanced modules")
            ],
            "🌟 Special Badges": [
                ("🏗️ Module Builder", "Save 10+ modules"),
                ("📚 Collector", "Save 5+ modules"),
                ("🧠 Expert", "Complete an expert-level module")
            ]
        }

        for category, badges in badge_categories.items():
            with st.expander(f"{category} ({len(badges)} badges)"):
                for badge, description in badges:
                    earned = badge in st.session_state.user_profile["badges"]
                    emoji = "✅" if earned else "⏳"
                    st.markdown(f"""
                    <div style="background: {'#2D2D2D' if st.session_state.dark_mode else '#F0F2F6'}; 
                              border-radius: 10px; padding: 15px; margin: 5px 0; 
                              border-left: 4px solid #6C63FF;">
                        <strong>{emoji} {badge}</strong><br>
                        <small>{description}</small>
                    </div>
                    """, unsafe_allow_html=True)

# -------------------- LEFT SIDEBAR CONTENT --------------------
# Saved Modules Section
with st.sidebar.expander("💾 Saved Modules", expanded=True):
    if st.session_state.saved_modules:
        st.markdown(f"### Your Modules ({len(st.session_state.saved_modules)})")

        for module_name, module_data in list(st.session_state.saved_modules.items()):
            # Get level emoji
            level_emoji = {
                "Beginner": "🟢",
                "Intermediate": "🟡",
                "Advanced": "🔴"
            }.get(module_data.get("level", "Beginner"), "📚")

            # Check if completed
            is_completed = module_name in st.session_state.user_profile["completed_modules"]
            status_emoji = "✅" if is_completed else "📖"

            st.markdown(f"""
            <div class="history-item">
                <strong>{status_emoji} {level_emoji} {module_name}</strong><br>
                <small>Level: {module_data.get('level', 'N/A')} • {module_data.get('timestamp', 'Recently')}</small>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Open", key=f"open_{module_name}", use_container_width=True):
                    st.session_state.currently_viewing_module = module_name
                    st.rerun()
            with col2:
                if st.button("Delete", key=f"delete_{module_name}", use_container_width=True):
                    st.session_state.show_delete_dialog = module_name
                    st.rerun()
            st.markdown("---")
    else:
        st.info("No saved modules yet. Generate and save your first module!")
    # History Section
    with st.sidebar.expander("📜 Search History", expanded=False):
        if st.session_state.search_history:
            st.markdown("### Recent Searches")

            # Add clear history button at the top
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear All History", use_container_width=True, key="clear_all_history"):
                    st.session_state.search_history = []
                    save_user_data()
                    st.success("History cleared!")
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear Oldest 5", use_container_width=True, key="clear_oldest"):
                    st.session_state.search_history = st.session_state.search_history[5:]
                    save_user_data()
                    st.success("Oldest 5 entries removed!")
                    st.rerun()

            for i, search in enumerate(st.session_state.search_history[:10]):  # Show last 10
                if search["type"] == "module":
                    title = f"📚 Module - {search['topic']}"
                    level = f"Level: {search.get('level', 'N/A')}"
                else:
                    title = f"🗺️ Roadmap - {search['topic']}"
                    level = ""

                # Create columns for each history item with delete button
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"""
                    <div class="history-item">
                        <strong>{title}</strong><br>
                        <small>{level}</small><br>
                        <small>📅 {search['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if search["type"] == "module":
                        if st.button("🔄", key=f"regen_module_{i}", help="Regenerate Module"):
                            st.info(f"Go to Home tab and enter '{search['topic']}' to regenerate")
                    else:
                        if st.button("🔄", key=f"regen_roadmap_{i}", help="Regenerate Roadmap"):
                            st.info(f"Go to Home tab and enter '{search['topic']}' to regenerate roadmap")

                with col3:
                    if st.button("❌", key=f"delete_history_{i}", help="Delete this entry"):
                        st.session_state.search_history.pop(i)
                        save_user_data()
                        st.success("Entry deleted!")
                        st.rerun()

                st.markdown("---")
        else:
            st.info("No search history yet.")

    # Saved Modules Section
    st.sidebar.markdown("### 💾 Saved Modules")
    if st.session_state.saved_modules:
        # Show count of saved modules
        st.sidebar.caption(f"Total: {len(st.session_state.saved_modules)} modules")

        for module_name, module_data in list(st.session_state.saved_modules.items()):
            with st.sidebar.container():
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    # Show module with level indicator
                    level_emoji = {
                        "Beginner": "🟢",
                        "Intermediate": "🟡",
                        "Advanced": "🔴"
                    }.get(module_data.get("level", "Beginner"), "📚")

                    if st.button(f"{level_emoji} {module_name}", key=f"sidebar_module_{module_name}",
                                 use_container_width=True):
                        st.session_state.currently_viewing_module = module_name
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"sidebar_delete_{module_name}"):
                        st.session_state.show_delete_dialog = module_name
                        st.rerun()
    else:
        st.sidebar.info("No saved modules yet. Generate and save your first module!")
    # Delete Module Dialog
    if st.session_state.get('show_delete_dialog'):
        module_to_delete = st.session_state.show_delete_dialog
        st.sidebar.markdown("---")
        st.sidebar.warning(f"Delete '{module_to_delete}'?")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("Yes, Delete", key="confirm_delete"):
                del st.session_state.saved_modules[module_to_delete]
                if module_to_delete in st.session_state.learning_progress:
                    del st.session_state.learning_progress[module_to_delete]
                # Remove from completed modules if it was there
                if module_to_delete in st.session_state.user_profile["completed_modules"]:
                    st.session_state.user_profile["completed_modules"].remove(module_to_delete)
                st.session_state.show_delete_dialog = None
                st.session_state.currently_viewing_module = None
                update_progress()
                save_user_data()
                st.rerun()
        with col2:
            if st.sidebar.button("Cancel", key="cancel_delete"):
                st.session_state.show_delete_dialog = None
                st.rerun()

    # -------------------- BADGES AND PROGRESS SECTION --------------------
    st.sidebar.markdown("### 🏆 Your Badges")
    if st.session_state.user_profile["badges"]:
        badges_html = '<div class="badge-container">'
        for badge in st.session_state.user_profile["badges"][:6]:  # Show first 6 badges
            badges_html += f'<span class="badge">{badge}</span>'
        badges_html += '</div>'
        st.sidebar.markdown(badges_html, unsafe_allow_html=True)
        if len(st.session_state.user_profile["badges"]) > 6:
            st.sidebar.info(f"+{len(st.session_state.user_profile['badges']) - 6} more badges earned!")
    else:
        st.sidebar.info("Complete modules to earn badges!")

    # -------------------- SETTINGS SECTION --------------------
    st.sidebar.markdown("### ⚙️ Settings")

    # Theme Settings
    with st.sidebar.expander("🎨 Theme", expanded=False):
        theme_options = ["Light", "Dark"]
        current_theme_idx = 1 if st.session_state.dark_mode else 0
        selected_theme = st.radio("Select Theme", theme_options, index=current_theme_idx, key="theme_radio")

        if st.button("Apply Theme", key="apply_theme"):
            st.session_state.dark_mode = (selected_theme == "Dark")
            save_user_data()
            st.success(f"Theme changed to {selected_theme}!")
            st.rerun()

    # Font Size Settings
    with st.sidebar.expander("🔠 Font Size", expanded=False):
        font_sizes = ["small", "medium", "large", "xlarge"]
        current_font_idx = font_sizes.index(st.session_state.font_size)
        selected_font = st.radio("Select Font Size", font_sizes, index=current_font_idx, key="font_radio")

        if st.button("Apply Font Size", key="apply_font"):
            st.session_state.font_size = selected_font
            save_user_data()
            st.success(f"Font size changed to {selected_font}!")
            st.rerun()

    # Edit Profile Settings
    with st.sidebar.expander("👤 Edit Profile", expanded=False):
        st.markdown("### Edit Your Profile")

        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input("Full Name", value=st.session_state.user_profile["name"])
                email = st.text_input("Email Address", value=st.session_state.user_profile.get("email", ""))

            with col2:
                daily_goal = st.number_input(
                    "Daily Study Goal (minutes)",
                    min_value=15,
                    max_value=240,
                    value=st.session_state.user_profile.get("daily_goal", 60),
                    step=15
                )

            expertise_level = st.selectbox(
                "Current Expertise Level",
                ["Beginner", "Intermediate", "Advanced", "Expert"],
                index=["Beginner", "Intermediate", "Advanced", "Expert"].index(
                    st.session_state.user_profile.get("expertise_level", "Beginner")
                )
            )

            if st.form_submit_button("Update Profile"):
                st.session_state.user_profile["name"] = new_name
                st.session_state.user_profile["email"] = email
                st.session_state.user_profile["daily_goal"] = daily_goal
                st.session_state.user_profile["expertise_level"] = expertise_level
                save_user_data()
                st.success("✅ Profile updated successfully!")
                st.rerun()

    # Progress Overview
    st.sidebar.markdown("### 📊 Learning Stats")
    st.sidebar.write(f"**Learning Streak:** {st.session_state.user_profile['streak']} days")
    st.sidebar.write(f"**Login Streak:** {st.session_state.user_profile['login_streak']} days")
    st.sidebar.write(f"**Completed:** {len(st.session_state.user_profile['completed_modules'])} modules")
    st.sidebar.write(f"**Progress:** {st.session_state.user_profile['progress']}%")
