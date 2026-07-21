from __future__ import annotations

from statistics import mean
from typing import Iterable, List

from .models import AIReview, CouncilDecision, DesignConcept, ReviewVerdict


class CouncilReviewEngine:
    REQUIRED_REVIEWERS = {"Hermes", "Minerva", "Ajani"}

    def decide(self, concept: DesignConcept, reviews: Iterable[AIReview]) -> CouncilDecision:
        review_list = list(reviews)
        reviewers = {review.reviewer for review in review_list}
        missing = self.REQUIRED_REVIEWERS - reviewers
        if missing:
            raise ValueError(f"Missing required Council reviews: {sorted(missing)}")
        if any(not 0.0 <= review.score <= 100.0 for review in review_list):
            raise ValueError("Review scores must be between 0 and 100")

        overall = round(mean(review.score for review in review_list), 2)
        verdicts = [review.verdict for review in review_list]
        required_changes = [change for review in review_list for change in review.required_changes]

        if ReviewVerdict.REBUILD in verdicts or overall < 45:
            verdict = ReviewVerdict.REBUILD
        elif ReviewVerdict.STUDY_FURTHER in verdicts:
            verdict = ReviewVerdict.STUDY_FURTHER
        elif ReviewVerdict.REVISE in verdicts or required_changes or overall < 75:
            verdict = ReviewVerdict.REVISE
        else:
            verdict = ReviewVerdict.APPROVE

        summary = self._summary(verdict, overall, review_list)
        return CouncilDecision(
            design_id=concept.design_id,
            verdict=verdict,
            overall_score=overall,
            reviews=review_list,
            summary=summary,
        )

    @staticmethod
    def _summary(verdict: ReviewVerdict, overall: float, reviews: List[AIReview]) -> str:
        concerns = [concern for review in reviews for concern in review.concerns]
        changes = [change for review in reviews for change in review.required_changes]
        text = f"Council verdict: {verdict.value}. Combined score: {overall:.2f}/100."
        if concerns:
            text += " Main concerns: " + "; ".join(concerns[:3]) + "."
        if changes:
            text += " Required changes: " + "; ".join(changes[:3]) + "."
        return text
