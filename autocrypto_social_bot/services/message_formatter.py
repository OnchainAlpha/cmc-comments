from typing import Dict, Optional
import re

class MessageFormatter:
    def __init__(self):
        # Base prompt templates for different promotion types
        self.prompt_templates = {
            1: {  # Market Making
                "title": "Market Making Promotion",
                "templates": [
                    """Start with: "Onchain Bureau market making positions have been strategically placed at [derive from analysis] for accumulation and [derive higher price] for distribution based on the following analysis:"

Then analyze: {ai_analysis}

Requirements:
- Lead with OCB's specific price positioning to establish market leadership
- Integrate the CMC analysis naturally after the positioning statement
- Focus on liquidity depth, execution quality, and institutional confidence
- Keep total response under 1800 characters for posting limits
- End with subtle engagement hook
- Make OCB appear as the liquidity authority"""
                ]
            },
            
            2: {  # Token Launch
                "title": "Token Launch Announcement",
                "templates": [
                    """Start with: "Onchain Bureau has identified strategic entry levels at [derive from analysis] for the upcoming {target_token} launch based on the following analysis:"

Then analyze: {ai_analysis}

Key Launch Details:
- Initial Price: {initial_price}
- Total Supply: {total_supply}
- Features: {key_features}

Requirements:
- Lead with OCB's strategic positioning for the launch
- Integrate CMC analysis with launch timing and pricing
- Focus on OCB's institutional backing and launch expertise
- Keep total response under 1800 characters for posting limits
- Position OCB as the authoritative launch partner"""
                ]
            },
            
            3: {  # Technical Update
                "title": "Technical Update",
                "templates": [
                    """Start with: "Onchain Bureau's technical analysis team has identified key levels at [derive from analysis] ahead of the {update_type} (v{version}) release on {release_date} based on the following analysis:"

Then analyze: {ai_analysis}

Key Improvements:
{key_improvements}

Requirements:
- Lead with OCB's technical positioning ahead of the update
- Integrate CMC analysis with technical developments
- Focus on OCB's technical expertise and institutional insights
- Keep total response under 1800 characters for posting limits
- Position OCB as the technical authority"""
                ]
            },
            
            4: {  # Partnership
                "title": "Partnership Announcement",
                "templates": [
                    """Start with: "Onchain Bureau's strategic analysis indicates optimal positioning at [derive from analysis] following the {partnership_type} partnership with {partner_name} based on the following analysis:"

Then analyze: {ai_analysis}

Partnership Benefits:
{partnership_benefits}

Timeline: {timeline}

Requirements:
- Lead with OCB's strategic positioning post-partnership
- Integrate CMC analysis with partnership synergies
- Focus on OCB's institutional partnerships and market impact
- Keep total response under 1800 characters for posting limits
- Position OCB as the strategic partnership authority"""
                ]
            },
            
            5: {  # Trading Group
                "title": "Trading Group Promotion",
                "templates": [
                    """Start with: "Onchain Bureau's institutional trading desk has identified key levels at [derive from analysis] for optimal entry/exit based on the following analysis:"

Then analyze: {ai_analysis}

Special Offer: {special_offer}
Community: {join_link}

Requirements:
- Lead with OCB's institutional trading positioning
- Integrate CMC analysis with OCB's trading expertise
- Focus on OCB's institutional-grade trading services
- Keep total response under 1800 characters for posting limits
- Position OCB as the institutional trading authority"""
                ]
            },
            
            6: {  # Default Settings
                "title": "Default Analysis",
                "templates": [
                    """Start with: "Onchain Bureau's market analysis team has identified strategic levels at [derive from analysis] for {analysis_timeframe} based on the following analysis:"

Then analyze: {ai_analysis}

Focus on these metrics:
{key_metrics}

Requirements:
- Lead with OCB's market analysis positioning
- Integrate CMC analysis with OCB's institutional insights
- Focus on OCB's comprehensive market expertise
- Keep total response under 1800 characters for posting limits
- Position OCB as the market analysis authority"""
                ]
            }
        }
        
        # Add market condition modifiers
        self.market_conditions = {
            "bull": {
                "prefix": """In this bullish market environment where momentum is key, enhance the analysis while maintaining credibility. Focus on:
                - Solid fundamentals that support upward momentum
                - Institutional interest and accumulation patterns
                - Technical indicators confirming the trend
                - Risk management despite bullish outlook
                """,
                "style_keywords": ["momentum", "breakout", "accumulation", "institutional", "uptrend"]
            },
            "bear": {
                "prefix": """In the current bear market conditions, provide a balanced perspective focused on fundamentals. Emphasize:
                - Strong fundamentals despite market weakness
                - Development progress and team commitment
                - Strategic advantages in challenging times
                - Value accumulation opportunities
                """,
                "style_keywords": ["resilience", "development", "fundamentals", "opportunity", "value"]
            },
            "neutral": {
                "prefix": """In the current ranging market, focus on distinguishing factors and catalysts. Highlight:
                - Unique value propositions
                - Upcoming catalysts and developments
                - Comparative advantages
                - Strategic positioning
                """,
                "style_keywords": ["catalyst", "development", "advantage", "strategy", "positioning"]
            }
        }
        
        # Add time-of-day optimizations
        self.time_optimizations = {
            "morning": {
                "tone": "energetic and forward-looking",
                "focus": "day's opportunities and market outlook"
            },
            "midday": {
                "tone": "analytical and detailed",
                "focus": "technical analysis and current performance"
            },
            "evening": {
                "tone": "reflective and strategic",
                "focus": "daily achievements and tomorrow's potential"
            }
        }
        
        # Add regional market focus
        self.regional_focus = {
            "asia": ["Asian market dynamics", "regional partnerships", "timezone-specific catalysts"],
            "europe": ["European regulatory landscape", "EU market penetration", "regional expansion"],
            "americas": ["US market sentiment", "SEC considerations", "American trading session"]
        }

    def detect_market_sentiment(self, ai_analysis: str) -> str:
        """
        Analyze the AI review to detect market sentiment.
        Returns: 'bull', 'bear', or 'neutral'
        """
        # Simple sentiment analysis based on key phrases
        bullish_indicators = ["bullish", "uptrend", "growth", "positive", "surge", "rally"]
        bearish_indicators = ["bearish", "downtrend", "decline", "negative", "drop", "correction"]
        
        text = ai_analysis.lower()
        bull_count = sum(1 for word in bullish_indicators if word in text)
        bear_count = sum(1 for word in bearish_indicators if word in text)
        
        if bull_count > bear_count + 2:
            return "bull"
        elif bear_count > bull_count + 2:
            return "bear"
        return "neutral"

    def get_time_optimization(self) -> Dict:
        """Get time-based optimization parameters"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 4 <= hour < 12:
            return self.time_optimizations["morning"]
        elif 12 <= hour < 18:
            return self.time_optimizations["midday"]
        else:
            return self.time_optimizations["evening"]

    def detect_token_category(self, symbol: str, description: str) -> str:
        """
        Detect token category for more targeted analysis
        """
        categories = {
            "defi": ["defi", "yield", "lending", "amm", "swap"],
            "gaming": ["game", "metaverse", "play", "nft", "virtual"],
            "infrastructure": ["layer", "scaling", "blockchain", "protocol"],
            "ai": ["ai", "machine learning", "data", "neural", "intelligence"],
            "privacy": ["privacy", "anonymous", "confidential", "secure"]
        }
        
        text = (symbol + " " + description).lower()
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        return "general"

    def enhance_prompt_with_context(self, base_prompt: str, ai_analysis: str, params: Dict) -> str:
        """
        Enhance the base prompt with contextual elements
        """
        # Detect market sentiment
        sentiment = self.detect_market_sentiment(ai_analysis)
        market_context = self.market_conditions[sentiment]["prefix"]
        
        # Get time optimization
        time_opt = self.get_time_optimization()
        
        # Detect token category if symbol is provided
        token_category = "general"
        if "token" in params:
            token_category = self.detect_token_category(params["token"], ai_analysis)
        
        # Combine everything
        enhanced_prompt = f"""
{market_context}

