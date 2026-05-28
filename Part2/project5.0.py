import streamlit as st
import json
import os
from datetime import datetime
from google import genai

# Set up the page layout
st.set_page_config(page_title="AI Multi-Library Hub", layout="centered")

# ------------------------------------------------------------------
# 🎨 VISUAL STYLING (Forcing Bold Black Text & Custom Layouts)
# ------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { 
        background-color: #F0F2F6; 
    }
    
    /* Force ALL typography to be solid black */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { 
        color: #000000 !important; 
    }
    
    /* Front Counter header decoration */
    .front-desk {
        background-color: #1E293B; 
        color: #FFFFFF !important;
        text-align: center; 
        padding: 12px; 
        border-radius: 6px;
        font-weight: bold; 
        font-size: 1.2rem; 
        margin-bottom: 25px;
    }
    .front-desk p { 
        color: #FFFFFF !important; 
    }
    
    /* 🟢 AVAILABLE SEATS: Green Background with Solid Black Text */
    div.stButton > button:not([disabled]) {
        background-color: #A3E635 !important; 
        border: 2px solid #4D7C0F !important; 
        border-radius: 6px !important;
    }
    div.stButton > button:not([disabled]) p { 
        color: #000000 !important; 
        font-size: 1.15rem !important; 
        font-weight: 900 !important; 
    }

    /* 🔴 BOOKED SEATS: Red Background with Solid Black Text */
    div.stButton > button[disabled] {
        background-color: #F87171 !important; 
        opacity: 1 !important; 
        border: 2px solid #B91C1C !important; 
        border-radius: 6px !important;
    }
    div.stButton > button[disabled] p { 
        color: #000000 !important; 
        font-size: 1.15rem !important; 
        font-weight: 900 !important; 
    }
    
    /* 🔘 LARGER MENU OPTIONS (Radio buttons) */
    div[data-testid="stRadio"] label {
        font-size: 1.2rem !important; 
        font-weight: 800 !important; 
        padding: 8px 16px !important;
        background-color: #FFFFFF; 
        border-radius: 8px; 
        border: 1px solid #CBD5E1; 
        margin-right: 15px !important;
    }
    label p { 
        font-weight: bold !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# Grid Dimensions
ROWS = 7
COLS = 6
TOTAL_SEATS = ROWS * COLS

# Initialize interactive tracking state for direct grid clicking
if "selected_row" not in st.session_state: st.session_state.selected_row = 1
if "selected_col" not in st.session_state: st.session_state.selected_col = 1

# ------------------------------------------------------------------
# 🗺️ 1. LIBRARY SELECTOR
# ------------------------------------------------------------------
st.title("📚 AI-Powered Library Booking Hub")
st.markdown("---")

selected_library = st.selectbox("🚪 Select a Library to view/book:", ["Library 1", "Library 2", "Library 3"])
DATA_FILE = f"{selected_library.lower().replace(' ', '_')}.json"

# ------------------------------------------------------------------
# 📂 2. DATA STORAGE HANDLERS WITH SAFE CONVERSION
# ------------------------------------------------------------------
def load_saved_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            saved_dict = json.load(f)
            seats = saved_dict.get("seats", [['O' for _ in range(COLS)] for _ in range(ROWS)])
            raw_bookings = saved_dict.get("bookings", {})
            
            # Safe Conversion check for legacy data formats
            bookings = {}
            for k, v in raw_bookings.items():
                if isinstance(v, str):
                    bookings[k] = {"name": v, "time": "Legacy Booking (No Timestamp)"}
                else:
                    bookings[k] = v
                    
            if len(seats) < ROWS:
                while len(seats) < ROWS:
                    seats.append(['O' for _ in range(COLS)])
            return seats, bookings
    else:
        return [['O' for _ in range(COLS)] for _ in range(ROWS)], {}

def save_data_to_file():
    data_to_save = {"seats": st.session_state.seats, "bookings": st.session_state.bookings}
    with open(DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

if "current_room" not in st.session_state or st.session_state.current_room != selected_library:
    st.session_state.current_room = selected_library
    loaded_seats, loaded_bookings = load_saved_data()
    st.session_state.seats = loaded_seats
    st.session_state.bookings = loaded_bookings

# Analytics Metrics Dashboard Panel
booked_count = len(st.session_state.bookings)
vacant_count = TOTAL_SEATS - booked_count
occupancy_rate = booked_count / TOTAL_SEATS

m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("🟢 Available Seats", f"{vacant_count} / {TOTAL_SEATS}")
m_col2.metric("🔴 Occupied Seats", f"{booked_count} / {TOTAL_SEATS}")
m_col3.metric("📊 Fill Rate", f"{int(occupancy_rate * 100)}%")
st.progress(occupancy_rate)
st.markdown("---")

# ------------------------------------------------------------------
# 🤖 3. INTELLIGENT GEMINI API ASSISTANT (Seamless Background Key)
# ------------------------------------------------------------------
st.subheader("🤖 Ask Gemini Library Assistant")

ai_prompt = st.text_input("💬 Ask about seat recommendations or layouts:", placeholder="e.g., Recommend me a quiet seat away from the front counter.")

if ai_prompt:
    try:
        # 👇 🔑 PASTE YOUR ACTUAL GEMINI API KEY DIRECTLY INSIDE THE QUOTES BELOW 🔑 👇
        MY_PRIVATE_API_KEY = "AIzaSyD0Oyv9qf64B4SXEjgEwhPWvd7hILLtCCI"
        client = genai.Client(api_key=MY_PRIVATE_API_KEY)
        
        layout_context = f"""
        You are an intelligent library assistant for {selected_library}. 
        The current room layout is a grid of 7 Rows and 6 Columns. 
        Row 1 is closest to the 'FRONT COUNTER / ENTRANCE' (and can be noisy). Row 7 is in the absolute back (quiet zone).
        Columns 1-3 are on the left wing, Columns 4-6 are on the right wing, divided by a walking aisle walkway in the middle.
        
        Here is a list of currently occupied seats and who is sitting in them with their timestamps:
        {json.dumps(st.session_state.bookings)}
        
        The user asks: "{ai_prompt}"
        Provide a concise, helpful answer and suggest specific Row and Column numbers based on their true intent.
        """
        
        with st.spinner("Gemini is analyzing the seating chart..."):
            try:
                # Attempt 1: Try the core Gemini 2.5 Flash model
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=layout_context,
                )
                st.info(f"💬 **Gemini:** {response.text}")
            except Exception as inner_e:
                # Fallback Attempt 2: If 2.5-flash is overloaded (503), immediately try 2.5-pro
                if "503" in str(inner_e) or "UNAVAILABLE" in str(inner_e):
                    response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=layout_context,
                    )
                    st.info(f"💬 **Gemini (Backup Engine):** {response.text}")
                else:
                    raise inner_e
                    
    except Exception as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e):
            st.error("⏳ Google servers are heavily overloaded right now. Please wait a moment and submit your question again!")
        else:
            st.error(f"❌ Connection Failed: {e}")
