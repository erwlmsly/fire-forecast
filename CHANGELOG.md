# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-09-04

### Added
- Enhanced data validation for SPC fire weather outlooks
- New `_has_valid_geometry_and_risk()` function to validate both geometry and risk levels
- Improved logging with specific messages for different data scenarios
- Support for mixed scenarios (fire weather outlooks empty but dry lightning data available)
- Summary statistics showing count of days with each type of forecast data

### Changed
- **BREAKING**: Updated validation logic to require both valid geometry AND dn != 0 for risk areas
- Enhanced plotting logic to handle no-risk areas (dn = 0) properly
- Updated dry lightning styling to use brown transparent fill with brown border
- Simplified legend labels by removing "Fire Weather" from elevated/critical/extreme
- Removed legend titles from both SPC and BOM maps for cleaner design
- Reduced horizontal spacing between map columns to give legend more room
- Improved "Limited Fire Weather Concerns" display logic for various scenarios

### Fixed
- Fixed issue where SPC API responses with valid geometry but dn = 0 were incorrectly reported as having active outlooks
- Fixed mixed scenario handling where dry lightning data wasn't displayed when fire weather outlooks were empty
- Fixed font consistency issues in legend titles
- Fixed plotting of no-risk areas that had geometry but represented no actual fire weather concerns

### Technical Details
- **SPC Data Validation**: Now properly distinguishes between:
  - No data (no geometry)
  - No-risk data (geometry with dn = 0) 
  - Actual risk data (geometry with dn != 0)
- **Visual Improvements**: 
  - Dry lightning areas: Brown fill/border
  - Fire weather areas: Orange (Elevated), Red (Critical), Purple (Extreme)
  - Clean legends without redundant titles
- **Logging Enhancements**:
  - "Both fire weather outlooks and dry lightning risk areas found"
  - "Fire weather outlooks found (no dry lightning risk)"
  - "Dry lightning risk areas found (no general fire weather outlooks)"
  - "No active fire weather outlooks (no elevated fire weather conditions)"

## [0.1.0] - 2025-01-01

### Added
- Initial release
- SPC fire weather outlook scraping and mapping
- BOM fire danger rating scraping and mapping
- Basic plotting functionality with Google Maps tiles
- Support for 4-day forecasts
- Custom Space Mono font integration
