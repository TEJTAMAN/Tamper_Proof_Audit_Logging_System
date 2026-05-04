-- =========================================================================
-- DATABASE: audit_chain_db
-- PURPOSE : Tamper-Proof Audit Logging System using Blockchain
-- ENGINE  : MySQL 8.0.46
-- HOST    : localhost
-- =========================================================================
--
-- This database implements a blockchain-based audit logging system.
-- Every data change is automatically logged with a SHA-256 hash that
-- links to the previous log entry, forming an unbreakable chain.
--
-- TABLE RELATIONSHIPS:
--
--   role ──< users ──< audit_logs ──< alert
--                          │
--                          ├──< blockchain_logs
--                          │
--   data_records ──────────┘
--       (trigger: after_insert_record)
--
-- CREATION ORDER (dependencies must be created first):
--   1. role              (no dependencies)
--   2. users             (depends on: role)
--   3. data_records      (no dependencies)
--   4. audit_logs        (depends on: users, data_records)
--   5. blockchain_logs   (depends on: audit_logs)
--   6. alert             (depends on: audit_logs)
--   7. TRIGGER           (depends on: data_records, audit_logs)
--
-- =========================================================================


-- -------------------------------------------------------------------------
-- SETUP: Character set and compatibility settings
-- -------------------------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- =========================================================================
-- TABLE 1: role
-- =========================================================================
-- Defines user roles (Admin, User) for access control.
--
-- Columns:
--   role_id   : Unique identifier for each role (auto-increment)
--   role_name : Name of the role (must be unique)
--
-- Sample Data:
--   1 = Admin  (full access)
--   2 = User   (limited access)
-- =========================================================================

DROP TABLE IF EXISTS `role`;

