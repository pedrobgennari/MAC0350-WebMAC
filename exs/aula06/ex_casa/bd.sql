CREATE TABLE user (
	user_id INTEGER PRIMARY KEY,
  	name TEXT,
  	password TEXT
);

CREATE TABLE calendar(
  	calendar_id INTEGER PRIMARY KEY,
  	user_id INTEGER,
  
  	FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE appointment(
	appointment_id INTEGER PRIMARY KEY,
    calendar_id INTEGER,
  
  	FOREIGN KEY (calendar_id) REFERENCES calendar(calendar_id)
);
