# ====== Builder stage ======
FROM ubuntu:22.04 AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG LIBFREENECT_BRANCH=master

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates cmake git python3 python3-dev python3-pip python3-numpy \
    pkg-config \
    libusb-1.0-0-dev freeglut3-dev libxmu-dev libxi-dev libgl1-mesa-dev libglfw3-dev \
  && rm -rf /var/lib/apt/lists/*

# Install a known stable Cython version (optional pinning)
RUN pip3 install cython==0.29.33

WORKDIR /opt
RUN git clone --depth=1 --branch ${LIBFREENECT_BRANCH} https://github.com/OpenKinect/libfreenect.git

WORKDIR /opt/libfreenect/build
RUN cmake -DBUILD_EXAMPLES=ON -DBUILD_FAKENECT=OFF -DBUILD_OPENNI2_DRIVER=OFF -DBUILD_PYTHON_WRAPPER=ON ..
RUN cmake --build . --config Release -j$(nproc)
RUN cmake --install .
RUN ldconfig

WORKDIR /opt/libfreenect/wrappers/python

RUN ls -l /opt/libfreenect/wrappers/python

# Patch setup.py to fix deprecated cython version call
RUN sed -i 's/Cython.Compiler.Main.Version.version/Cython.__version__/g' setup.py && \
    sed -i 's/Cython.Compiler.Main.version/Cython.__version__/g' setup.py

# Generate C sources from .pyx
RUN cython freenect.pyx

# Build python extension in place
RUN python3 setup.py build_ext --inplace

RUN ls -l /opt/libfreenect/wrappers/python/freenect*.so

# Install the python extension into site-packages
RUN python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")') \
    && mkdir -p /usr/local/lib/python${python_version}/dist-packages/freenect \
    && cp /opt/libfreenect/wrappers/python/freenect*.so /usr/local/lib/python${python_version}/dist-packages/freenect/ \
    && touch /usr/local/lib/python${python_version}/dist-packages/freenect/__init__.py

# ====== Runtime stage ======
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 freeglut3 libxmu6 libxi6 libgl1 libglfw3 udev \
    python3 python3-pip python3-numpy python3-venv \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /opt/libfreenect/platform/linux/udev/51-kinect.rules /etc/udev/rules.d/51-kinect.rules
# optional, remove if not needed
COPY --from=builder /opt/libfreenect /opt/libfreenect  

# Add /usr/local/lib to linker config
RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/libfreenect.conf && ldconfig

RUN getent group plugdev || groupadd -r plugdev \
 && useradd -m -g plugdev devuser

USER devuser
WORKDIR /home/devuser

CMD ["bash"]