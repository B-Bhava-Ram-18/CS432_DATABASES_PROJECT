import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "project.db"

if not DB_PATH.exists():
    subprocess.run([sys.executable, str(ROOT / "DB_Create.py")], check=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.executescript("""
DELETE FROM Complaint;
DELETE FROM Performance;
DELETE FROM Team_Event;
DELETE FROM Team_Roster;
DELETE FROM Booking;
DELETE FROM Equipment_Loan;
DELETE FROM Event;
DELETE FROM Equipment;
DELETE FROM Team;
DELETE FROM Coach;
DELETE FROM Player;
DELETE FROM Administrator;
DELETE FROM Facility;
DELETE FROM Sport;
DELETE FROM Member;
""")

cursor.executescript("""
CREATE TRIGGER IF NOT EXISTS prevent_booking_overlap
BEFORE INSERT ON Booking
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (
      SELECT 1 FROM Booking
      WHERE Facility_ID = NEW.Facility_ID
        AND (
          NEW.Time_In < IFNULL(Time_Out, '9999-12-31 23:59:59')
          AND IFNULL(NEW.Time_Out, '9999-12-31 23:59:59') > Time_In
        )
    ) THEN RAISE(ABORT, 'Booking time conflict')
  END;
END;

CREATE TRIGGER IF NOT EXISTS check_equipment_availability
BEFORE INSERT ON Equipment_Loan
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN (
      (SELECT IFNULL(SUM(Quantity), 0) FROM Equipment_Loan WHERE Equipment_ID = NEW.Equipment_ID AND Return_Time IS NULL)
      + NEW.Quantity
    ) > (
      SELECT Total_Qty FROM Equipment WHERE Equipment_ID = NEW.Equipment_ID
    ) THEN RAISE(ABORT, 'Not enough equipment available')
  END;
END;

CREATE TRIGGER IF NOT EXISTS prevent_player_multi_role
BEFORE INSERT ON Player
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Coach WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Administrator WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;

CREATE TRIGGER IF NOT EXISTS prevent_coach_multi_role
BEFORE INSERT ON Coach
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Player WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Administrator WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;

CREATE TRIGGER IF NOT EXISTS prevent_admin_multi_role
BEFORE INSERT ON Administrator
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Player WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Coach WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;

CREATE TRIGGER IF NOT EXISTS prevent_team_coach_sport_mismatch_insert
BEFORE INSERT ON Team
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1 FROM Coach
      WHERE Coach_ID = NEW.Coach_ID
        AND Sport_ID = NEW.Sport_ID
    ) THEN RAISE(ABORT, 'Team coach must specialize in the team sport')
  END;
END;

CREATE TRIGGER IF NOT EXISTS prevent_team_coach_sport_mismatch_update
BEFORE UPDATE OF Coach_ID, Sport_ID ON Team
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1 FROM Coach
      WHERE Coach_ID = NEW.Coach_ID
        AND Sport_ID = NEW.Sport_ID
    ) THEN RAISE(ABORT, 'Team coach must specialize in the team sport')
  END;
END;
""")

cursor.executemany(
    """
    INSERT INTO Member(Member_ID, Name, Email, Phone_Number, Gender, Age, DOB, Image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    [
        ("M001", "Alice Perera", "alice@example.com", "0711111111", "F", 22, "2003-04-15", None),
        ("M002", "Brian Silva", "brian@example.com", "0722222222", "M", 30, "1995-08-02", None),
        ("M003", "Chris Fernando", "chris@example.com", "0733333333", "M", 24, "2001-11-07", None),
        ("M004", "Diana Jayasuriya", "diana@example.com", "0744444444", "F", 27, "1998-02-21", None),
    ],
)

cursor.executemany(
    """
    INSERT INTO Sport(Sport_ID, Sport_Name, Category)
    VALUES (?, ?, ?)
    """,
    [("S01", "Athletics", "Outdoor"), ("S02", "Swimming", "Water")],
)

cursor.executemany(
    """
    INSERT INTO Facility(Facility_ID, Facility_Name, Description, Status)
    VALUES (?, ?, ?, ?)
    """,
    [(1, "Track Arena", "100m running track", "Available"), (2, "Pool Complex", "Indoor swimming pool", "Available")],
)

cursor.executemany(
    """
    INSERT INTO Administrator(Member_ID, Administrator_ID, Admin_Level, Department, Office_Location)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("M001", 1001, 3, "Operations", "Office A")],
)

cursor.executemany(
    """
    INSERT INTO Coach(Member_ID, Coach_ID, Sport_ID, Years_Experience, Salary, Joining_Date)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    [("M002", 2001, "S01", 8, 65000.0, "2020-01-15")],
)

cursor.executemany(
    """
    INSERT INTO Player(Member_ID, Player_ID, Height, Weight, Blood_Group)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("M003", 3001, 175.5, 68.0, "O+")],
)

cursor.executemany(
    """
    INSERT INTO Team(Team_ID, Team_Name, Category, Sport_ID, Coach_ID)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("T01", "Track Sprinters", "Junior", "S01", 2001)],
)

cursor.executemany(
    """
    INSERT INTO Team_Roster(Team_ID, Member_ID)
    VALUES (?, ?)
    """,
    [("T01", "M003")],
)

cursor.executemany(
    """
    INSERT INTO Event(Event_ID, Event_Name, Start_Time, End_Time, Status)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("E01", "100m Sprint", "2026-07-24 09:00:00", "2026-07-24 10:00:00", "Scheduled")],
)

cursor.executemany(
    """
    INSERT INTO Team_Event(Event_ID, Team_ID)
    VALUES (?, ?)
    """,
    [("E01", "T01")],
)

cursor.executemany(
    """
    INSERT INTO Equipment(Equipment_ID, Equipment_Name, Total_Qty, Status, Sport_ID)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("EQ01", "Running Spikes", 20, "Available", "S01")],
)

cursor.executemany(
    """
    INSERT INTO Booking(Booking_ID, Facility_ID, Member_ID, Time_In, Time_Out)
    VALUES (?, ?, ?, ?, ?)
    """,
    [(1, 1, "M001", "2026-07-24 08:00:00", "2026-07-24 09:00:00")],
)

cursor.executemany(
    """
    INSERT INTO Equipment_Loan(Member_ID, Equipment_ID, Quantity, Issue_Time, Return_Time)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("M004", "EQ01", 2, "2026-07-24 07:30:00", "2026-07-24 09:30:00")],
)

cursor.executemany(
    """
    INSERT INTO Performance(Member_ID, Event_ID, Metric_Name, Metric_Value, Recorded_Date)
    VALUES (?, ?, ?, ?, ?)
    """,
    [("M003", "E01", "100m Time", "10.50", "2026-07-24")],
)

cursor.executemany(
    """
    INSERT INTO Complaint(Complaint_ID, Raised_By, Description, Status, Date_Filed, Resolved_By)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    [("C001", "M004", "Lighting issue in track area", "Open", "2026-07-23", None)],
)

conn.commit()
conn.close()

print("Data synced successfully")
