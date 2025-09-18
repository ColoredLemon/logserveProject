# parser.py
def count_lines(filepath):
    """
    Counts the total number of lines in a given file.
    """
    try:
        with open(filepath, 'r') as file:
            line_count = sum(1 for line in file)
        return line_count, None # Returns the count and no error
    except FileNotFoundError:
        return None, "Error: The file was not found."