import streamlit as st
import json
import os
from datetime import datetime

# Set up the page layout
st.set_page_config(page_title="Library Seating", layout="centered")

# ------------------------------------------------------------------
# 🎨 VISUAL STYLING (Forcing high contrast and clear layouts)
# ------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { 
        background-color: #F8FAFC; 
    }
    h1, h2, h3, h4, p, span, label { 
        color: #0F172A !important; 
        font-family: sans-serif;
    }
    .front-desk {
        background-color: #334155; 
        color: #F8FAFC !important;
        text-align: center; 
        padding: 10px; 
        border-radius: 6px;
        font-weight: bold; 
        margin-bottom: 20px;
    }
    
    /* 🟢 GREEN AVAILABLE SEATS */
    div.stButton > button:not([disabled]) {
        background-color: #4ADE80 !important; 
        border: 2px solid #166534 !important; 
        border-radius: 6px !important;
    }
    div.stButton > button:not([disabled]) p { 
        color: #0F172A !important; 
        font-size: 1.1rem !important; 
        font-weight: bold !important; 
    }

    /* 🔴 RED TAKEN SEATS */
    div.stButton > button[disabled] {
        background-color: #F87171 !important; 
        opacity: 1 !important; 
        border: 2px solid #991B1B !important; 
        border-radius: 6px !important;
    }
    div.stButton > button[disabled] p { 
        color: #0F172A !important; 
        font-size: 1.1rem !important; 
        font-weight: bold !important; 
    }
    </style>
    """, unsafe_allow_html=True)

ROWS = 7
COLS = 6
TOTAL_SEATS = ROWS * COLS

if "selected_row" not in st.session_state: st.session_state.selected_row = 1
if "selected_col" not in st.session_state: st.session_state.selected_col = 1

# ------------------------------------------------------------------
# 🚪 1. CHOOSE LIBRARY
# ------------------------------------------------------------------
st.title("📚 Library Seating Manager")

selected_library = st.selectbox("Select a Library:", ["Library 1", "Library 2", "Library 3"])
DATA_FILE = f"{selected_library.lower().replace(' ', '_')}.json"

# ------------------------------------------------------------------
# 📂 2. LOAD & SAVE DATA
# ------------------------------------------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                saved_dict = json.load(f)
                seats = saved_dict.get("seats", [['O' for _ in range(COLS)] for _ in range(ROWS)])
                bookings = saved_dict.get("bookings", {})
                return seats, bookings
        except:
            pass
    return [['O' for _ in range(COLS)] for _ in range(ROWS)], {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"seats": st.session_state.seats, "bookings": st.session_state.bookings}, f, indent=4)

if "current_room" not in st.session_state or st.session_state.current_room != selected_library:
    st.session_state.current_room = selected_library
    st.session_state.seats, st.session_state.bookings = load_data()

# Quick counters
taken_count = len(st.session_state.bookings)
open_count = TOTAL_SEATS - taken_count

col_m1, col_m2 = st.columns(2)
col_m1.metric("🟢 Available Seats", open_count)
col_m2.metric("🔴 Occupied Seats", taken_count)
st.markdown("---")

# ------------------------------------------------------------------
# 🔍 3. SEARCH INFO
# ------------------------------------------------------------------
search_query = st.text_input("🔍 Find a student's seat:", placeholder="Type student name...").strip()

if search_query:
    found = False
    for coord, info in st.session_state.bookings.items():
        if search_query.lower() in info["name"].lower():
            r, c = coord.split(",")
            st.success(f"📍 **{info['name']}** is sitting at **Row {r}, Column {c}** (Booked: {info['time']})")
            found = True
    if not found:
        st.error(f"❌ Could not find anyone named '{search_query}'.")

# ------------------------------------------------------------------
# 📍 4. SEATING CHART GRID
# ------------------------------------------------------------------
st.markdown('<div class="front-desk">🖥️ FRONT COUNTER / ENTRANCE</div>', unsafe_allow_html=True)

for r in range(ROWS):
    grid_cols = st.columns([1, 1, 1, 0.4, 1, 1, 1]) 
    row_num = r + 1

    # Left Wing (Columns 1-3)
    for c in range(3):
        col_num = c + 1
        coord_key = f"{row_num},{col_num}"
        status = st.session_state.seats[r][c]
        
        label = f"R{row_num}C{col_num}\n[ O ]" if status == 'O' else f"R{row_num}C{col_num}\n[{st.session_state.bookings.get(coord_key, {}).get('name', 'X')}]"
        
        with grid_cols[c]:
            if st.button(label, key=f"btn_L_{row_num}_{col_num}", disabled=(status == 'X'), use_container_width=True):
                st.session_state.selected_row = row_num
                st.session_state.selected_col = col_num
                st.rerun()

    # Center Aisle Walkway
    with grid_cols[3]:
        st.markdown("<p style='text-align:center; margin-top:12px; color:#94A3B8;'>🚶‍♂️</p>", unsafe_allow_html=True)

    # Right Wing (Columns 4-6)
    for c in range(3, 6):
        col_num = c + 1
        coord_key = f"{row_num},{col_num}"
        status = st.session_state.seats[r][c]
        
        label = f"R{row_num}C{col_num}\n[ O ]" if status == 'O' else f"R{row_num}C{col_num}\n[{st.session_state.bookings.get(coord_key, {}).get('name', 'X')}]"
        
        with grid_cols[c+1]:
            if st.button(label, key=f"btn_R_{row_num}_{col_num}", disabled=(status == 'X'), use_container_width=True):
                st.session_state.selected_row = row_num
                st.session_state.selected_col = col_num
                st.rerun()

st.write("💡 *Tip: Click any green seat above to auto-fill the numbers below.*")
st.markdown("---")

# ------------------------------------------------------------------
# ⚙️ 5. BOOK / CANCEL ACTIONS
# ------------------------------------------------------------------
action = st.radio("Choose action:", ["🟢 Book a Seat", "🔴 Cancel a Booking"], horizontal=True)

if action == "🟢 Book a Seat":
    st.subheader("✨ New Booking")
    name = st.text_input("Student Name:").strip()
    
    c1, c2 = st.columns(2)
    row_input = c1.number_input("Row Number:", min_value=1, max_value=ROWS, value=st.session_state.selected_row, step=1)
    col_input = c2.number_input("Column Number:", min_value=1, max_value=COLS, value=st.session_state.selected_col, step=1)
    
    if st.button("Confirm Booking", type="primary"):
        r_idx, c_idx = row_input - 1, col_input - 1
        key = f"{row_input},{col_input}"
        
        already_booked = any(info.get("name").lower() == name.lower() for info in st.session_state.bookings.values())
        
        if not name:
            st.error("❌ Please enter a student name.")
        elif st.session_state.seats[r_idx][c_idx] == 'X':
            st.error("❌ That seat is already taken!")
        elif already_booked:
            st.error(f"❌ {name} already has a seat booked in this library.")
        else:
            now_str = datetime.now().strftime("%I:%M %p")
            st.session_state.seats[r_idx][c_idx] = 'X'
            st.session_state.bookings[key] = {"name": name, "time": now_str}
            save_data()
            st.success(f"🎉 Seat R{row_input}C{col_input} successfully booked for {name}!")
            st.rerun()

elif action == "🔴 Cancel a Booking":
    st.subheader("🔄 Cancel Booking")
    
    c1, c2 = st.columns(2)
    row_input = c1.number_input("Row Number:", min_value=1, max_value=ROWS, step=1)
    col_input = c2.number_input("Column Number:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Remove Booking", type="primary"):
        r_idx, c_idx = row_input - 1, col_input - 1
        key = f"{row_input},{col_input}"
        
        if st.session_state.seats[r_idx][c_idx] == 'O':
            st.warning("⚠️ This seat is already empty.")
        else:
            removed = st.session_state.bookings.pop(key, {})
            st.session_state.seats[r_idx][c_idx] = 'O'
            save_data()
            st.success(f"🔄 Cancelled booking for {removed.get('name', 'Unknown')}.")
            st.rerun()