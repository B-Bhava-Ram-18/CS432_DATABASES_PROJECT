BEGIN TRANSACTION;
CREATE TABLE Administrator(
    Member_ID TEXT PRIMARY KEY,
    Administrator_ID INTEGER NOT NULL UNIQUE,
    Admin_Level INTEGER CHECK(Admin_Level BETWEEN 1 AND 5),
    Department TEXT,
    Office_Location TEXT,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Administrator" VALUES('M001',1001,3,'Operations','Office A');
CREATE TABLE Booking(
    Booking_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Facility_ID INTEGER NOT NULL,
    Member_ID TEXT NOT NULL,
    Time_In TEXT NOT NULL CHECK(strftime('%Y-%m-%d %H:%M:%S', Time_In) = Time_In),
    Time_Out TEXT CHECK(Time_Out IS NULL OR
        (strftime('%Y-%m-%d %H:%M:%S', Time_Out) = Time_Out AND Time_Out >= Time_In)),
    FOREIGN KEY(Facility_ID) REFERENCES Facility(Facility_ID) ON DELETE CASCADE,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Booking" VALUES(1,1,'M001','2026-07-24 08:00:00','2026-07-24 09:00:00');
CREATE TABLE Coach(
    Member_ID TEXT PRIMARY KEY,
    Coach_ID INTEGER NOT NULL UNIQUE,
    Sport_ID TEXT NOT NULL,
    Years_Experience INTEGER DEFAULT 0,
    Salary REAL DEFAULT 0.0,
    Joining_Date TEXT,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE
);
INSERT INTO "Coach" VALUES('M002',2001,'S01',8,65000.0,'2020-01-15');
CREATE TABLE Complaint(
    Complaint_ID TEXT PRIMARY KEY,
    Raised_By TEXT NOT NULL,
    Description TEXT NOT NULL,
    Status TEXT NOT NULL CHECK(Status IN ('Open','Resolved')),
    Date_Filed TEXT NOT NULL DEFAULT (date('now')),
    Resolved_By TEXT,
    FOREIGN KEY(Raised_By) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Resolved_By) REFERENCES Administrator(Member_ID) ON DELETE SET NULL
);
INSERT INTO "Complaint" VALUES('C001','M004','Lighting issue in track area','Open','2026-07-23',NULL);
CREATE TABLE Equipment(
    Equipment_ID TEXT PRIMARY KEY,
    Equipment_Name TEXT NOT NULL,
    Total_Qty INTEGER NOT NULL CHECK(Total_Qty >= 0),
    Status TEXT NOT NULL CHECK(Status IN ('Available','Damaged','Out of Stock')),
    Sport_ID TEXT NOT NULL,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE
);
INSERT INTO "Equipment" VALUES('EQ01','Running Spikes',20,'Available','S01');
CREATE TABLE Equipment_Loan(
    Member_ID TEXT NOT NULL,
    Equipment_ID TEXT NOT NULL,
    Quantity INTEGER NOT NULL CHECK(Quantity > 0),
    Issue_Time TEXT NOT NULL CHECK(strftime('%Y-%m-%d %H:%M:%S', Issue_Time) = Issue_Time),
    Return_Time TEXT CHECK(Return_Time IS NULL OR
        (strftime('%Y-%m-%d %H:%M:%S', Return_Time) = Return_Time AND Return_Time >= Issue_Time)),
    PRIMARY KEY(Member_ID, Equipment_ID, Issue_Time),
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Equipment_ID) REFERENCES Equipment(Equipment_ID) ON DELETE CASCADE
);
INSERT INTO "Equipment_Loan" VALUES('M004','EQ01',2,'2026-07-24 07:30:00','2026-07-24 09:30:00');
CREATE TABLE Event(
    Event_ID TEXT PRIMARY KEY,
    Event_Name TEXT NOT NULL,
    Start_Time TEXT NOT NULL CHECK(strftime('%Y-%m-%d %H:%M:%S', Start_Time) = Start_Time),
    End_Time TEXT NOT NULL CHECK(strftime('%Y-%m-%d %H:%M:%S', End_Time) = End_Time AND End_Time > Start_Time),
    Status TEXT NOT NULL CHECK(Status IN ('Scheduled','Completed','Cancelled','Postponed','Preponed'))
);
INSERT INTO "Event" VALUES('E01','100m Sprint','2026-07-24 09:00:00','2026-07-24 10:00:00','Scheduled');
CREATE TABLE Facility(
    Facility_ID INTEGER PRIMARY KEY,
    Facility_Name TEXT NOT NULL UNIQUE,
    Description TEXT NOT NULL,
    Status TEXT NOT NULL CHECK(Status IN ('Available','Maintenance','Closed'))
);
INSERT INTO "Facility" VALUES(1,'Track Arena','100m running track','Available');
INSERT INTO "Facility" VALUES(2,'Pool Complex','Indoor swimming pool','Available');
CREATE TABLE Member(
    Member_ID TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Phone_Number TEXT UNIQUE,
    Gender TEXT NOT NULL CHECK(Gender IN ('M','F')),
    Age INTEGER NOT NULL CHECK(Age > 0),
    DOB TEXT,
    Image BLOB
);
INSERT INTO "Member" VALUES('M001','Alice Perera','alice@example.com','0711111111','F',22,'2003-04-15',NULL);
INSERT INTO "Member" VALUES('M002','Brian Silva','brian@example.com','0722222222','M',30,'1995-08-02',NULL);
INSERT INTO "Member" VALUES('M003','Chris Fernando','chris@example.com','0733333333','M',24,'2001-11-07',NULL);
INSERT INTO "Member" VALUES('M004','Diana Jayasuriya','diana@example.com','0744444444','F',27,'1998-02-21',NULL);
CREATE TABLE Performance(
    Member_ID TEXT NOT NULL,
    Event_ID TEXT NOT NULL,
    Metric_Name TEXT NOT NULL,
    Metric_Value TEXT NOT NULL,
    Recorded_Date TEXT NOT NULL CHECK(strftime('%Y-%m-%d', Recorded_Date) = Recorded_Date),
    PRIMARY KEY(Member_ID, Event_ID, Metric_Name, Recorded_Date),
    FOREIGN KEY(Member_ID) REFERENCES Player(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Event_ID) REFERENCES Event(Event_ID) ON DELETE CASCADE
);
INSERT INTO "Performance" VALUES('M003','E01','100m Time','10.50','2026-07-24');
CREATE TABLE Player(
    Member_ID TEXT PRIMARY KEY,
    Player_ID INTEGER NOT NULL UNIQUE,
    Height REAL,
    Weight REAL,
    Blood_Group TEXT CHECK(Blood_Group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Player" VALUES('M003',3001,175.5,68.0,'O+');
CREATE TABLE Sport(
    Sport_ID TEXT PRIMARY KEY,
    Sport_Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL CHECK(Category IN ('Indoor','Outdoor','Water'))
);
INSERT INTO "Sport" VALUES('S01','Athletics','Outdoor');
INSERT INTO "Sport" VALUES('S02','Swimming','Water');
CREATE TABLE Team(
    Team_ID TEXT PRIMARY KEY,
    Team_Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL,
    Sport_ID TEXT NOT NULL,
    Coach_ID INTEGER NOT NULL,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE,
    FOREIGN KEY(Coach_ID) REFERENCES Coach(Coach_ID) ON DELETE CASCADE
);
INSERT INTO "Team" VALUES('T01','Track Sprinters','Junior','S01',2001);
CREATE TABLE Team_Event(
    Event_ID TEXT NOT NULL,
    Team_ID TEXT NOT NULL,
    PRIMARY KEY(Event_ID, Team_ID),
    FOREIGN KEY(Event_ID) REFERENCES Event(Event_ID) ON DELETE CASCADE,
    FOREIGN KEY(Team_ID) REFERENCES Team(Team_ID) ON DELETE CASCADE
);
INSERT INTO "Team_Event" VALUES('E01','T01');
CREATE TABLE Team_Roster(
    Team_ID TEXT NOT NULL,
    Member_ID TEXT NOT NULL,
    PRIMARY KEY(Team_ID, Member_ID),
    FOREIGN KEY(Team_ID) REFERENCES Team(Team_ID) ON DELETE CASCADE,
    FOREIGN KEY(Member_ID) REFERENCES Player(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Team_Roster" VALUES('T01','M003');
CREATE TRIGGER prevent_booking_overlap
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
CREATE TRIGGER check_equipment_availability
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
CREATE TRIGGER prevent_player_multi_role
BEFORE INSERT ON Player
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Coach WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Administrator WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;
CREATE TRIGGER prevent_coach_multi_role
BEFORE INSERT ON Coach
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Player WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Administrator WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;
CREATE TRIGGER prevent_admin_multi_role
BEFORE INSERT ON Administrator
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Player WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Coach WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;
CREATE TRIGGER prevent_team_coach_sport_mismatch_insert
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
CREATE TRIGGER prevent_team_coach_sport_mismatch_update
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
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('Booking',1);
COMMIT;
