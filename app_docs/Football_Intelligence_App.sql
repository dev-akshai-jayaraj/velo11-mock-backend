CREATE TABLE "home_clubs" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "short_name" varchar,
  "logo_url" varchar,
  "country" varchar,
  "timezone" varchar,
  "primary_color" varchar,
  "secondary_color" varchar,
  "home_venue_id" uuid,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "home_club_id" uuid NOT NULL,
  "first_name" varchar NOT NULL,
  "last_name" varchar,
  "email" varchar UNIQUE NOT NULL,
  "password_hash" varchar NOT NULL,
  "phone" varchar,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "last_login_at" timestamp,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "roles" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "code" varchar UNIQUE NOT NULL,
  "description" text,
  "is_system_role" boolean NOT NULL DEFAULT false,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "permissions" (
  "id" uuid PRIMARY KEY,
  "module_code" varchar NOT NULL,
  "action_code" varchar NOT NULL,
  "name" varchar NOT NULL,
  "description" text,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "user_roles" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "role_id" uuid NOT NULL,
  "assigned_at" timestamp NOT NULL,
  "assigned_by" uuid
);

CREATE TABLE "role_permissions" (
  "id" uuid PRIMARY KEY,
  "role_id" uuid NOT NULL,
  "permission_id" uuid NOT NULL,
  "created_at" timestamp NOT NULL
);

