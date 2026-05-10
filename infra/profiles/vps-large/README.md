# Profile · VPS Large

**Target**: 8 vCPU, 32 GB RAM, optional 12+ GB GPU.
**Users**: small team 10-20.
**LLM**: local `qwen2.5:14b` Q4 (GPU) + cloud `claude-sonnet-4-6`.

| Service | CPUs | Memory |
|---------|------|--------|
| server | 4.0 | 4 GB |
| postgres | 4.0 | 16 GB |
| redis | 1.0 | 768 MB |
| qdrant | 2.0 | 6 GB |
| pgbouncer | 0.5 | 256 MB |

PgBouncer is added at this scale (transaction pooling: 200 client conns
multiplexed onto 20 real Postgres conns).