Current Context:
- Market Sentiment: {sentiment.title()}
- Time Focus: {time_opt['focus']}
- Category: {token_category.title()}

{base_prompt}

Additional Guidelines:
- Maintain a {time_opt['tone']} tone
- Focus on {token_category}-specific metrics and comparisons
- Address current {sentiment} market dynamics
"""
        return enhanced_prompt

    def get_promotion_prompt(self, promotion_type, ai_analysis: str, params: dict) -> str:
        """
        Generate a promotion prompt based on type and parameters.
        Now with enhanced contextual awareness and parameter validation.
        """
        # Convert string promotion type to integer for template lookup
        if isinstance(promotion_type, str):
            type_mapping = {
                'market_making': 1,
                'token_shilling': 2,  # Updated from token_launch
                'trading_group': 5
            }
            promotion_type = type_mapping.get(promotion_type, 1)
        
        # Handle token shilling with creative cross-referencing
        if promotion_type == 2:  # Token Shilling
            promoted_ticker = params.get('promoted_ticker', 'PROMOTED')
            promoted_name = params.get('promoted_name', 'Promoted Token')
            
            # Create varied cross-referencing approaches
            import random
            approaches = [
                f"Analyze {ai_analysis} and then naturally transition to: 'Onchain data reveals top traders of the current token are quietly rotating into ${promoted_ticker} - institutional flow patterns suggest this transition accelerated 48hrs ago. Our tracking indicates ${promoted_ticker} ({promoted_name}) receiving significant whale accumulation from profit-takers.'",
                
                f"Build on {ai_analysis} then seamlessly add: 'Smart money analysis shows ${promoted_ticker} emerging as the primary beneficiary of current market dynamics - whale transactions from major holders indicate coordinated positioning into {promoted_name}.'",
                
                f"Use {ai_analysis} as foundation, then integrate: 'Cross-chain analytics expose ${promoted_ticker} as institutional favorite amid current market conditions - sophisticated wallets demonstrating clear preference for {promoted_name} over traditional alternatives.'",
                
                f"Start with {ai_analysis} insights, then reveal: 'Institutional tracking reveals ${promoted_ticker} receiving unprecedented inflows from diversification strategies - {promoted_name} positioning suggests major players anticipating significant developments.'",
                
                f"Leverage {ai_analysis} data, then connect: 'Onchain intelligence indicates ${promoted_ticker} becoming the preferred hedge for current market exposure - elite trader behavior around {promoted_name} suggests exclusive information driving accumulation.'"
            ]
            
            selected_approach = random.choice(approaches)
            return f"""Create a sophisticated analysis that {selected_approach}
            
