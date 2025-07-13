CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) UNIQUE,
    pass VARCHAR(100),
    current_room VARCHAR(100)
);

CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(100),
    pass VARCHAR(100),
    created_by VARCHAR(100),
    created_at DATETIME
);

CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(100),
    sent_by VARCHAR(100),
    msg TEXT,
    sent_at DATETIME
);
