# shared by local docker-compose (which overrides the command per service,
# so this file's default CMD is ignored locally) and HF Spaces (which uses
# this file's default CMD directly, since it only runs one container).
#
# runs as a non-root user - HF Spaces' documented convention for Docker
# Spaces, and just genuinely better practice than running everything as root.

FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .
RUN chmod +x start.sh

USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH

EXPOSE 7860

# default command - what HF Spaces actually runs. docker-compose.yml
# overrides this per-service for local dev instead.
CMD ["./start.sh"]
