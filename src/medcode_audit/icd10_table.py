"""Hand-checked ICD-10-CM lookup table. See docs/specs/012-code-lookup.md.

Provenance and license: every description is the official ICD-10-CM code
title. ICD-10-CM is maintained by CDC/NCHS, a US federal agency, and is a
public-domain work: the CDC Use of Agency Materials policy states CDC
information is not subject to copyright and may be freely used and
reproduced (cdc.gov/other/agencymaterials.html), and CMS describes NCHS/CDC
ICD-10-CM reference materials as "public domain" (cms.gov GEMs document).
Titles were checked against the FY2026/2027 titles on 2026-10-26 using
icd10data.com as a readable mirror of the official NCHS/CMS files. Per the
NCHS preface, unofficial modifications are not official ICD-10-CM; this
table quotes titles verbatim and modifies nothing. The table covers the five provisional codes plus near relatives
in the same categories. It is NOT a full code set: the day-2 license
question about redistributing the complete set stays open, so nothing is
scraped or bundled. Family membership is structural (same 3-character
category); no severity ordering is recorded or implied.
"""

_CH3 = {'chapter': '3', 'chapter_range': 'D50-D89',
        'chapter_title': 'Diseases of the blood and blood-forming organs '
                         'and certain disorders involving the immune mechanism'}
_CH4 = {'chapter': '4', 'chapter_range': 'E00-E89',
        'chapter_title': 'Endocrine, nutritional and metabolic diseases'}
_CH9 = {'chapter': '9', 'chapter_range': 'I00-I99',
        'chapter_title': 'Diseases of the circulatory system'}
_CH10 = {'chapter': '10', 'chapter_range': 'J00-J99',
         'chapter_title': 'Diseases of the respiratory system'}
_CH14 = {'chapter': '14', 'chapter_range': 'N00-N99',
         'chapter_title': 'Diseases of the genitourinary system'}

# code: (description, category, category_description, block, block_title,
#        chapter-fields)
_ROWS = {
    'E11.9': ('Type 2 diabetes mellitus without complications',
              'E11', 'Type 2 diabetes mellitus',
              'E08-E13', 'Diabetes mellitus', _CH4),
    'E11.8': ('Type 2 diabetes mellitus with unspecified complications',
              'E11', 'Type 2 diabetes mellitus',
              'E08-E13', 'Diabetes mellitus', _CH4),
    'E10.9': ('Type 1 diabetes mellitus without complications',
              'E10', 'Type 1 diabetes mellitus',
              'E08-E13', 'Diabetes mellitus', _CH4),
    'I10': ('Essential (primary) hypertension',
            'I10', 'Essential (primary) hypertension',
            'I10-I16', 'Hypertensive diseases', _CH9),
    'I11.9': ('Hypertensive heart disease without heart failure',
              'I11', 'Hypertensive heart disease',
              'I10-I16', 'Hypertensive diseases', _CH9),
    'I15.9': ('Secondary hypertension, unspecified',
              'I15', 'Secondary hypertension',
              'I10-I16', 'Hypertensive diseases', _CH9),
    'J45.20': ('Mild intermittent asthma, uncomplicated',
               'J45', 'Asthma',
               'J40-J47', 'Chronic lower respiratory diseases', _CH10),
    'J45.30': ('Mild persistent asthma, uncomplicated',
               'J45', 'Asthma',
               'J40-J47', 'Chronic lower respiratory diseases', _CH10),
    'J45.40': ('Moderate persistent asthma, uncomplicated',
               'J45', 'Asthma',
               'J40-J47', 'Chronic lower respiratory diseases', _CH10),
    'J45.50': ('Severe persistent asthma, uncomplicated',
               'J45', 'Asthma',
               'J40-J47', 'Chronic lower respiratory diseases', _CH10),
    'N18.1': ('Chronic kidney disease, stage 1',
              'N18', 'Chronic kidney disease (CKD)',
              'N17-N19', 'Acute kidney failure and chronic kidney disease',
              _CH14),
    'N18.2': ('Chronic kidney disease, stage 2 (mild)',
              'N18', 'Chronic kidney disease (CKD)',
              'N17-N19', 'Acute kidney failure and chronic kidney disease',
              _CH14),
    'N18.31': ('Chronic kidney disease, stage 3a',
               'N18', 'Chronic kidney disease (CKD)',
               'N17-N19', 'Acute kidney failure and chronic kidney disease',
               _CH14),
    'N18.32': ('Chronic kidney disease, stage 3b',
               'N18', 'Chronic kidney disease (CKD)',
               'N17-N19', 'Acute kidney failure and chronic kidney disease',
               _CH14),
    'N18.4': ('Chronic kidney disease, stage 4 (severe)',
              'N18', 'Chronic kidney disease (CKD)',
              'N17-N19', 'Acute kidney failure and chronic kidney disease',
              _CH14),
    'N18.5': ('Chronic kidney disease, stage 5',
              'N18', 'Chronic kidney disease (CKD)',
              'N17-N19', 'Acute kidney failure and chronic kidney disease',
              _CH14),
    'N18.9': ('Chronic kidney disease, unspecified',
              'N18', 'Chronic kidney disease (CKD)',
              'N17-N19', 'Acute kidney failure and chronic kidney disease',
              _CH14),
    'D50.0': ('Iron deficiency anemia secondary to blood loss (chronic)',
              'D50', 'Iron deficiency anemia',
              'D50-D53', 'Nutritional anemias', _CH3),
    'D50.8': ('Other iron deficiency anemias',
              'D50', 'Iron deficiency anemia',
              'D50-D53', 'Nutritional anemias', _CH3),
    'D50.9': ('Iron deficiency anemia, unspecified',
              'D50', 'Iron deficiency anemia',
              'D50-D53', 'Nutritional anemias', _CH3),
    'D64.9': ('Anemia, unspecified',
              'D64', 'Other anemias',
              'D60-D64', 'Aplastic and other anemias and other bone marrow '
                          'failure syndromes', _CH3),
}

TABLE = {
    code: {
        'code': code,
        'description': description,
        'category': category,
        'category_description': category_description,
        'block': block,
        'block_title': block_title,
        **chapter_fields,
    }
    for code, (description, category, category_description, block,
               block_title, chapter_fields) in _ROWS.items()
}
