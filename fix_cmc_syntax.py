#!/usr/bin/env python3
"""
Quick syntax fix for CMC scraper
"""
import re

def fix_cmc_syntax():
    """Fix the syntax errors in the CMC scraper file"""
    print("🔧 FIXING CMC SCRAPER SYNTAX ERRORS...")
    
    # Read the file
    with open('autocrypto_social_bot/scrapers/cmc_scraper.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the broken indentation and syntax issues
    fixes = [
        # Fix the broken content_appeared line
        ('                        content_appeared = driver.execute_script("""', 
         '                            content_appeared = driver.execute_script("""'),
        
        # Fix the broken if/else indentation
        ('                        if content_appeared:\n                                print(f"✅ AI content appeared after click strategy {i + 1}...")\n                                self.logger.info("AI content area appeared after click")\n                            return True\n                            else:\n                                print(f"⚠️ Click strategy {i + 1} didn\'t trigger AI content, trying next...")',
         '                            if content_appeared:\n                                print(f"✅ AI content appeared after click strategy {i + 1}...")\n                                self.logger.info("AI content area appeared after click")\n                                return True\n                            else:\n                                print(f"⚠️ Click strategy {i + 1} didn\'t trigger AI content, trying next...")'),
        
        # Fix the broken except clause
        ('                    except Exception as e:\n                            print(f"❌ Click strategy {i + 1} failed: {str(e)}")\n                            continue',
         '                        except Exception as e:\n                            print(f"❌ Click strategy {i + 1} failed: {str(e)}")\n                            continue'),
        
        # Fix broken wait_for_ai_content method indentation
        ('                            # Get fresh elements each time\n                    elements = self.driver.find_elements(By.XPATH, selector)\n                    for element in elements:\n                                try:\n                        if element.is_displayed():',
         '                            # Get fresh elements each time\n                            elements = self.driver.find_elements(By.XPATH, selector)\n                            for element in elements:\n                                try:\n                                    if element.is_displayed():'),
        
        # Fix return statement indentation
        ('                                    return content\n                                except Exception:\n                                    # Element became stale, continue to next\n                                    continue\n                        except Exception:\n                            continue',
         '                                            return content\n                                except Exception:\n                                    # Element became stale, continue to next\n                                    continue\n                        except Exception:\n                            continue'),
        
        # Fix final return statement
        ('                                    return content\n                                        except Exception:\n                                            continue',
         '                                                return content\n                                        except Exception:\n                                            continue')
    ]
    
    # Apply fixes
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Write the fixed content back
    with open('autocrypto_social_bot/scrapers/cmc_scraper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ CMC scraper syntax errors fixed!")
    return True

if __name__ == "__main__":
    fix_cmc_syntax() 