CRITICAL EXECUTION:
- Start with 2-3 sentences analyzing the current token using the CMC data
- Naturally transition using onchain/whale/institutional language
- Position the cross-reference as exclusive OCB intelligence 
- Make ${promoted_ticker} mention feel organic, not forced
- Keep total response under 1600 characters
- End with subtle engagement question about the connection
- Use authoritative, insider knowledge tone"""
        
        # Handle other promotion types with existing logic
        if promotion_type not in self.prompt_templates:
            raise ValueError(f"Unknown promotion type: {promotion_type}")
            
        # Get base template for non-shilling types
        import random
        base_template = random.choice(self.prompt_templates[promotion_type]["templates"])
        
        # Prepare parameters
        formatted_params = params.copy()
        formatted_params['ai_analysis'] = ai_analysis
        
        # Add region-specific focus if region is provided
        if promotion_type == 1:  # Market Making
            if 'region' in formatted_params:
                region = formatted_params['region']
                region_points = self.regional_focus.get(region, [])
                formatted_params['region_focus'] = "\n- " + "\n- ".join(region_points) if region_points else ""
            else:
                formatted_params['region_focus'] = ""
        
        # Handle list parameters
        if 'key_features' in formatted_params:
            formatted_params['key_features'] = '\n- ' + '\n- '.join(formatted_params['key_features'])
        if 'key_improvements' in formatted_params:
            formatted_params['key_improvements'] = '\n- ' + '\n- '.join(formatted_params['key_improvements'])
        if 'partnership_benefits' in formatted_params:
            formatted_params['partnership_benefits'] = '\n- ' + '\n- '.join(formatted_params['partnership_benefits'])
        if 'key_metrics' in formatted_params:
            formatted_params['key_metrics'] = '\n- ' + '\n- '.join(formatted_params['key_metrics'])
        
        # Format base template with parameters
        try:
            base_prompt = base_template.format(**formatted_params)
            return base_prompt
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {str(e)}")

    def format_final_message(self, enhanced_analysis: str, token_symbol: str) -> str:
        """
        Format the final message with improved structure and engagement elements
        """
        # Extract key points for summary
        key_points = re.findall(r'[•\-\*]\s+([^\n]+)', enhanced_analysis)
        
        # Create a TL;DR if we have enough key points
        tldr = ""
        if len(key_points) >= 3:
            tldr = "\n\nTL;DR 🎯\n" + "\n".join(f"• {point}" for point in key_points[:3])
        
        # Add relevant hashtags based on content
        hashtags = ["#crypto", "#analysis"]
        if "defi" in enhanced_analysis.lower():
            hashtags.append("#DeFi")
        if "nft" in enhanced_analysis.lower():
            hashtags.append("#NFT")
        if "metaverse" in enhanced_analysis.lower():
            hashtags.append("#Metaverse")
        
        # Format the final message
        message = f"${token_symbol} Analysis 🔍\n\n{enhanced_analysis}{tldr}\n\n{' '.join(hashtags)}"
        
        # Add engagement prompt if message isn't too long
        if len(message) < 1800:  # Leave room for character limits
            message += "\n\n💭 What's your take on this analysis? Share your thoughts below!"
        
        return message

    def format_comprehensive_promotional_message(self, enhanced_analysis: str, token_symbol: str) -> str:
        """
        Format a comprehensive promotional message under 2000 characters for single posting
        """
        # Clean up the enhanced analysis
        cleaned_analysis = enhanced_analysis.strip()
        
        # Ensure we stay under character limits (CMC has 2000 char limit)
        max_content_length = 1700  # Leave room for hashtags and engagement
        
        if len(cleaned_analysis) > max_content_length:
            # Truncate intelligently at sentence boundary
            truncated = cleaned_analysis[:max_content_length]
            last_period = truncated.rfind('.')
            if last_period > max_content_length - 200:  # If period is reasonably close to end
                cleaned_analysis = truncated[:last_period + 1]
            else:
                cleaned_analysis = truncated + "..."
        
        # Create the message structure
        message = cleaned_analysis
        
        # Add professional closing if not present
        if not message.endswith('.') and not message.endswith('...'):
            message += "."
        
        # Add relevant hashtags (concise for character limits)
        hashtags = ["#crypto", "#trading"]
        
        # Smart hashtag detection (limit to most relevant)
        content_lower = cleaned_analysis.lower()
        if "bitcoin" in content_lower or "btc" in content_lower:
            hashtags.append("#Bitcoin")
        elif "ethereum" in content_lower or "eth" in content_lower:
            hashtags.append("#Ethereum")
        elif any(word in content_lower for word in ["defi", "yield"]):
            hashtags.append("#DeFi")
            
        if "institutional" in content_lower or "liquidity" in content_lower:
            hashtags.append("#institutional")
        
        # Add hashtags (limit to 4 to save characters)
        message += f"\n\n{' '.join(hashtags[:4])}"
        
        # Add engagement hook (short to save characters)
        message += "\n\n[THOUGHTS] Your take on these levels?"
        
        # Final check - ensure under 2000 characters
        if len(message) > 1950:
            # Emergency truncation
            base_message = cleaned_analysis[:1500] + "..."
            message = f"{base_message}\n\n{' '.join(hashtags[:3])}\n\n[THOUGHTS] Thoughts?"
        
        return message
    
    def format_tldr_message(self, enhanced_analysis: str, token_symbol: str) -> str:
        """
        DEPRECATED: Use format_comprehensive_promotional_message instead
        Keeping for backwards compatibility
        """
        return self.format_comprehensive_promotional_message(enhanced_analysis, token_symbol)

    def get_base_templates(self) -> Dict:
        """Return the original prompt templates"""
        # Return the existing prompt_templates dictionary
        return {
            "market_making": {
                # ... (keep existing templates)
            },
            # ... (keep other existing categories)
        }

class CMCMessageFormatter:
    @staticmethod
    def format_analysis(analysis: dict) -> str:
        """Format analysis results for CMC community post"""
        
        # Get risk assessment
        risk = analysis['risk_assessment']
        health = analysis['community_health']
        
        # Format the message
        message = f"""🔍 Community Analysis Report for {analysis['coin_info']['name']} (${analysis['coin_info']['symbol']})

