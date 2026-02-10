def convert_sector_or_index(name: str) -> str:
    """
    Convert between sector name and index name.
    Case-insensitive. Returns the corresponding name if found, else raises an error.
    """
    mapping = {
        'Commercial Banks': 'Banking SubIndex',
        'Development Banks': 'Development Bank Index',
        'Finance': 'Finance Index',
        'Hotels And Tourism': 'Hotels And Tourism',
        'Hydro Power': 'HydroPower Index',
        'Investment': 'Investment',
        'Life Insurance': 'Life Insurance',
        'Manufacturing And Processing': 'Manufacturing And Processing',
        'Microfinance': 'Microfinance Index',
        'Non Life Insurance': 'Non Life Insurance',
        'Others': 'Others Index',
        'Tradings': 'Trading Index'
    }

    # Build reverse mapping
    reverse_mapping = {v.lower(): k for k, v in mapping.items()}

    # Normalize input
    name_clean = name.strip().lower()

    # Check and return match from either direction
    for sector, index in mapping.items():
        if name_clean == sector.lower():
            return index
        if name_clean == index.lower():
            return sector

    raise ValueError(f"No match found for '{name}' in sector or index names.")
