import streamlit as st

# Set up the page layout
st.set_page_config(page_title="Library Seating System", layout="centered")

# Library size (From the first code: 5 rows, 6 columns)
ROWS = 5
COLS = 6

# ------------------------------------------------------------------
# BACKEND INITIALIZATION (Equivalent to __init__ in your first code)
# ------------------------------------------------------------------
if "seats" not in st.session_state:
    # Initialize all seats as Available ('O')
    st.session_state.seats = [['O' for _ in range(COLS)] for _ in range(ROWS)]

if "bookings" not in st.session_state:
    # Dictionary to track who booked which seat: {(row, col): student_name}
    st.session_state.bookings = {}

# ------------------------------------------------------------------
# VISUAL DISPLAY (Equivalent to display_seats in your first code)
# ------------------------------------------------------------------
st.title("📚 Library Seating System")
st.subheader("=== LIBRARY SEATING CHART ===")
st.write("📍 **Front of Library (Reference Section)**")

# Generate the visual grid using columns
for r in range(ROWS):
    cols = st.columns(COLS)
    for c in range(COLS):
        seat_status = st.session_state.seats[r][c]
        seat_label = f"R{r+1}C{c+1}\n[{seat_status}]"
        
        with cols[c]:
            # Use green for available, red for booked
            if seat_status == 'O':
                st.button(seat_label, key=f"display_R{r}C{c}", disabled=True, use_container_width=True)
            else:
                st.button(seat_label, key=f"display_R{r}C{c}", type="primary", disabled=True, use_container_width=True)

st.write("**Legend:** `O` = Available | `X` = Booked")
st.markdown("---")

# ------------------------------------------------------------------
# MENU ACTIONS (Equivalent to the main() while loop)
# ------------------------------------------------------------------
st.subheader("--- Menu ---")
choice = st.radio("Choose an option:", ["1. Book a Seat", "2. Cancel a Booking"], horizontal=True)

# --- OPTION 1: BOOK A SEAT ---
if choice == "1. Book a Seat":
    st.markdown("### 🟢 Book a Seat")
    
    # Inputs
    name = st.text_input("Enter student name:").strip()
    row = st.number_input("Enter Row number:", min_value=1, max_value=ROWS, step=1)
    col = st.number_input("Enter Column number:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Submit Booking", type="primary"):
        r, c = row - 1, col - 1  # Adjust for 0-indexed matrix
        
        if not name:
            st.error("❌ Name cannot be empty.")
        elif st.session_state.seats[r][c] == 'X':
            st.error(f"❌ Error: Seat R{row}C{col} is already taken!")
        else:
            # Book the seat
            st.session_state.seats[r][c] = 'X'
            st.session_state.bookings[(row, col)] = name
            st.success(f"🎉 Success! Seat R{row}C{col} has been booked for {name}.")
            st.rerun()

# --- OPTION 2: CANCEL A BOOKING ---
elif choice == "2. Cancel a Booking":
    st.markdown("### 🔄 Cancel a Booking")
    
    # Inputs
    row = st.number_input("Enter Row number to cancel:", min_value=1, max_value=ROWS, step=1)
    col = st.number_input("Enter Column number to cancel:", min_value=1, max_value=COLS, step=1)
    
    if st.button("Cancel Reservation", type="primary"):
        r, c = row - 1, col - 1  # Adjust for 0-indexed matrix
        
        if st.session_state.seats[r][c] == 'O':
            st.warning(f"⚠️ Warning: Seat R{row}C{col} is already empty.")
        else:
            # Cancel the booking
            student = st.session_state.bookings.pop((row, col), "Unknown")
            st.session_state.seats[r][c] = 'O'
            st.success(f"🔄 Success: Booking for {student} at Seat R{row}C{col} has been cancelled.")
            st.rerun()