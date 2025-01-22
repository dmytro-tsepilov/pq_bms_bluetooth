## [0.1.4] - 2025.01.20

### Added
- Added handling exceptions
- Added new fields to response:
    `error_code` - different from zero means error
    `error_message` - human readable error message
- `error_code` added as exit code of script
- Added variable `dischargeSwitchState` - state of internal bluetooth controlled discharge switch

### Fixed
- Fixed rounding of the calculated `watt` variable to two digits
- Fixed detection of cells amount and voltage
- Fixed issue with negative temperature of sensors (thanks @nopeee535)

### Changed
- `SOC` and `SOH` variables changed to integer, without percentage string
- Changed parsing `heat` variable to hex
- Updated minor version of `dbus-fast` library

## [0.1.3] - 2024.11.12

### Added
- Added `--timeout` option for setting timeout in seconds for bluetooth device communication

### Changed
- Updated minor versions of `bleak` and `dbus-fast` libraries

## [0.1.2] - 2024.11.02

### Added
- Added calculated signed `watt` variable
- Added human readable battery status variables: `battery_status`, `balance_status`, `cell_status`

### Changed
- Variables `heat`, `protectState`, `failureState` changed to type list

### Fixed
- Variable `remianAh` changed to `remainAh` (typo fix)
- Fixed parsing `current` value, with output in ampere
- Minor typo fixes

## [0.1.1] - 2024.09.21

### Added
- Added `--pair` option for pairing \ unpairing with devices

## [0.1.0] - 2024.09.21

Initial version.

### Added
 
### Changed

### Fixed
