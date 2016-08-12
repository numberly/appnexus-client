# Change Log
All notable changes to this project will be documented in this file
This project adheres to [Semantic Versioning](http://semver.org/)

## [Unreleased]
 - There is no unreleased changes yet

## [0.1.3] - 2016-08-12
### Removed
 - Remove the envelope creation in services, since at least `custom-model`
   behave differently than other services and it breaks it

## [0.1.2] - 2016-08-11
### Added
 - Allow to change `representation`, `debug` and `test` settings with `connect`
   method
 - Automaticaly create the envelope in services

### Fixed
 - Fixed an IndexError occuring when getting first element of an empty cursor


[Unreleased]: https://github.com/numberly/appnexus-client/compare/0.1.2...HEAD
[0.1.2]: https://github.com/numberly/appnexus-client/compare/04af0c9a447c235bb8ba2512f710ac905c5d0c48...0.1.2
