"""
Niche Classification Module

Classifies content into TikTok niches (BookTok, FitTok, etc.).
"""


class NicheClassifier:
    """Classifies content into TikTok niches."""

    SUPPORTED_NICHES = [
        "BookTok",
        "FitTok",
        "FoodTok",
        "MusicTok",
        "DanceTok",
        "BeautyTok",
        "EducationTok",
        "ComedyTok",
        "GamingTok",
        "FinanceTok",
        "TravelTok",
        "FashionTok",
        "HealthTok",
        "DiyTok",
        "PetsTok",
    ]

    def classify(self, content: str, hashtags: list) -> str:
        """
        Classify content into a niche.

        Args:
            content: Content text or description
            hashtags: List of hashtags

        Returns:
            Niche classification
        """
        # TODO: Implement classification logic
        return self.SUPPORTED_NICHES[0]

    def get_all_niches(self) -> list:
        """
        Get list of all supported niches.

        Returns:
            List of supported niches
        """
        return self.SUPPORTED_NICHES
