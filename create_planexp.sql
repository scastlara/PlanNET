-- MySQL Script generated by MySQL Workbench
-- lun 05 nov 2018 12:42:21 CET
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema db_plannet
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema db_plannet
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `db_plannet` ;
USE `db_plannet` ;

-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_experiments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_experiments` (
  `id_experiment` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `description` VARCHAR(500) NULL,
  `citation` VARCHAR(100) NULL,
  `type` INT NULL,
  PRIMARY KEY (`id_experiment`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_conditions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_conditions` (
  `id_condition` INT NOT NULL AUTO_INCREMENT,
  `id_experiment` VARCHAR(45) NULL,
  `condition_name` VARCHAR(45) NULL,
  `condition_type` INT NULL,
  `condition_description` VARCHAR(500) NULL,
  PRIMARY KEY (`id_condition`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_cells`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_cells` (
  `id_cell` INT NOT NULL AUTO_INCREMENT,
  `cell_name` VARCHAR(45) NULL,
  `id_experiment` INT NULL,
  `id_condition` INT NULL,
  PRIMARY KEY (`id_cell`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_expression_absolute`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_expression_absolute` (
  `id_experiment_expression` INT NOT NULL AUTO_INCREMENT,
  `id_experiment` INT NULL,
  `id_condition-cell` INT NULL,
  `dataset` VARCHAR(45) NULL,
  `gene_symbol` VARCHAR(45) NULL,
  `expression_value` DOUBLE NULL,
  `expression_value_units` VARCHAR(45) NULL,
  PRIMARY KEY (`id_experiment_expression`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_expression_relative`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_expression_relative` (
  `id_experiment_expression_relative` INT NOT NULL AUTO_INCREMENT,
  `id_experiment` INT NULL,
  `condition1_id` INT NULL,
  `condition2_id` INT NULL,
  `fold_change` FLOAT NULL,
  `pvalue` DOUBLE NULL,
  PRIMARY KEY (`id_experiment_expression_relative`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_cell_clustering`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_cell_clustering` (
  `id_cell_clustering` INT NOT NULL AUTO_INCREMENT,
  `id_experiment` INT NULL,
  `clustering_name` VARCHAR(45) NULL,
  `clustering_method` VARCHAR(45) NULL,
  `number_of_clusters` INT NULL,
  PRIMARY KEY (`id_cell_clustering`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_cell_clusters`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_cell_clusters` (
  `id_cell_cluster` INT NOT NULL AUTO_INCREMENT,
  `id_cell_clustering` INT NULL,
  `cluster_name` VARCHAR(45) NULL,
  `cluster_celltype` VARCHAR(45) NULL,
  PRIMARY KEY (`id_cell_cluster`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_plannet`.`planexp_cell_cluster_membership`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_plannet`.`planexp_cell_cluster_membership` (
  `id_cell_cluster_membership` INT NOT NULL AUTO_INCREMENT,
  `id_cell` INT NULL,
  `id_cell_clustering` INT NULL,
  `id_cell_cluster` INT NULL,
  PRIMARY KEY (`id_cell_cluster_membership`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