CREATE TABLE `role` (
  `role_id`   INT         NOT NULL AUTO_INCREMENT,
  `role_name` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert default roles
LOCK TABLES `role` WRITE;
INSERT INTO `role` VALUES (1, 'Admin'), (2, 'User');
UNLOCK TABLES;


-- =========================================================================
-- TABLE 2: users
-- =========================================================================
-- Stores user accounts. Each user has a role (Admin or User).
--
-- Columns:
--   user_id       : Unique identifier (auto-increment)
--   username      : Login name (must be unique)
--   password_hash : Hashed password (never store plain text!)
--   role_id       : Foreign key -> role.role_id
--
-- Sample Data:
--   admin1 (Admin role), user1 (User role)
-- =========================================================================

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `user_id`       INT          NOT NULL AUTO_INCREMENT,
  `username`      VARCHAR(50)  NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role_id`       INT          DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert default users
LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES (1, 'admin1', 'hash123', 1), (2, 'user1', 'hash123', 2);
UNLOCK TABLES;


-- =========================================================================
-- TABLE 3: data_records
-- =========================================================================
-- Stores the actual data being tracked/audited.
-- When a new record is inserted, the TRIGGER (defined later)
-- automatically creates an audit log entry with a blockchain hash.
--
-- Columns:
--   record_id    : Unique identifier (auto-increment)
--   data_content : The actual data content
--   created_at   : Timestamp of when the record was created
--
-- Sample Data:
--   record_id=1, data_content='Test Entry'
-- =========================================================================

DROP TABLE IF EXISTS `data_records`;

CREATE TABLE `data_records` (
  `record_id`    INT  NOT NULL AUTO_INCREMENT,
  `data_content` TEXT NOT NULL,
  `created_at`   TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert sample data
LOCK TABLES `data_records` WRITE;
INSERT INTO `data_records` VALUES (1, 'Test Entry', '2026-05-03 10:55:38');
UNLOCK TABLES;


-- =========================================================================
-- TABLE 4: audit_logs  *** MUST come BEFORE the trigger ***
-- =========================================================================
-- The core audit log table — stores WHO did WHAT and WHEN.
-- Each entry has a SHA-256 hash that links to the previous entry,
-- forming a blockchain-style chain.
--
-- Columns:
--   log_id        : Unique identifier (auto-increment)
--   user_id       : Foreign key -> users.user_id (who did it)
--   record_id     : Foreign key -> data_records.record_id (what was affected)
--   action_type   : Type of action (INSERT, UPDATE, DELETE)
--   action_time   : When the action occurred
--   current_hash  : SHA-256 hash of this log entry
--   previous_hash : SHA-256 hash of the PREVIOUS log entry (the chain link!)
--
-- BLOCKCHAIN CONCEPT:
--   current_hash = SHA2( record_id + timestamp + previous_hash, 256 )
--   If anyone changes an old log, its hash changes, breaking the chain.
-- =========================================================================

DROP TABLE IF EXISTS `audit_logs`;

CREATE TABLE `audit_logs` (
  `log_id`        INT          NOT NULL AUTO_INCREMENT,
  `user_id`       INT          DEFAULT NULL,
  `record_id`     INT          DEFAULT NULL,
  `action_type`   VARCHAR(20)  DEFAULT NULL,
  `action_time`   TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
  `current_hash`  VARCHAR(256) DEFAULT NULL,
  `previous_hash` VARCHAR(256) DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  KEY `record_id` (`record_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `audit_logs_ibfk_2` FOREIGN KEY (`record_id`) REFERENCES `data_records` (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert existing audit log data
LOCK TABLES `audit_logs` WRITE;
INSERT INTO `audit_logs` VALUES
  (1, 1, 1, 'INSERT', '2026-05-03 10:55:38',
   'c94c1cf9f273bde24ee71ca19342919b8f0dbf2e3ad6182ed7af7b9f5d83810b', NULL);
UNLOCK TABLES;


-- =========================================================================
-- TABLE 5: blockchain_logs
-- =========================================================================
-- Stores blockchain-specific hash records linked to audit logs.
-- Acts as a secondary verification layer.
--
-- Columns:
--   bc_log_id       : Unique identifier (auto-increment)
--   log_id          : Foreign key -> audit_logs.log_id
--   blockchain_hash : SHA-256 hash for blockchain verification
--   created_at      : Timestamp of when this record was created
-- =========================================================================

DROP TABLE IF EXISTS `blockchain_logs`;

CREATE TABLE `blockchain_logs` (
  `bc_log_id`       INT          NOT NULL AUTO_INCREMENT,
  `log_id`          INT          DEFAULT NULL,
  `blockchain_hash` VARCHAR(256) DEFAULT NULL,
  `created_at`      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`bc_log_id`),
  KEY `log_id` (`log_id`),
  CONSTRAINT `blockchain_logs_ibfk_1` FOREIGN KEY (`log_id`) REFERENCES `audit_logs` (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- =========================================================================
-- TABLE 6: alert
-- =========================================================================
-- Stores alert messages triggered when suspicious activity is detected
-- (e.g. blockchain tampering, unauthorized access attempts).
--
-- Columns:
--   alert_id      : Unique identifier (auto-increment)
--   log_id        : Foreign key -> audit_logs.log_id (which log triggered it)
--   alert_message : Description of the alert
--   created_at    : When the alert was generated
-- =========================================================================

DROP TABLE IF EXISTS `alert`;

CREATE TABLE `alert` (
  `alert_id`      INT          NOT NULL AUTO_INCREMENT,
  `log_id`        INT          DEFAULT NULL,
  `alert_message` VARCHAR(255) DEFAULT NULL,
  `created_at`    TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`alert_id`),
  KEY `log_id` (`log_id`),
  CONSTRAINT `alert_ibfk_1` FOREIGN KEY (`log_id`) REFERENCES `audit_logs` (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- =========================================================================
-- TRIGGER: after_insert_record
-- =========================================================================
-- Fires AFTER a new row is inserted into data_records.
-- MUST be defined AFTER both data_records AND audit_logs tables exist.
--
-- WHAT IT DOES:
--   1. Gets the hash of the LAST audit log entry (previous_hash)
--   2. Creates a NEW hash using SHA2-256:
--        SHA2( record_id + timestamp + previous_hash, 256 )
--   3. Inserts a new row into audit_logs with both hashes
--
-- WHY THIS MATTERS:
--   This is the BLOCKCHAIN part — each log entry's hash depends on
--   the previous entry. Changing any old entry would break the chain.
-- =========================================================================

/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;

DELIMITER ;;

/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_insert_record` AFTER INSERT ON `data_records` FOR EACH ROW BEGIN
    DECLARE prev_hash VARCHAR(256);

    -- Step 1: Get the hash of the most recent audit log (the "previous block")
    SELECT current_hash INTO prev_hash
    FROM audit_logs
    ORDER BY log_id DESC
    LIMIT 1;

    -- Step 2: Insert a new audit log with a chained hash
    INSERT INTO audit_logs (
        user_id,
        record_id,
        action_type,
        current_hash,
        previous_hash
    )
    VALUES (
        1,
        NEW.record_id,
        'INSERT',
        SHA2(CONCAT(NEW.record_id, NOW(), IFNULL(prev_hash, '0')), 256),
        prev_hash
    );
END */;;

DELIMITER ;

/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


-- =========================================================================
-- CLEANUP: Restore original settings
-- =========================================================================

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- =========================================================================
-- END OF SCHEMA
-- =========================================================================
