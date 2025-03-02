# SPDX-License-Identifier: GPL-3.0-or-later
"""
Formats the data queried from Wikidata using query_verbs.sparql.
"""

import argparse
import collections

from scribe_data.utils import (
    export_formatted_data,
    load_queried_data,
    remove_queried_data,
)

parser = argparse.ArgumentParser()
parser.add_argument("--dir-path")
parser.add_argument("--language")
parser.add_argument("--data_type")
args = parser.parse_args()


def format_data(
    dir_path: str = args.dir_path,
    language: str = args.language,
    data_type: str = args.data_type,
):
    """
    Format data queried from the Wikidata Query Service.

    Parameters
    ----------
    dir_path : str
        The output directory path for results.

    language : str
        The language for which the data is being loaded.

    data_type : str
        The type of data being loaded (e.g. 'nouns', 'verbs').

    Returns
    -------
    None
        Saves and formatted data file for the given language and data type.
    """
    data_list, data_path = load_queried_data(
        dir_path=dir_path, language=language, data_type=data_type
    )

    data_formatted = {}

    for data_vals in data_list:
        lexeme_id = data_vals["lexemeID"]
        modified_date = data_vals["lastModified"]

        # Initialize a new entry if this lexeme hasn't been seen yet.
        if lexeme_id not in data_formatted:
            data_formatted[lexeme_id] = {}
            for key, value in data_vals.items():
                if key not in ["lexemeID", "lastModified"]:
                    data_formatted[lexeme_id][key] = value
            data_formatted[lexeme_id]["lastModified"] = modified_date
        else:
            # Merge fields for an existing lexeme.
            for field, value in data_vals.items():
                if field in ["lexemeID", "lastModified"]:
                    continue
                if value:  # Only process non-empty values.
                    if (
                        field in data_formatted[lexeme_id]
                        and data_formatted[lexeme_id][field]
                    ):
                        # Merge field values into a comma-separated string using a set for uniqueness.
                        existing_values = set(
                            data_formatted[lexeme_id][field].split(", ")
                        )
                        existing_values.add(value)
                        data_formatted[lexeme_id][field] = ", ".join(
                            sorted(existing_values)
                        )
                    else:
                        data_formatted[lexeme_id][field] = value

    # Convert the dictionary to an ordered dictionary for consistent output.
    data_formatted = collections.OrderedDict(sorted(data_formatted.items()))

    export_formatted_data(
        dir_path=dir_path,
        formatted_data=data_formatted,
        language=language,
        data_type=data_type,
    )

    remove_queried_data(dir_path=dir_path, language=language, data_type=data_type)


if __name__ == "__main__":
    format_data()
