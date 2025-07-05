import mysql.connector

class Database:
    def __init__(self):
        try:
            self.con = mysql.connector.connect(
                host="127.0.0.1",
                port=3308,
                user="root",
                password="Saru@2002",
                database="flightreservation"
            )
            self.cur = self.con.cursor()
        except mysql.connector.Error as err:
            print(f"Database Connection Failed: {err}")
            exit()

class Flight(Database):
    def listflights(self, boarding, arrival):
        try:
            self.cur.execute("SELECT f.id, f.flightname, f.totalseats, (f.totalseats - IFNULL(t.booked, 0)) AS availableseats, f.price FROM flights f LEFT JOIN (SELECT flightid, COUNT(*) AS booked FROM tickets GROUP BY flightid) t ON f.id = t.flightid WHERE f.boarding = %s AND f.arrival = %s", (boarding, arrival))
            flights = self.cur.fetchall()
            if not flights:
                print("No flights found for this route.")
                return []
            print("\nAvailable Flights:")
            for f in flights:
                print(f"ID: {f[0]}, Name: {f[1]}, Available Seats: {f[3]}, Price: {f[4]}")
            return flights
        except Exception as e:
            print(f"Error listing flights: {e}")
            return []

class Passenger(Database):
    def signup(self):
        try:
            name = input("Enter your name: ")
            email = input("Enter your email: ")
            password = input("Create password: ")
            self.cur.execute("INSERT INTO passengers (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            self.con.commit()
            print(f"Signup successful! Your Registration ID is: {self.cur.lastrowid}")
        except Exception as e:
            print(f"Error during signup: {e}")

    def signin(self):
        try:
            regid = int(input("Enter Registration ID: "))
            password = input("Enter password: ")
            self.cur.execute("SELECT id FROM passengers WHERE id = %s AND password = %s", (regid, password))
            if self.cur.fetchone():
                print("Login successful!")
                self.passengerportal(regid)
            else:
                print("Invalid credentials.")
        except Exception as e:
            print(f"Error during signin: {e}")

    def forgetpassword(self):
        try:
            regid = int(input("Enter your Registration ID: "))
            self.cur.execute("SELECT email FROM passengers WHERE id = %s", (regid,))
            if self.cur.fetchone():
                newpassword = input("Enter your new password: ")
                self.cur.execute("UPDATE passengers SET password = %s WHERE id = %s", (newpassword, regid))
                self.con.commit()
                print("Password updated successfully!")
            else:
                print("No passenger found in that Registration ID.")
        except Exception as e:
            print(f"Error during password reset: {e}")

    def passengerportal(self, passengerid):
        flightobj = Flight()
        while True:
            print("\n1. Search Flights\n2. Book Ticket\n3. View My Tickets\n4. Cancel Tickets\n5. Logout")
            try:
                ch = int(input("Enter choice: "))
                if ch == 1:
                    boarding = input("Enter boarding location: ")
                    arrival = input("Enter arrival location: ")
                    flightobj.listflights(boarding, arrival)
                elif ch == 2:
                    flightid = int(input("Enter Flight ID to book: "))
                    self.cur.execute("SELECT totalseats FROM flights WHERE id = %s", (flightid,))
                    if not self.cur.fetchone():
                        print("Invalid Flight ID.")
                        continue
                    num = int(input("How many tickets to book? "))
                    for i in range(num):
                        name = input("Passenger name: ")
                        age = int(input("Age: "))
                        status = "Waiting for approval"
                        self.cur.execute("INSERT INTO tickets (flightid, passengerid, name, age, status) VALUES (%s, %s, %s, %s, %s)",(flightid, passengerid, name, age, status))
                    self.con.commit()
                    print("Tickets booked successfully!")
                elif ch == 3:
                    self.cur.execute("SELECT t.id, f.flightname, t.name, t.age, t.status FROM tickets t JOIN flights f ON t.flightid = f.id WHERE t.passengerid = %s", (passengerid,))
                    tickets = self.cur.fetchall()
                    if not tickets:
                        print("No tickets booked.")
                    else:
                        for t in tickets:
                            print(f"TicketID: {t[0]}, Flight: {t[1]}, Name: {t[2]}, Age: {t[3]}, Status: {t[4]}")
                elif ch == 4:
                    ticketid = int(input("Enter Ticket ID to cancel: "))
                    self.cur.execute("DELETE FROM tickets WHERE id = %s AND passengerid = %s", (ticketid, passengerid))
                    self.con.commit()
                    print("Ticket cancelled if it existed.")
                else:
                    break
            except Exception as e:
                print(f"Error: {e}")

class Cashier(Database):
    def signupcashier(self):
        try:
            name = input("Enter Cashier Name: ")
            password = input("Create Password: ")
            self.cur.execute("INSERT INTO cashier (name, password) VALUES (%s, %s)", (name, password))
            self.con.commit()
            print(f"Cashier account created! Your Cashier ID is: {self.cur.lastrowid}")
        except Exception as e:
            print(f"Error creating cashier account: {e}")

    def logincashier(self):
        try:
            cashierid = int(input("Enter Cashier ID: "))
            password = input("Enter Password: ")
            self.cur.execute("SELECT id FROM cashier WHERE id = %s AND password = %s", (cashierid, password))
            if self.cur.fetchone():
                print("Cashier Login Successful!")
                self.cashierportal()
            else:
                print("Invalid Cashier credentials.")
        except Exception as e:
            print(f"Error during cashier login: {e}")

    def approvetickets(self):
        try:
            self.cur.execute("UPDATE tickets SET status = 'Issued' WHERE status = 'Waiting for approval'")
            self.con.commit()
            print("All pending tickets approved.")
        except Exception as e:
            print(f"Error approving tickets: {e}")

    def viewalltickets(self):
        try:
            self.cur.execute("SELECT t.id, f.flightname, p.name, t.name, t.age, t.status FROM tickets t JOIN flights f ON t.flightid = f.id JOIN passengers p ON t.passengerid = p.id")
            records = self.cur.fetchall()
            if not records:
                print("No tickets found.")
            else:
                for rec in records:
                    print(f"TicketID: {rec[0]}, Flight: {rec[1]}, Passenger: {rec[2]}, Name: {rec[3]}, Age: {rec[4]}, Status: {rec[5]}")
        except Exception as e:
            print(f"Error viewing tickets: {e}")

    def showpassengers(self):
        try:
            self.cur.execute("SELECT id, name, email FROM passengers")
            records = self.cur.fetchall()
            if not records:
                print("No passengers found.")
            else:
                for rec in records:
                    print(f"ID: {rec[0]}, Name: {rec[1]}, Email: {rec[2]}")
        except Exception as e:
            print(f"Error fetching passengers: {e}")

    def cashierportal(self):
        while True:
            print("\n1. Approve Tickets\n2. View All Tickets\n3. View Passengers\n4. Logout")
            try:
                ch = int(input("Enter choice: "))
                if ch == 1:
                    self.approvetickets()
                elif ch == 2:
                    self.viewalltickets()
                elif ch == 3:
                    self.showpassengers()
                else:
                    break
            except Exception as e:
                print(f"Invalid input: {e}")

# Main Program
print("Welcome to Flight Reservation System")
passengerobj = Passenger()
cashierobj = Cashier()

while True:
    print("\n1. Passenger Login\n2. Cashier Login\n3. Cashier Signup\n4. Exit")
    try:
        choice = int(input("Enter choice: "))
        if choice == 1:
            while True:
                print("\n1. Signup\n2. Signin\n3. Forget Password\n4. Back")
                opt = int(input("Enter choice: "))
                if opt == 1:
                    passengerobj.signup()
                elif opt == 2:
                    passengerobj.signin()
                elif opt == 3:
                    passengerobj.forgetpassword()
                else:
                    break
        elif choice == 2:
            cashierobj.logincashier()
        elif choice == 3:
            cashierobj.signupcashier()
        else:
            break
    except Exception as e:
        print(f"Invalid input: {e}")
