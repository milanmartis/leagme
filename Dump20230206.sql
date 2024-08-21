-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: darts
-- ------------------------------------------------------
-- Server version	8.0.26-google

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '008565be-a3a9-11ed-ac32-42010a400005:1-52003';

--
-- Dumping data for table `duel`
--

LOCK TABLES `duel` WRITE;
/*!40000 ALTER TABLE `duel` DISABLE KEYS */;
INSERT INTO `duel` VALUES (1,'2023-01-16 14:30:47',1,1),(2,'2023-01-16 14:30:47',1,1),(3,'2023-01-16 14:30:47',1,1),(4,'2023-01-16 14:30:47',1,1),(5,'2023-01-16 14:30:47',1,1),(6,'2023-01-16 14:30:47',1,1),(7,'2023-01-16 14:30:47',1,1),(8,'2023-01-16 14:30:47',1,1),(9,'2023-01-16 14:30:47',1,1),(10,'2023-01-16 14:30:47',1,1),(11,'2023-01-16 14:30:47',1,1),(12,'2023-01-16 14:30:47',1,1),(13,'2023-01-16 14:30:47',1,1),(14,'2023-01-16 14:30:47',1,1),(15,'2023-01-16 14:30:47',1,1),(16,'2023-01-16 14:30:47',1,1),(17,'2023-01-16 14:30:47',1,1),(18,'2023-01-16 14:30:47',1,1),(19,'2023-01-16 14:30:47',1,1),(20,'2023-01-16 14:30:47',1,1),(21,'2023-01-16 14:30:47',1,1),(22,'2023-01-16 14:30:47',1,1),(23,'2023-01-16 14:30:47',1,1),(24,'2023-01-16 14:30:47',1,1),(25,'2023-01-16 14:30:48',1,1),(26,'2023-01-16 14:30:48',1,1),(27,'2023-01-16 14:30:48',1,1),(28,'2023-01-16 14:30:48',1,1),(29,'2023-01-16 14:30:48',1,1),(30,'2023-01-16 14:30:48',1,1),(91,'2023-01-17 22:40:19',1,1),(92,'2023-01-17 22:40:19',1,1),(93,'2023-01-17 22:40:19',1,1),(94,'2023-01-17 22:40:19',1,1),(95,'2023-01-17 22:40:19',1,1),(96,'2023-01-17 22:40:19',1,1),(97,'2023-01-17 22:40:19',1,1),(98,'2023-01-17 22:40:19',1,1),(99,'2023-01-17 22:40:19',1,1),(100,'2023-01-17 22:40:19',1,1),(101,'2023-02-01 10:29:59',1,2),(102,'2023-02-01 10:29:59',1,2),(103,'2023-02-01 10:29:59',1,2),(104,'2023-02-01 10:29:59',1,2),(105,'2023-02-01 10:29:59',1,2),(106,'2023-02-01 10:29:59',1,2),(107,'2023-02-01 10:29:59',1,2),(108,'2023-02-01 10:29:59',1,2),(109,'2023-02-01 10:29:59',1,2),(110,'2023-02-01 10:29:59',1,2),(111,'2023-02-01 10:29:59',1,2),(112,'2023-02-01 10:30:00',1,2),(113,'2023-02-01 10:30:00',1,2),(114,'2023-02-01 10:30:00',1,2),(115,'2023-02-01 10:30:00',1,2),(116,'2023-02-01 10:30:00',1,2),(117,'2023-02-01 10:30:00',1,2),(118,'2023-02-01 10:30:00',1,2),(119,'2023-02-01 10:30:00',1,2),(120,'2023-02-01 10:30:00',1,2),(121,'2023-02-01 10:30:00',1,2),(122,'2023-02-01 10:30:00',1,2),(123,'2023-02-01 10:30:00',1,2),(124,'2023-02-01 10:30:00',1,2),(125,'2023-02-01 10:30:00',1,2),(126,'2023-02-01 10:30:00',1,2),(127,'2023-02-01 10:30:00',1,2),(128,'2023-02-01 10:30:00',1,2),(129,'2023-02-01 10:30:00',1,2),(130,'2023-02-01 10:30:00',1,2),(131,'2023-02-01 10:30:00',1,2),(132,'2023-02-01 10:30:00',1,2),(133,'2023-02-01 10:30:00',1,2),(134,'2023-02-01 10:30:00',1,2),(135,'2023-02-01 10:30:00',1,2),(136,'2023-02-01 10:30:00',1,2),(137,'2023-02-01 10:30:00',1,2),(138,'2023-02-01 10:30:00',1,2),(139,'2023-02-01 10:30:00',1,2),(140,'2023-02-01 10:30:00',1,2),(141,'2023-02-01 10:30:00',1,2),(142,'2023-02-01 10:30:01',1,2),(143,'2023-02-01 10:30:01',1,2),(144,'2023-02-01 10:30:01',1,2),(145,'2023-02-01 10:30:01',1,2),(146,'2023-02-01 10:30:01',1,2),(147,'2023-02-01 10:30:01',1,2),(148,'2023-02-01 10:30:01',1,2),(149,'2023-02-01 10:30:01',1,2),(150,'2023-02-01 10:30:01',1,2);
/*!40000 ALTER TABLE `duel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `groupz`
--

LOCK TABLES `groupz` WRITE;
/*!40000 ALTER TABLE `groupz` DISABLE KEYS */;
INSERT INTO `groupz` VALUES (1,'Group 1','A',1,1),(2,'Group 2','B1',1,1),(3,'Group 3','B2',1,1),(7,'Group 4','C1',1,1),(8,'Group 1','A',1,2),(9,'Group 2','B1',1,2),(10,'Group 3','B2',1,2),(11,'Group 4','C1',1,2),(12,'Group 5','C2',1,2);
/*!40000 ALTER TABLE `groupz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `note`
--

LOCK TABLES `note` WRITE;
/*!40000 ALTER TABLE `note` DISABLE KEYS */;
/*!40000 ALTER TABLE `note` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `openhour`
--

LOCK TABLES `openhour` WRITE;
/*!40000 ALTER TABLE `openhour` DISABLE KEYS */;
/*!40000 ALTER TABLE `openhour` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `round`
--

LOCK TABLES `round` WRITE;
/*!40000 ALTER TABLE `round` DISABLE KEYS */;
INSERT INTO `round` VALUES (1,1),(2,1);
/*!40000 ALTER TABLE `round` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `season`
--

LOCK TABLES `season` WRITE;
/*!40000 ALTER TABLE `season` DISABLE KEYS */;
INSERT INTO `season` VALUES (1,'First Season#2','2023-01-16 12:27:26','2023-01-16 12:27:26',NULL);
/*!40000 ALTER TABLE `season` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'hery@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','hery',3),(2,'andy@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','andy',1),(3,'imre@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','imre',2),(4,'juso@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','juso',6),(5,'jardo@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','jardo',11),(6,'matis@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','matis',12),(7,'peto@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','peto',7),(8,'demo@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','demo',4),(9,'h1@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','h1',10),(10,'magnum@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','magnum',21),(11,'foxo@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','foxo',16),(12,'edo@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','edo',13),(13,'h2@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','h2',15),(14,'tomas_v@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','tomáš v',5),(15,'majo@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','majo',8),(16,'tomas@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','tomáš',14),(17,'pista@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','pišta',22),(18,'samo_n@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','samo n',9),(19,'marek@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','marek',17),(20,'h3@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','h3',20),(21,'milanmartis@gmail.com','sha256$qqXJ4Xs1PbkXn7PJ$1f9b18ff17b435232ae8fdf5321cd52f212b5dbb6b4b02ba6b8ce7959c30a1c8','milanko',0),(22,'petko@dartsclub.sk','sha256$Abu3aAAp0hYha4fJ$8ea439c4796c6d9b4d02f1c252d4ee3974f6580c7cc03434ec8aa248585535a8','Peter Grič',0),(23,'konik_r@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','Koník R',18),(24,'gric_j@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','Grič J',19),(25,'juhasz_a@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','Juhász A',23),(26,'drahos@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','Drahoš',24),(27,'h4@dartsclub.sk','sha256$bAP8swh72ZFzw2Wo$997746eff2d7c50e774dede206c43848fa8f8e1714227d2969147156d001785d','h4',25);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user_duel`
--

LOCK TABLES `user_duel` WRITE;
/*!40000 ALTER TABLE `user_duel` DISABLE KEYS */;
INSERT INTO `user_duel` VALUES (1,1,3,6,0,'true',NULL,1),(2,1,6,3,2,'true',NULL,1),(1,2,2,6,0,'true',NULL,1),(3,2,6,2,2,'true',NULL,1),(1,3,6,1,2,'true',NULL,1),(4,3,1,6,0,'true',NULL,1),(1,4,6,4,2,'true',NULL,1),(5,4,4,6,0,'true',NULL,1),(2,5,6,4,2,'true',NULL,1),(3,5,4,6,0,'true',NULL,1),(2,6,6,1,2,'true',NULL,1),(4,6,1,6,0,'true',NULL,1),(2,7,6,0,2,'true',NULL,1),(5,7,0,6,0,'true',NULL,1),(3,8,6,1,2,'true',NULL,1),(4,8,1,6,0,'true',NULL,1),(3,9,6,0,2,'true',NULL,1),(5,9,0,6,0,'true',NULL,1),(4,10,1,6,0,'true',NULL,1),(5,10,6,1,2,'true',NULL,1),(6,11,6,3,2,'true',NULL,1),(7,11,3,6,0,'true',NULL,1),(6,12,4,6,0,'true',NULL,1),(8,12,6,4,2,'true',NULL,1),(6,13,4,0,2,'true',NULL,1),(9,13,0,4,0,'true',NULL,1),(6,14,6,1,2,'true',NULL,1),(10,14,1,6,0,'true',NULL,1),(7,15,3,6,0,'true',NULL,1),(8,15,6,3,2,'true',NULL,1),(7,16,4,0,2,'true',NULL,1),(9,16,0,4,0,'true',NULL,1),(7,17,4,0,2,'true',NULL,1),(10,17,0,4,0,'true',NULL,1),(8,18,4,0,2,'true',NULL,1),(9,18,0,4,0,'true',NULL,1),(8,19,4,0,2,'true',NULL,1),(10,19,0,4,0,'true',NULL,1),(9,20,0,4,0,'true',NULL,1),(10,20,4,0,2,'true',NULL,1),(11,21,4,6,0,'true',NULL,1),(12,21,6,4,2,'true',NULL,1),(11,22,4,0,2,'true',NULL,1),(13,22,0,4,0,'true',NULL,1),(11,23,4,6,0,'true',NULL,1),(14,23,6,4,2,'true',NULL,1),(11,24,3,6,0,'true',NULL,1),(15,24,6,3,2,'true',NULL,1),(12,25,4,0,2,'true',NULL,1),(13,25,0,4,0,'true',NULL,1),(12,26,0,6,0,'true',NULL,1),(14,26,6,0,2,'true',NULL,1),(12,27,3,6,0,'true',NULL,1),(15,27,6,3,2,'true',NULL,1),(13,28,0,4,0,'true',NULL,1),(14,28,4,0,2,'true',NULL,1),(13,29,0,4,0,'true',NULL,1),(15,29,4,0,2,'true',NULL,1),(14,30,6,4,2,'true',NULL,1),(15,30,4,6,0,'true',NULL,1),(16,91,6,4,2,'true',NULL,1),(17,91,4,6,0,'true',NULL,1),(16,92,1,6,0,'true',NULL,1),(18,92,6,1,2,'true',NULL,1),(16,93,6,3,2,'true',NULL,1),(19,93,3,6,0,'true',NULL,1),(16,94,4,0,2,'true',NULL,1),(20,94,0,4,0,'true',NULL,1),(17,95,0,6,0,'true',NULL,1),(18,95,6,0,2,'true',NULL,1),(17,96,6,4,2,'true',NULL,1),(19,96,4,6,0,'true',NULL,1),(17,97,4,0,2,'true',NULL,1),(20,97,0,4,0,'true',NULL,1),(18,98,6,0,2,'true',NULL,1),(19,98,0,6,0,'true',NULL,1),(18,99,4,0,2,'true',NULL,1),(20,99,0,4,0,'true',NULL,1),(19,100,4,0,2,'true',NULL,1),(20,100,0,4,0,'true',NULL,1),(14,101,0,0,0,'false',NULL,1),(2,101,0,0,0,'false',NULL,1),(14,102,0,0,0,'false',NULL,1),(1,102,0,0,0,'false',NULL,1),(14,103,0,0,0,'false',NULL,1),(3,103,0,0,0,'false',NULL,1),(14,104,0,0,0,'false',NULL,1),(8,104,0,0,0,'false',NULL,1),(2,105,0,0,0,'false',NULL,1),(1,105,0,0,0,'false',NULL,1),(2,106,0,0,0,'false',NULL,1),(3,106,0,0,0,'false',NULL,1),(2,107,0,0,0,'false',NULL,1),(8,107,0,0,0,'false',NULL,1),(1,108,0,0,0,'false',NULL,1),(3,108,0,0,0,'false',NULL,1),(1,109,0,0,0,'false',NULL,1),(8,109,0,0,0,'false',NULL,1),(3,110,0,0,0,'false',NULL,1),(8,110,0,0,0,'false',NULL,1),(18,111,2,6,0,'true',NULL,1),(4,111,6,2,2,'true',NULL,1),(18,112,3,6,0,'true',NULL,1),(7,112,6,3,2,'true',NULL,1),(18,113,0,0,0,'false',NULL,1),(15,113,0,0,0,'false',NULL,1),(18,114,0,0,0,'false',NULL,1),(9,114,0,0,0,'false',NULL,1),(4,115,0,0,0,'false',NULL,1),(7,115,0,0,0,'false',NULL,1),(4,116,0,0,0,'false',NULL,1),(15,116,0,0,0,'false',NULL,1),(4,117,0,0,0,'false',NULL,1),(9,117,0,0,0,'false',NULL,1),(7,118,0,0,0,'false',NULL,1),(15,118,0,0,0,'false',NULL,1),(7,119,0,0,0,'false',NULL,1),(9,119,0,0,0,'false',NULL,1),(15,120,0,0,0,'false',NULL,1),(9,120,0,0,0,'false',NULL,1),(12,121,0,0,0,'false',NULL,1),(16,121,0,0,0,'false',NULL,1),(12,122,0,0,0,'false',NULL,1),(5,122,0,0,0,'false',NULL,1),(12,123,0,0,0,'false',NULL,1),(13,123,0,0,0,'false',NULL,1),(12,124,0,0,0,'false',NULL,1),(6,124,0,0,0,'false',NULL,1),(16,125,0,0,0,'false',NULL,1),(5,125,0,0,0,'false',NULL,1),(16,126,0,0,0,'false',NULL,1),(13,126,0,0,0,'false',NULL,1),(16,127,0,0,0,'false',NULL,1),(6,127,0,0,0,'false',NULL,1),(5,128,0,0,0,'false',NULL,1),(13,128,0,0,0,'false',NULL,1),(5,129,0,0,0,'false',NULL,1),(6,129,0,0,0,'false',NULL,1),(13,130,0,0,0,'false',NULL,1),(6,130,0,0,0,'false',NULL,1),(20,131,0,0,0,'false',NULL,1),(11,131,0,0,0,'false',NULL,1),(20,132,0,0,0,'false',NULL,1),(23,132,0,0,0,'false',NULL,1),(20,133,0,0,0,'false',NULL,1),(19,133,0,0,0,'false',NULL,1),(20,134,0,4,0,'false',NULL,1),(24,134,4,0,2,'true',NULL,1),(11,135,0,0,0,'false',NULL,1),(23,135,0,0,0,'false',NULL,1),(11,136,0,0,0,'false',NULL,1),(19,136,0,0,0,'false',NULL,1),(11,137,0,0,0,'false',NULL,1),(24,137,0,0,0,'false',NULL,1),(23,138,0,0,0,'false',NULL,1),(19,138,0,0,0,'false',NULL,1),(23,139,0,0,0,'false',NULL,1),(24,139,0,0,0,'false',NULL,1),(19,140,0,0,0,'false',NULL,1),(24,140,0,0,0,'false',NULL,1),(25,141,6,4,2,'true',NULL,1),(10,141,4,6,0,'true',NULL,1),(25,142,0,0,0,'false',NULL,1),(17,142,0,0,0,'false',NULL,1),(25,143,0,0,0,'false',NULL,1),(26,143,0,0,0,'false',NULL,1),(25,144,0,0,0,'false',NULL,1),(27,144,0,0,0,'false',NULL,1),(10,145,0,0,0,'false',NULL,1),(17,145,0,0,0,'false',NULL,1),(10,146,0,0,0,'false',NULL,1),(26,146,0,0,0,'false',NULL,1),(10,147,0,0,0,'false',NULL,1),(27,147,0,0,0,'false',NULL,1),(17,148,0,0,0,'false',NULL,1),(26,148,0,0,0,'false',NULL,1),(17,149,0,0,0,'false',NULL,1),(27,149,0,0,0,'false',NULL,1),(26,150,0,0,0,'false',NULL,1),(27,150,0,0,0,'false',NULL,1);
/*!40000 ALTER TABLE `user_duel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user_group`
--

LOCK TABLES `user_group` WRITE;
/*!40000 ALTER TABLE `user_group` DISABLE KEYS */;
INSERT INTO `user_group` VALUES (1,1,1,1),(2,1,1,1),(3,1,1,1),(4,1,1,1),(5,1,1,1),(6,2,1,1),(7,2,1,1),(8,2,1,1),(9,2,1,1),(10,2,1,1),(11,3,1,1),(12,3,1,1),(13,3,1,1),(14,3,1,1),(15,3,1,1),(16,7,1,1),(17,7,1,1),(18,7,1,1),(19,7,1,1),(20,7,1,1),(2,8,1,2),(3,8,1,2),(1,8,1,2),(8,8,1,2),(14,8,1,2),(4,9,1,2),(7,9,1,2),(15,9,1,2),(18,9,1,2),(9,9,1,2),(5,10,1,2),(6,10,1,2),(12,10,1,2),(16,10,1,2),(13,10,1,2),(11,11,1,2),(19,11,1,2),(23,11,1,2),(24,11,1,2),(20,11,1,2),(10,12,1,2),(17,12,1,2),(25,12,1,2),(26,12,1,2),(27,12,1,2);
/*!40000 ALTER TABLE `user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user_season`
--

LOCK TABLES `user_season` WRITE;
/*!40000 ALTER TABLE `user_season` DISABLE KEYS */;
INSERT INTO `user_season` VALUES (1,1,'2023-01-16 13:29:42',3),(2,1,'2023-01-16 13:29:42',1),(3,1,'2023-01-16 13:29:42',2),(4,1,'2023-01-16 13:29:42',6),(5,1,'2023-01-16 13:29:42',11),(6,1,'2023-01-16 13:29:42',12),(7,1,'2023-01-16 13:29:42',7),(8,1,'2023-01-16 13:29:42',4),(9,1,'2023-01-16 13:29:42',10),(10,1,'2023-01-16 13:29:42',21),(11,1,'2023-01-16 13:29:42',16),(12,1,'2023-01-16 13:29:42',13),(13,1,'2023-01-16 13:29:42',15),(14,1,'2023-01-16 13:29:42',5),(15,1,'2023-01-16 13:29:42',8),(16,1,'2023-01-16 13:29:42',14),(17,1,'2023-01-16 13:29:42',22),(18,1,'2023-01-16 13:29:42',9),(19,1,'2023-01-16 13:29:42',17),(20,1,'2023-01-16 13:29:42',20),(23,1,'2023-01-16 13:29:42',18),(24,1,'2023-01-16 13:29:42',19),(25,1,'2023-01-16 13:29:42',23),(26,1,'2023-01-16 13:29:42',24),(27,1,'2023-01-16 13:29:42',25);
/*!40000 ALTER TABLE `user_season` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-02-06 11:06:57
