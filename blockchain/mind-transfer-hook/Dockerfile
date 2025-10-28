FROM ubuntu:22.04
SHELL ["/bin/bash", "-lc"]

# deps
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  curl ca-certificates build-essential pkg-config libssl-dev git \
  nodejs npm python3 jq && rm -rf /var/lib/apt/lists/*

# rust (pin 1.79.0)
ARG RUST=1.79.0
RUN curl -sSf https://sh.rustup.rs | bash -s -- -y --default-toolchain ${RUST}
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustc --version

# solana (pin 1.18.21) — use tarball, no installer
ARG SOLANA=1.18.21
RUN curl -sSfL --retry 5 https://release.solana.com/v${SOLANA}/solana-release-x86_64-unknown-linux-gnu.tar.bz2 \
    -o /tmp/solana.tar.bz2 && \
    apt-get update && apt-get install -y bzip2 && \
    tar -xjf /tmp/solana.tar.bz2 -C /tmp && \
    mv /tmp/solana-release/solana/* /usr/local/bin/ && \
    rm -rf /tmp/solana* && \
    solana --version && which cargo-build-bpf

# anchor (pin 0.29.0)
RUN cargo install --locked --version 0.29.0 anchor-cli
RUN anchor --version

# optional: transfer-hook cli
RUN cargo install --locked spl-transfer-hook-cli || true

WORKDIR /work
