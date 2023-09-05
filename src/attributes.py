pairings = [
    "Lithology",
    "Primary alteration",
    "Secondary alteration",
    "Lithology-Primary alteration",
    "Lithology-Secondary alteration",
    "Primary alteration-Secondary alteration",
    "Lithology-Primary alteration-Secondary alteration",
]
namemap = dict(
    zip(
        pairings,
        [
            "lithology_relog",
            "primary_alteration",
            "secondary_alteration",
            "lithology_relog_primary_alteration",
            "lithology_relog_secondary_alteration",
            "primary_alteration_secondary_alteration",
            "lithology_relog_primary_alteration_secondary_alteration",
        ],
    )
)
