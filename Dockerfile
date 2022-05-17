FROM odoo:14

USER root

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip \
    && pip3 install debugpy \
    && pip3 install -r /tmp/requirements.txt

# this environment vars allows you to connect to postgres
# directly with psql command from this odoo container
ENV PGDATABASE=postgres
ENV PGPASSWORD=odoo
ENV PGUSER=odoo
ENV PGHOST=db

USER odoo
