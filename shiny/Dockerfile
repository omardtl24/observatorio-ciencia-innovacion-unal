FROM rocker/shiny:latest

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

# Verify cmake is installed (fails build if not)
RUN cmake --version

RUN R -e "install.packages('renv', repos='https://cloud.r-project.org')"

ENV RENV_PATHS_CACHE=/renv/cache
ENV RENV_CONFIG_SANDBOX_ENABLED=FALSE
ENV RENV_CONFIG_USE_CACHE=TRUE

RUN mkdir -p /renv/cache && chmod -R 777 /renv

EXPOSE 3838

CMD ["/usr/bin/shiny-server"]