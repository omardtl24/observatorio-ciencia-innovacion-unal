#!/bin/bash
set -e

echo "🔍 Scanning Shiny apps..."

# Search apps inside both target directories
for base in /srv/shiny-server/visor /srv/shiny-server/simulator; do
  if [ -d "$base" ]; then

    for app in "$base"/*; do
      if [ -d "$app" ]; then

        echo "➡️ Checking: $app"

        if [ -f "$app/renv.lock" ]; then
          echo "📦 renv.lock found → restoring $app"

          Rscript -e "
            setwd('$app')

            # IMPORTANT: ensure stable lib path
            .libPaths(Sys.getenv('R_LIBS_USER'))

            # enable cache safely
            Sys.setenv(RENV_PATHS_CACHE = Sys.getenv('RENV_PATHS_CACHE'))
            Sys.setenv(RENV_CONFIG_CACHE_ENABLED = 'TRUE')

            renv::restore(
              prompt = FALSE,
              clean = FALSE,
              rebuild = FALSE
            )
          "

        else
          echo "⚠️ No renv.lock → skipping $app"
        fi

      fi
    done

  else
    echo "⚠️ Directory not found: $base"
  fi
done

echo "🚀 Starting Shiny Server..."
exec /usr/bin/shiny-server