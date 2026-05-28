import streamlit as st
import json
import os

# Set up the page layout
st.set_page_config(page_title="Ultimate Multi-Library Hub", layout="centered")

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
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    label p {
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)


# Grid Dimensions (7 rows, 6 columns)
ROWS = 7
COLS = 6
TOTAL_SEATS = ROWS * COLS

# Initialize clicked inputs into session state memory for Feature #1
if "selected_row" not in st.session_state:
    st.session_state.selected_row = 1
if "selected_col" not in st.session_state:
    st.session_state.selected_col = 1

# ------------------------------------------------------------------
# 🗺️ LIBRARY SELECTOR
# ------------------------------------------------------------------
st.title("📚 Multi-Library Booking Hub")
st.markdown("---")

selected_library = st.selectbox(
    "🚪 Select a Library to view/book:",
    ["Library 1", "Library 2", "Library 3"]
)

DATA_FILE = f"{selected_library.lower().replace(' ', '_')}.json"

# ------------------------------------------------------------------
# 📂 FILE STORAGE FUNCTIONS
# ------------------------------------------------------------------
def load_saved_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            saved_dict = json.load(f)
            seats = saved_dict.get("seats", [['O' for _ in range(COLS)] for _ in range(ROWS)])
            raw_bookings = saved_dict.get("bookings", {})
            bookings = {(int(k.split(",")[0]), int(k.split(",")[1])): v for k, v in raw_bookings.items()}
            
            if len(seats) < ROWS:
                while len(seats) < ROWS:
                    seats.append(['O' for _ in range(COLS)])
            return seats, bookings
    else:
        seats = [['O' for _ in range(COLS)] for _ in range(ROWS)]
        bookings = {}
        return seats, bookings

