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