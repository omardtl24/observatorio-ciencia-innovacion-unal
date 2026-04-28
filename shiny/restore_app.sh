#!/bin/bash
set -e

APP_ID="$1"
BASE_DIR="/srv/shiny-server"
APP_PATH="$BASE_DIR/$APP_ID"

# Validate input parameter
if [ -z "$APP_ID" ]; then
  echo "❌ Error: you must provide the app ID"
  exit 1
fi

# Check if app directory exists
if [ ! -d "$APP_PATH" ]; then
  echo "❌ Error: app does not exist at $APP_PATH"
  exit 1
fi

echo "➡️ Processing app: $APP_PATH"

LOCK_FILE="$APP_PATH/renv.lock"
DONE_MARK="$APP_PATH/.renv_restored"
LOCK_MARK="$APP_PATH/.restore.lock"

# Prevent concurrent restores
if [ -f "$LOCK_MARK" ]; then
  echo "⏳ Restore already in progress for $APP_ID, exiting..."
  exit 0
fi

# Skip if already restored
if [ -f "$DONE_MARK" ]; then
  echo "✅ Already restored: $APP_ID"
  exit 0
fi

# Run restore only if renv.lock exists
if [ -f "$LOCK_FILE" ]; then
  echo "📦 renv.lock found → restoring $APP_ID"

  touch "$LOCK_MARK"

  Rscript -e "
    setwd('$APP_PATH')

    # Ensure stable library path
    .libPaths(Sys.getenv('R_LIBS_USER'))

    # Configure renv cache
    Sys.setenv(RENV_PATHS_CACHE = Sys.getenv('RENV_PATHS_CACHE'))
    Sys.setenv(RENV_CONFIG_CACHE_ENABLED = 'TRUE')

    renv::restore(
      prompt = FALSE,
      clean = FALSE,
      rebuild = FALSE
    )
  "

  rm -f "$LOCK_MARK"
  touch "$DONE_MARK"

  echo "✅ Restore completed: $APP_ID"

else
  echo "⚠️ No renv.lock → skipping $APP_ID"
fi