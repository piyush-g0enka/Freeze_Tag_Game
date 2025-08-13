FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including libgl1 for OpenCV imshow
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    ca-certificates \
    libglib2.0-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir numpy opencv-python

# Build LCM from source
RUN git clone https://github.com/lcm-proj/lcm.git /tmp/lcm && \
    cd /tmp/lcm && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_JAVA=OFF .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd / && rm -rf /tmp/lcm

# Install Python bindings for LCM
RUN pip install --no-cache-dir lcm

# Copy project files
COPY . .

# Set entrypoint to run the game
ENTRYPOINT ["python3", "game.py"]
