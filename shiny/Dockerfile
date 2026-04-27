FROM rocker/shiny:latest

RUN R -e "install.packages('renv', repos='https://cloud.r-project.org')"

ENV RENV_PATHS_CACHE=/renv/cache

RUN mkdir -p /renv/cache

EXPOSE 3838

CMD ["/usr/bin/shiny-server"]