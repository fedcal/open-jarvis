#!/usr/bin/env python3
"""Open-Jarvis sizing calculator.

Given hardware (RAM, CPU, optional GPU VRAM, expected users), prints
the recommended configuration values for the FastAPI server, Postgres,
Redis, Qdrant, the LLM router and Docker Compose deploy.resources.

Numbers and rationale are documented in
`docs/it/operations/resource-management.md`.

Usage:
    uv run scripts/sizing.py --ram 16 --cpu 4 --users 5

Optional `--profile-out infra/profiles/<name>` writes a complete profile
directory mirroring the structure of `infra/profiles/home/`.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


@dataclass(frozen=True)
class SizingInputs:
    ram_gb: int
    cpu: int
    users: int
    gpu_vram_gb: int
    pure_async: bool
    memory_vectors: int
    vector_dim: int


@dataclass(frozen=True)
class SizingReport:
    profile: str
    workers: int
    pool_size: int
    max_overflow: int
    pg_shared_buffers_mb: int
    pg_effective_cache_mb: int
    pg_work_mem_mb: int
    pg_maintenance_work_mem_mb: int
    pg_max_connections: int
    redis_maxmemory_mb: int
    qdrant_quantization: str
    qdrant_ram_mb: int
    llm_local: str | None
    llm_cloud: str
    ollama_num_parallel: int
    server_cpu_limit: float
    server_mem_limit_mb: int
    postgres_cpu_limit: float
    postgres_mem_limit_mb: int
    redis_cpu_limit: float
    redis_mem_limit_mb: int
    qdrant_cpu_limit: float
    qdrant_mem_limit_mb: int


def detect_profile(inp: SizingInputs) -> str:
    """Return the closest pre-built profile name."""
    if inp.ram_gb <= 8 and inp.cpu <= 2:
        return "vps-small"
    if inp.ram_gb <= 12 and inp.cpu <= 4:
        return "vps-medium"
    if inp.ram_gb <= 24 and inp.cpu <= 6:
        return "vps-medium"
    if inp.ram_gb >= 24 and inp.cpu >= 8:
        return "vps-large"
    return "home"


def workers(inp: SizingInputs) -> int:
    """Async-aware worker count."""
    if inp.pure_async:
        if inp.cpu <= 2:
            return min(2, inp.cpu)
        return min(inp.cpu, max(2, inp.cpu // 2 + 1))
    return min(2 * inp.cpu + 1, 12)


def llm_recommendation(inp: SizingInputs) -> tuple[str | None, str]:
    """Return (local_model_or_None, cloud_fallback_model)."""
    cloud = "anthropic/claude-haiku-4-5-20251001"
    if inp.gpu_vram_gb >= 24:
        return ("ollama/qwen2.5:14b", "anthropic/claude-sonnet-4-6")
    if inp.gpu_vram_gb >= 8:
        return ("ollama/llama3.1:8b", cloud)
    if inp.gpu_vram_gb >= 4:
        return ("ollama/llama3.2:3b", cloud)
    if inp.ram_gb >= 12:
        return ("ollama/llama3.2:3b", cloud)
    return (None, cloud)


def qdrant_ram_mb(num_vectors: int, dim: int) -> tuple[int, int, str]:
    """Return (float32_mb, int8_mb, recommendation)."""
    overhead = 1.5
    f32 = math.ceil(num_vectors * dim * 4 * overhead / 1024 / 1024)
    i8 = math.ceil(num_vectors * dim * 1 * overhead / 1024 / 1024)
    if dim >= 1024 and num_vectors >= 1_000_000:
        rec = "binary"
    else:
        rec = "int8"
    return f32, i8, rec


def compute(inp: SizingInputs) -> SizingReport:
    profile = detect_profile(inp)

    # PG ratio: 25% RAM dedicated to Postgres
    pg_ram_mb = max(int(inp.ram_gb * 1024 * 0.25), 512)
    if profile == "vps-large":
        pg_ram_mb = int(inp.ram_gb * 1024 * 0.5)

    pg_max_conn = max(25, min(200, inp.users * 20))
    work_mem_mb = max(8, min(64, pg_ram_mb // pg_max_conn))

    # Qdrant
    f32, i8, qrec = qdrant_ram_mb(inp.memory_vectors, inp.vector_dim)

    # LLM
    local, cloud = llm_recommendation(inp)

    return SizingReport(
        profile=profile,
        workers=workers(inp),
        pool_size=max(3, min(10, inp.users * 2)),
        max_overflow=10,
        pg_shared_buffers_mb=pg_ram_mb // 4,
        pg_effective_cache_mb=int(pg_ram_mb * 0.75),
        pg_work_mem_mb=work_mem_mb,
        pg_maintenance_work_mem_mb=min(2048, pg_ram_mb // 8),
        pg_max_connections=pg_max_conn,
        redis_maxmemory_mb=128 if inp.ram_gb < 8 else (256 if inp.ram_gb < 24 else 512),
        qdrant_quantization=qrec,
        qdrant_ram_mb=i8 if qrec == "int8" else f32,
        llm_local=local,
        llm_cloud=cloud,
        ollama_num_parallel=max(1, inp.users),
        server_cpu_limit=min(float(inp.cpu) / 2, 4.0),
        server_mem_limit_mb=max(512, min(4096, inp.ram_gb * 64)),
        postgres_cpu_limit=min(float(inp.cpu) / 2, 4.0),
        postgres_mem_limit_mb=pg_ram_mb,
        redis_cpu_limit=0.5 if inp.cpu >= 4 else 0.25,
        redis_mem_limit_mb=128 if inp.ram_gb < 8 else 384,
        qdrant_cpu_limit=min(float(inp.cpu) / 4, 2.0),
        qdrant_mem_limit_mb=max(512, i8 + 256),
    )


def render(inp: SizingInputs, r: SizingReport) -> str:
    return dedent(f"""
        == Open-Jarvis sizing report ==
        Inputs: RAM={inp.ram_gb}GB · CPU={inp.cpu} · users={inp.users} · GPU={inp.gpu_vram_gb}GB VRAM
        Profile match: {r.profile}

        Backend
          workers              : {r.workers}
          pool_size            : {r.pool_size}
          max_overflow         : {r.max_overflow}
          total_pg_connections : {r.workers * (r.pool_size + r.max_overflow)}

        Postgres
          shared_buffers          : {r.pg_shared_buffers_mb}MB
          effective_cache_size    : {r.pg_effective_cache_mb}MB
          work_mem                : {r.pg_work_mem_mb}MB
          maintenance_work_mem    : {r.pg_maintenance_work_mem_mb}MB
          max_connections         : {r.pg_max_connections}

        Redis
          maxmemory               : {r.redis_maxmemory_mb}mb
          maxmemory-policy        : volatile-lru

        Qdrant
          recommended quantization: {r.qdrant_quantization}
          RAM @ {inp.memory_vectors:,} × {inp.vector_dim} dim : ~{r.qdrant_ram_mb} MB

        LLM
          local model    : {r.llm_local or '<<<no local — cloud only>>>'}
          cloud fallback : {r.llm_cloud}
          ollama parallel: {r.ollama_num_parallel}

        Docker compose deploy.resources
          server   cpus={r.server_cpu_limit}  memory={r.server_mem_limit_mb}MB
          postgres cpus={r.postgres_cpu_limit}  memory={r.postgres_mem_limit_mb}MB
          redis    cpus={r.redis_cpu_limit}  memory={r.redis_mem_limit_mb}MB
          qdrant   cpus={r.qdrant_cpu_limit}  memory={r.qdrant_mem_limit_mb}MB

        Tip: copia il profilo più vicino e personalizza:
          cp -r infra/profiles/{r.profile}/ infra/profiles/<your-name>/
    """).strip()


def write_profile(out_dir: Path, inp: SizingInputs, r: SizingReport) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "docker-compose.override.yml").write_text(dedent(f"""\
        # Generated by scripts/sizing.py
        # RAM={inp.ram_gb}GB CPU={inp.cpu} users={inp.users} GPU={inp.gpu_vram_gb}GB
        services:
          postgres:
            command:
              - postgres
              - -c
              - config_file=/etc/postgresql/postgresql.conf
            volumes:
              - ./{out_dir.as_posix()}/postgresql.conf:/etc/postgresql/postgresql.conf:ro
            deploy:
              resources:
                limits:       {{ cpus: "{r.postgres_cpu_limit}", memory: "{r.postgres_mem_limit_mb}M" }}
          redis:
            command:
              - redis-server
              - /usr/local/etc/redis/redis.conf
            volumes:
              - ./{out_dir.as_posix()}/redis.conf:/usr/local/etc/redis/redis.conf:ro
            deploy:
              resources:
                limits:       {{ cpus: "{r.redis_cpu_limit}", memory: "{r.redis_mem_limit_mb}M" }}
          qdrant:
            deploy:
              resources:
                limits:       {{ cpus: "{r.qdrant_cpu_limit}", memory: "{r.qdrant_mem_limit_mb}M" }}
          server:
            deploy:
              resources:
                limits:       {{ cpus: "{r.server_cpu_limit}", memory: "{r.server_mem_limit_mb}M" }}
            command: >
              sh -c "alembic upgrade head &&
                     exec uvicorn jarvis_server.api.main:app
                          --host 0.0.0.0 --port 8080
                          --workers {r.workers} --proxy-headers"
    """))

    (out_dir / "postgresql.conf").write_text(dedent(f"""\
        # Generated by scripts/sizing.py
        listen_addresses = '*'
        max_connections = {r.pg_max_connections}
        shared_buffers = {r.pg_shared_buffers_mb}MB
        effective_cache_size = {r.pg_effective_cache_mb}MB
        work_mem = {r.pg_work_mem_mb}MB
        maintenance_work_mem = {r.pg_maintenance_work_mem_mb}MB
        wal_buffers = 16MB
        checkpoint_completion_target = 0.9
        random_page_cost = 1.1
        effective_io_concurrency = 200
        log_min_duration_statement = 1000
        log_line_prefix = '%m [%p] %q%u@%d '
    """))

    (out_dir / "redis.conf").write_text(dedent(f"""\
        # Generated by scripts/sizing.py
        bind 0.0.0.0
        protected-mode no
        maxmemory {r.redis_maxmemory_mb}mb
        maxmemory-policy volatile-lru
        maxmemory-samples 10
        save 600 100
        appendonly no
    """))

    (out_dir / "README.md").write_text(dedent(f"""\
        # Profile · {out_dir.name} (generated)

        Inputs: RAM={inp.ram_gb}GB · CPU={inp.cpu} · users={inp.users} · GPU={inp.gpu_vram_gb}GB

        | Service | CPUs | Memory |
        |---------|------|--------|
        | server | {r.server_cpu_limit} | {r.server_mem_limit_mb}MB |
        | postgres | {r.postgres_cpu_limit} | {r.postgres_mem_limit_mb}MB |
        | redis | {r.redis_cpu_limit} | {r.redis_mem_limit_mb}MB |
        | qdrant | {r.qdrant_cpu_limit} | {r.qdrant_mem_limit_mb}MB |

        ## Apply

        ```bash
        export COMPOSE_FILE=docker-compose.yml:{out_dir.as_posix()}/docker-compose.override.yml
        docker compose up -d
        ```

        Closest pre-built profile: `{r.profile}`. See full sizing rationale in
        [docs/it/operations/resource-management.md](../../../docs/it/operations/resource-management.md).
    """))


def main() -> None:
    p = argparse.ArgumentParser(
        description="Open-Jarvis sizing calculator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--ram", type=int, required=True, help="GB of RAM")
    p.add_argument("--cpu", type=int, required=True, help="number of vCPUs")
    p.add_argument("--users", type=int, default=1, help="concurrent users")
    p.add_argument("--gpu-vram", type=int, default=0, help="GB of GPU VRAM")
    p.add_argument("--pure-async", action="store_true", default=True,
                   help="app is fully async (default)")
    p.add_argument("--memory-vectors", type=int, default=100_000,
                   help="max user memory items expected")
    p.add_argument("--vector-dim", type=int, default=384,
                   help="embedding dimension")
    p.add_argument("--profile-out", type=Path,
                   help="write a new profile directory")
    args = p.parse_args()

    inp = SizingInputs(
        ram_gb=args.ram,
        cpu=args.cpu,
        users=args.users,
        gpu_vram_gb=args.gpu_vram,
        pure_async=args.pure_async,
        memory_vectors=args.memory_vectors,
        vector_dim=args.vector_dim,
    )
    r = compute(inp)
    print(render(inp, r))

    if args.profile_out:
        write_profile(args.profile_out, inp, r)
        print(f"\nWritten: {args.profile_out}")


if __name__ == "__main__":
    main()
