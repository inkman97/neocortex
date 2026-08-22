FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Brain model package
COPY neocortex_realistico_gpu ./neocortex_realistico_gpu

# Shared server pieces (schemas, target mapping)
COPY server_support ./server_support

# Entrypoints and everything they import
COPY gpu_server.py .
COPY run_discovery.py .
COPY drug_simulator.py .
COPY drug_discovery.py .
COPY docking_utils.py .
COPY molecular_generator_ai.py .
COPY emergent_neuromodulation.py .
COPY neuromodulator_receptors.py .
COPY advanced_plasticity.py .
COPY plasticity_integration.py .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 8001

ENV PYTHONUNBUFFERED=1
ENV GPU_SERVER_PORT=8000
ENV DISCOVERY_SERVER_PORT=8001

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
