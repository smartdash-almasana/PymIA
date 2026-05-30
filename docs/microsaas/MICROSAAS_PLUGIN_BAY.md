# MicroSaaS Plugin Bay

## Purpose

This package defines an internal bay for future pluggable MicroSaaS modules in
PymIA. Modules will be described through explicit descriptors and capabilities
before any runtime integration is introduced.

## Boundary

This milestone does not modify Domain Core V1. It does not add runtime services,
database storage, authentication, frontend code, or external integrations.

Future MicroSaaS modules will plug into the bay through
`MicroSaaSDescriptor` and `MicroSaaSCapability` contracts. The first candidate
for a later milestone is Exceland Template Generator.

## Import Rule

A MicroSaaS module must not import `pymia/domain` directly unless an explicit
contract authorizes that dependency.
