-- Création de la base de données
DROP DATABASE IF EXISTS pokweb;
CREATE DATABASE pokweb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pokweb;

-- Table des ligues
CREATE TABLE leagues (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL UNIQUE,
   description VARCHAR(500)
);

-- Table des utilisateurs
CREATE TABLE users (
   id INT AUTO_INCREMENT PRIMARY KEY,
   email VARCHAR(255) NOT NULL UNIQUE,
   username VARCHAR(50) NOT NULL UNIQUE,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   hashed_password VARCHAR(255) NOT NULL,
   address VARCHAR(255),
   member_status VARCHAR(255),
   profile_image_path VARCHAR(255),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   last_login TIMESTAMP NULL,
   league_id INT,
   FOREIGN KEY (league_id) REFERENCES leagues(id)
);

-- Table d'association admin-ligue
CREATE TABLE league_admins (
   league_id INT,
   user_id INT,
   PRIMARY KEY (league_id, user_id),
   FOREIGN KEY (league_id) REFERENCES leagues(id),
   FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des configurations de tournoi
CREATE TABLE tournament_configurations (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   tournament_type ENUM('JAPT', 'CLASSIQUE', 'MTT') NOT NULL,
   is_default BOOLEAN DEFAULT FALSE,
   starting_chips INT NOT NULL,
   buy_in DECIMAL(10,2) NOT NULL,
   blinds_structure JSON NOT NULL,
   rebuy_levels INT DEFAULT 0,
   payouts_structure JSON NOT NULL,
   created_by_id INT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Table des configurations sonores
CREATE TABLE sound_configurations (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   is_default BOOLEAN DEFAULT FALSE,
   sounds JSON NOT NULL,
   created_by_id INT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Table des tournois
CREATE TABLE tournaments (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   tournament_type ENUM('CLASSIQUE', 'MTT', 'JAPT') NOT NULL,
   status ENUM('PLANNED', 'IN_PROGRESS', 'COMPLETED') DEFAULT 'PLANNED',
   configuration_id INT NOT NULL,
   sound_configuration_id INT NOT NULL,
   date TIMESTAMP NOT NULL,
   start_time TIMESTAMP NULL,
   end_time TIMESTAMP NULL,
   current_level INT DEFAULT 0,
   seconds_remaining INT NULL,
   level_duration INT NULL,
   paused_at TIMESTAMP NULL,
   last_timer_update TIMESTAMP NULL,
   max_players INT NOT NULL,
   buy_in DECIMAL(10,2) NOT NULL,
   num_tables INT DEFAULT 1,
   players_per_table INT DEFAULT 10,
   total_buyin DECIMAL(10,2) DEFAULT 0,
   total_rebuys INT DEFAULT 0,
   prize_pool DECIMAL(10,2) DEFAULT 0,
   clay_token_holder_id INT,
   bounty_hunter_id INT,
   tables_state JSON,
   admin_id INT NOT NULL,
   league_id INT NOT NULL,
   FOREIGN KEY (configuration_id) REFERENCES tournament_configurations(id),
   FOREIGN KEY (sound_configuration_id) REFERENCES sound_configurations(id),
   FOREIGN KEY (admin_id) REFERENCES users(id),
   FOREIGN KEY (clay_token_holder_id) REFERENCES users(id),
   FOREIGN KEY (bounty_hunter_id) REFERENCES users(id),
   FOREIGN KEY (league_id) REFERENCES leagues(id)
);

-- Table des participations aux tournois
CREATE TABLE tournament_participations (
   id INT AUTO_INCREMENT PRIMARY KEY,
   tournament_id INT NOT NULL,
   user_id INT NOT NULL,
   is_registered BOOLEAN DEFAULT TRUE,
   is_active BOOLEAN DEFAULT TRUE,
   registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   elimination_time TIMESTAMP NULL,
   current_position INT NULL,
   num_rebuys INT DEFAULT 0,
   total_buyin DECIMAL(10,2) DEFAULT 0,
   prize_won DECIMAL(10,2) DEFAULT 0,
   action_history JSON,
   FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
   FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des articles du blog
CREATE TABLE blog_posts (
   id INT AUTO_INCREMENT PRIMARY KEY,
   title VARCHAR(200) NOT NULL,
   content TEXT NOT NULL,
   author_id INT NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Table des images du blog
CREATE TABLE blog_post_images (
   id INT AUTO_INCREMENT PRIMARY KEY,
   blog_post_id INT NOT NULL,
   image_path VARCHAR(255) NOT NULL,
   description VARCHAR(200),
   FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id) ON DELETE CASCADE
);

-- Insertion des configurations par défaut
INSERT INTO tournament_configurations (
    name,
    is_default,
    tournament_type,
    starting_chips,
    buy_in,
    blinds_structure,
    rebuy_levels,
    payouts_structure
) VALUES
(
    'JAPT Standard',
    TRUE,
    'JAPT',
    20000,
    20.00,
    '[
        {"level":1,"small_blind":50,"big_blind":100,"duration":15},
        {"level":2,"small_blind":100,"big_blind":200,"duration":15},
        {"level":3,"small_blind":150,"big_blind":300,"duration":15},
        {"level":4,"small_blind":200,"big_blind":400,"duration":15},
        {"level":5,"small_blind":300,"big_blind":600,"duration":15},
        {"level":6,"small_blind":400,"big_blind":800,"duration":15},
        {"level":7,"small_blind":500,"big_blind":1000,"duration":15},
        {"level":8,"small_blind":700,"big_blind":1400,"duration":15},
        {"level":9,"small_blind":1000,"big_blind":2000,"duration":15},
        {"level":10,"small_blind":1500,"big_blind":3000,"duration":15}
    ]',
    6,
    '[
        {
            "num_players":10,
            "prizes":[
                {"position":1,"percentage":50},
                {"position":2,"percentage":30},
                {"position":3,"percentage":20}
            ]
        },
        {
            "num_players":6,
            "prizes":[
                {"position":1,"percentage":60},
                {"position":2,"percentage":40}
            ]
        }
    ]'
),
(
    'MTT Standard',
    TRUE,
    'MTT',
    25000,
    30.00,
    '[
        {"level":1,"small_blind":25,"big_blind":50,"duration":20},
        {"level":2,"small_blind":50,"big_blind":100,"duration":20},
        {"level":3,"small_blind":75,"big_blind":150,"duration":20},
        {"level":4,"small_blind":100,"big_blind":200,"duration":20},
        {"level":5,"small_blind":150,"big_blind":300,"duration":20},
        {"level":6,"small_blind":200,"big_blind":400,"duration":20},
        {"level":7,"small_blind":300,"big_blind":600,"duration":20},
        {"level":8,"small_blind":400,"big_blind":800,"duration":20},
        {"level":9,"small_blind":500,"big_blind":1000,"duration":20},
        {"level":10,"small_blind":700,"big_blind":1400,"duration":20}
    ]',
    8,
    '[
        {
            "num_players":18,
            "prizes":[
                {"position":1,"percentage":45},
                {"position":2,"percentage":25},
                {"position":3,"percentage":15},
                {"position":4,"percentage":10},
                {"position":5,"percentage":5}
            ]
        },
        {
            "num_players":12,
            "prizes":[
                {"position":1,"percentage":50},
                {"position":2,"percentage":30},
                {"position":3,"percentage":20}
            ]
        }
    ]'
),
(
    'Classique Standard',
    TRUE,
    'CLASSIQUE',
    20000,
    25.00,
    '[
        {"level":1,"small_blind":50,"big_blind":100,"duration":15},
        {"level":2,"small_blind":100,"big_blind":200,"duration":15},
        {"level":3,"small_blind":150,"big_blind":300,"duration":15},
        {"level":4,"small_blind":200,"big_blind":400,"duration":15},
        {"level":5,"small_blind":300,"big_blind":600,"duration":15},
        {"level":6,"small_blind":400,"big_blind":800,"duration":15},
        {"level":7,"small_blind":500,"big_blind":1000,"duration":15},
        {"level":8,"small_blind":700,"big_blind":1400,"duration":15}
    ]',
    4,
    '[
        {
            "num_players":8,
            "prizes":[
                {"position":1,"percentage":60},
                {"position":2,"percentage":40}
            ]
        },
        {
            "num_players":10,
            "prizes":[
                {"position":1,"percentage":50},
                {"position":2,"percentage":30},
                {"position":3,"percentage":20}
            ]
        }
    ]'
);

INSERT INTO sound_configurations (
    name,
    is_default,
    sounds
) VALUES
(
    'Sons par défaut',
    TRUE,
    '{
        "level_start": "default_start.mp3",
        "level_warning": "default_warning.mp3",
        "break_start": "default_break.mp3",
        "break_end": "default_break_end.mp3"
    }'
);

-- Création des répertoires pour les uploads
-- Ces commandes devraient être exécutées au niveau du système, pas par MySQL
-- mkdir -p uploads/profile_images
-- mkdir -p uploads/blog
-- mkdir -p uploads/sounds
-- chmod -R 755 uploads