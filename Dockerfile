FROM r-base

WORKDIR /usr/src/app

COPY assets/pi_sim.R assets/Rprofile.site.in ./

Run apt-get update && apt-get -y install redis-tools

RUN cat > /etc/R/Rprofile.site << Rprofile.site.in

RUN chmod ugo+x pi_sim.R