st.markdown("---")

# ------------------------------------------------------------------
# 🔍 4. SEARCH AND LOCATE A STUDENT
# ------------------------------------------------------------------
st.subheader("🔍 Find a Student's Seat")
search_query = st.text_input("Type student name to locate their seat:", placeholder="e.g. John").strip()

if search_query:
    found = False
    for coord_str, info in st.session_state.bookings.items():
        if search_query.lower() in info["name"].lower():
            row_num, col_num = coord_str.split(",")
            st.success(f"📍 **{info['name']}** is at **Row {row_num}, Column {col_num}** (Reserved on: {info['time']})")
            found = True
    if not found:
        st.error(f"❌ '{search_query}' does not have a registered seat in {selected_library}.")
st.markdown("---")

# ------------------------------------------------------------------
# 📍 5. VISUAL DISPLAY SEATING CHART (Walkway Aisle + Click Tracker)
# ------------------------------------------------------------------
st.subheader(f"📍 Seating Chart: {selected_library}")
st.markdown('<div class="front-desk">🖥️ FRONT COUNTER / ENTRANCE</div>', unsafe_allow_html=True)

for r in range(ROWS):
    cols = st.columns([1, 1, 1, 0.4, 1, 1, 1]) 
    
    # Left Wing (Columns 1-3)
    for c in range(3):
        coord_key = f"{r+1},{c+1}"
        seat_status = st.session_state.seats[r][c]
        seat_label = f"R{r+1}C{c+1}\n[ O ]" if seat_status == 'O' else f"R{r+1}C{c+1}\n[{st.session_state.bookings.get(coord_key, {}).get('name', 'X')}]"
        
        with cols[c]:
            if st.button(seat_label, key=f"btn_L_R{r}C{c}", disabled=(seat_status == 'X'), use_container_width=True):
                st.session_state.selected_row = r + 1
                st.session_state.selected_col = c + 1
                st.rerun()

    # Central Walkway Gap
    with cols[3]:
        st.markdown("<p style='text-align:center; padding-top:10px; font-size:0.8rem; color:#94A3B8 !important;'>🚶‍♂️</p>", unsafe_allow_html=True)

    # Right Wing (Columns 4-6)
    for c in range(3, 6):
        coord_key = f"{r+1},{c+1}"
        seat_status = st.session_state.seats[r][c]
        seat_label = f"R{r+1}C{c+1}\n[ O ]" if seat_status == 'O' else f"R{r+1}C{c+1}\n[{st.session_state.bookings.get(coord_key, {}).get('name', 'X')}]"
        
        with cols[c+1]:
            if st.button(seat_label, key=f"btn_R_R{r}C{c}", disabled=(seat_status == 'X'), use_container_width=True):
                st.session_state.selected_row = r + 1
                st.session_state.selected_col = c + 1
                st.rerun()

