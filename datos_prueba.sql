-- =====================================================================
-- Datos de prueba - Club Deportivo Encuentro
-- ---------------------------------------------------------------------
-- Requiere: haber corrido init_db.sql (tablas creadas).
-- Uso:      sudo mysql < datos_sql.sql
--
-- El script BORRA las canchas, socios y reservas existentes y vuelve a
-- cargar estos datos, así siempre se prueba desde el mismo punto de
-- partida.
--
-- Fechas: "pasadas" y "futuras" están pensadas respecto de fines de
-- septiembre de 2026. Si prueban después del 15/10/2026, corran las
-- fechas futuras hacia adelante.
--
-- IMPORTANTE: init_db.sql usa CREATE TABLE IF NOT EXISTS. Si la base se
-- creó con el esquema viejo de reservas (fecha / hora_inicio /
-- hora_final), hay que borrarla y recrearla antes:
--   sudo mysql -e "DROP DATABASE club_deportivo;"
--   sudo mysql < init_db.sql
-- =====================================================================

USE club_deportivo;

-- ---------------------------------------------------------------------
-- Deportes (idealmente viven en init_db.sql; INSERT IGNORE evita
-- errores si ya están cargados)
-- ---------------------------------------------------------------------
INSERT IGNORE INTO deportes (id_deporte, nombre, cantidad_jugadores) VALUES
    (1, 'Fútbol', 10),
    (2, 'Tenis', 2),
    (3, 'Pádel', 4);

-- ---------------------------------------------------------------------
-- Limpieza (TRUNCATE además reinicia los AUTO_INCREMENT)
-- ---------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE reservas;
TRUNCATE TABLE canchas;
TRUNCATE TABLE socios;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- Canchas (12 en total: con el _limit por defecto de 10 hay 2 páginas)
-- Deportes: 1 = Fútbol, 2 = Tenis, 3 = Pádel
-- Precios en centavos: 1000000 = $10.000,00
-- precio_reserva se omite (queda NULL)
-- ---------------------------------------------------------------------
INSERT INTO canchas (id_cancha, nombre, id_deporte, precio_hora, techada, activa) VALUES
    (1,  'Cancha 1 - Fútbol 5',          1, 1000000, FALSE, TRUE),   -- tiene reservas -> DELETE da 409
    (2,  'Cancha 2 - Fútbol 5 Techada',  1, 1000000, TRUE,  TRUE),
    (3,  'Cancha 3 - Fútbol 7',          1, 1500000, FALSE, TRUE),   -- sin reservas
    (4,  'Cancha 4 - Fútbol 11',         1, 2500000, FALSE, FALSE),  -- INACTIVA, con una reserva vigente
    (5,  'Tenis 1 - Polvo de ladrillo',  2,  800000, FALSE, TRUE),
    (6,  'Tenis 2 - Cemento',            2,  700000, FALSE, TRUE),   -- sin reservas
    (7,  'Tenis 3 - Cubierta',           2,  900000, TRUE,  TRUE),   -- sin reservas
    (8,  'Tenis 4 - Cemento',            2,  700000, FALSE, FALSE),  -- INACTIVA, sin reservas
    (9,  'Pádel 1 - Techada',            3,  600000, TRUE,  TRUE),
    (10, 'Pádel 2 - Techada',            3,  600000, TRUE,  TRUE),   -- sin reservas
    (11, 'Pádel 3',                      3,  550000, FALSE, TRUE),   -- sin reservas
    (12, 'Pádel 4',                      3,  550000, FALSE, TRUE);   -- sin reservas -> DELETE da 204

-- ---------------------------------------------------------------------
-- Socios (la columna de habilitación se llama 'estado' en la tabla)
-- ---------------------------------------------------------------------
INSERT INTO socios (id_socio, nombre, email, estado) VALUES
    (1, 'Juan Pérez',       'juan.perez@example.com',       TRUE),
    (2, 'María González',   'maria.gonzalez@example.com',   TRUE),
    (3, 'Lucas Fernández',  'lucas.fernandez@example.com',  TRUE),
    (4, 'Sofía Martínez',   'sofia.martinez@example.com',   FALSE),  -- INACTIVA, con una reserva vigente
    (5, 'Diego Romero',     'diego.romero@example.com',     TRUE);

-- ---------------------------------------------------------------------
-- Reservas
-- Horarios en GMT-3, guardados sin zona horaria.
-- tarifa_historica = precio por hora al momento de reservar
-- total = horas * tarifa_historica
-- ---------------------------------------------------------------------
INSERT INTO reservas
    (id, id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, estado, tarifa_historica, total)
VALUES
    -- Futuras, cancha 1 el 15/10: 18-20 y 20-21 son consecutivas (válidas)
    -- La #1 se reservó a 900000/h (total 1800000) aunque hoy la cancha cuesta 1000000
    (1,  1, 1, '2026-10-15 18:00:00', '2026-10-15 20:00:00', 'confirmada', 900000,  1800000),
    (2,  1, 2, '2026-10-15 20:00:00', '2026-10-15 21:00:00', 'confirmada', 1000000, 1000000),
    -- Cancelada: el horario 16-18 de la cancha 1 queda libre
    (3,  1, 3, '2026-10-15 16:00:00', '2026-10-15 18:00:00', 'cancelada',  1000000, 2000000),

    -- Otras futuras confirmadas
    (4,  5, 1, '2026-10-16 10:00:00', '2026-10-16 11:00:00', 'confirmada', 800000,  800000),
    (5,  9, 2, '2026-10-16 19:00:00', '2026-10-16 22:00:00', 'confirmada', 600000,  1800000),

    -- Pasadas: finalizada, confirmada (se puede pasar a finalizada con PUT) y cancelada
    (6,  2, 1, '2026-09-10 18:00:00', '2026-09-10 20:00:00', 'finalizada', 950000,  1900000),
    (7,  2, 3, '2026-09-20 21:00:00', '2026-09-20 22:00:00', 'confirmada', 1000000, 1000000),
    (8,  9, 5, '2026-09-15 09:00:00', '2026-09-15 10:00:00', 'cancelada',  600000,  600000),

    -- Desactivar no cancela lo existente: socio inactivo y cancha inactiva con reservas vigentes
    (9,  5, 4, '2026-10-20 08:00:00', '2026-10-20 09:00:00', 'confirmada', 800000,  800000),
    (10, 4, 5, '2026-10-18 11:00:00', '2026-10-18 13:00:00', 'confirmada', 2500000, 5000000);

-- ---------------------------------------------------------------------
-- Verificación rápida (debería dar 3 / 12 / 5 / 10)
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM deportes) AS deportes,
    (SELECT COUNT(*) FROM canchas)  AS canchas,
    (SELECT COUNT(*) FROM socios)   AS socios,
    (SELECT COUNT(*) FROM reservas) AS reservas;