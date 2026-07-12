import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# --- CONFIG & STYLING ENGINE ---
st.set_page_config(page_title="TransitOps Platform", layout="wide", initial_sidebar_state="expanded")

# --- DARK MODE & MODERN MOTION CSS (NotYourCollege Vibe) ---
st.markdown("""
    <style>
    /* Base Dark Mode Override to protect against Brave's forced theme */
    .stApp { background-color: #050505 !important; }
    
    /* Global Typography Force Contrast */
    h1, h2, h3, h4, p, label, span, .st-emotion-cache-10trblm {
        color: #EDEDED !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sleek Startup Cards (Brutalist + Glow) */
    .fleet-card {
        background-color: #0A0A0C;
        padding: 24px;
        border-radius: 6px;
        border: 1px solid #1E1E24;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 1rem;
    }
    .fleet-card:hover {
        border-color: #00F0FF;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.12);
        transform: translateY(-4px);
    }
    
    /* Animated Neon Route Tracker */
    .route-container { position: relative; width: 100%; height: 60px; margin-top: 15px; }
    .route-line {
        position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #1E1E24; transform: translateY(-50%);
    }
    .route-pointer {
        position: absolute; top: 50%; left: 45%; transform: translate(-50%, -50%);
        width: 12px; height: 12px; background: #00F0FF; border-radius: 50%;
        box-shadow: 0 0 10px #00F0FF;
        animation: pulse-pointer 1.5s infinite;
    }
    @keyframes pulse-pointer {
        0% { box-shadow: 0 0 0 0px rgba(0, 240, 255, 0.5); }
        100% { box-shadow: 0 0 0 12px rgba(0, 240, 255, 0); }
    }
    
    /* Modern Minimalist Buttons */
    .stButton>button {
        background-color: #0A0A0C !important;
        border: 1px solid #333 !important;
        color: #EDEDED !important;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px;
        transition: 0.2s all ease-in-out;
    }
    .stButton>button:hover {
        border-color: #00F0FF !important;
        color: #00F0FF !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CSV FILE PERSISTENCE ---
VEHICLES_FILE = "vehicles.csv"
DRIVERS_FILE = "drivers.csv"
TRIPS_FILE = "trips.csv"
MAINTENANCE_FILE = "maintenance.csv"

# --- SYSTEM INITIALIZATION & DATA HEALING ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = ''
    st.session_state['username'] = ''

# Load Vehicles and HEAL missing columns (Fixes the KeyError)
if 'vehicles' not in st.session_state:
    if os.path.exists(VEHICLES_FILE):
        df = pd.read_csv(VEHICLES_FILE)
        # Self-healing missing columns
        required_cols = {'Revenue Earned ($)': 0, 'Fuel Costs ($)': 0, 'Maintenance Costs ($)': 0, 'Region': 'North'}
        for col, val in required_cols.items():
            if col not in df.columns:
                df[col] = val
        st.session_state['vehicles'] = df
    else:
        st.session_state['vehicles'] = pd.DataFrame({
            'Reg Number': ['V-001', 'V-002'], 'Model': ['Ford Transit', 'Volvo Truck'],
            'Type': ['Van', 'Heavy Truck'], 'Region': ['North', 'South'],
            'Max Capacity (kg)': [1000, 5000], 'Odometer (km)': [12000, 45000],
            'Acquisition Cost ($)': [25000, 85000], 'Revenue Earned ($)': [5000, 12000],
            'Fuel Costs ($)': [1200, 3400], 'Maintenance Costs ($)': [400, 1500],
            'Status': ['🟢 Available', '🟡 In Progress']
        })
        st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)

if 'drivers' not in st.session_state:
    if os.path.exists(DRIVERS_FILE):
        st.session_state['drivers'] = pd.read_csv(DRIVERS_FILE)
    else:
        st.session_state['drivers'] = pd.DataFrame({
            'Name': ['Alex Jones', 'Mike Miller'], 'License Number': ['L-1234', 'L-9999'],
            'Category': ['Heavy Commercial', 'Heavy Commercial'], 'Expiry Date': ['2027-12-31', '2023-01-01'],
            'Contact': ['555-0192', '555-0188'], 'Safety Score': [95, 45], 'Status': ['🟢 Available', '🔴 Suspended']
        })
        st.session_state['drivers'].to_csv(DRIVERS_FILE, index=False)

if 'trips' not in st.session_state:
    if os.path.exists(TRIPS_FILE):
        st.session_state['trips'] = pd.read_csv(TRIPS_FILE)
    else:
        st.session_state['trips'] = pd.DataFrame(columns=[
            'Trip ID', 'Source', 'Destination', 'Cargo Weight (kg)', 'Vehicle', 'Driver', 'Status'
        ])
        st.session_state['trips'].to_csv(TRIPS_FILE, index=False)

if 'maintenance' not in st.session_state:
    if os.path.exists(MAINTENANCE_FILE):
        st.session_state['maintenance'] = pd.read_csv(MAINTENANCE_FILE)
    else:
        st.session_state['maintenance'] = pd.DataFrame(columns=[
            'Ticket ID', 'Vehicle', 'Issue', 'Cost ($)', 'Status'
        ])
        st.session_state['maintenance'].to_csv(MAINTENANCE_FILE, index=False)


# --- LOGIN APP WITH RBAC [Section 3.1 & 3.2] ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; color: #00F0FF !important;'>TransitOps // System Access</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Try: <b>admin</b>, <b>driver1</b>, or <b>finance</b> (Password: pass)</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            user = st.text_input("Operator ID")
            pwd = st.text_input("Security Protocol (pass)", type="password")
            if st.form_submit_button("Initialize Uplink"):
                if pwd == 'pass':
                    if user == 'admin':
                        st.session_state['role'] = 'Fleet Manager'
                    elif user == 'driver1':
                        st.session_state['role'] = 'Driver'
                    elif user == 'finance':
                        st.session_state['role'] = 'Financial Analyst'
                    else:
                        st.error("Invalid Operator ID")
                        st.stop()
                    
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.rerun()
                else:
                    st.error("Authorization Failed.")
    st.stop()

# --- MAIN CORE SYSTEM ---
st.sidebar.markdown(f"<h2 style='color:#00F0FF !important;'>{st.session_state['role']} Portal</h2>", unsafe_allow_html=True)
app_menu_options = ["Dashboard", "Vehicle Management", "Driver Management", "Trip Management", "Maintenance Hub"]
selected_menu = st.sidebar.radio("Command Modules", app_menu_options)

if st.sidebar.button("Sever Connection"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- 1. DASHBOARD HUB (NOW WITH FILTERS) ---
if selected_menu == "Dashboard":
    st.markdown("<h1>System Telemetry // Analytics</h1>", unsafe_allow_html=True)
    
    # Missing Feature: Dashboard Filters [Section 3.2]
    f_col1, f_col2, f_col3 = st.columns(3)
    filter_type = f_col1.selectbox("Filter by Asset Class", ["All"] + list(st.session_state['vehicles']['Type'].unique()))
    filter_status = f_col2.selectbox("Filter by Status", ["All"] + list(st.session_state['vehicles']['Status'].unique()))
    
    # Apply Filters to a temporary dataframe
    v_df = st.session_state['vehicles'].copy()
    if filter_type != "All": v_df = v_df[v_df['Type'] == filter_type]
    if filter_status != "All": v_df = v_df[v_df['Status'] == filter_status]

    total_v = len(v_df)
    active_v = len(v_df[v_df['Status'] == '🟡 In Progress'])
    utilization = (active_v / total_v) * 100 if total_v > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Filtered Asset Count", total_v)
    c2.metric("Active Routing", active_v)
    c3.metric("Fleet Utilization", f"{utilization:.1f}%")
    
    st.divider()
    st.markdown("<h3>Financial Return on Investment</h3>", unsafe_allow_html=True)
    
    # Safety Check: Prevent Division by Zero just in case
    v_df['Computed ROI %'] = v_df.apply(lambda row: ((row['Revenue Earned ($)'] - (row['Fuel Costs ($)'] + row['Maintenance Costs ($)'])) / row['Acquisition Cost ($)']) * 100 if row['Acquisition Cost ($)'] > 0 else 0, axis=1)
    
    st.dataframe(v_df[['Reg Number', 'Model', 'Status', 'Revenue Earned ($)', 'Computed ROI %']], use_container_width=True, hide_index=True)

# --- 2. VEHICLE REGISTRY ---
elif selected_menu == "Vehicle Management":
    st.markdown("<h1>Asset Inventory</h1>", unsafe_allow_html=True)
    
    for idx, row in st.session_state['vehicles'].iterrows():
        with st.container():
            st.markdown(f"""
            <div class="fleet-card">
                <h3 style="margin-top:0; color:#00F0FF !important;">{row['Reg Number']} // {row['Model']}</h3>
                <p><b>Type:</b> {row['Type']} | <b>Region:</b> {row['Region']} | <b>Cap:</b> {row['Max Capacity (kg)']} kg</p>
                <p><b>State:</b> {row['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
            
    t1, t2 = st.tabs(["➕ Initialize Asset", "❌ Decommission"])
    with t1:
        with st.form("add_v", clear_on_submit=True):
            reg = st.text_input("Registration ID").upper()
            mod = st.text_input("Model")
            vtype = st.selectbox("Class", ["Van", "Light Truck", "Heavy Truck"])
            reg_area = st.selectbox("Operating Region", ["North", "South", "East", "West"])
            cap = st.number_input("Max Capacity (kg)", min_value=0)
            odo = st.number_input("Odometer (km)", min_value=0)
            acq = st.number_input("Acquisition Cost ($)", min_value=0)
            
            if st.form_submit_button("Commit"):
                if reg in st.session_state['vehicles']['Reg Number'].values: st.error("ID exists!")
                else:
                    new_v = pd.DataFrame([{'Reg Number': reg, 'Model': mod, 'Type': vtype, 'Region': reg_area, 'Max Capacity (kg)': cap, 'Odometer (km)': odo, 'Acquisition Cost ($)': acq, 'Revenue Earned ($)': 0, 'Fuel Costs ($)': 0, 'Maintenance Costs ($)': 0, 'Status': '🟢 Available'}])
                    st.session_state['vehicles'] = pd.concat([st.session_state['vehicles'], new_v], ignore_index=True)
                    st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
                    st.rerun()

    with t2:
        del_v = st.selectbox("Asset to Purge", st.session_state['vehicles']['Reg Number'])
        if st.button("Purge"):
            st.session_state['vehicles'] = st.session_state['vehicles'][st.session_state['vehicles']['Reg Number'] != del_v]
            st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
            st.rerun()

# --- 3. DRIVER REGISTRY ---
elif selected_menu == "Driver Management":
    st.markdown("<h1>Personnel Roster</h1>", unsafe_allow_html=True)
    st.dataframe(st.session_state['drivers'], use_container_width=True, hide_index=True)

# --- 4. TRIP MANAGEMENT ---
elif selected_menu == "Trip Management":
    st.markdown("<h1>Logistics Routing</h1>", unsafe_allow_html=True)
    
    if not st.session_state['trips'].empty:
        for _, t_row in st.session_state['trips'][st.session_state['trips']['Status'] == '🟡 In Progress'].iterrows():
            st.markdown(f"""
                <div style="margin-top: 20px;">
                    <span style="color:#00F0FF;">{t_row['Trip ID']}</span> // {t_row['Vehicle']}
                </div>
                <div class="route-container">
                    <div style="float:left; font-size:12px; color:#888;">{t_row['Source']}</div>
                    <div style="float:right; font-size:12px; color:#888;">{t_row['Destination']}</div>
                    <div class="route-line"></div>
                    <div class="route-pointer"></div>
                </div>
            """, unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🚀 Outbound", "🏁 Inbound Delivery"])
    with t1:
        v_clear = st.session_state['vehicles'][st.session_state['vehicles']['Status'] == '🟢 Available']
        d_clear = st.session_state['drivers'][st.session_state['drivers']['Status'] == '🟢 Available']
        
        with st.form("dispatch_f"):
            tid = st.text_input("Trip ID").upper()
            src = st.text_input("Origin")
            dest = st.text_input("Destination")
            weight = st.number_input("Cargo Weight (kg)", min_value=0)
            sel_v = st.selectbox("Vehicle", v_clear['Reg Number'] if not v_clear.empty else ["None Available"])
            sel_d = st.selectbox("Driver", d_clear['Name'] if not d_clear.empty else ["None Available"])
            
            if st.form_submit_button("Sanction Dispatch"):
                if sel_v == "None Available" or sel_d == "None Available": st.error("Assets required.")
                else:
                    v_idx = st.session_state['vehicles'][st.session_state['vehicles']['Reg Number'] == sel_v].index[0]
                    if weight > st.session_state['vehicles'].loc[v_idx, 'Max Capacity (kg)']: st.error("Weight violation!")
                    else:
                        new_t = pd.DataFrame([{'Trip ID': tid, 'Source': src, 'Destination': dest, 'Cargo Weight (kg)': weight, 'Vehicle': sel_v, 'Driver': sel_d, 'Status': '🟡 In Progress'}])
                        st.session_state['trips'] = pd.concat([st.session_state['trips'], new_t], ignore_index=True)
                        st.session_state['vehicles'].loc[v_idx, 'Status'] = '🟡 In Progress'
                        st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
                        st.session_state['trips'].to_csv(TRIPS_FILE, index=False)
                        st.rerun()

    with t2:
        active = st.session_state['trips'][st.session_state['trips']['Status'] == '🟡 In Progress']
        if not active.empty:
            sel_t = st.selectbox("Arriving Trip ID", active['Trip ID'])
            with st.form("complete_trip_form"):
                rev = st.number_input("Revenue ($)", min_value=0.0)
                fuel = st.number_input("Fuel Cost ($)", min_value=0.0)
                
                if st.form_submit_button("Complete Manifest"):
                    t_idx = st.session_state['trips'][st.session_state['trips']['Trip ID'] == sel_t].index[0]
                    v_id = st.session_state['trips'].loc[t_idx, 'Vehicle']
                    v_idx = st.session_state['vehicles'][st.session_state['vehicles']['Reg Number'] == v_id].index[0]
                    
                    st.session_state['vehicles'].loc[v_idx, 'Revenue Earned ($)'] += rev
                    st.session_state['vehicles'].loc[v_idx, 'Fuel Costs ($)'] += fuel
                    st.session_state['vehicles'].loc[v_idx, 'Status'] = '🟢 Available'
                    st.session_state['vehicles'].to_csv(VEHICLES_FILE, index=False)
                    
                    st.session_state['trips'].loc[t_idx, 'Status'] = '🟢 Completed'
                    st.session_state['trips'].to_csv(TRIPS_FILE, index=False)
                    st.rerun()

# --- 5. MAINTENANCE HUB ---
elif selected_menu == "Maintenance Hub":
    st.markdown("<h1>Hardware Diagnostics</h1>", unsafe_allow_html=True)
    st.dataframe(st.session_state['maintenance'], use_container_width=True, hide_index=True)