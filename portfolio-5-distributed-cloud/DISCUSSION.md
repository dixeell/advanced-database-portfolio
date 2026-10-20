# Portfolio 5: Distributed and Cloud Database Exercise

Case study: Northgate University Result Portal. Traffic is highly bursty: normal days are light, but **result release day** and **registration deadlines** create sharp peaks, and a read outage during results would be very visible.

## 1. Replication and availability
Primary plus two replicas (see `docker-compose.yml`, **UNTESTED here**). Writes (score entry, registration) go to the primary; transcript reads go to replicas. If the primary fails, a replica is promoted, so the portal stays readable. Streaming replication is asynchronous by default, so a replica can lag. `simulate_distribution.py` shows a grade update invisible on both replicas for ~100 ms.

## 2. Consistency choices (CAP / PACELC)
- **Registration and grade entry: consistency first.** A seat must never be sold twice, so these go to a single primary (or W=2 quorum). During a partition we prefer rejecting writes to accepting conflicting ones.
- **Transcript browsing: availability and latency first.** Slightly stale reads are acceptable; to give a lecturer *read-your-writes* after correcting a grade, route that user's reads to the primary for a short period.
- Quorum rule R + W > N gives strong reads; with N=3, W=2/R=2 tolerates one failure (see simulation).

## 3. Sharding
Shard key candidates compared in the simulation (2,000 students, 3 shards):

| Key | Distribution | Release-day behaviour |
|---|---|---|
| Hash(matric_no) | 737 / 634 / 629 | Newest intake's traffic spreads over all 3 shards |
| Range(entry_year) | 985 / 508 / 507 | Newest intake sits on **one** shard: hot spot |

**Decision:** hash-shard student documents by `matric_no`. Co-locate each student's registrations/results with the student (embedded in the document model), so a transcript touches one shard. Cross-student analytics (department fail rates) are scatter-gather queries, so run them on a dedicated analytics replica.

## 4. Cloud deployment options
Managed services (for example Amazon RDS/Aurora or Azure Database for PostgreSQL, and MongoDB Atlas) provide automated backups, multi-zone failover and read replicas, which suits a university IT team without 24/7 database staff. Trade-offs: recurring cost, vendor lock-in, and **data-protection obligations**: student records are personal data, so choose a region that satisfies Nigerian data-protection rules (NDPA 2023) and encrypt at rest and in transit. Auto-scaling read replicas before result release is cheaper than provisioning for peak all year.

## 5. Evidence
`output/distribution_results.txt` (simulation), `docker-compose.yml` (deployment definition, UNTESTED). If you run the compose file, add screenshots (`docker ps`, replication status queries) to `evidence/`.