📊 Current Status:
• Price: {analysis['coin_info']['price']}
• 24h Change: {analysis['coin_info']['change_24h']}%

🏥 Community Health:
• Active Users: {health['total_users']}
• Verified Users: {health['verified_ratio']*100:.1f}%
• New Accounts: {health['new_account_ratio']*100:.1f}%

⚠️ Risk Assessment:
• Risk Level: {risk['risk_level']}

🚩 Risk Factors:
"""
        # Add risk factors
        for factor in risk['risk_factors']:
            message += f"• {factor}\n"
            
        # Add manipulation signals if any
        manip = analysis['manipulation_signals']
        if manip['coordinated_posting'] or manip['repeated_phrases'] or manip['suspicious_accounts']:
            message += "\n🚨 Manipulation Signals Detected:\n"
            if manip['coordinated_posting']:
                message += "• Coordinated posting patterns\n"
            if manip['repeated_phrases']:
                message += "• Suspicious promotional language\n"
            if manip['suspicious_accounts']:
                message += f"• {len(manip['suspicious_accounts'])} suspicious accounts\n"
        
        # Add recommendation
        message += f"\n📊 Assessment: {analysis['recommendation']}\n"
        
        # Add warning flags
        if analysis['warning_flags']:
            message += "\n⚠️ Warning Flags:\n"
            for flag in analysis['warning_flags']:
                message += f"• {flag}\n"
        
        message += "\n💡 This is an automated analysis. Always DYOR."
        
        return message 