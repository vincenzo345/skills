# Standards and implementation plan

Apply the repository's flat skill-package contract to the two missing companions. Keep automatic discovery enabled, use one portable behavior contract per skill, add required UI metadata, declare both in the plugin and README, and bump the plugin version. Change Workbench's specialist language at its routing and discovery seams, then add structural and behavior-contract regression checks.

Acceptance is the combined pass of repository skill validation, both individual skill validators, Claude marketplace and plugin validation, the focused adherence tests, and the complete local test suite. No migration, external release, or persisted-data work is required.
