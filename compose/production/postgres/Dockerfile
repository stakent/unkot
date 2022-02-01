FROM postgres:14.1

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
COPY ./postgresql-fts-polish/polish.* /usr/share/postgresql/14/tsearch_data/
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