CREATE TABLE "own_teams" (
  "id" uuid PRIMARY KEY,
  "home_club_id" uuid NOT NULL,
  "name" varchar NOT NULL,
  "short_name" varchar,
  "team_type" varchar,
  "gender" varchar,
  "age_group" varchar,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "venues" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "country" varchar,
  "city" varchar,
  "address" text,
  "surface_type" varchar,
  "capacity" int,
  "is_home_venue" boolean NOT NULL DEFAULT false,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "seasons" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "start_date" date,
  "end_date" date,
  "is_active" boolean NOT NULL DEFAULT false,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "competitions" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "type" varchar,
  "country" varchar,
  "level" varchar,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "player_positions" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "code" varchar UNIQUE NOT NULL,
  "position_group" varchar,
  "display_order" int,
  "status" varchar NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "system_modules" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "code" varchar UNIQUE NOT NULL,
  "description" text,
  "is_active" boolean NOT NULL DEFAULT true,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "approval_workflows" (
  "id" uuid PRIMARY KEY,
  "module_id" uuid NOT NULL,
  "name" varchar NOT NULL,
  "code" varchar NOT NULL,
  "is_required" boolean NOT NULL DEFAULT false,
  "is_active" boolean NOT NULL DEFAULT true,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "approval_stages" (
  "id" uuid PRIMARY KEY,
  "workflow_id" uuid NOT NULL,
  "name" varchar NOT NULL,
  "stage_order" int NOT NULL,
  "approval_type" varchar NOT NULL DEFAULT 'ANY',
  "is_final_stage" boolean NOT NULL DEFAULT false,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "approval_stage_approvers" (
  "id" uuid PRIMARY KEY,
  "approval_stage_id" uuid NOT NULL,
  "role_id" uuid,
  "user_id" uuid,
  "approver_type" varchar NOT NULL DEFAULT 'ROLE',
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "approval_requests" (
  "id" uuid PRIMARY KEY,
  "workflow_id" uuid NOT NULL,
  "module_id" uuid NOT NULL,
  "record_id" uuid NOT NULL,
  "record_type" varchar NOT NULL,
  "current_status" varchar NOT NULL DEFAULT 'SUBMITTED',
  "current_stage_order" int,
  "submitted_by" uuid NOT NULL,
  "submitted_at" timestamp,
  "completed_at" timestamp,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "approval_actions" (
  "id" uuid PRIMARY KEY,
  "approval_request_id" uuid NOT NULL,
  "approval_stage_id" uuid,
  "action_by" uuid NOT NULL,
  "action" varchar NOT NULL,
  "comments" text,
  "action_at" timestamp NOT NULL
);

CREATE TABLE "audit_logs" (
  "id" uuid PRIMARY KEY,
  "module_code" varchar NOT NULL,
  "record_id" uuid NOT NULL,
  "action" varchar NOT NULL,
  "changed_by" uuid,
  "old_value" jsonb,
  "new_value" jsonb,
  "source_type" varchar NOT NULL DEFAULT 'MANUAL',
  "changed_at" timestamp NOT NULL
);

CREATE INDEX ON "home_clubs" ("name");

CREATE INDEX ON "home_clubs" ("status");

CREATE INDEX ON "users" ("home_club_id");

CREATE UNIQUE INDEX ON "users" ("email");

CREATE INDEX ON "users" ("status");

CREATE UNIQUE INDEX ON "roles" ("code");

CREATE UNIQUE INDEX ON "permissions" ("module_code", "action_code");

CREATE UNIQUE INDEX ON "user_roles" ("user_id", "role_id");

CREATE INDEX ON "user_roles" ("user_id");

CREATE INDEX ON "user_roles" ("role_id");

CREATE UNIQUE INDEX ON "role_permissions" ("role_id", "permission_id");

CREATE INDEX ON "role_permissions" ("role_id");

CREATE INDEX ON "role_permissions" ("permission_id");

CREATE INDEX ON "own_teams" ("home_club_id");

CREATE INDEX ON "own_teams" ("status");

CREATE INDEX ON "venues" ("name");

CREATE INDEX ON "venues" ("city");

CREATE INDEX ON "venues" ("status");

CREATE UNIQUE INDEX ON "seasons" ("name");

CREATE INDEX ON "seasons" ("is_active");

CREATE INDEX ON "seasons" ("status");

CREATE INDEX ON "competitions" ("name");

CREATE INDEX ON "competitions" ("status");

CREATE UNIQUE INDEX ON "player_positions" ("code");

CREATE INDEX ON "player_positions" ("position_group");

CREATE INDEX ON "player_positions" ("status");

CREATE UNIQUE INDEX ON "system_modules" ("code");

CREATE INDEX ON "system_modules" ("is_active");

CREATE UNIQUE INDEX ON "approval_workflows" ("module_id", "code");

CREATE INDEX ON "approval_workflows" ("module_id");

CREATE INDEX ON "approval_workflows" ("is_active");

CREATE UNIQUE INDEX ON "approval_stages" ("workflow_id", "stage_order");

CREATE INDEX ON "approval_stages" ("workflow_id");

CREATE INDEX ON "approval_stage_approvers" ("approval_stage_id");

CREATE INDEX ON "approval_stage_approvers" ("role_id");

CREATE INDEX ON "approval_stage_approvers" ("user_id");

CREATE INDEX ON "approval_requests" ("workflow_id");

CREATE INDEX ON "approval_requests" ("module_id");

CREATE INDEX ON "approval_requests" ("record_id");

CREATE INDEX ON "approval_requests" ("current_status");

CREATE INDEX ON "approval_requests" ("submitted_by");

CREATE INDEX ON "approval_actions" ("approval_request_id");

CREATE INDEX ON "approval_actions" ("approval_stage_id");

CREATE INDEX ON "approval_actions" ("action_by");

CREATE INDEX ON "approval_actions" ("action");

CREATE INDEX ON "audit_logs" ("module_code");

CREATE INDEX ON "audit_logs" ("record_id");

CREATE INDEX ON "audit_logs" ("action");

CREATE INDEX ON "audit_logs" ("changed_by");

CREATE INDEX ON "audit_logs" ("changed_at");

ALTER TABLE "users" ADD FOREIGN KEY ("home_club_id") REFERENCES "home_clubs" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "home_clubs" ADD FOREIGN KEY ("home_venue_id") REFERENCES "venues" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "own_teams" ADD FOREIGN KEY ("home_club_id") REFERENCES "home_clubs" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "user_roles" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "user_roles" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "user_roles" ADD FOREIGN KEY ("assigned_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "role_permissions" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "role_permissions" ADD FOREIGN KEY ("permission_id") REFERENCES "permissions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_workflows" ADD FOREIGN KEY ("module_id") REFERENCES "system_modules" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_stages" ADD FOREIGN KEY ("workflow_id") REFERENCES "approval_workflows" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_stage_approvers" ADD FOREIGN KEY ("approval_stage_id") REFERENCES "approval_stages" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_stage_approvers" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_stage_approvers" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_requests" ADD FOREIGN KEY ("workflow_id") REFERENCES "approval_workflows" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_requests" ADD FOREIGN KEY ("module_id") REFERENCES "system_modules" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_requests" ADD FOREIGN KEY ("submitted_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_actions" ADD FOREIGN KEY ("approval_request_id") REFERENCES "approval_requests" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_actions" ADD FOREIGN KEY ("approval_stage_id") REFERENCES "approval_stages" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "approval_actions" ADD FOREIGN KEY ("action_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "audit_logs" ADD FOREIGN KEY ("changed_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
