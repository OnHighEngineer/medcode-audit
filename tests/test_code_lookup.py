"""Frozen tests for spec 012 (code lookup). Written before the module."""
import pytest

from medcode_audit.code_lookup import (family, is_known, known_codes, lookup)

FIVE = ('E11.9', 'I10', 'J45.30', 'N18.31', 'D50.9')


def test_five_provisional_codes_present():
    for code in FIVE:
        assert is_known(code), code
        entry = lookup(code)
        assert entry['code'] == code
        assert entry['description']


def test_exact_descriptions():
    assert lookup('E11.9')['description'] == (
        'Type 2 diabetes mellitus without complications')
    assert lookup('I10')['description'] == 'Essential (primary) hypertension'
    assert lookup('J45.30')['description'] == (
        'Mild persistent asthma, uncomplicated')
    assert lookup('N18.31')['description'] == (
        'Chronic kidney disease, stage 3a')
    assert lookup('D50.9')['description'] == (
        'Iron deficiency anemia, unspecified')


def test_hierarchy_fields_complete():
    for code in FIVE:
        entry = lookup(code)
        for key in ('category', 'category_description', 'block',
                    'block_title', 'chapter', 'chapter_range',
                    'chapter_title', 'family'):
            assert key in entry, (code, key)
        assert code.startswith(entry['category'].rstrip('.')) or \
            entry['category'].startswith(code[:3])
        assert code in entry['family']


def test_family_groups_same_category():
    assert 'N18.32' in family('N18.31')
    assert 'N18.31' in family('N18.32')
    assert 'J45.20' in family('J45.30')
    assert 'J45.50' in family('J45.40')
    assert 'E11.9' not in family('I10')


def test_normalization_case_and_whitespace():
    assert lookup('e11.9')['code'] == 'E11.9'
    assert lookup('  N18.31\n')['code'] == 'N18.31'
    assert is_known('j45.30')


def test_unknown_valid_shape_raises_lookup_error():
    with pytest.raises(LookupError):
        lookup('A00.0')
    assert not is_known('A00.0')
    with pytest.raises(LookupError):
        family('Z99.9')


@pytest.mark.parametrize('bad', ['11.9', 'E1', 'E119X', 'E.11', 'E11.9X7',
                                 'E11..9', ''])
def test_bad_shape_raises_value_error(bad):
    with pytest.raises(ValueError):
        lookup(bad)


@pytest.mark.parametrize('bad', [None, 119, 11.9, ['E11.9'], {'c': 'E11.9'}])
def test_non_string_raises_value_error(bad):
    with pytest.raises(ValueError):
        lookup(bad)


def test_is_known_tolerates_garbage_without_raising():
    assert is_known(None) is False
    assert is_known('not-a-code') is False


def test_known_codes_sorted_and_contains_five():
    codes = known_codes()
    assert tuple(sorted(codes)) == codes
    for code in FIVE:
        assert code in codes


def test_returned_dict_is_a_fresh_copy():
    entry = lookup('E11.9')
    entry['description'] = 'corrupted'
    assert lookup('E11.9')['description'] == (
        'Type 2 diabetes mellitus without complications')
    again = lookup('E11.9')
    assert again is not entry
