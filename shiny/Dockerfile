FROM rocker/shiny:latest

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    cmake \
    build-essential \
    git \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# renv
RUN R -e "install.packages('renv', repos='https://cloud.r-project.org')"

# === renv cache (SAFE for Docker volume) ===
ENV RENV_PATHS_CACHE=/renv/cache
ENV RENV_CONFIG_CACHE_ENABLED=true
ENV RENV_CONFIG_SANDBOX_ENABLED=false

# site library FIX (IMPORTANT)
ENV R_LIBS_USER=/usr/local/lib/R/site-library

# Create required directories
RUN mkdir -p /renv/cache /usr/local/lib/R/site-library /scripts

# Copy restore script
COPY restore_app.sh /scripts/restore_app.sh

# Make script executable
RUN chmod +x /scripts/restore_app.sh

# entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3838

ENTRYPOINT ["/entrypoint.sh"]