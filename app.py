import streamlit as st
import plotly.express as px
from supabase import create_client

# Page Setup
st.set_page_config(page_title="Apex Golf Suite", page_icon="⛳", layout="centered")

# --- MASTER DATABASE CONNECTION ---
SUPABASE_URL = "https://supabase.co"
# Paste your sb_secret_... master key directly inside these quotes:
SUPABASE_KEY = "sb_secret_af0d-D0KIMngye7ERnHMGQ_xVkdSu6l"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CLOUD DATABASE STORAGE FUNCTIONS ---
def load_profiles():
    """Fetches all player rows from the Supabase cloud table."""
    try:
        response = supabase.table("golf_profiles").select("*").execute()
        data_dict = {}
        for row in response.data:
            data_dict[row["username"]] = {
                "password": row["password"],
                "rounds": row["rounds"]
            }
        return data_dict
    except Exception:
        return {}

def save_new_profile_cloud(username, password):
    """Inserts a brand new user row into the cloud database."""
    supabase.table("golf_profiles").insert({
        "username": username,
        "password": password,
        "rounds": []
    }).execute()

def update_user_rounds_cloud(username, rounds_list):
    """Updates the rounds list for an existing user in the cloud database."""
    supabase.table("golf_profiles").update({
        "rounds": rounds_list
    }).eq("username", username).execute()


# --- COURSE DATABASE ---
COURSE_DATA = {
    "basset 12 hole": {"pars": [4,3,4,3,5,4,4,4,4,4,4,5], "rating": 46.2, "slope": 115},
    "broome 9 hole": {"pars": [3,4,3,5,3,3,4,4,3], "rating": 34.5, "slope": 113},
    "broome 18 hole": {"pars": [5,4,3,4,4,3,4,4,4,4,3,5,4,4,3,4,5,4], "rating": 70.2, "slope": 124},
    "basset 18 hole": {"pars": [4,3,4,4,4,4,4,4,5,4,3,4,4,4,4,4,4,5], "rating": 69.8, "slope": 121},
    "ogbourne": {"pars": [4,4,4,3,4,4,4,3,5,5,4,4,4,5,3,4,3,4], "rating": 71.1, "slope": 128},
    "wragbarn": {"pars": [4,4,3,5,3,5,4,4,4,5,4,3,4,4,4,3,5,4], "rating": 71.5, "slope": 131}
}


# --- ENGINE MATHEMATICS ---
def calculate_differential(score_list, course_name):
    course = COURSE_DATA.get(course_name)
    total_strokes = sum(score_list)
    is_9_hole = len(course["pars"]) == 9
    multiplier = 113
    if is_9_hole:
        diff = ((total_strokes - course["rating"]) * (multiplier / course["slope"])) * 2
    else:
        diff = (total_strokes - course["rating"]) * (multiplier / course["slope"])
    return round(diff, 1)

def calculate_course_handicap(handicap_index, course_name):
    course = COURSE_DATA.get(course_name)
    if not course or handicap_index == "No rounds played":
        return 0
    total_par = sum(course["pars"])
    return round(handicap_index * (course["slope"] / 113) + (course["rating"] - total_par))

def calculate_stableford(score_list, course_name, handicap_index):
    course = COURSE_DATA.get(course_name)
    if not course: return 0
    course_handicap = calculate_course_handicap(handicap_index, course_name)
    pars = course["pars"]
    num_holes = len(pars)
    base_strokes = course_handicap // num_holes
    extra_strokes = course_handicap % num_holes
    
    total_points = 0
    for i, gross in enumerate(score_list):
        allowed_strokes = base_strokes + (1 if i < extra_strokes else 0)
        net_score = gross - allowed_strokes
        points = pars[i] - net_score + 2
        if points > 0:
            total_points += points
    return total_points

def get_counting_rounds_indices(differentials):
    roundsplayed = len(differentials)
    if roundsplayed == 0: return []
    recent_indices = list(range(max(0, roundsplayed - 20), roundsplayed))
    sorted_by_val = sorted(recent_indices, key=lambda idx: differentials[idx])
    if roundsplayed < 3: return recent_indices
    elif roundsplayed <= 5: return [sorted_by_val]
    elif roundsplayed >= 20: return sorted_by_val[:8]
    else:
        count = 3 if roundsplayed < 15 else 4
        return sorted_by_val[:count]

def calculate_handicap_value(differentials):
    roundsplayed = len(differentials)
    if roundsplayed == 0: return "No rounds played"
    counting_indices = get_counting_rounds_indices(differentials)
    counting_vals = [differentials[idx] for idx in counting_indices]
    return round(sum(counting_vals) / len(counting_vals), 1)

