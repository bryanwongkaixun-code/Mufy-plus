import streamlit as st
import json
import os
from datetime import datetime, timedelta
import zoneinfo

# Set up the page layout
st.set_page_config(page_title="Pro Library Seating", layout="centered")

# ------------------------------------------------------------------
# 🌐 TIMEZONE CORRECTION UTILITY
# ------------------------------------------------------------------
detected_tz_str = st.context.timezone
MANUAL_TIMEZONE_OVERRIDE = "Asia/Kuala_Lumpur" 

if detected_tz_str:
    try:
        LOCAL_TZ = zoneinfo.ZoneInfo(detected_tz_str)
    except:
        LOCAL_TZ = zoneinfo.ZoneInfo(MANUAL_TIMEZONE_OVERRIDE)
else:
    LOCAL_TZ = zoneinfo.ZoneInfo(MANUAL_TIMEZONE_OVERRIDE)

# Calculate correct local clock values 
now = datetime.now(LOCAL_TZ)
current_time_str = now.strftime("%I:%M %p")
current_date_str = now.strftime("%Y-%m-%d")

# ------------------------------------------------------------------
# 🎨 VISUAL STYLING
# ------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3, h4, p, span, label { color: #0F172A !important; font-family: sans-serif; }
    .front-desk {
        background-color: #334155; color: #F8FAFC !important; text-align: center; 
        padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 20px;
    }
    
    /* 🟢 GREEN AVAILABLE SEATS */
    div.stButton > button:not([disabled]) {
        background-color: #4ADE80 !important; border: 2px solid #166534 !important; border-radius: 6px !important;
        min-height: 65px !important; padding: 5px !important;
    }
    div.stButton > button:not([disabled]) p { color: #0F172A !important; font-size: 0.95rem !important; font-weight: bold !important; line-height: 1.2 !important; }

    /* 🔴 RED TAKEN SEATS */
    div.stButton > button[disabled] {
        background-color: #F87171 !important; opacity: 1 !important; border: 2px solid #991B1B !important; border-radius: 6px !important;
        min-height: 65px !important; padding: 5px !important;
    }
    div.stButton > button[disabled] p { color: #0F172A !important; font-size: 0.85rem !important; font-weight: bold !important; line-height: 1.2 !important; }
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
st.title("🕒 Smart Library Seating Hub")

selected_library = st.selectbox("Select a Library Branch:", ["Library 1", "Library 2", "Library 3"])
DATA_FILE = os.path.join("/tmp", f"{selected_library.lower().replace(' ', '_')}_v4.json")

# Display correct local clock details
st.write(f"📅 **Date:** {now.strftime('%A, %b %d, %Y')} | ⏰ **Local Time:** {current_time_str} ({LOCAL_TZ.key})")

# ------------------------------------------------------------------
# 📂 2. CACHE STORAGE DATA WITH AUTO-CLEANUP
# ------------------------------------------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                saved = json.load(f)
                seats = saved.get("seats", [['O' for _ in range(COLS)] for _ in range(ROWS)])
                bookings = saved.get("bookings", {})
                
                # Check timestamps and automatically remove expired seats!
                expired_keys = []
                for key, info in bookings.items():
                    if "expiry_timestamp" in info:
                        if now.timestamp() > info["expiry_timestamp"]:
                            expired_keys.append(key)
                
                for key in expired_keys:
                    r, c = map(int, key.split(","))
                    seats[r-1][c-1] = 'O'
                    bookings.pop(key, None)
                    
                return seats, bookings
        except:
            pass
    return [['O' for _ in range(COLS)] for _ in range(ROWS)], {}

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump({"seats": st.session_state.seats, "bookings": st.session_state.bookings}, f, indent=4)
    except:
        pass

if "current_room" not in st.session_state or st.session_state.current_room != selected_library:
    st.session_state.current_room = selected_library
    st.session_state.seats, st.session_state.bookings = load_data()

# Metrics
taken_count = len(st.session_state.bookings)
open_count = TOTAL_SEATS - taken_count

col_m1, col_m2 = st.columns(2)
col_m1.metric("🟢 Seats Available Right Now", open_count)
col_m2.metric("🔴 Active Reservations", taken_count)
st.markdown("---")

# ------------------------------------------------------------------
# 🔍 3. SEARCH DIRECTORY
# ------------------------------------------------------------------
search_query = st.text_input("🔍 Search Student Database:", placeholder="Type student name to find their desk...").strip()

if search_query:
    found = False
    for coord, info in st.session_state.bookings.items():
        if search_query.lower() in info["name"].lower():
            r, c = coord.split(",")
            st.success(f"📍 **{info['name']}** is reserved at **Row {r}, Column {c}** [Date: {info['date']} | Till: {info['expiry_time']}]")
            found = True
    if not found:
        st.error(f"❌ No active booking found matching '{search_query}'.")

# ------------------------------------------------------------------
# 📍 4. INTERACTIVE SEATING MATRIX
# ------------------------------------------------------------------
st.markdown('<div class="front-desk">🖥️ MAIN ENTRANCE AREA & RECEPTION</div>', unsafe_allow_html=True)

for r in range(ROWS):
    grid_cols = st.columns([1, 1, 1, 0.4, 1, 1, 1]) 
    row_num = r + 1

    # Left Wing Matrix (Columns 1-3)
    for c in range(3):
        col_num = c + 1
        coord_key = f"{row_num},{col_num}"
        status = st.session_state.seats[r][c]
        
        if status == 'O':
            label = f"R{row_num}C{col_num}\n[ O ]"
        else:
            b_info = st.session_state.bookings.get(coord_key, {})
            # Displays the name (shortened if too long) and expiration time
            student_display = b_info.get('name', 'Taken')[:8]
            label = f"R{row_num}C{col_num}\n👤 {student_display}\n⏳ {b_info.get('expiry_time', 'X')}"
        
        with grid_cols[c]:
            if st.button(label, key=f"btn_L_{selected_library}_{row_num}_{col_num}", disabled=(status == 'X'), use_container_width=True):
                st.session_state.selected_row = row_num
                st.session_state.selected_col = col_num
                st.rerun()

    # Walkway Gap Aisle Spacer
    with grid_cols[3]:
        st.markdown("<p style='text-align:center; margin-top:22px; color:#94A3B8;'>🚶‍♂️</p>", unsafe_allow_html=True)

    # Right Wing Matrix (Columns 4-6)
    for c in range(3, 6):
        col_num = c + 1
        coord_key = f"{row_num},{col_num}"
        status = st.session_state.seats[r][c]
        
        if status == 'O':
            label = f"R{row_num}C{col_num}\n[ O ]"
        else:
            b_info = st.session_state.bookings.get(coord_key, {})
            # Displays the name (shortened if too long) and expiration time
            student_display = b_info.get('name', 'Taken')[:8]
            label = f"R{row_num}C{col_num}\n👤 {student_display}\n⏳ {b_info.get('expiry_time', 'X')}"
        
        with grid_cols[c+1]:
            if st.button(label, key=f"btn_R_{selected_library}_{row_num}_{col_num}", disabled=(status == 'X'), use_container_width=True):
                st.session_state.selected_row = row_num
                st.session_state.selected_col = col_num
                st.rerun()

st.write("💡 *Tip: Click any green seat above to auto-fill the form coordinates below.*")
st.markdown("---")

# ------------------------------------------------------------------
# ⚙️ 5. INTERACTIVE BOOKING PANEL
# ------------------------------------------------------------------
action = st.radio("Management Selection Menu:", ["🟢 Reserve a Desk Slot", "🔴 Release / Cancel Slot"], horizontal=True)

if action == "🟢 Reserve a Desk Slot":
    st.subheader("✨ Clear Booking Setup Form")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        name = st.text_input("Enter Student Full Name:").strip()
        booking_date = st.radio("Choose Date Window:", ["Today Only", "Tomorrow Advance Reserve"], horizontal=True)
    with col_input2:
        duration = st.selectbox("Booking Session Duration Profile:", ["1 Hour Slot", "2 Hours Slot", "4 Hours Slot", "8 Hours All-Day Study Session"])
        
    c1, c2 = st.columns(2)
    row_input = c1.number_input("Selected Row:", min_value=1, max_value=ROWS, value=st.session_state.selected_row, step=1)
    col_input = c2.number_input("Selected Column:", min_value=1, max_value=COLS, value=st.session_state.selected_col, step=1)
    
    if st.button("Submit Reservation", type="primary", use_container_width=True):
        r_idx, c_idx = row_input - 1, col_input - 1
        key = f"{row_input},{col_input}"
        
        already_booked = any(info.get("name").lower() == name.lower() for info in st.session_state.bookings.values())
        
        if not name:
            st.error("❌ Action stopped: You must provide a student name.")
        elif st.session_state.seats[r_idx][c_idx] == 'X':
            st.error("❌ Action stopped: Someone else has locked that seat coordinate.")
        elif already_booked:
            st.error(f"❌ Target conflict: '{name}' already owns an active desk inside this library registry.")
        else:
            duration_map = {"1 Hour Slot": 1, "2 Hours Slot": 2, "4 Hours Slot": 4, "8 Hours All-Day Study Session": 8}
            hours_added = duration_map.get(duration, 2)
            
            target_date = now if booking_date == "Today Only" else (now + timedelta(days=1))
            expiry_datetime = target_date + timedelta(hours=hours_added)
            
            st.session_state.seats[r_idx][c_idx] = 'X'
            st.session_state.bookings[key] = {
                "name": name,
                "date": target_date.strftime("%Y-%m-%d"),
                "start_time": current_time_str,
                "expiry_time": expiry_datetime.strftime("%I:%M %p"),
                "expiry_timestamp": expiry_datetime.timestamp()
            }
            save_data()
            st.success(f"🎉 R{row_input}C{col_input} locked for {name}! Reserved until {expiry_datetime.strftime('%I:%M %p')}.")
            st.rerun()

elif action == "🔴 Release / Cancel Slot":
    st.subheader("🔄 Clear Running Slot Session")
    
    c1, c2 = st.columns(2)
    row_input = c1.number_input("Target Row location:", min_value=1, max_value=ROWS, step=1)
    col_input = c2.number_input("Target Column location:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Execute Node Reset Release", type="primary", use_container_width=True):
        r_idx, c_idx = row_input - 1, col_input - 1
        key = f"{row_input},{col_input}"
        
        if st.session_state.seats[r_idx][c_idx] == 'O':
            st.warning("⚠️ Notice: The requested coordinate target is already empty.")
        else:
            removed = st.session_state.bookings.pop(key, {})
            st.session_state.seats[r_idx][c_idx] = 'O'
            save_data()
            st.success(f"🔄 Success: Desk session linked to {removed.get('name', 'Unknown Student')} removed.")
            st.rerun()

# ------------------------------------------------------------------
# 💾 6. BONUS: EMERGENCY DATA ADMIN BACKUP GENERATOR
# ------------------------------------------------------------------
st.markdown("---")
with st.expander("🛠️ System Administrator Backup Tool"):
    st.write("Since cloud instances reset periodically, use the text field below to copy out your data backup block text or paste it back in to restore data!")
    raw_json_backup = json.dumps({"seats": st.session_state.seats, "bookings": st.session_state.bookings})
    st.text_area("Current Database Backup Payload String:", value=raw_json_backup, height=70)