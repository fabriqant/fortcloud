import unittest
from datetime import date

from fortcloud_crucible import core

TODAY = date(2026, 11, 21)


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_load_model_counts(self):
        self.assertEqual(len(core.env_map(self.model)), 3)
        self.assertEqual(len(core.participant_map(self.model)), 5)
        self.assertEqual(len(core.scenario_map(self.model)), 6)
        self.assertEqual(len(core.channel_map(self.model)), 2)
        self.assertEqual(len(core.stakeholder_map(self.model)), 3)
        self.assertEqual(len(core.check_map(self.model)), 6)
        self.assertEqual(len(core.signoff_map(self.model)), 3)

    def test_durations_round_trip(self):
        self.assertEqual(core.parse_duration("0"), 0)
        self.assertEqual(core.parse_duration("1h30m"), 5_400_000)
        self.assertEqual(core.parse_duration("2d6h"), 194_400_000)
        self.assertIsNone(core.parse_duration("two weeks"))
        self.assertEqual(core.format_duration(5_400_000), "1h30m")
        self.assertEqual(core.format_duration(core.parse_duration("1h30m45s250ms")), "1h30m45s250ms")
        self.assertEqual(core.format_duration(0), "0")

    def test_dates_and_ages(self):
        self.assertEqual(core.age_days("2026-11-18", TODAY), 3)
        self.assertIsNone(core.parse_date("not-a-date"))
        self.assertEqual(core.parse_date("2026-11-21"), TODAY)

    def test_controlled_environments(self):
        envs = core.env_map(self.model)
        self.assertTrue(core.is_controlled(envs["sandbox"]))
        self.assertTrue(core.is_controlled(envs["staging"]))
        self.assertFalse(core.is_controlled(envs["prod"]))
        self.assertFalse(core.is_controlled(None))
        unapproved = dict(envs["sandbox"], approved=False)
        self.assertFalse(core.is_controlled(unapproved))

    def test_controlled_first_evidence(self):
        scenarios = core.scenario_map(self.model)
        evidence = core.controlled_first_evidence(self.model, scenarios["ex-restore-prod"])
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence["id"], "ex-restore-sandbox")
        isolated = dict(scenarios["ex-restore-prod"], kind="recovery")
        evidence = core.controlled_first_evidence(self.model, isolated)
        self.assertIsNotNone(evidence)  # ex-recovery-sandbox is a passed recovery
        isolated = dict(scenarios["ex-restore-prod"], kind="unknown-kind")
        self.assertIsNone(core.controlled_first_evidence(self.model, isolated))

    def test_roles_checks_and_targets(self):
        scenarios = core.scenario_map(self.model)
        scenario = scenarios["ex-failover-prod"]
        for role in core.REQUIRED_ROLES:
            self.assertIsNotNone(core.person_for_role(self.model, scenario, role))
        self.assertEqual(core.assignment_for_role(scenario, "verifier")["person"], "dave")
        self.assertEqual(len(core.checks_for_scenario(self.model, "ex-restore-sandbox")), 2)
        self.assertEqual(core.target_rto_ms(scenario), 900_000)
        self.assertEqual(core.target_rpo_ms(scenario), 0)
        self.assertEqual(core.scenario_duration(scenario), 3_600_000)


if __name__ == "__main__":
    unittest.main()
