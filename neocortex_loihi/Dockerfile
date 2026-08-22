# NeoCortex Loihi - deployed independently from the RunPod GPU image.
#
# This image runs the NumPy fallback backend. NxSDK is not publicly
# installable and needs Intel INRC membership plus physical board access,
# so to drive real Loihi hardware rebuild this on the INRC base image and
# uncomment nxsdk in requirements_loihi.txt. The servers auto-detect the
# board at startup and report the active backend on /health.

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_loihi.txt .
RUN pip install --no-cache-dir -r requirements_loihi.txt

# Brain model
COPY core ./core
COPY embodiment ./embodiment
COPY brain_loihi.py .
COPY loihi_hardware_init.py .

# Shared server pieces (schemas, target mapping)
COPY server_support ./server_support

# Entrypoints and everything they import
COPY server ./server
COPY drug_simulator_loihi.py .
COPY drug_discovery_loihi.py .
COPY docking_utils.py .
COPY molecular_generator_ai.py .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 8001

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOIHI_SERVER_PORT=8000
ENV DISCOVERY_SERVER_PORT=8001

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
