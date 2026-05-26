import streamlit as st
import json
import os

# Set up the page layout
st.set_page_config(page_title="Multi-Library Seating System", layout="centered")

# ------------------------------------------------------------------
# 🎨 VISUAL STYLING (Forcing Bold Black Text everywhere)
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
    
    /* Whiteboard/Front desk header decoration */
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
    
    .stRadio label, label p {
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)


# Grid Dimensions (7 rows, 6 columns)
ROWS = 7
COLS = 6

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
# VISUAL DISPLAY
# ------------------------------------------------------------------
st.subheader(f"📍 Seating Chart: {selected_library}")
st.markdown('<div class="front-desk">🖥️ FRONT COUNTER / ENTRANCE</div>', unsafe_allow_html=True)

for r in range(ROWS):
    cols = st.columns(COLS)
    for c in range(COLS):
        seat_status = st.session_state.seats[r][c]
        
        if seat_status == 'O':
            seat_label = f"R{r+1}C{c+1}\n[ O ]"
            with cols[c]:
                st.button(seat_label, key=f"display_R{r}C{c}", use_container_width=True)
        else:
            student_occupant = st.session_state.bookings.get((r+1, c+1), "X")
            seat_label = f"R{r+1}C{c+1}\n[{student_occupant}]"
            with cols[c]:
                st.button(seat_label, key=f"display_R{r}C{c}", disabled=True, use_container_width=True)

st.write("💡 **Legend:** Green `[ O ]` = Available | Red `[ Name ]` = Booked")
st.markdown("---")

# ------------------------------------------------------------------
# MENU ACTIONS
# ------------------------------------------------------------------
st.subheader("--- Menu ---")
choice = st.radio("Choose an action:", ["1. Book a Seat", "2. Cancel a Booking"], horizontal=True)

# --- OPTION 1: BOOK A SEAT ---
if choice == "1. Book a Seat":
    st.markdown(f"### ✨ Reserve a Seat in {selected_library} (Strictly 1 seat per user)")
    
    name = st.text_input("Enter student name:").strip()
    row = st.number_input("Enter Row number:", min_value=1, max_value=ROWS, step=1)
    col = st.number_input("Enter Column number:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Submit Booking", type="primary"):
        r, c = row - 1, col - 1
        
        # Check if this student already booked a seat in this library
        has_already_booked = name in st.session_state.bookings.values()
        
        if not name:
            st.error("❌ Name cannot be empty.")
        elif st.session_state.seats[r][c] == 'X':
            st.error(f"❌ Error: Seat R{row}C{col} is already taken by someone else!")
        elif has_already_booked:
            st.error(f"❌ Error: {name} already has a seat reserved in {selected_library}! Cancel it first to move seats.")
        else:
            # Update state and save
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