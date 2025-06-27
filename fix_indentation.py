#!/usr/bin/env python3
"""
Fix specific indentation errors in CMC scraper
"""
import re

def fix_indentation_errors():
    """Fix the specific indentation errors causing syntax issues"""
    print("🔧 FIXING INDENTATION ERRORS IN CMC SCRAPER...")
    
    # Read the file
    with open('autocrypto_social_bot/scrapers/cmc_scraper.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix specific problematic lines
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Fix the problematic lines around 1310-1336
        if line_num == 1310 and '                        # ENHANCED:' in line:
            # Fix over-indented comment
            fixed_lines.append('                            # ENHANCED: Check for AI content appearance with more indicators\n')
        elif line_num == 1311 and 'content_appeared = driver.execute_script(' in line:
            # Fix over-indented content_appeared
            fixed_lines.append('                            content_appeared = driver.execute_script("""\n')
        elif line_num == 1336 and '                            except Exception as e:' in line:
            # Fix misaligned except
            fixed_lines.append('                        except Exception as e:\n')
        elif line_num == 1337 and '                            print(' in line:
            # Fix print statement alignment
            fixed_lines.append('                            print(f"❌ Click strategy {i + 1} failed: {str(e)}")\n')
        elif line_num == 1338 and '                            continue' in line:
            # Fix continue alignment
            fixed_lines.append('                            continue\n')
        elif 'return content' in line and '                                    return content' in line:
            # Fix over-indented return statements
            fixed_lines.append('                                            return content\n')
        else:
            # Keep line as-is
            fixed_lines.append(line)
    
    # Write the fixed content back
    with open('autocrypto_social_bot/scrapers/cmc_scraper.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Indentation errors fixed!")
    
    # Test compilation
    try:
        import py_compile
        py_compile.compile('autocrypto_social_bot/scrapers/cmc_scraper.py', doraise=True)
        print("✅ CMC scraper compiles successfully!")
        return True
    except Exception as e:
        print(f"❌ Still has syntax errors: {str(e)}")
        return False

if __name__ == "__main__":
    fix_indentation_errors() 