def check_achievements(user_rounds):
    badges = []
    course_counts = {}
    for r in user_rounds:
        course_counts[r["course"]] = course_counts.get(r["course"], 0) + 1
        for i, stroke in enumerate(r["hole_scores"]):
            par = COURSE_DATA[r["course"]]["pars"][i]
            if stroke == par - 1:
                if "🦅 Birdie Hunter" not in badges: badges.append("🦅 Birdie Hunter")
            if stroke <= par - 2:
                if "⚡ Albatross/Eagle Eye" not in badges: badges.append("⚡ Albatross/Eagle Eye")
    if len(user_rounds) >= 1: badges.append("🌱 First Tee Drop")
    if len(user_rounds) >= 10: badges.append("🎒 Grinder (10+ Rounds)")
    for course, count in course_counts.items():
        if count >= 5:
            badges.append(f"👑 Local King ({course.capitalize()})")
            break
    return badges


# --- APPLICATION CONTROLLER ---
profiles = load_profiles()

st.sidebar.header("🔐 Player Auth")
name_input = st.sidebar.text_input("Profile Name:").strip().lower()
password_input = st.sidebar.text_input("Password:", type="password")

authenticated = False

if name_input and password_input:
    if name_input in profiles:
        if profiles[name_input]["password"] == password_input:
            st.sidebar.success(f"Logged in as {name_input.capitalize()}")
            authenticated = True
        else:
            st.sidebar.error("Incorrect password.")
    else:
        if st.sidebar.button("Create Secure Profile"):
            save_new_profile_cloud(name_input, password_input)
            st.sidebar.success("Account created in cloud database!")
            st.rerun()

if not authenticated:
    st.warning("Please sign in or create an account in the sidebar to load the features.")
else:
    display_name = name_input.capitalize()
    user_rounds = profiles[name_input].get("rounds", [])
    differentials = [r["differential"] for r in user_rounds]
    current_hc = calculate_handicap_value(differentials)
    hc_float = current_hc if isinstance(current_hc, float) else 0.0

    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 Live Scorecard", 
        "📊 Dashboard & Badges", 
        "👥 Versus Match", 
        "🏆 Leaderboards"
    ])

    # TAB 1: LIVE INTERACTIVE DIGITAL SCORECARD
    with tab1:
        st.header("Live Round Scorecard")
        course_select = st.selectbox("Select Target Course Layout:", list(COURSE_DATA.keys()))
        course_pars = COURSE_DATA[course_select]["pars"]
        
        st.write("---")
        if "live_scores" not in st.session_state or st.session_state.get("current_course_track") != course_select:
            st.session_state["live_scores"] = [int(p) for p in course_pars]
            st.session_state["current_course_track"] = course_select

        cols = st.columns(3)
        for idx, par_val in enumerate(course_pars):
            col_target = cols[idx % 3]
            with col_target:
                st.session_state["live_scores"][idx] = st.number_input(
                    f"Hole {idx+1} (Par {par_val})", 
                    min_value=1, max_value=15, 
                    value=st.session_state["live_scores"][idx], 
                    key=f"hole_input_{idx}"
                )
        
        st.write("---")
        total_live_gross = sum(st.session_state["live_scores"])
        st.metric("Total Cumulative Gross Strokes", total_live_gross)
        
        if st.button("Finalise and Save Live Score"):
            diff = calculate_differential(st.session_state["live_scores"], course_select)
            stableford_pts = calculate_stableford(st.session_state["live_scores"], course_select, hc_float)
            
            user_rounds.append({
                "course": course_select,
                "gross_score": total_live_gross,
                "differential": diff,
                "stableford": stableford_pts,
                "hole_scores": list(st.session_state["live_scores"])
            })
            
            update_user_rounds_cloud(name_input, user_rounds)
            st.success("Round successfully saved to the cloud database!")
            st.rerun()

    # TAB 2: DASHBOARD WITH GAMIFIED ACHIEVEMENT BADGES
    with tab2:
        st.header(f"Performance Stats: {display_name}")
        if not user_rounds:
            st.info("Log a game scorecard entry first to build performance trends.")
        else:
            col1, col2 = st.columns(2)
            col1.metric("WHS Handicap Index", str(current_hc))
            col2.metric("Total Played Rounds", len(user_rounds))
            
            historical_indices = [calculate_handicap_value(differentials[:i]) for i in range(1, len(differentials) + 1)]
            fig = px.line(x=list(range(1, len(user_rounds) + 1)), y=historical_indices, labels={"x":"Round Tracker No.", "y":"Handicap"}, markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("🏅 Unlocked Achievement Badges")
            unlocked_badges = check_achievements(user_rounds)
            if unlocked_badges:
                badge_cols = st.columns(2)
                for b_idx, badge in enumerate(unlocked_badges):
                    badge_cols[b_idx % 2].info(f"**{badge}**")
            else:
                st.caption("No custom metric achievement targets unlocked yet.")
                
            st.write("---")
            st.subheader("WHS Verification Tracking Table")
            counting_indices = get_counting_rounds_indices(differentials)
            for idx, r in enumerate(user_rounds):
                if idx in counting_indices:
