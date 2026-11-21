# Concepts

## False redundancy

Two instances are only redundant if an event can destroy one without destroying the other. Failover considers a pair false redundancy when both components are in the same `region`, and warns when they share the same `provider`. Zone-level differences are not enough for a regional outage.

## Pair and roles

A `pair` identifier links exactly one `primary` and one `standby`. The validator checks that both components exist, that their roles match, and that the pair identifier is identical. A P0 component referenced by a service but not covered by any strategy is an error.

## Switchover budget

The time to recover is not just the promotion:

```text
detection_time + promotion_time <= RTO
```

Failover uses the **tightest RTO** among the services that reference the primary or the standby. A 30-minute RTO service and a 15-minute RTO service sharing the same primary give a 15-minute budget.

## Replication versus RPO

RPO is the maximum acceptable data loss. `sync` and `stateless` can support `RPO: 0`; `async` implies a window of loss. Declaring `async` on a strategy protecting a service with `RPO: 0` is an error.

## Capacity

A standby sized at 50 when the primary is sized at 100 will not absorb the load during promotion. This is a warning because a degraded but working service can still be preferable to a hard outage — but it must be a conscious decision.

## DNS TTL and automation

A DNS TTL above the RTO keeps sending traffic to the dead primary after the switch. A manual switchover for a P0 service is flagged because human reaction time is rarely in the RTO budget.

## Drill evidence

A design is only as good as its last rehearsal. Failover expects at least one drill per strategy, dated within 90 days, with `result: passed` and an evidence link. A `partial` result is a warning: it means something worked but the objective was not fully met.

## Standalone by design

Failover does not read Atlas's files and does not import its code. The two tools solve different problems and can be adopted independently. Duplicating a small amount of model-loading code is preferred over a runtime coupling that would force users to install both.
