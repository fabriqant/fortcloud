# Concepts

## Evidence over claims

A backup policy is a claim. A dated restore with a measured duration and an evidence link is proof. Ark treats the restore test as the unit of truth: no test means no proof, even if the backup dashboard is green.

## Tightest target wins

A data asset can feed several services. Ark takes the tightest RTO and RPO among the services that reference the asset and compares measured restore values against those targets. Optimising for the least demanding service hides the risk.

## Schedule versus RPO

RPO is the maximum acceptable data loss. A daily snapshot has a potential 24-hour loss window, so it cannot satisfy a 5-minute RPO. Continuous data capture (`type: cdc`, `schedule: "0"`) or a sufficiently short incremental schedule is required.

## Immutability and ransomware

An immutable backup cannot be deleted or altered within its retention window, including by compromised admin credentials. Ark requires immutability for P0 assets and expects at least one `ransomware` or `deletion` restore scenario per P0 asset: a clean restore is not the same as recovering from hostile deletion.

## Cross-region copy and retention

A P0 backup stored in a single region shares the fate of the primary. Ark warns when no cross-region copy exists and when retention is below 30 days. Those are warnings because a deliberate, documented exception can be acceptable — but the exception must be visible.

## Freshness

Two clocks matter:

- the last **successful backup** (warning after 2 days),
- the last **restore test** (warning after 90 days).

A fresh backup with a stale restore test is still unproven.

## Standalone by design

Ark does not read Atlas's or Failover's files and does not import their code. Keepers of the three tools may maintain separate models; a small amount of duplicated loading code is preferred over runtime coupling.
