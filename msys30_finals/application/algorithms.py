def merge_sort(product_list, field):
    # base case
    if len(product_list) <= 1:
        return product_list

    midpoint = len(product_list) // 2

    left_half = merge_sort(product_list[:midpoint], field)
    right_half = merge_sort(product_list[midpoint:], field)

    return merge_lists(left_half, right_half, field)


def get_field_value(obj, field):
    # Product fields

    field_map = {
        "sku": lambda o: o.sku.lower(),
        "name": lambda o: o.name.lower(),
        "category": lambda o: o.category.lower(),
        "supplier": lambda o: o.supplier.name.lower(),
        "quantity": lambda o: o.quantity,
        "reorder": lambda o: o.reorder_level,
        "price": lambda o: o.unit_price,
        "contact_person": lambda o: o.contact_person.lower()
    }

    # basically If field exists in dictionary, call the stuff
    if field in field_map:
        return field_map[field](obj)

    return ""




def merge_lists(left_list, right_list, field):
    merged_list = []

    left_index = 0
    right_index = 0

    while left_index < len(left_list) and right_index < len(right_list):
        left_value = get_field_value(left_list[left_index], field)
        right_value = get_field_value(right_list[right_index], field)

        if left_value <= right_value:
            merged_list.append(left_list[left_index])
            left_index += 1
        else:
            merged_list.append(right_list[right_index])
            right_index += 1

    # add any remaining items
    while left_index < len(left_list):
        merged_list.append(left_list[left_index])
        left_index += 1

    while right_index < len(right_list):
        merged_list.append(right_list[right_index])
        right_index += 1

    return merged_list

def binary_search(sorted_list, target, field):
    left = 0
    right = len(sorted_list) - 1
    found_index = -1

    # First: standard binary search to find *a* matching index
    while left <= right:
        mid = (left + right) // 2
        mid_value = get_field_value(sorted_list[mid], field)

        if mid_value == target:
            found_index = mid
            break
        elif mid_value < target:
            left = mid + 1
        else:
            right = mid - 1

    # No match
    if found_index == -1:
        return []

    # Second: expand left and right to gather all matches
    results = []

    # go left
    i = found_index
    while i >= 0 and get_field_value(sorted_list[i], field) == target:
        results.append(sorted_list[i])
        i -= 1

    # go right
    j = found_index + 1
    while j < len(sorted_list) and get_field_value(sorted_list[j], field) == target:
        results.append(sorted_list[j])
        j += 1

    return results



def safety_stock(z: float, sigma_demand: Optional[float], lead_time: Optional[float]) -> float:
    """
    safety_stock = z * sigma_demand * sqrt(lead_time)

    - z: service-level z-score (e.g., 1.65 for ≈95% service)
    - sigma_demand: standard deviation of daily demand (can be None)
    - lead_time: lead time in days (can be None)

    Returns float (units). If inputs missing or invalid returns 0.0.
    Complexity: O(1)
    """
    try:
        if sigma_demand is None or lead_time is None:
            return 0.0
        sigma = float(sigma_demand)
        lt = float(lead_time)
        if sigma < 0 or lt <= 0:
            return 0.0
        return float(z) * sigma * math.sqrt(lt)
    except Exception:
        return 0.0


def reorder_point(lead_time: Optional[float],
                  avg_daily_demand: Optional[float],
                  z: float,
                  sigma_demand: Optional[float]) -> float:
    """
    reorder_point = lead_time * avg_daily_demand + safety_stock

    - lead_time: lead time in days
    - avg_daily_demand: average daily demand
    - z, sigma_demand: used by safety_stock()

    Returns float (units). If avg_daily_demand or lead_time missing, returns safety_stock as fallback.
    Complexity: O(1)
    """
    ss = safety_stock(z, sigma_demand, lead_time)
    try:
        if avg_daily_demand is None or lead_time is None:
            return ss
        avg = float(avg_daily_demand)
        lt = float(lead_time)
        return lt * avg + ss
    except Exception:
        return ss
