import io
import json
import pstats
import cProfile
from typing import Any, Optional, Tuple, Union

import numpy as np


# ----------------------------------------------------------------------
def JSON(obj: Any, max_list_len: int = 5, indent: int = 2) -> None:
    """
    JSON representation with truncation and indentation.

    Parameters
    ----------
    obj : Any
        The object to convert to JSON format.
    max_list_len : int, optional
        The maximum number of items to include from a list (default is 5).
    indent : int, optional
        The number of spaces to use as indentation (default is 2).

    Returns
    -------
    None
        This function doesn't return anything; it prints the JSON object.

    """
    # ----------------------------------------------------------------------
    def truncate_list(lst: list) -> list:
        """
        Truncate a list to the specified maximum length and add an ellipsis.

        Parameters
        ----------
        lst : list
            List to be truncated.

        Returns
        -------
        list
            Truncated list.

        """
        if len(lst) > max_list_len:
            return lst[:max_list_len] + ['...']
        else:
            return lst

    # ----------------------------------------------------------------------
    def format_list(lst: list) -> str:
        """
        Format a list as a string, adding an ellipsis if it exceeds the maximum length.

        Parameters
        ----------
        lst : list
            List to be formatted.

        Returns
        -------
        str
            Formatted string representation of the list.

        """
        if len(lst) > max_list_len:
            return '[' + ', '.join(str(item) for item in lst[:max_list_len]) + ', ...]'
        else:
            return '[' + ', '.join(str(item) for item in lst) + ']'

    # ----------------------------------------------------------------------
    def truncate_and_format_lists(obj: Union[list, dict], level: int = 0) -> Union[list, dict, str]:
        """
        Truncate and format lists and dictionaries within the JSON object.

        Parameters
        ----------
        obj : Union[list, dict]
            JSON object to be formatted and truncated.
        level : int, optional
            The current depth level within the JSON object (default is 0).

        Returns
        -------
        Union[list, dict, str]
            Formatted and truncated JSON object.

        """

        # Handle lists within the JSON object
        if isinstance(obj, list):
            return format_list(truncate_list([truncate_and_format_lists(item, level + 1) for item in obj]))

        # Handle dictionaries within the JSON object
        elif isinstance(obj, dict):
            result = '\n' + ' ' * (indent * (level)) + '{\n'
            for key, value in obj.items():
                result += ' ' * (indent * (level + 1)) + f'"{key}": {truncate_and_format_lists(value, level+1)},\n'
            result += ' ' * (indent * level) + '}'
            return result

        # Handle other JSON data types
        else:
            return json.dumps(obj, indent=indent)

    # Process the JSON object and create a truncated and formatted version
    truncated_obj = truncate_and_format_lists(obj)
    # Load the truncated and formatted JSON object as a string
    formatted_obj_str = json.loads(json.dumps(truncated_obj, indent=indent))
    # Correct some formatting issues related to ellipses
    formatted_obj_str = formatted_obj_str.replace(', [...]', ', ...]')
    formatted_obj_str = formatted_obj_str.replace('[...', '[ ...')
    formatted_obj_str = formatted_obj_str.replace(']...', ', ...]')
    # Print the formatted JSON object
    print(formatted_obj_str)


class Profile:
    """
    Context manager for profiling Python code using cProfile and pstats.

    Parameters
    ----------
    sort_key : Optional[pstats.SortKey], default=pstats.SortKey.CUMULATIVE
        The sort key to use for sorting the profiling output.
    stats : Optional[Tuple[str, ...]], default=('ncalls', 'primitive calls', 'time')
        A tuple of stats to display in the profiling output.

    Examples
    --------
    with Profile() as profile:
        some_function()
    print(profile)
    """

    # ----------------------------------------------------------------------
    def __init__(self, sort_key: Optional[pstats.SortKey] = pstats.SortKey.CUMULATIVE,
                 stats: Optional[Tuple[str, ...]] = ('ncalls', 'primitive calls', 'time')) -> None:
        """Initialize the Profile context manager with the specified sort key and stats."""
        self.sort_key = sort_key
        self.stats = stats

    # ----------------------------------------------------------------------
    def __enter__(self) -> None:
        """
        Start the profiling process when entering the context.

        Returns
        -------
        None
        """
        # Create a cProfile.Profile instance and enable it
        self.pr = cProfile.Profile()
        self.pr.enable()

    # ----------------------------------------------------------------------
    def __exit__(self, exc_type: Optional[Any], exc_val: Optional[Any], exc_tb: Optional[Any]) -> None:
        """
        End profiling, process the collected data, and store the results.

        Parameters
        ----------
        exc_type : Optional[Any]
            The exception type, if any.
        exc_val : Optional[Any]
            The exception value, if any.
        exc_tb : Optional[Any]
            The exception traceback, if any.

        Returns
        -------
        None
        """
        # Disable the cProfile.Profile instance and process the results
        self.pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(self.pr, stream=s).sort_stats(self.sort_key)
        ps.print_stats(*self.stats)
        # Store the profiling results as a string
        self.execution_output = s.getvalue()
        # Calculate the total execution time
        total_time = sum(st[2] for st in ps.stats.values())
        self.execution_time = total_time

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        """
        Return the formatted profiling output as a string.

        Returns
        -------
        str
            The formatted profiling output.
        """
        return self.execution_output


# Create a default Profile instance
profile = Profile()


# ----------------------------------------------------------------------
def get_data(data_trials_response: Union[dict, list]) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
    """
    This function processes the input data trials response which could be a dictionary or a list of dictionaries.
    The goal is to convert the input into structured numpy arrays containing data and classes (when available).

    Parameters
    ----------
    data_trials_response : Union[dict, list]
        The data trials response that contains data for trials. Each trial data is
        represented as a dictionary or a list of dictionaries.
        The structure is:
        - 'results': holds the trial results, can be a dictionary or a list of dictionaries.
            - 'values': holds the channel values, which are extracted and added to the data list.
            - 'chunk': when present, represents the class label for a trial, which is added to the classes list.

    Returns
    -------
    Union[Tuple[np.ndarray, np.ndarray], np.ndarray]
        If class labels ('chunk') are available in the input, a tuple containing two numpy arrays is returned:
        the first array represents the data and the second array represents the classes.
        If no class labels are found, a concatenated data array is returned.

    """
    # Convert input to a list if it is a dictionary
    if isinstance(data_trials_response, dict):
        data_trials_response = [data_trials_response]

    data = []
    classes = []

    # Iterate over the data trials response
    for data_trials in data_trials_response:

        # Skip invalid pages
        if data_trials.get('detail', None) == 'Invalid page.':
            continue

        # Process single result dictionaries
        if isinstance(data_trials['results'], dict):
            t = []
            # Extract channel values
            for channel in data_trials['results']['values']:
                t.append(data_trials['results']['values'][channel])
            data.append(t)

        # Process multiple results within a data trial
        else:
            for trial in data_trials['results']:
                t = []

                # Extract channel values
                for channel in trial['values']:
                    t.append(trial['values'][channel])
                data.append(t)

                # Append class label
                classes.append(trial['chunk'])

    # Convert data and classes to numpy arrays
    data = np.array(data)
    classes = np.array(classes)

    # Clean up by deleting the original data_trials_response
    del data_trials_response

    # Return data and classes as a tuple if classes are available, otherwise return concatenated data array
    if classes.size:
        return data, classes
    else:
        return np.concatenate(data, axis=0)
