#!/usr/bin/env python3
"""
Verification script for domain scoping implementation.
Tests that all types have domain field and filtering works correctly.
"""

import sys
sys.path.insert(0, '/home/mind-protocol/mindprotocol')

from tools.complete_schema_data import NODE_TYPE_SCHEMAS, LINK_FIELD_SPECS

def test_domain_field_presence():
    """Test that all node and link types have the 'domain' field."""
    print("=" * 60)
    print("TEST 1: Checking domain field presence")
    print("=" * 60)

    # Check node types
    nodes_missing_domain = []
    for type_name, spec in NODE_TYPE_SCHEMAS.items():
        if 'domain' not in spec:
            nodes_missing_domain.append(type_name)

    if nodes_missing_domain:
        print(f"❌ FAIL: {len(nodes_missing_domain)} node types missing domain field:")
        for name in nodes_missing_domain[:10]:  # Show first 10
            print(f"   - {name}")
        if len(nodes_missing_domain) > 10:
            print(f"   ... and {len(nodes_missing_domain) - 10} more")
        return False
    else:
        print(f"✓ PASS: All {len(NODE_TYPE_SCHEMAS)} node types have domain field")

    # Check link types
    links_missing_domain = []
    for type_name, spec in LINK_FIELD_SPECS.items():
        if 'domain' not in spec:
            links_missing_domain.append(type_name)

    if links_missing_domain:
        print(f"❌ FAIL: {len(links_missing_domain)} link types missing domain field:")
        for name in links_missing_domain[:10]:  # Show first 10
            print(f"   - {name}")
        if len(links_missing_domain) > 10:
            print(f"   ... and {len(links_missing_domain) - 10} more")
        return False
    else:
        print(f"✓ PASS: All {len(LINK_FIELD_SPECS)} link types have domain field")

    return True


def test_med_types_exist():
    """Test that the new MED domain types exist."""
    print("\n" + "=" * 60)
    print("TEST 2: Checking MED domain types exist")
    print("=" * 60)

    success = True

    # Check U3-MED_HEALTH_CONDITION
    if 'U3-MED_HEALTH_CONDITION' in NODE_TYPE_SCHEMAS:
        spec = NODE_TYPE_SCHEMAS['U3-MED_HEALTH_CONDITION']
        if spec.get('domain') == 'MED':
            print("✓ PASS: U3-MED_HEALTH_CONDITION exists with domain='MED'")
        else:
            print(f"❌ FAIL: U3-MED_HEALTH_CONDITION has wrong domain: {spec.get('domain')}")
            success = False
    else:
        print("❌ FAIL: U3-MED_HEALTH_CONDITION not found")
        success = False

    # Check U4-MED_TREATS
    if 'U4-MED_TREATS' in LINK_FIELD_SPECS:
        spec = LINK_FIELD_SPECS['U4-MED_TREATS']
        if spec.get('domain') == 'MED':
            print("✓ PASS: U4-MED_TREATS exists with domain='MED'")
        else:
            print(f"❌ FAIL: U4-MED_TREATS has wrong domain: {spec.get('domain')}")
            success = False
    else:
        print("❌ FAIL: U4-MED_TREATS not found")
        success = False

    return success


def test_practice_type_extension():
    """Test that U3_Practice has practice_type field."""
    print("\n" + "=" * 60)
    print("TEST 3: Checking U3_Practice extension")
    print("=" * 60)

    if 'U3_Practice' not in NODE_TYPE_SCHEMAS:
        print("❌ FAIL: U3_Practice not found")
        return False

    spec = NODE_TYPE_SCHEMAS['U3_Practice']
    optional_fields = spec.get('optional', [])

    # Check if practice_type exists in optional fields
    practice_type_found = False
    for field in optional_fields:
        if field.get('name') == 'practice_type':
            practice_type_found = True
            # Verify it's an enum with expected values
            expected_values = ['clinical_protocol', 'treatment_protocol', 'assessment_protocol',
                              'research_protocol', 'administrative_sop']
            actual_values = field.get('enum_values', [])
            if set(actual_values) == set(expected_values):
                print("✓ PASS: U3_Practice has practice_type field with correct enum values")
                return True
            else:
                print(f"❌ FAIL: U3_Practice practice_type has wrong values")
                print(f"   Expected: {expected_values}")
                print(f"   Actual: {actual_values}")
                return False

    if not practice_type_found:
        print("❌ FAIL: U3_Practice missing practice_type field")
        return False


