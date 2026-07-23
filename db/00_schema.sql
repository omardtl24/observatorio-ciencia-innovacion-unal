-- ==========================
-- ROLES & USERS
-- ==========================

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE users (
    email VARCHAR(120) PRIMARY KEY,
    names VARCHAR(120) NOT NULL,
    last_names VARCHAR(120) NOT NULL,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);


-- ==========================
-- CENTRALIZED FILE STORAGE
-- ==========================

CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,  -- e.g. /srv/resources/data_sources/myfile.csv
    file_type TEXT,              -- csv, sql, pdf, etc.
    size_bytes BIGINT,
    checksum_sha256 TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- ==========================
-- MAIN RESOURCES
-- ==========================

CREATE TABLE simulators (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    from_file BOOLEAN NOT NULL DEFAULT TRUE,
    simulator_url TEXT,
    specs_file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE visors (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    from_file BOOLEAN NOT NULL DEFAULT TRUE,
    visor_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    document_file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE documents_presentations (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);


-- ==========================
-- DATA SOURCES & LINKS
-- ==========================

CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE RESTRICT,  -- currently published version
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);

-- historic of every file ever published under a data source (many-to-many)
CREATE TABLE data_source_files (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE RESTRICT,
    published_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (data_source_id, file_id)
);

-- data sources used by reports
CREATE TABLE report_data_sources (
    report_id INTEGER REFERENCES reports(id),
    data_source_id INTEGER REFERENCES data_sources(id),
    PRIMARY KEY (report_id, data_source_id)
);

-- data sources used by visors
CREATE TABLE visor_data_sources (
    visor_id INTEGER REFERENCES visors(id),
    data_source_id INTEGER REFERENCES data_sources(id),
    PRIMARY KEY (visor_id, data_source_id)
);

-- data sources used by simulators
CREATE TABLE simulator_data_sources (
    simulator_id INTEGER REFERENCES simulators(id),
    data_source_id INTEGER REFERENCES data_sources(id),
    PRIMARY KEY (simulator_id, data_source_id)
);

-- ==========================
-- ROLE-BASED ACCESS CONTROL
-- ==========================

CREATE TABLE role_reports (
    role_id INTEGER REFERENCES roles(id),
    report_id INTEGER REFERENCES reports(id),
    PRIMARY KEY (role_id, report_id)
);

CREATE TABLE role_visors (
    role_id INTEGER REFERENCES roles(id),
    visor_id INTEGER REFERENCES visors(id),
    PRIMARY KEY (role_id, visor_id)
);

CREATE TABLE role_simulators (
    role_id INTEGER REFERENCES roles(id),
    simulator_id INTEGER REFERENCES simulators(id),
    PRIMARY KEY (role_id, simulator_id)
);

CREATE TABLE role_data_sources (
    role_id INTEGER REFERENCES roles(id),
    data_source_id INTEGER REFERENCES data_sources(id),
    PRIMARY KEY (role_id, data_source_id)
);

CREATE TABLE user_roles (
    email VARCHAR(120) REFERENCES users(email) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (email, role_id)
);

CREATE TABLE role_documents_presentations (
    role_id INTEGER REFERENCES roles(id),
    documents_presentation_id INTEGER REFERENCES documents_presentations(id),
    PRIMARY KEY (role_id, documents_presentation_id)
);

ALTER DATABASE observatorio
SET timezone TO 'America/Bogota';