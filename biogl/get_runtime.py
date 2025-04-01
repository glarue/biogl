import time

def get_runtime(start_time, p=3):
    """
    Takes a start time and optional decimal precision p,
    returns a string of the total run-time until current
    time with appropriate units.

    """

    total = time.time() - start_time  # start with seconds
    divided = total/60.0
    if divided < 2:
        run_time = total
        units = "seconds"
    elif divided < 60:
        run_time = divided
        units = "minutes"
    else:
        run_time = divided/60.0
        units = "hours"
    rounded = round(run_time, p)

    return "{} {}".format(rounded, units)