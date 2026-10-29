-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: hhp_loco_info
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `hhp_loco_info`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hhp_loco_info` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `hhp_loco_info`;

--
-- Table structure for table `dmi_lp_ocip`
--

DROP TABLE IF EXISTS `dmi_lp_ocip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmi_lp_ocip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_verification_table`
--

DROP TABLE IF EXISTS `document_verification_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `document_verification_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `earthing`
--

DROP TABLE IF EXISTS `earthing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `earthing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emi_filter_box`
--

DROP TABLE IF EXISTS `emi_filter_box`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `emi_filter_box` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_type` varchar(255) DEFAULT NULL,
  `loco_id` varchar(255) NOT NULL,
  `s_no` varchar(50) NOT NULL,
  `image_path` varchar(500) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_images_loco_sno` (`loco_id`,`s_no`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `initial_time`
--

DROP TABLE IF EXISTS `initial_time`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `initial_time` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `initial_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_init_time` (`loco_id`,`section_id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `iru_faviely_units_fixing_for_e70_type_loco`
--

DROP TABLE IF EXISTS `iru_faviely_units_fixing_for_e70_type_loco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iru_faviely_units_fixing_for_e70_type_loco` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loco`
--

DROP TABLE IF EXISTS `loco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loco` (
  `Loco_Id` varchar(50) NOT NULL,
  `Loco_type` varchar(255) NOT NULL,
  `Brake_type` varchar(255) NOT NULL,
  `Railway_Division` varchar(255) NOT NULL,
  `Shed_name` varchar(255) NOT NULL,
  `inspection_Date` date NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_time` datetime DEFAULT NULL,
  `completed_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`Loco_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loco_antenna_and_gps_gsm_antenna`
--

DROP TABLE IF EXISTS `loco_antenna_and_gps_gsm_antenna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loco_antenna_and_gps_gsm_antenna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loco_kavach`
--

DROP TABLE IF EXISTS `loco_kavach`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loco_kavach` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loginpage`
--

DROP TABLE IF EXISTS `loginpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loginpage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT 'user',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pgs_and_speedo_meter_units_fixing`
--

DROP TABLE IF EXISTS `pgs_and_speedo_meter_units_fixing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pgs_and_speedo_meter_units_fixing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pneumatic_fittings_and_ep_valve_cocks_fixing`
--

DROP TABLE IF EXISTS `pneumatic_fittings_and_ep_valve_cocks_fixing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pneumatic_fittings_and_ep_valve_cocks_fixing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pressure_sensors_installation_in_loco`
--

DROP TABLE IF EXISTS `pressure_sensors_installation_in_loco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pressure_sensors_installation_in_loco` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `psjb_tpm_units_fixing_for_ccb_type_loco`
--

DROP TABLE IF EXISTS `psjb_tpm_units_fixing_for_ccb_type_loco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `psjb_tpm_units_fixing_for_ccb_type_loco` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `radio_power`
--

DROP TABLE IF EXISTS `radio_power`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `radio_power` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `report`
--

DROP TABLE IF EXISTS `report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(100) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `upload_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rfid_ps_unit`
--

DROP TABLE IF EXISTS `rfid_ps_unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rfid_ps_unit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rfid_reader_assembly`
--

DROP TABLE IF EXISTS `rfid_reader_assembly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rfid_reader_assembly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rib_cab_input_box`
--

DROP TABLE IF EXISTS `rib_cab_input_box`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rib_cab_input_box` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sifa_valve_fixing_for_ccb_type_loco`
--

DROP TABLE IF EXISTS `sifa_valve_fixing_for_ccb_type_loco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sifa_valve_fixing_for_ccb_type_loco` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `verify_serial_numbers_of_equipment_as_per_ic`
--

DROP TABLE IF EXISTS `verify_serial_numbers_of_equipment_as_per_ic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `verify_serial_numbers_of_equipment_as_per_ic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loco_id` varchar(50) NOT NULL,
  `section_id` varchar(50) NOT NULL,
  `loco_type` varchar(50) NOT NULL,
  `brake_type` varchar(50) NOT NULL,
  `railway_division` varchar(100) NOT NULL,
  `shed_name` varchar(100) NOT NULL,
  `inspection_date` date NOT NULL,
  `observation_text` text NOT NULL,
  `remarks` text NOT NULL,
  `S_no` varchar(50) NOT NULL,
  `barcode` varchar(255) DEFAULT NULL,
  `image_path` varchar(1000) NOT NULL,
  `observation_status` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_loco_id` (`loco_id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'hhp_loco_info'
--

--
-- Dumping routines for database 'hhp_loco_info'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-29  9:44:16


-- Default login credentials
-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: hhp_loco_info
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `loginpage`
--

LOCK TABLES `loginpage` WRITE;
/*!40000 ALTER TABLE `loginpage` DISABLE KEYS */;
INSERT INTO `loginpage` VALUES (6,'52477','52477','admin'),(8,'25010','25010','user'),(9,'25016','25016','admin'),(10,'53364','53364','admin');
/*!40000 ALTER TABLE `loginpage` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-29  9:44:16
