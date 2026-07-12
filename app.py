import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CSV FILE PATHS FOR PERSISTENCE ---
VEHICLES_FILE = "vehicles.csv"
DRIVERS_FILE = "drivers.csv"

# --- 1. DATABASE INITIALIZATION (LOAD FROM CSV OR MOCK DATA) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = ''

# Load or initialize Vehicles [cite: 23]
if 'vehicles' not in st.session_state:
    if os.path.exists(VEHICLES_FILE):
        st.session_state['vehicles'] = pd.read_csv(VEHICLES_FILE)
    else:
        st.session_state['vehicles'] = pd.DataFrame({
            'Reg Number': ['V-001', 'V-002', 'V-003'],
            'Model': ['Ford Transit', 'Volvo Truck', 'Sprinter Van'],
            'Type': ['Van', 'Heavy Truck', 'Van'],
            'Max Capacity (kg)': [1000, 5000, 1500],
            'Odometer (km)': [12000, 45000, 8500],
            'Acquisition Cost ($)': [25000, 85000, 32000],
            'Status': ['Available', 'On Trip', 'In Shop']
        })
        st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)

# Load or initialize Drivers [cite: 26]
if 'drivers' not in st.session_state:
    if os.path.exists(DRIVERS_FILE):
        st.session_state['drivers'] = pd.read_csv(DRIVERS_FILE)
    else:
        st.session_state['drivers'] = pd.DataFrame({
            'Name': ['Alex Jones', 'Sarah Smith', 'Mike Miller'],
            'License Number': ['L-1234', 'L-5678', 'L-9999'],
            'Category': ['Heavy Commercial', 'Light Commercial', 'Heavy Commercial'],
            'Expiry Date': ['2027-12-31', '2028-05-14', '2023-01-01'],
            'Contact': ['555-0192', '555-0143', '555-0188'],
            'Safety Score': [95, 88, 45],
            'Status': ['Available', 'On Trip', 'Suspended']
        })
        st.session_state['drivers'].to_csv(DRIVERS_FILE, index=False)

# --- STATUS COLOR COLORING FUNCTION ---
def style_status(val):
    if val == 'Available':
        return 'background-color: #d4edda; color: #155724; font-weight: bold;' # Soft Green
    else:
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;' # Soft Red

# --- 2. LOGIN SCREEN ---
def login_screen():
    st.title("TransitOps Login")
    with st.form("login_form"):
        username = st.text_input("Username (Type 'admin')")
        password = st.text_input("Password (Type 'password')", type="password")
        submit = st.form_submit_button("Log In")
        if submit:
            if username == 'admin' and password == 'password':
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Fleet Manager'
                st.rerun()
            else:
                st.error("Incorrect username or password")

