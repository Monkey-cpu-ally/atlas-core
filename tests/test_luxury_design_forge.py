import unittest

from atlas_core.luxury import (
    AIReview,
    DesignConcept,
    DesignForge,
    OriginalityEngine,
    ReviewVerdict,
)


class DesignForgeTests(unittest.TestCase):
    def setUp(self) -> None:
        originality = OriginalityEngine(
            {
                "Example Brand": ["example protected checker identity"],
            }
        )
        self.forge = DesignForge(originality_engine=originality)
        self.concept = DesignConcept(
            design_id="hof-001",
            name="Sapphire Knight Field Bag",
            product_type="bag",
            description="A balanced repairable field bag with original cathedral geometry.",
            story="The Sapphire Knight protects tools and records during travel.",
            materials=["vegetable-tanned leather", "wool lining"],
            hardware=["Forge buckle"],
            patterns=["Knight Grid"],
            repair_plan="Replaceable straps, lining, buckle, and zipper.",
            manufacturing_notes="Reinforced load points with staged assembly and accessible fasteners.",
        )

    def test_forge_scores_and_approves_complete_design(self) -> None:
        record = self.forge.begin(self.concept)
        record = self.forge.evaluate(
            record,
            {
                "beauty": 82,
                "story": 85,
                "engineering": 86,
                "craftsmanship": 84,
                "materials": 88,
                "innovation": 78,
                "originality": 90,
                "repairability": 91,
                "longevity": 89,
                "manufacturability": 82,
                "comfort": 80,
                "emotional_impact": 84,
            },
        )
        reviews = [
            AIReview("Hermes", ReviewVerdict.APPROVE, 88, strengths=["Buildable and repairable"]),
            AIReview("Minerva", ReviewVerdict.APPROVE, 86, strengths=["Story remains subtle"]),
            AIReview("Ajani", ReviewVerdict.APPROVE, 84, strengths=["Strong product family potential"]),
        ]
        record = self.forge.submit_to_council(record, reviews)

        self.assertIsNotNone(record.genome)
        self.assertGreater(record.genome.overall, 80)
        self.assertEqual(record.council_decision.verdict, ReviewVerdict.APPROVE)
        self.assertEqual(record.stage.value, "archive")

    def test_weak_design_is_returned_for_revision(self) -> None:
        weak = DesignConcept(
            design_id="hof-002",
            name="Unresolved Coat",
            product_type="coat",
            description="A decorative coat concept.",
        )
        record = self.forge.evaluate(self.forge.begin(weak), {"originality": 45})
        reviews = [
            AIReview("Hermes", ReviewVerdict.REVISE, 60, concerns=["No construction plan"]),
            AIReview("Minerva", ReviewVerdict.REVISE, 62, concerns=["No clear story"]),
            AIReview("Ajani", ReviewVerdict.REVISE, 58, concerns=["No manufacturing case"]),
        ]
        record = self.forge.submit_to_council(record, reviews)

        self.assertEqual(record.council_decision.verdict, ReviewVerdict.REVISE)
        self.assertTrue(record.critiques)

    def test_missing_reviewer_is_rejected(self) -> None:
        record = self.forge.evaluate(self.forge.begin(self.concept), {})
        with self.assertRaises(ValueError):
            self.forge.submit_to_council(
                record,
                [
                    AIReview("Hermes", ReviewVerdict.APPROVE, 85),
                    AIReview("Minerva", ReviewVerdict.APPROVE, 85),
                ],
            )


if __name__ == "__main__":
    unittest.main()
