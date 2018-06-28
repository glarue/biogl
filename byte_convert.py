def byte_convert(byte_size):
    """
    Converts a number of bytes to a more human-readable
    format.

    """
    # Calculate and display total size of selected data
    adjusted = byte_size / (1024 * 1024)  # bytes to MB
    if adjusted < 1:
        adjusted = byte_size / 1024
        unit = "KB"
    elif adjusted < 1024:
        unit = "MB"
    else:
        adjusted /= 1024
        unit = "GB"
    size_string = "{:.2f} {}".format(adjusted, unit)

    return size_string