st.write("💡 **Tip:** Click any green seat above to fill out your booking numbers instantly below!")
st.markdown("---")

# ------------------------------------------------------------------
# ⚙️ 6. MENU ACTIONS (Book / Cancel Options)
# ------------------------------------------------------------------
st.subheader("⚙️ Select Action")
choice = st.radio("Choose action:", ["1. Book a Seat", "2. Cancel a Booking"], horizontal=True, label_visibility="collapsed")
st.markdown(" ")

# --- OPTION 1: BOOK A SEAT ---
if choice == "1. Book a Seat":
    st.markdown(f"### ✨ Reserve a Seat in {selected_library}")
    name = st.text_input("Enter student name:").strip()
    row = st.number_input("Enter Row number:", min_value=1, max_value=ROWS, value=st.session_state.selected_row, step=1)
    col = st.number_input("Enter Column number:", min_value=1, max_value=COLS, value=st.session_state.selected_col, step=1)
    
    if st.button("Submit Booking", type="primary"):
        r, c = row - 1, col - 1
        target_key = f"{row},{col}"
        
        has_already_booked = any(info.get("name").lower() == name.lower() for info in st.session_state.bookings.values())
        
        if not name:
            st.error("❌ Name cannot be empty.")
        elif st.session_state.seats[r][c] == 'X':
            st.error(f"❌ Error: Seat R{row}C{col} is already taken!")
        elif has_already_booked:
            st.error(f"❌ Error: {name} already has a reservation in this room! Cancel it first to move locations.")
        else:
            current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            st.session_state.seats[r][c] = 'X'
            st.session_state.bookings[target_key] = {
                "name": name,
                "time": current_time_str
            }
            save_data_to_file()
            st.success(f"🎉 Success! Seat R{row}C{col} booked for {name} at {current_time_str}.")
            st.rerun()

# --- OPTION 2: CANCEL A BOOKING ---
elif choice == "2. Cancel a Booking":
    st.markdown(f"### 🔄 Remove a Reservation from {selected_library}")
    row = st.number_input("Enter Row number to cancel:", min_value=1, max_value=ROWS, step=1)
    col = st.number_input("Enter Column number to cancel:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Cancel Reservation", type="primary"):
        r, c = row - 1, col - 1
        target_key = f"{row},{col}"
        
        if st.session_state.seats[r][c] == 'O':
            st.warning(f"⚠️ Warning: Seat R{row}C{col} is already empty.")
        else:
            removed_info = st.session_state.bookings.pop(target_key, {})
            st.session_state.seats[r][c] = 'O'
            save_data_to_file()
            st.success(f"🔄 Success: Booking for {removed_info.get('name', 'Unknown')} was cancelled.")
            st.rerun()