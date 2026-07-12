# TransitOps - Delivery Management System

TransitOps is a simple website designed to help a transport and delivery company manage its business[cite: 3]. Instead of using paper logs or messy Excel sheets, this platform tracks trucks, drivers, trips, and expenses in one central place[cite: 3].

## What This Website Does

### 1. Simple Login
* Users can log in safely with an email and password[cite: 3].
* The website changes depending on who logs in (Fleet Managers, Drivers, Safety Officers, or Financial Analysts)[cite: 3].

### 2. Main Dashboard
* Shows quick numbers like how many trucks are currently driving, how many are ready, and how many are broken[cite: 3].
* Includes simple filters to search by region or vehicle type[cite: 3].

### 3. Truck List
* A simple list to register and view company trucks[cite: 3].
* Stores the truck's name, unique registration number, maximum weight limit, odometer reading, and current status (Available, On Trip, In Shop, or Retired)[cite: 3].

### 4. Driver Directory
* A list to keep track of drivers[cite: 3].
* Stores the driver's name, license number, license expiry date, phone number, and current status (Available, On Trip, Off Duty, or Suspended)[cite: 3].

### 5. Trip Planner
* A form to create new delivery routes by selecting a starting point, destination, cargo weight, an available truck, and an available driver[cite: 3].
* Tracks trips as Draft, Dispatched, Completed, or Cancelled[cite: 3].

### 6. Repair Log (Maintenance)
* A page to log when a truck needs fixing[cite: 3].
* Putting a truck on this list automatically marks it as "In Shop" so nobody accidentally chooses it for a delivery trip[cite: 3].

### 7. Expense Tracker
* A simple form to type in gas logs (liters and cost) and other fees like highway tolls[cite: 3].
* Automatically adds up all the gas and repair bills to show the total cost of running each truck[cite: 3].

---

## Automatic Rules (The Website's Brain)

To prevent mistakes, the website automatically checks these simple rules[cite: 3]:
* **No Duplicates:** You cannot register two trucks with the exact same registration number[cite: 3].
* **Safety First:** You cannot assign a trip to a driver if their license is expired or if they are suspended[cite: 3].
* **No Double-Booking:** A truck or driver that is already out "On Trip" cannot be picked for another trip at the same time[cite: 3].
* **Weight Limit Check:** The website will block a trip if the cargo weight is heavier than the truck's maximum weight limit[cite: 3].
* **Auto-Updates:** 
  * Starting a trip automatically changes the truck and driver status to "On Trip"[cite: 3].
  * Finishing a trip automatically changes them back to "Available"[cite: 3].
  * Sending a truck for repairs changes it to "In Shop"[cite: 3], and finishing the repairs makes it "Available" again[cite: 3].

---

## Simple Calculations Used

The website uses basic math to show business insights on the dashboard[cite: 3]:

* **Gas Efficiency:** Distance Traveled divided by Fuel Consumed[cite: 3].
* **Truck Profit (ROI):** (Money Earned minus Gas and Repair Costs) divided by what the truck originally cost to buy[cite: 3].

---

## How to Run This Project

1. Download or clone this repository to your computer.
2. Open your terminal or command prompt in the project folder.
3. Run the application launch command (depending on the tool you chose to build it).