from bisect import bisect_left, bisect_right

def coord_overlap(coords, coord_list):
    """
    Check a tuple <coords> for overlap within 
    the list of integer coordinate tuples
    <coord_list>. Returns the FIRST overlapping
    tuple and its index from <coord_list>, or 
    None if no overlapping tuples found.
    
    """
    if not coord_list:
        return None
    coord_list = sorted([(c[0], c[1]) for c in coord_list])
    starts, stops = zip(*coord_list)
    c_start, c_stop = coords
    start_idx = bisect_left(stops, c_start)
    stop_idx = bisect_right(starts, c_stop)
    if start_idx != stop_idx:
        overlap_idx = min(start_idx, stop_idx)
        return coord_list[overlap_idx], overlap_idx
    else:
        return None
