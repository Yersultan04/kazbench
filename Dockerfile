FROM python:3.11-slim

LABEL maintainer="KazBench" \
      description="KazBench evaluation harness — reproducible offline smoke run"

# Working directory inside the container
WORKDIR /kazbench

# Copy the entire repo (respects .dockerignore if present)
COPY . .

# No pip install needed for the dummy model — pure stdlib harness.
# Install pytest only so the image can also be used to run the test suite.
RUN pip install --no-cache-dir pytest==8.2.2

# Output directory
RUN mkdir -p results

# Default command: run the offline dummy eval end-to-end.
# Override with:
#   docker run kazbench python -m pytest tests/ -v
CMD ["python", "-m", "harness.run_eval", \
     "--model", "dummy", \
     "--split", "dev", \
     "--out",   "results/dummy.json"]
