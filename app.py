import streamlit as st
import math

# 1. CONSTANTS & WEIGHTS (Extracted from your 'Model' sheet)
# If you run the Solver in Excel and weights change, update these values.
WEIGHTS = {
    'wInf_Atk': 0.0853, 'wInf_Def': 0.1150, 'wInf_Let': 0.0664, 'wInf_HP': 0.1333,
    'wLan_Atk': 0.0643, 'wLan_Def': 0.0823, 'wLan_Let': 0.0608, 'wLan_HP': 0.0475,
    'wMar_Atk': 0.0807, 'wMar_Def': 0.0735, 'wMar_Let': 0.1130, 'wMar_HP': 0.0780,
    'k': 10.0,
    'b': 0.0
}

# 2. CALCULATION LOGIC
def calculate_team_score(levels, counts, boosts):
    """
    Replicates the 'RawScore' logic: 
    Sum of (Level * Count * (1 + Boost_Decimal)) * Weight for each attribute.
    """
    score = 0
    types = ['Inf', 'Lan', 'Mar']
    attributes = ['Atk', 'Def', 'Let', 'HP']
    
    for t in types:
        lvl = levels[t]
        cnt = counts[t]
        for attr in attributes:
            weight_key = f'w{t}_{attr}'
            boost_val = boosts[t][attr]
            # Core Formula: (Level * Count * (1 + Boost)) * Weight
            score += (lvl * cnt * (1 + boost_val)) * WEIGHTS[weight_key]
            
    return score

# 3. STREAMLIT UI SETUP
st.set_page_config(page_title="Battle Predictor v10", layout="wide", page_icon="⚔️")

st.title("⚔️ Battle Outcome Predictor v10")
st.markdown("Enter the stats for Team A and Team B to predict the win probability based on your model.")

col_a, col_b = st.columns(2)

# --- TEAM A INPUTS ---
with col_a:
    st.header("🛡️ Team A (Attacker)")
    
    with st.expander("Troop Levels & Counts", expanded=True):
        a_levels = {
            'Inf': st.number_input("Infantry Level (A)", value=10.0, step=0.1, key="a_inf_l"),
            'Lan': st.number_input("Lancers Level (A)", value=10.0, step=0.1, key="a_lan_l"),
            'Mar': st.number_input("Marksmen Level (A)", value=10.0, step=0.1, key="a_mar_l")
        }
        a_counts = {
            'Inf': st.number_input("Infantry Count (A)", value=74642, key="a_inf_c"),
            'Lan': st.number_input("Lancers Count (A)", value=24714, key="a_lan_c"),
            'Mar': st.number_input("Marksmen Count (A)", value=24714, key="a_mar_c")
        }

    st.subheader("Boosts (Decimal %)")
    a_boosts = {'Inf': {}, 'Lan': {}, 'Mar': {}}
    for t in ['Inf', 'Lan', 'Mar']:
        with st.expander(f"{t} Boosts (A)"):
            a_boosts[t]['Atk'] = st.number_input(f"{t} Atk Boost", value=3.0, format="%.3f", key=f"a_{t}_atk")
            a_boosts[t]['Def'] = st.number_input(f"{t} Def Boost", value=3.0, format="%.3f", key=f"a_{t}_def")
            a_boosts[t]['Let'] = st.number_input(f"{t} Let Boost", value=2.0, format="%.3f", key=f"a_{t}_let")
            a_boosts[t]['HP'] = st.number_input(f"{t} HP Boost", value=2.0, format="%.3f", key=f"a_{t}_hp")

# --- TEAM B INPUTS ---
with col_b:
    st.header("🏰 Team B (Defender)")
    
    with st.expander("Troop Levels & Counts", expanded=True):
        b_levels = {
            'Inf': st.number_input("Infantry Level (B)", value=10.0, step=0.1, key="b_inf_l"),
            'Lan': st.number_input("Lancers Level (B)", value=10.0, step=0.1, key="b_lan_l"),
            'Mar': st.number_input("Marksmen Level (B)", value=10.0, step=0.1, key="b_mar_l")
        }
        b_counts = {
            'Inf': st.number_input("Infantry Count (B)", value=36444, key="b_inf_c"),
            'Lan': st.number_input("Lancers Count (B)", value=36897, key="b_lan_c"),
            'Mar': st.number_input("Marksmen Count (B)", value=48947, key="b_mar_c")
        }

    st.subheader("Boosts (Decimal %)")
    b_boosts = {'Inf': {}, 'Lan': {}, 'Mar': {}}
    for t in ['Inf', 'Lan', 'Mar']:
        with st.expander(f"{t} Boosts (B)"):
            b_boosts[t]['Atk'] = st.number_input(f"{t} Atk Boost", value=3.0, format="%.3f", key=f"b_{t}_atk")
            b_boosts[t]['Def'] = st.number_input(f"{t} Def Boost", value=3.0, format="%.3f", key=f"b_{t}_def")
            b_boosts[t]['Let'] = st.number_input(f"{t} Let Boost", value=2.0, format="%.3f", key=f"b_{t}_let")
            b_boosts[t]['HP'] = st.number_input(f"{t} HP Boost", value=2.0, format="%.3f", key=f"b_{t}_hp")

# --- CALCULATION & RESULTS ---
st.markdown("---")
if st.button("🚀 PREDICT BATTLE OUTCOME", use_container_width=True):
    # Calculate scores
    score_a = calculate_team_score(a_levels, a_counts, a_boosts)
    score_b = calculate_team_score(b_levels, b_counts, b_boosts)
    
    # Logistic Equation: 1 / (1 + exp(-(k * (ScoreA - ScoreB) + b)))
    diff = (WEIGHTS['k'] * (score_a - score_b)) + WEIGHTS['b']
    
    # Clamp extreme values for math stability
    try:
        prob_a = 1 / (1 + math.exp(-diff))
    except OverflowError:
        prob_a = 1.0 if diff > 0 else 0.0

    # Display Result
    st.subheader("Prediction Result")
    
    if prob_a > 0.5:
        st.success(f"**Team A** is predicted to win with **{prob_a:.2%}** probability.")
    else:
        st.error(f"**Team B** is predicted to win. (Team A Win Chance: {prob_a:.2%})")
        
    st.progress(prob_a)
    st.write(f"Raw Score Team A: `{score_a:,.4f}` | Raw Score Team B: `{score_b:,.4f}`")
