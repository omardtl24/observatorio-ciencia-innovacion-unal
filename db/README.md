# Database schema

This document summarizes the database schema used in the web application

## Entities & attributes

The main entities and their attributes (concise) — relationship/join tables are omitted here and described in the Relationships section below.

| Table            | Description |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **roles**        | Stores each system role with a unique ID, name, optional description, and timestamps for creation and updates.                         |
| **users**        | Stores each user identified by email, including their names, assigned role, login history, and creation/update timestamps.             |
| **files**        | Stores information about every file saved on the server, including filename, storage path, type, size, checksum, and upload timestamp. |
| **simulators**   | Stores each simulator with a name, description, and an optional reference to a specification file.                                     |
| **visors**       | Stores each visor with a name, description, type (`bi` or `looker`), and an optional URL link.                                         |
| **reports**      | Stores each report with a name, description, and an optional reference to a document file.                                             |
| **data_sources** | Stores each data source with a name, description, a required reference to a stored file, and timestamps for creation and updates.      |


## Relationships (concise)

- users -> roles: Many users belong to one role via `users.role_id` → `roles.id`.
- files -> simulators/reports/data_sources: Resources attach files via `specs_file_id`, `document_file_id`, and `file_id` referencing `files.id`.
- data_sources ↔ reports/visors/simulators: Many-to-many links via `report_data_sources`, `visor_data_sources`, and `simulator_data_sources`.
- roles ↔ reports/visors/simulators: Access control through `role_reports`, `role_visors`, and `role_simulators` join tables.
- Integrity note: `data_sources.file_id` is `ON DELETE RESTRICT`, preventing deletion of a `files` row while referenced by a data source.

## Conventions & notes

- Most main tables use `SERIAL` integer primary keys.
- `users.email` is used as the primary key for `users` (not an integer id).
- Composite primary keys in join tables enforce uniqueness of links.
- Timestamps commonly default to `NOW()` (`created_at`, `uploaded_at`).
- `visors.type` is constrained by a CHECK to the values `bi` or `looker`.

## E‑R diagram

![E-R diagram](er_diagram.png)