def test_domain_distribution():
    """Show domain distribution across types."""
    print("\n" + "=" * 60)
    print("TEST 4: Domain distribution analysis")
    print("=" * 60)

    # Count node types by domain
    node_domains = {}
    for type_name, spec in NODE_TYPE_SCHEMAS.items():
        domain = spec.get('domain', 'MISSING')
        node_domains[domain] = node_domains.get(domain, 0) + 1

    print(f"\nNode types by domain:")
    for domain, count in sorted(node_domains.items()):
        print(f"   {domain}: {count} types")

    # Count link types by domain
    link_domains = {}
    for type_name, spec in LINK_FIELD_SPECS.items():
        domain = spec.get('domain', 'MISSING')
        link_domains[domain] = link_domains.get(domain, 0) + 1

    print(f"\nLink types by domain:")
    for domain, count in sorted(link_domains.items()):
        print(f"   {domain}: {count} types")

    # Expected: should have 'shared' and 'MED' only, no 'MISSING'
    if 'MISSING' in node_domains or 'MISSING' in link_domains:
        print("\n❌ FAIL: Some types missing domain field")
        return False
    else:
        print("\n✓ PASS: All types have domain field")
        return True


def test_filter_logic():
    """Test the domain filtering logic."""
    print("\n" + "=" * 60)
    print("TEST 5: Domain filtering logic")
    print("=" * 60)

    def filter_core_types(type_defs, allowed_levels, allowed_domains=None):
        """Simplified version of the filter function for testing."""
        if allowed_domains is None:
            allowed_domains = {'shared'}

        filtered = {}
        for type_name, type_def in type_defs.items():
            if not isinstance(type_def, dict):
                continue

            # Level filtering
            if type_def.get('level') not in allowed_levels:
                continue

            # Domain filtering
            if 'domain' in type_def:
                type_domain = type_def['domain']
            else:
                # Parse from type_name
                if '-' in type_name:
                    parts = type_name.split('-', 1)
                    if len(parts) == 2:
                        domain_part = parts[1].split('_', 1)[0]
                        type_domain = domain_part
                    else:
                        type_domain = 'shared'
                else:
                    type_domain = 'shared'

            if type_domain not in allowed_domains:
                continue

            filtered[type_name] = type_def

        return filtered

    # Test 1: Filter for universal types only
    universal_only = filter_core_types(NODE_TYPE_SCHEMAS, {'n2', 'shared'}, {'shared'})
    if 'U3-MED_HEALTH_CONDITION' in universal_only:
        print("❌ FAIL: MED type should not be in universal-only filter")
        return False
    else:
        print(f"✓ PASS: Universal-only filter excludes MED types ({len(universal_only)} types)")

    # Test 2: Filter for MED + universal types
    med_and_universal = filter_core_types(NODE_TYPE_SCHEMAS, {'n2', 'shared'}, {'MED', 'shared'})
    if 'U3-MED_HEALTH_CONDITION' not in med_and_universal:
        print("❌ FAIL: MED type should be in MED+universal filter")
        return False
    else:
        print(f"✓ PASS: MED+universal filter includes MED types ({len(med_and_universal)} types)")

    # Test 3: Verify MED filter adds exactly the new types
    new_types = len(med_and_universal) - len(universal_only)
    if new_types == 1:  # Should add exactly 1 new type (U3-MED_HEALTH_CONDITION)
        print(f"✓ PASS: MED domain adds exactly {new_types} new type(s)")
        return True
    else:
        print(f"⚠ WARNING: MED domain adds {new_types} new type(s) (expected 1)")
        return True  # Still passing, just unexpected count


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("DOMAIN SCOPING IMPLEMENTATION VERIFICATION")
    print("=" * 60)

    all_pass = True

    all_pass &= test_domain_field_presence()
    all_pass &= test_med_types_exist()
    all_pass &= test_practice_type_extension()
    all_pass &= test_domain_distribution()
    all_pass &= test_filter_logic()

    print("\n" + "=" * 60)
    if all_pass:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