def save_data_to_file():
    serializable_bookings = {f"{k[0]},{k[1]}": v for k, v in st.session_state.bookings.items()}
    data_to_save = {
        "seats": st.session_state.seats,
        "bookings": serializable_bookings
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

if "current_room" not in st.session_state or st.session_state.current_room != selected_library:
    st.session_state.current_room = selected_library
    loaded_seats, loaded_bookings = load_saved_data()
    st.session_state.seats = loaded_seats
    st.session_state.bookings = loaded_bookings

# ------------------------------------------------------------------
# 📈 FEATURE #2: LIVE ANALYTICS METRICS DASHBOARD
# ------------------------------------------------------------------
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
# 🔍 FEATURE #4: SEARCH AND LOCATE A STUDENT
# ------------------------------------------------------------------
st.subheader("🔍 Find a Student's Seat")
search_query = st.text_input("Type student name to locate their seat:", placeholder="e.g. John").strip()

if search_query:
    found_seats = [seat for seat, student in st.session_state.bookings.items() if search_query.lower() in student.lower()]
    if found_seats:
        for seat in found_seats:
            st.success(f"📍 **{st.session_state.bookings[seat]}** is sitting at **Row {seat[0]}, Column {seat[1]}** in {selected_library}!")
    else:
        st.error(f"❌ '{search_query}' does not have a registered seat in {selected_library}.")
st.markdown("---")

# ------------------------------------------------------------------
# VISUAL DISPLAY WITH FEATURE #3 (WALKWAY AISLE LAYOUT)
# ------------------------------------------------------------------
st.subheader(f"📍 Seating Chart: {selected_library}")
st.markdown('<div class="front-desk">🖥️ FRONT COUNTER / ENTRANCE</div>', unsafe_allow_html=True)

# Generate grid using 7 columns (3 left seats + 1 walkway gap + 3 right seats)
for r in range(ROWS):
    cols = st.columns([1, 1, 1, 0.4, 1, 1, 1]) 
    
    # Left Block (Columns 1, 2, 3)
    for c in range(3):
        seat_status = st.session_state.seats[r][c]
        seat_label = f"R{r+1}C{c+1}\n[ O ]" if seat_status == 'O' else f"R{r+1}C{c+1}\n[{st.session_state.bookings.get((r+1, c+1), 'X')}]"
        isDisabled = False if seat_status == 'O' else True
        
        with cols[c]:
            if st.button(seat_label, key=f"btn_R{r}C{c}", disabled=isDisabled, use_container_width=True):
                st.session_state.selected_row = r + 1
                st.session_state.selected_col = c + 1
                st.rerun()

    # Central Walkway Aisle Gap
    with cols[3]:
        st.markdown("<p style='text-align:center; padding-top:10px; font-size:0.8rem; color:#94A3B8 !important;'>🚶‍♂️</p>", unsafe_allow_html=True)

    # Right Block (Columns 4, 5, 6)
    for c in range(3, 6):
        seat_status = st.session_state.seats[r][c]
        seat_label = f"R{r+1}C{c+1}\n[ O ]" if seat_status == 'O' else f"R{r+1}C{c+1}\n[{st.session_state.bookings.get((r+1, c+1), 'X')}]"
        isDisabled = False if seat_status == 'O' else True
        
        with cols[c+1]: # Shifted right by 1 to skip aisle column
            if st.button(seat_label, key=f"btn_R{r}C{c}", disabled=isDisabled, use_container_width=True):
                st.session_state.selected_row = r + 1
                st.session_state.selected_col = c + 1
                st.rerun()

st.write("💡 **Tip:** Click any green seat above to fill out your booking numbers instantly below!")
st.markdown("---")

# ------------------------------------------------------------------
# MENU ACTIONS
# ------------------------------------------------------------------
st.subheader("⚙️ Select Action")
choice = st.radio("Choose action:", ["1. Book a Seat", "2. Cancel a Booking"], horizontal=True, label_visibility="collapsed")
st.markdown(" ")

# --- OPTION 1: BOOK A SEAT ---
if choice == "1. Book a Seat":
    st.markdown(f"### ✨ Reserve a Seat in {selected_library}")
    
    name = st.text_input("Enter student name:").strip()
    
    # Automatically links to values modified by interactive button clicks
    row = st.number_input("Enter Row number:", min_value=1, max_value=ROWS, value=st.session_state.selected_row, step=1)
    col = st.number_input("Enter Column number:", min_value=1, max_value=COLS, value=st.session_state.selected_col, step=1)
    
    if st.button("Submit Booking", type="primary"):
        r, c = row - 1, col - 1
        has_already_booked = name in st.session_state.bookings.values()
        
        if not name:
            st.error("❌ Name cannot be empty.")
        elif st.session_state.seats[r][c] == 'X':
            st.error(f"❌ Error: Seat R{row}C{col} is already taken by someone else!")
        elif has_already_booked:
            st.error(f"❌ Error: {name} already has a seat reserved in {selected_library}! Cancel it first to switch seats.")
        else:
            st.session_state.seats[r][c] = 'X'
            st.session_state.bookings[(row, col)] = name
            save_data_to_file()
            st.success(f"🎉 Success! Seat R{row}C{col} has been booked for {name}.")
            st.rerun()

# --- OPTION 2: CANCEL A BOOKING ---
elif choice == "2. Cancel a Booking":
    st.markdown(f"### 🔄 Remove a Reservation from {selected_library}")
    
    row = st.number_input("Enter Row number to cancel:", min_value=1, max_value=ROWS, step=1)
    col = st.number_input("Enter Column number to cancel:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Cancel Reservation", type="primary"):
        r, c = row - 1, col - 1
        
        if st.session_state.seats[r][c] == 'O':
            st.warning(f"⚠️ Warning: Seat R{row}C{col} is already empty in this room.")
        else:
            student = st.session_state.bookings.pop((row, col), "Unknown")
            st.session_state.seats[r][c] = 'O'
            save_data_to_file()
            st.success(f"🔄 Success: Booking for {student} at Seat R{row}C{col} cancelled.")
            st.rerun()