# DEV
# 0.0.12
- Update for django 1.11.7
- Make serve and redirect views configurable
- Move endpoint settings into API_ENDPOINTS dict (backwards incompatible change)
- Update for dj-core-drf 0.0.8
# 0.0.11
- Revert to using dj-core['defaults'] in defaults
# 0.0.10
- Use dj-core-drf's 'defaults' extras install option
- Update for dj-core-drf 0.0.7
- Fix bug when getting values from QueryDict
# 0.0.9
- Update for dj-core-drf 0.0.6
- Fix bug in Image endpoint modifying immutable data
# 0.0.8
- Fix bug in `skeleton_data` using old settings
# 0.0.7
- Update for dj-core 0.0.6
- Add wagtailnest to apps if not detected by dj-core
# 0.0.6
- Add .pyup.yml
- Update user forms for wagtail 1.12
- Move dependencies onto dj-core-drf
- Add LICENSE, CHANGELOG.md
- Change setup.py to use requirements-production.txt
- Remove email, tests modules from package
# 0.0.5
- Remove requirements.txt, local-dev requirements
- Split paragraphs in README
# 0.0.4
- Move Metadata class to its own module
- Add Metadata class which more information
- Fix CSRF_TRUSTED_ORIGINS defaults
- Add default LOGIN_URL
- Add default CSRF_TRUSTED_ORIGINS defaults
- Add django_filters to installed apps
- Add ability to define panels on the admin
- Fix setting the debug defaults
- Use wagtailnest's LoginSerializer by default
- Catch exception when user model is not standard
- Lowercase email address on login
- Lowercase email address in PasswordResetSerializer
- Handle DEPLOYMENT_ env prefix more seamlessly
- Add admins/managers config
# 0.0.3
- Allow djdt to be disabled
- Add disable switch for account registration
- Update defaults config in settings
- Clean up python package requirements
- Stop appending port number to domain if 80 or 443
- Stop development settings overriding defaults
- Remove project specific implementation
- Add skeleton_data to setup default Sites and User
- Stop DEBUG settings being overridden
- Add MANIFEST.in to include all files in src/ dir
- Fix issue with anymail backend naming
- Install all files in src directory
- Remove proxies
- Add more settings, adds settings from environment
# 0.0.2
- Update directories in settings
- Add more explicit settings config via globals()
- Add development requirements
- Remove default DJANGO_SETTINGS_MODULE
- Fold individual Django wrapper into project
- Move from a submodule to a package
# 0.0.1
Initial release
