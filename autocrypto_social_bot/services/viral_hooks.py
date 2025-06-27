from typing import List, Dict
import random
from datetime import datetime

class ViralHooks:
    def __init__(self):
        self.hook_templates = {
            "question": [
                "🤔 Did you know {token} is {key_fact}?",
                "💡 Want to know why {token} is trending today?",
                "🔍 What's driving {token}'s recent momentum?",
                "⚡ Ready to discover why whales are watching {token}?",
                "🎯 Curious about {token}'s next move?"
            ],
            "statistic": [
                "📊 {token} just hit {stat}! Here's why it matters...",
                "🚀 {stat} and counting! {token}'s journey explained",
                "💹 From {old_stat} to {stat}: {token}'s incredible run",
                "📈 Breaking: {token} reaches {stat}",
                "🔥 {stat} milestone achieved! What's next for {token}?"
            ],
            "prediction": [
                "🔮 Here's why {token} might be preparing for a major move",
                "🎯 Three catalysts that could send {token} higher",
                "📊 Technical analysis suggests {token} is at a crucial point",
                "🚀 Why {token} could be the next big mover",
                "💫 The perfect storm brewing for {token}?"
            ],
            "urgency": [
                "🚨 Critical {token} analysis - Time-sensitive",
                "⚡ Breaking: Major development for {token}",
                "🔥 Don't miss this {token} update",
                "⏰ Time-sensitive {token} analysis inside",
                "🎯 Urgent: {token} at key level"
            ],
            "insight": [
                "🧠 The {token} insight nobody's talking about",
                "💡 Hidden bullish signals in {token}'s data",
                "🔍 What the charts reveal about {token}",
                "🎯 Three things you missed about {token}",
                "💫 The untold story of {token}'s recent moves"
            ]
        }
        
        self.time_based_hooks = {
            "morning": [
                "☀️ Morning {token} Analysis",
                "🌅 Start your day with {token} insights",
                "🎯 Your morning {token} briefing"
            ],
            "midday": [
                "📊 Midday {token} Update",
                "🎯 Lunchtime {token} Analysis",
                "💫 Afternoon {token} Insights"
            ],
            "evening": [
                "🌙 Evening {token} Wrap-up",
                "📈 End of day {token} Analysis",
                "🎯 Night owl's {token} Update"
            ]
        }
        
        self.trend_hooks = {
            "bull": [
                "🚀 Momentum building in {token}",
                "💫 {token} showing strength",
                "📈 {token} breaking out"
            ],
            "bear": [
                "💎 Value opportunity in {token}?",
                "🎯 {token} at support level",
                "💫 Accumulation zone for {token}?"
            ],
            "neutral": [
                "🎯 {token} coiling up",
                "📊 {token} at decision point",
                "💫 Key level for {token}"
            ]
        }

    def get_time_period(self) -> str:
        """Get current time period for hooks"""
        hour = datetime.now().hour
        if 4 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "midday"
        else:
            return "evening"

    def extract_key_statistic(self, analysis: str) -> str:
        """Extract a key statistic from the analysis"""
        # Look for percentage changes
        import re
        percentages = re.findall(r'(\d+(?:\.\d+)?%)', analysis)
        if percentages:
            return max(percentages, key=lambda x: float(x.strip('%')))
        
        # Look for price levels
        prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', analysis)
        if prices:
            return f"${max(prices, key=lambda x: float(x.replace(',', '')))}"
        
        return "new milestone"  # fallback

    def generate_hooks(self, token: str, analysis: str, market_sentiment: str) -> Dict[str, str]:
        """Generate a set of viral hooks for the post"""
        time_period = self.get_time_period()
        stat = self.extract_key_statistic(analysis)
        
        # Generate one hook of each type
        hooks = {
            "question": random.choice(self.hook_templates["question"]).format(
                token=token,
                key_fact=random.choice(["making waves", "turning heads", "gaining momentum"])
            ),
            "statistic": random.choice(self.hook_templates["statistic"]).format(
                token=token,
                stat=stat,
                old_stat="previous levels"
            ),
            "prediction": random.choice(self.hook_templates["prediction"]).format(token=token),
            "urgency": random.choice(self.hook_templates["urgency"]).format(token=token),
            "insight": random.choice(self.hook_templates["insight"]).format(token=token),
            "time_based": random.choice(self.time_based_hooks[time_period]).format(token=token),
            "trend": random.choice(self.trend_hooks[market_sentiment]).format(token=token)
        }
        
        return hooks

    def get_ab_test_variations(self, token: str, analysis: str, market_sentiment: str, count: int = 3) -> List[str]:
        """Generate multiple variations for A/B testing"""
        hooks = self.generate_hooks(token, analysis, market_sentiment)
        variations = []
        
        # Create different combinations of hooks
        hook_combinations = [
            [hooks["question"], hooks["insight"]],
            [hooks["statistic"], hooks["prediction"]],
            [hooks["urgency"], hooks["trend"]],
            [hooks["time_based"], hooks["insight"]],
            [hooks["trend"], hooks["prediction"]]
        ]
        
        for combo in hook_combinations[:count]:
            variations.append("\n".join(combo))
        
        return variations 