# --- 3. MAIN APPLICATION ---
def main_app():
    st.sidebar.title(f"Welcome, {st.session_state['role']}")
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Vehicle Management", "Driver Management"])
    
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = ''
        st.rerun()

    # --- DASHBOARD ---
    if menu == "Dashboard":
        st.title("📊 Fleet Dashboard")
        
        total_v = len(st.session_state['vehicles'])
        active_v = len(st.session_state['vehicles'][st.session_state['vehicles']['Status'] == 'On Trip'])
        in_shop_v = len(st.session_state['vehicles'][st.session_state['vehicles']['Status'] == 'In Shop'])
        utilization = (active_v / total_v) * 100 if total_v > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Vehicles", total_v)
        col2.metric("Active On Trip", active_v)
        col3.metric("In Shop (Maintenance)", in_shop_v)
        col4.metric("Fleet Utilization", f"{utilization:.1f}%")
        
        st.divider()
        st.subheader("Current Fleet Status")
        styled_df = st.session_state['vehicles'].style.map(style_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- VEHICLE MANAGEMENT ---
    elif menu == "Vehicle Management":
        st.title("🚛 Vehicle Registry & Management")
        
        styled_v = st.session_state['vehicles'].style.map(style_status, subset=['Status'])
        st.dataframe(styled_v, use_container_width=True, hide_index=True)
        
        tab1, tab2, tab3 = st.tabs(["➕ Add New Vehicle", "✏️ Edit / Change Status", "❌ Remove Vehicle"])
        
        with tab1:
            with st.form("add_vehicle", clear_on_submit=True):
                reg_num = st.text_input("Registration Number (Unique)", key="add_v_reg").strip().upper()
                model = st.text_input("Vehicle Model/Name", key="add_v_model")
                v_type = st.selectbox("Vehicle Type", ["Van", "Light Truck", "Heavy Truck", "Container"])
                capacity = st.number_input("Maximum Load Capacity (kg)", min_value=0, step=500, key="add_v_cap")
                odom = st.number_input("Current Odometer (km)", min_value=0, step=1000, key="add_v_odom")
                cost = st.number_input("Acquisition Cost ($)", min_value=0, step=5000, key="add_v_cost")
                submit = st.form_submit_button("Register Vehicle")
                
                if submit:
                    if not reg_num or not model:
                        st.error("Registration Number and Model are required!")
                    elif reg_num in st.session_state['vehicles']['Reg Number'].astype(str).values:
                        st.error("Mandatory Rule: Vehicle Registration Number must be unique!") [cite: 46]
                    else:
                        new_row = pd.DataFrame([{
                            'Reg Number': reg_num, 'Model': model, 'Type': v_type,
                            'Max Capacity (kg)': capacity, 'Odometer (km)': odom,
                            'Acquisition Cost ($)': cost, 'Status': 'Available'
                        }])
                        st.session_state['vehicles'] = pd.concat([st.session_state['vehicles'], new_row], ignore_index=True)
                        # Save directly to file so it survives a refresh
                        st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
                        st.success(f"Vehicle {reg_num} successfully registered!")
                        st.rerun()

        with tab2:
            if not st.session_state['vehicles'].empty:
                selected_reg = st.selectbox("Select Vehicle to Edit", st.session_state['vehicles']['Reg Number'])
                idx = st.session_state['vehicles'][st.session_state['vehicles']['Reg Number'] == selected_reg].index[0]
                
                with st.form("edit_vehicle"):
                    current_status = st.session_state['vehicles'].loc[idx, 'Status']
                    status_options = ['Available', 'On Trip', 'In Shop', 'Retired']
                    
                    new_status = st.selectbox("Change Status", status_options, index=status_options.index(current_status))
                    new_odom = st.number_input("Update Odometer (km)", value=int(st.session_state['vehicles'].loc[idx, 'Odometer (km)']))
                    submit_edit = st.form_submit_button("Save Changes")
                    
                    if submit_edit:
                        st.session_state['vehicles'].loc[idx, 'Status'] = new_status
                        st.session_state['vehicles'].loc[idx, 'Odometer (km)'] = new_odom
                        st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
                        st.success("Vehicle data updated!")
                        st.rerun()
            else:
                st.write("No vehicles available to edit.")

        with tab3:
            if not st.session_state['vehicles'].empty:
                delete_reg = st.selectbox("Select Vehicle to Remove", st.session_state['vehicles']['Reg Number'], key="del_v")
                if st.button("Permanently Delete Vehicle", type="primary"):
                    st.session_state['vehicles'] = st.session_state['vehicles'][st.session_state['vehicles']['Reg Number'] != delete_reg]
                    st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
                    st.success(f"Vehicle {delete_reg} deleted.")
                    st.rerun()

    # --- DRIVER MANAGEMENT ---
    elif menu == "Driver Management":
        st.title("🧑‍✈️ Driver Registry & Management")
        
        styled_d = st.session_state['drivers'].style.map(style_status, subset=['Status'])
        st.dataframe(styled_d, use_container_width=True, hide_index=True)
        
        tab1, tab2, tab3 = st.tabs(["➕ Add New Driver", "✏️ Edit Driver Profile", "❌ Remove Driver"])
        
        with tab1:
            with st.form("add_driver", clear_on_submit=True):
                name = st.text_input("Driver Name", key="add_d_name")
                lic_num = st.text_input("License Number", key="add_d_lic")
                category = st.selectbox("License Category", ["Light Commercial", "Heavy Commercial", "Dangerous Goods"])
                expiry = st.date_input("License Expiry Date")
                contact = st.text_input("Contact Number", key="add_d_phone")
                safety = st.slider("Initial Safety Score", 0, 100, 100)
                submit = st.form_submit_button("Register Driver")
                
                if submit:
                    if not name or not lic_num:
                        st.error("Name and License Number are mandatory.")
                    else:
                        new_row = pd.DataFrame([{
                            'Name': name, 'License Number': lic_num, 'Category': category,
                            'Expiry Date': str(expiry), 'Contact': contact, 'Safety Score': safety,
                            'Status': 'Available'
                        }])
                        st.session_state['drivers'] = pd.concat([st.session_state['drivers'], new_row], ignore_index=True)
                        st.session_state['drivers'].to_csv(DRIVERS_FILE, index=False)
                        st.success(f"Driver {name} registered!")
                        st.rerun()

        with tab2:
            if not st.session_state['drivers'].empty:
                selected_driver = st.selectbox("Select Driver to Edit", st.session_state['drivers']['Name'])
                idx = st.session_state['drivers'][st.session_state['drivers']['Name'] == selected_driver].index[0]
                
                with st.form("edit_driver"):
                    curr_status = st.session_state['drivers'].loc[idx, 'Status']
                    status_opts = ['Available', 'On Trip', 'Off Duty', 'Suspended']
                    
                    new_status = st.selectbox("Change Status", status_opts, index=status_opts.index(curr_status))
                    new_score = st.slider("Update Safety Score", 0, 100, int(st.session_state['drivers'].loc[idx, 'Safety Score']))
                    submit_edit = st.form_submit_button("Save Driver Profile")
                    
                    if submit_edit:
                        st.session_state['drivers'].loc[idx, 'Status'] = new_status
                        st.session_state['drivers'].loc[idx, 'Safety Score'] = new_score
                        st.session_state['drivers'].to_csv(DRIVERS_FILE, index=False)
                        st.success("Driver details updated!")
                        st.rerun()

        with tab3:
            if not st.session_state['drivers'].empty:
                delete_driver = st.selectbox("Select Driver to Remove", st.session_state['drivers']['Name'], key="del_d")
                if st.button("Permanently Delete Driver", type="primary"):
                    st.session_state['drivers'] = st.session_state['drivers'][st.session_state['drivers']['Name'] != delete_driver]
                    st.session_state['drivers'].to_csv(DRIVERS_FILE, index=False)
                    st.success(f"Driver {delete_driver} removed.")
                    st.rerun()

# --- APP ROUTING ---
if st.session_state['logged_in']:
    main_app()
else:
    login_screen()