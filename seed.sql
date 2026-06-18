-- ============================================================
--  Canchas Deportivas — DDL + Seed Data para PostgreSQL
--  Refleja exactamente models.py (SQLAlchemy)
-- ============================================================

-- ── Limpieza segura (útil al re-ejecutar durante desarrollo) ──
DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS canchas  CASCADE;

-- ── Tabla: canchas ────────────────────────────────────────────
CREATE TABLE canchas (
    id               SERIAL        PRIMARY KEY,
    nombre           VARCHAR       NOT NULL,
    tipo             VARCHAR       NOT NULL,
    precio_por_hora  FLOAT         NOT NULL,
    imagen_url       VARCHAR       DEFAULT '',
    esta_disponible  BOOLEAN       DEFAULT TRUE
);

-- ── Tabla: reservas ───────────────────────────────────────────
CREATE TABLE reservas (
    id              SERIAL   PRIMARY KEY,
    cancha_id       INTEGER  NOT NULL
                             REFERENCES canchas(id)
                             ON DELETE CASCADE,
    fecha           DATE     NOT NULL,
    hora_inicio     TIME     NOT NULL,
    hora_fin        TIME     NOT NULL,
    nombre_cliente  VARCHAR  NOT NULL,
    total           FLOAT
);

-- ── Índices útiles ────────────────────────────────────────────
CREATE INDEX idx_reservas_cancha_fecha
    ON reservas (cancha_id, fecha);

-- ==============================================================
--  SEED DATA
-- ==============================================================

-- ── 4 Canchas con diferentes tipos, precios y estados ─────────
INSERT INTO canchas (nombre, tipo, precio_por_hora, imagen_url, esta_disponible)
VALUES
    (
        'Cancha Central Grass',
        'Fútbol',
        80.00,
        'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800',
        TRUE
    ),
    (
        'Court Rojo Tenis',
        'Tenis',
        60.00,
        'https://images.unsplash.com/photo-1542144612-1b2e9d4b4c0a?w=800',
        TRUE
    ),
    (
        'Cancha Básquet Techada',
        'Básquet',
        50.00,
        'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800',
        TRUE
    ),
    (
        'Cancha Fútbol 7 Norte',
        'Fútbol',
        70.00,
        'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=800',
        FALSE   -- en mantenimiento; no admite nuevas reservas
    );

-- ── 5 Reservas sin traslape, fechas 2026 en adelante ──────────
--
--  Cancha 1 — "Cancha Central Grass"  (precio: S/. 80/hr)
--    Reserva A: 2026-07-10  08:00–10:00  (2 h × 80 = S/. 160)
--    Reserva B: 2026-07-10  14:00–16:00  (2 h × 80 = S/. 160)  ← mismo día, sin traslape
--
--  Cancha 2 — "Court Rojo Tenis"      (precio: S/. 60/hr)
--    Reserva C: 2026-07-12  09:00–10:00  (1 h × 60 = S/.  60)
--
--  Cancha 3 — "Cancha Básquet Techada" (precio: S/. 50/hr)
--    Reserva D: 2026-08-05  16:00–18:00  (2 h × 50 = S/. 100)
--    Reserva E: 2026-08-05  10:00–12:00  (2 h × 50 = S/. 100)  ← mismo día, distinto bloque

INSERT INTO reservas (cancha_id, fecha, hora_inicio, hora_fin, nombre_cliente, total)
VALUES
    -- Reserva A
    (1, '2026-07-10', '08:00:00', '10:00:00', 'Carlos Ramírez',   160.00),
    -- Reserva B (mismo día que A pero en bloque diferente → sin colisión)
    (1, '2026-07-10', '14:00:00', '16:00:00', 'Sofía Mendoza',    160.00),
    -- Reserva C
    (2, '2026-07-12', '09:00:00', '10:00:00', 'Andrés Torres',     60.00),
    -- Reserva D
    (3, '2026-08-05', '16:00:00', '18:00:00', 'Lucía Paredes',    100.00),
    -- Reserva E (mismo día que D, bloque mañana → sin colisión)
    (3, '2026-08-05', '10:00:00', '12:00:00', 'Miguel Quispe',    100.00);

-- ── Verificación rápida ───────────────────────────────────────
SELECT
    r.id,
    c.nombre          AS cancha,
    r.fecha,
    r.hora_inicio,
    r.hora_fin,
    r.nombre_cliente,
    r.total
FROM reservas r
JOIN canchas  c ON c.id = r.cancha_id
ORDER BY r.cancha_id, r.fecha, r.hora_inicio;
