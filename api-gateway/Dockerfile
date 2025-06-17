FROM kong:3.4

# Copy Kong configuration
COPY kong.yml /opt/kong/kong.yml

# Set environment variables
ENV KONG_DATABASE=postgres
ENV KONG_PG_HOST=kong-postgres
ENV KONG_PG_USER=kong
ENV KONG_PG_PASSWORD=kong
ENV KONG_DECLARATIVE_CONFIG=/opt/kong/kong.yml
ENV KONG_PROXY_ACCESS_LOG=/dev/stdout
ENV KONG_ADMIN_ACCESS_LOG=/dev/stdout
ENV KONG_PROXY_ERROR_LOG=/dev/stderr
ENV KONG_ADMIN_ERROR_LOG=/dev/stderr
ENV KONG_ADMIN_LISTEN=0.0.0.0:8001

EXPOSE 8000 8001 8443 8444

CMD ["kong", "start", "--vv"]