CREATE DATABASE IF NOT EXISTS club_deportivo;
USE club_deportivo;

CREATE TABLE IF NOT EXISTS deportes (
    id_deporte INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR (50) NOT NULL,
    cantidad_jugadores INT NOT NULL
);

CREATE TABLE IF NOT EXISTS canchas (
    id_cancha INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL,
    techada BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    precio_reserva INT NOT NULL,
    FOREIGN KEY (id_deporte) REFERENCES deportes(id_deporte)
);

CREATE TABLE IF NOT EXISTS socios (
    id_socio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cancha INT NOT NULL,
    id_socio INT NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin DATETIME(6) NOT NULL,
    estado ENUM('confirmada', 'cancelada', 'finalizada') NOT NULL DEFAULT 'confirmada',
    tarifa_historica INT NOT NULL,
    total INT NOT NULL,
    FOREIGN KEY (id_cancha) REFERENCES canchas(id_cancha),
    FOREIGN KEY (id_socio) REFERENCES socios(id_socio)
);
