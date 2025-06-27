#!/usr/bin/env python3
"""
Direct CMC Automation Script
Bypasses all menus and starts the comment generation process immediately
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 DIRECT CMC AUTOMATION - STARTING COMMENT GENERATION")
    print("="*80)
    print("🎯 This will immediately start:")
    print("   1. Finding trending coins on CMC")
    print("   2. Getting AI reviews from CMC") 
    print("   3. Processing with DeepSeek AI")
    print("   4. Mixing with promotional content")
    print("   5. Posting comments to CMC community")
    print("="*80)
    
    try:
        from autocrypto_social_bot.main import CryptoAIAnalyzer
        
        print("\n📊 Initializing analyzer...")
        analyzer = CryptoAIAnalyzer()
        
        print("\n🎯 Starting AUTOMATED CMC mode...")
        print("This will process trending coins and generate promotional comments")
        
        # Run the automated mode directly
        analyzer._run_automated_mode()
        
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 