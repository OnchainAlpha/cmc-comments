# Unused Files Archive

This directory contains files that were moved from the main project directory to keep the repository organized and clean.

## Directory Structure

### `test_files/`
Contains standalone test files and verification scripts that are not part of the main application flow:
- `test_ai_review.py` - Standalone test for AI review functionality (different from the one in autocrypto_social_bot/)
- `test_ai_button.py` - Standalone button testing script
- `test_button_finder.py` - Button finder testing utility
- `test_cmc_connectivity.py` - CMC connectivity testing script
- `test_enterprise_proxy_system.py` - Enterprise proxy system testing script
- `test_ip_rotation.py` - IP rotation testing script
- `verify_enhanced_ip_rotation.py` - IP rotation verification utility (referenced in troubleshooting docs)

### `documentation/`
Contains development documentation and implementation notes:
- `COMPREHENSIVE_FIXES.md` - Development notes on fixes applied
- `ENHANCED_COMPLETE.md` - Enhancement completion documentation
- `ENHANCED_IP_ROTATION_COMPLETE.md` - IP rotation implementation documentation
- `FIXES_APPLIED.md` - List of fixes that were applied
- `IP_ROTATION_IMPLEMENTATION.md` - IP rotation implementation details
- `roadmap.txt` - Development roadmap notes

### `temp_files/`
Contains temporary files, analysis outputs, and old configuration files:
- `button_analysis.json` - Button analysis output
- `cmc_page_source.html` - Captured CMC page source
- `analysis_*.txt` - Various token analysis outputs
- `failed_post_*.txt` - Failed post log files
- `*.png` - Screenshot files
- `old_promotion_config.json` - Old promotion configuration (from autocrypto_social_bot/config/)
- `old_proxy_config.json` - Old proxy configuration (from autocrypto_social_bot/config/)
- `old_enterprise_proxy_config.json` - Old enterprise proxy configuration (from autocrypto_social_bot/config/)

### `build_artifacts/`
Contains build-related files:
- `autocrypto_social_bot.egg-info/` - Python package build artifacts

## Active Configuration

The main application uses the following configuration structure:
- `config/` (root level) - Active configuration directory used by the application
- `autocrypto_social_bot/config/` - Module-specific settings (settings.py, config.json, etc.)

## Notes

- All files moved here were either duplicates, temporary outputs, or standalone utilities not integrated into the main application flow
- The main application functionality remains intact
- Test files can still be run if needed for debugging or development
- Configuration files were moved to avoid confusion between active and old configurations

Last organized: June 23, 2025 