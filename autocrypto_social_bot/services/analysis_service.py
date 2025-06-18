from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import re
from collections import Counter

class AnalysisService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Token age thresholds (in days)
        self.token_age_thresholds = {
            'very_new': 7,      # Less than 7 days old - Extremely High Risk
            'new': 30,          # Less than 30 days - High Risk
            'developing': 90,    # 1-3 months - Medium Risk
            'established': 180,  # 3-6 months - Lower Risk
            'mature': 365       # Over 1 year - Lowest Risk
        }
        
        # Price movement thresholds
        self.price_thresholds = {
            'extreme_pump': 100,  # >100% in 24h - Extremely High Risk
            'high_pump': 50,      # >50% in 24h - High Risk
            'medium_pump': 25,    # >25% in 24h - Medium Risk
            'normal': 10          # <10% in 24h - Normal
        }
        
        # Suspicious patterns in tweets
        self.suspicious_phrases = [
            r"(?i)to\s*the\s*moon",
            r"(?i)x{1,}\s*gains?",
            r"(?i)pump",
            r"(?i)buy\s*now",
            r"(?i)next\s*gem",
            r"(?i)don'?t\s*miss",
            r"(?i)early",
            r"(?i)presale",
            r"(?i)huge\s*potential",
            r"(?i)100x",
            r"(?i)1000x",
            r"(?i)guaranteed",
            r"(?i)easy\s*money",
            r"(?i)airdrop",
            r"(?i)free\s*tokens?",
            r"(?i)get\s*in\s*now",
            r"(?i)before\s*it'?s\s*too\s*late",
            r"(?i)the\s*next\s*bitcoin",
            r"(?i)massive\s*gains?",
            r"(?i)limited\s*time",
            r"(?i)act\s*fast",
            r"(?i)get\s*rich",
        ]
        
        # Red flags in account profiles
        self.account_red_flags = {
            'new_account': 90,           # days
            'very_new_account': 30,      # days
            'low_followers': 200,
            'very_low_followers': 50,
            'high_daily_tweets': 50,
            'extreme_daily_tweets': 100,
            'multi_coin_threshold': 3,
            'coordinated_post_window': 300,  # seconds
            'min_engagement_ratio': 0.001    # likes/followers ratio
        }
        
        # Market cap thresholds (in USD)
        self.market_cap_thresholds = {
            'micro': 1_000_000,        # <1M - Extremely High Risk
            'small': 10_000_000,       # <10M - High Risk
            'medium': 100_000_000,     # <100M - Medium Risk
            'large': 1_000_000_000     # >1B - Lower Risk
        }

    def analyze_coin_community(self, name: str, symbol: str, tweets_data: list, coin_info: dict) -> dict:
        """Generate dynamic analysis based on social data"""
        try:
            # Extract key metrics
            total_tweets = len(tweets_data)
            verified_users = len([t for t in tweets_data if t['user']['verified']])
            
            # Analyze tweet content
            key_insights = []
            sentiment_data = []
            topics = {}
            influencers = []
            
            for tweet in tweets_data:
                text = tweet['text'].lower()
                user = tweet['user']
                
                # Track influential users
                if user['verified'] or user['followers_count'] > 10000:
                    influencers.append({
                        'username': user['screen_name'],
                        'followers': user['followers_count'],
                        'verified': user['verified'],
                        'sentiment': 'positive' if any(term in text for term in ['bullish', 'buy', 'moon']) else 
                                   'negative' if any(term in text for term in ['bearish', 'sell', 'dump']) else 'neutral'
                    })
                
                # Extract key topics and context
                for topic in ['partnership', 'development', 'roadmap', 'listing', 'update', 'launch', 
                             'airdrop', 'staking', 'burn', 'utility', 'adoption']:
                    if topic in text:
                        topics[topic] = topics.get(topic, [])
                        topics[topic].append(text)
            
            # Generate dynamic insights
            price_change = float(coin_info['change_24h'])
            
            # Price analysis
            if abs(price_change) > 30:
                key_insights.append(f"Significant price movement of {price_change}% in 24h suggests high market interest")
            
            # Community analysis
            if influencers:
                sentiment_distribution = {
                    'positive': len([i for i in influencers if i['sentiment'] == 'positive']),
                    'negative': len([i for i in influencers if i['sentiment'] == 'negative']),
                    'neutral': len([i for i in influencers if i['sentiment'] == 'neutral'])
                }
                dominant_sentiment = max(sentiment_distribution.items(), key=lambda x: x[1])[0]
                key_insights.append(
                    f"Notable community engagement with {len(influencers)} influential voices showing "
                    f"predominantly {dominant_sentiment} sentiment"
                )
            
            # Development/Project analysis
            if 'development' in topics or 'update' in topics:
                key_insights.append("Active development signals with recent updates and progress discussions")
            
            # Market dynamics
            if 'listing' in topics:
                key_insights.append("Potential market catalysts with discussions about new listings")
            
            if 'utility' in topics or 'adoption' in topics:
                key_insights.append("Community focus on real-world adoption and utility development")
            
            # Generate the analysis message
            message = f"${symbol} Community Analysis\n\n"
            
            # Market Context
            message += f"Current market position shows ${coin_info['price']} with {coin_info['change_24h']}% movement. "
            
            # Key Insights
            if key_insights:
                message += "\n\nKey Observations:\n"
                message += "\n".join(f"• {insight}" for insight in key_insights)
            
            # Community Health
            message += f"\n\nCommunity Overview:\n"
            message += f"• {total_tweets} recent discussions analyzed\n"
            message += f"• {verified_users} verified contributors\n"
            
            # Risk Assessment
            risk_factors = []
            if abs(price_change) > 50:
                risk_factors.append("Extreme price volatility")
            if len([i for i in influencers if i['sentiment'] == 'positive']) > len(influencers) * 0.8:
                risk_factors.append("Potentially over-optimistic sentiment")
            
            if risk_factors:
                message += "\nRisk Factors to Consider:\n"
                message += "\n".join(f"• {factor}" for factor in risk_factors)
            
            message += "\n\nThis analysis is AI-generated based on recent social data. DYOR."
            
            return {
                'coin_info': coin_info,
                'community_metrics': {
                    'total_tweets': total_tweets,
                    'verified_users': verified_users,
                    'influencers': influencers,
                    'key_topics': topics
                },
                'risk_assessment': {
                    'risk_factors': risk_factors,
                    'risk_level': 'HIGH' if len(risk_factors) > 2 else 'MEDIUM' if risk_factors else 'LOW'
                },
                'key_insights': key_insights,
                'message': message
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            return None

    def _analyze_token_metrics(self, price_data: Dict) -> Dict:
        """Analyze token metrics for risk factors"""
        metrics = {
            'age_risk': 0,
            'price_risk': 0,
            'market_cap_risk': 0,
            'risk_factors': []
        }
        
        # Analyze token age
        if 'creation_date' in price_data:
            age_days = (datetime.now() - datetime.fromtimestamp(price_data['creation_date'])).days
            if age_days < self.token_age_thresholds['very_new']:
                metrics['age_risk'] = 5
                metrics['risk_factors'].append("⚠️ EXTREME RISK: Token is less than 7 days old")
            elif age_days < self.token_age_thresholds['new']:
                metrics['age_risk'] = 4
                metrics['risk_factors'].append("Token is less than 30 days old")
            elif age_days < self.token_age_thresholds['developing']:
                metrics['age_risk'] = 2
                metrics['risk_factors'].append("Token is relatively new (1-3 months)")
        
        # Analyze price movement
        price_change = float(price_data.get('change_24h', 0))
        if abs(price_change) > self.price_thresholds['extreme_pump']:
            metrics['price_risk'] = 5
            metrics['risk_factors'].append(f"⚠️ EXTREME RISK: {price_change}% price change in 24h")
        elif abs(price_change) > self.price_thresholds['high_pump']:
            metrics['price_risk'] = 4
            metrics['risk_factors'].append(f"Suspicious price movement: {price_change}% in 24h")
        elif abs(price_change) > self.price_thresholds['medium_pump']:
            metrics['price_risk'] = 2
            metrics['risk_factors'].append(f"High volatility: {price_change}% in 24h")
        
        # Analyze market cap
        if 'market_cap' in price_data:
            market_cap = float(price_data['market_cap'])
            if market_cap < self.market_cap_thresholds['micro']:
                metrics['market_cap_risk'] = 5
                metrics['risk_factors'].append("⚠️ EXTREME RISK: Micro market cap (<$1M)")
            elif market_cap < self.market_cap_thresholds['small']:
                metrics['market_cap_risk'] = 3
                metrics['risk_factors'].append("High Risk: Small market cap (<$10M)")
        
        return metrics

    def _analyze_community_health(self, tweets_data: Dict) -> Dict:
        """Enhanced community health analysis"""
        stats = tweets_data['community_stats']
        user_stats = tweets_data['user_stats']
        
        # Calculate key metrics
        total_users = stats['unique_users']
        verified_ratio = stats['verified_users'] / total_users if total_users > 0 else 0
        
        new_accounts = 0
        very_new_accounts = 0
        low_followers = 0
        very_low_followers = 0
        multi_promoters = 0
        bot_like_activity = 0
        
        for username, user_data in user_stats.items():
            if user_data:
                # Check account age
                if user_data.get('join_date') != "Unknown":
                    join_date = datetime.strptime(user_data['join_date'], "%B %Y")
                    account_age = (datetime.now() - join_date).days
                    if account_age < self.account_red_flags['very_new_account']:
                        very_new_accounts += 1
                    elif account_age < self.account_red_flags['new_account']:
                        new_accounts += 1
                
                # Check follower count
                if user_data.get('followers') != "Unknown":
                    try:
                        followers = int(user_data['followers'].replace(',', ''))
                        if followers < self.account_red_flags['very_low_followers']:
                            very_low_followers += 1
                        elif followers < self.account_red_flags['low_followers']:
                            low_followers += 1
                    except:
                        pass
                
                # Check for bot-like behavior
                if user_data.get('tweets_per_day', 0) > self.account_red_flags['extreme_daily_tweets']:
                    bot_like_activity += 1
                
                # Check multi-coin promotion
                promoted_coins = user_data.get('promoted_coins', [])
                if len(promoted_coins) > self.account_red_flags['multi_coin_threshold']:
                    multi_promoters += 1
        
        return {
            'total_users': total_users,
            'verified_ratio': verified_ratio,
            'new_account_ratio': new_accounts / total_users if total_users > 0 else 0,
            'very_new_account_ratio': very_new_accounts / total_users if total_users > 0 else 0,
            'low_follower_ratio': low_followers / total_users if total_users > 0 else 0,
            'very_low_follower_ratio': very_low_followers / total_users if total_users > 0 else 0,
            'multi_promoter_ratio': multi_promoters / total_users if total_users > 0 else 0,
            'bot_ratio': bot_like_activity / total_users if total_users > 0 else 0
        }

    def _detect_manipulation(self, tweets_data: Dict) -> Dict:
        """Detect potential manipulation patterns"""
        top_tweets = tweets_data['top_tweets']
        latest_tweets = tweets_data['latest_tweets']
        
        # Analyze tweet patterns
        repeated_phrases = self._find_repeated_phrases(top_tweets + latest_tweets)
        coordinated_posting = self._detect_coordinated_posting(latest_tweets)
        
        return {
            'repeated_phrases': repeated_phrases,
            'coordinated_posting': coordinated_posting,
            'suspicious_accounts': self._identify_suspicious_accounts(tweets_data)
        }

    def _assess_risk(self, tweets_data: Dict, token_metrics: Dict) -> Dict:
        """Enhanced risk assessment without numerical scoring"""
        risk_factors = []
        risk_level = "LOW"
        
        # Token metrics risks
        if token_metrics['risk_factors']:
            risk_factors.extend(token_metrics['risk_factors'])
            # Update risk level based on severity of factors
            if any("EXTREME RISK" in factor for factor in token_metrics['risk_factors']):
                risk_level = "CRITICAL"
            elif any("High Risk" in factor for factor in token_metrics['risk_factors']):
                risk_level = "HIGH"
        
        # Community health risks
        health = self._analyze_community_health(tweets_data)
        
        if health['very_new_account_ratio'] > 0.2:
            risk_factors.append("⚠️ EXTREME RISK: High ratio of very new accounts (>20%)")
            risk_level = "CRITICAL"
        elif health['new_account_ratio'] > 0.3:
            risk_factors.append("High ratio of new accounts (>30%)")
            risk_level = max(risk_level, "HIGH")
        
        if health['very_low_follower_ratio'] > 0.3:
            risk_factors.append("⚠️ High ratio of extremely low-follower accounts (>30%)")
            risk_level = max(risk_level, "HIGH")
        elif health['low_follower_ratio'] > 0.4:
            risk_factors.append("High ratio of low-follower accounts (>40%)")
            risk_level = max(risk_level, "MEDIUM")
        
        if health['bot_ratio'] > 0.2:
            risk_factors.append("⚠️ High ratio of bot-like activity detected (>20%)")
            risk_level = "CRITICAL"
        
        # Manipulation patterns
        manipulation = self._detect_manipulation(tweets_data)
        
        if manipulation['coordinated_posting']:
            risk_factors.append("⚠️ Coordinated posting patterns detected")
            risk_level = max(risk_level, "HIGH")
        
        repeated_phrases = len(manipulation['repeated_phrases'])
        if repeated_phrases > 5:
            risk_factors.append("⚠️ Multiple suspicious promotional phrases detected")
            risk_level = max(risk_level, "HIGH")
        elif repeated_phrases > 2:
            risk_factors.append("Suspicious promotional language detected")
            risk_level = max(risk_level, "MEDIUM")
        
        suspicious_accounts = len(manipulation['suspicious_accounts'])
        if suspicious_accounts > 5:
            risk_factors.append(f"⚠️ High number of suspicious accounts ({suspicious_accounts})")
            risk_level = max(risk_level, "HIGH")
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'community_health': health,
            'manipulation_signals': manipulation
        }

    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate detailed recommendation based on risk level"""
        risk = analysis['risk_assessment']
        health = analysis['community_health']
        token_metrics = analysis.get('token_metrics', {})
        
        warning_flags = []
        recommendation = ""
        
        # Risk level based recommendations
        if risk['risk_level'] == "CRITICAL":
            warning_flags.append("🚨 CRITICAL RISK DETECTED - High probability of scam!")
            recommendation = "STRONG WARNING: Multiple critical risk factors detected"
        elif risk['risk_level'] == "HIGH":
            warning_flags.append("⚠️ HIGH RISK - Exercise extreme caution!")
            recommendation = "WARNING: Significant risk factors present"
        elif risk['risk_level'] == "MEDIUM":
            warning_flags.append("⚠️ MEDIUM RISK - Proceed with caution")
            recommendation = "CAUTION: Some concerning factors found"
        else:
            recommendation = "Standard caution advised - Always DYOR"
        
        # Add specific warnings based on findings
        if token_metrics.get('age_risk', 0) >= 4:
            warning_flags.append("Very new token - High manipulation risk")
        
        if token_metrics.get('price_risk', 0) >= 4:
            warning_flags.append("Suspicious price movement detected")
        
        if health['very_new_account_ratio'] > 0.2:
            warning_flags.append("Suspicious community composition")
        
        analysis['warning_flags'] = warning_flags
        return recommendation

    def _find_repeated_phrases(self, tweets: List[Dict]) -> List[str]:
        """Find commonly repeated phrases that might indicate coordinated activity"""
        # Extract all text content
        all_text = ' '.join([tweet['text'].lower() for tweet in tweets])
        
        # Find phrases that match suspicious patterns
        suspicious_matches = []
        for pattern in self.suspicious_phrases:
            matches = re.findall(pattern, all_text)
            if matches:
                suspicious_matches.extend(matches)
        
        # Count occurrences
        phrase_counts = Counter(suspicious_matches)
        
        # Return phrases that appear multiple times
        return [phrase for phrase, count in phrase_counts.items() if count >= 2]

    def _detect_coordinated_posting(self, tweets: List[Dict]) -> bool:
        """Detect patterns of coordinated posting"""
        if not tweets:
            return False
            
        try:
            # Sort tweets by timestamp
            sorted_tweets = sorted(tweets, key=lambda x: x['timestamp'])
            
            # Check for clusters of similar posts
            time_clusters = []
            current_cluster = [sorted_tweets[0]]
            
            for i in range(1, len(sorted_tweets)):
                current_time = datetime.fromisoformat(sorted_tweets[i]['timestamp'].replace('Z', '+00:00'))
                prev_time = datetime.fromisoformat(sorted_tweets[i-1]['timestamp'].replace('Z', '+00:00'))
                
                time_diff = (current_time - prev_time).total_seconds()
                
                if time_diff <= self.account_red_flags['coordinated_post_window']:
                    current_cluster.append(sorted_tweets[i])
                else:
                    if len(current_cluster) >= 3:  # If we found a cluster of 3 or more
                        time_clusters.append(current_cluster)
                    current_cluster = [sorted_tweets[i]]
            
            # Check last cluster
            if len(current_cluster) >= 3:
                time_clusters.append(current_cluster)
            
            # If we found any suspicious clusters
            return len(time_clusters) > 0
            
        except Exception as e:
            self.logger.error(f"Error detecting coordinated posting: {str(e)}")
            return False

    def _identify_suspicious_accounts(self, tweets_data: Dict) -> List[str]:
        """Identify potentially suspicious accounts"""
        suspicious_accounts = []
        user_stats = tweets_data['user_stats']
        
        for username, stats in user_stats.items():
            if not stats:
                continue
                
            flags = []
            
            # Check account age
            if stats.get('join_date') != "Unknown":
                join_date = datetime.strptime(stats['join_date'], "%B %Y")
                if (datetime.now() - join_date) < timedelta(days=self.account_red_flags['new_account']):
                    flags.append("New account")
            
            # Check followers
            if stats.get('followers') != "Unknown":
                try:
                    followers = int(stats['followers'].replace(',', ''))
                    if followers < self.account_red_flags['low_followers']:
                        flags.append("Low followers")
                except:
                    pass
            
            # Check multi-coin promotion
            promoted_coins = stats.get('promoted_coins', [])
            if len(promoted_coins) > self.account_red_flags['multi_coin_threshold']:
                flags.append(f"Promotes {len(promoted_coins)} coins")
            
            # Add account to suspicious list if it has multiple flags
            if len(flags) >= 2:
                suspicious_accounts.append({
                    'username': username,
                    'flags': flags
                })
        
        return suspicious_accounts 