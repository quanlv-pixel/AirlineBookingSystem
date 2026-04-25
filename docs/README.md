# Airline Flight Booking and Passenger Management System

## Project Overview

This project is a **desktop application** developed using **Python (PySide6)** that simulates an airline management system.
It allows users to manage flights, passengers, and bookings through a graphical user interface (GUI).

The system supports full **CRUD operations**, database integration, and search functionality, fulfilling the requirements of the final project.

---

## Objectives

* Build a **GUI-based application** using PySide6
* Connect and manage data using **SQLite database**
* Implement **CRUD operations** for all entities
* Provide **search and filtering features**
* Apply clean project structure and modular programming

---

## Technologies Used

* Python 3.12.9
* PySide6 (GUI)
* SQLite3 (Database)
* Qt Style Sheets (QSS) for UI styling

---

## 🗂️ Project Structure

```
AirlineBookingSystem/
│── main.py
│── requirements.txt
│── .gitignore
│
│── database/
│   ├── airline.db
│   ├── schema.sql
│   └── db.py
│
│── modules/
│   ├── flights.py
│   ├── passengers.py
│   ├── bookings.py
│   └── utils.py
│
│── ui/
│   ├── main_window.py
│   ├── flight_ui.py
│   ├── passenger_ui.py
│   ├── booking_ui.py
│   └── dashboard_ui.py
│
│── assets/
│   └── styles.qss
│
│── docs/
│   └── report.md
|   └── README.md
```

---

## Features

### Flight Management

* Add, update, delete flights
* View all flights in table format
* Search flights by origin, destination, or date

### Passenger Management

* Add, update, delete passenger information
* Search passengers by name or passport

### Booking Management

* Create booking (link passenger + flight)
* Cancel booking
* Display combined booking information

### Dashboard (Optional / Bonus)

* Total number of flights, passengers, bookings
* Data visualization (charts)

---

## Database Design

### Flights Table

* id (Primary Key)
* flight_no
* origin
* destination
* date
* seats

### Passengers Table

* id (Primary Key)
* name
* passport
* phone

### Bookings Table

* id (Primary Key)
* passenger_id (Foreign Key)
* flight_id (Foreign Key)
* seat_no

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone <https://github.com/quanlv-pixel/AirlineBookingSystem>
cd AirlineBookingSystem
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

* Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize database

```bash
sqlite3 database/airline.db < database/schema.sql
```

### 6. Run application

```bash
python main.py
```

---

## Key Functionalities

* Graphical User Interface (GUI)
* Database connectivity
* Full CRUD operations
* Data search functionality
* Modular code structure

---

## User Interface

* Built with PySide6
* Styled using QSS (Qt Style Sheets)
* Sidebar navigation + stacked pages
* Responsive and clean layout

---

## Screenshots

*(Add your application screenshots here)*

---

## Version Control

* GitHub is used for source code management
* Commit history shows development progress

---

## Future Improvements

* User authentication (login system)
* Advanced analytics dashboard
* Online booking integration
* Export data to Excel/PDF

---

## Author

* Name: *Le Van Quan*
* Course: Python Programming
* Project: Python Final Project

---

## Conclusion

This project demonstrates the application of Python programming concepts, GUI development, and database management in building a real-world airline booking system.

---
