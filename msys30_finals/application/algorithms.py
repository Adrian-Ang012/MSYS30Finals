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



def generate_reorder_alerts(product_list: List[Any],
                            z: float = 1.65,
                            default_lead_time: float = 7.0) -> List[Tuple[Any, float, float]]:
    """
    Generate reorder alerts.

    For each product in product_list, compute a reorder point (ROP) using:
      safety_stock = z * sigma_demand * sqrt(lead_time)
      reorder_point = lead_time * avg_daily_demand + safety_stock

    If avg_daily_demand is missing, fall back to comparing quantity <= reorder_level (if present).
    Returns a list of tuples: (product, reorder_point, days_to_stockout), for products where
    quantity <= reorder_point or quantity <= reorder_level (fallback).
    The returned list is sorted by urgency (days_to_stockout ascending).

    Complexity: O(n) to scan n products; sorting the candidate list is O(k log k) where
    k is number of candidates.
    """
    candidates: List[Tuple[Any, float, float]] = []

    def _get_attr_or_key(p, key):
        # try attribute access first, then dict access
        if hasattr(p, key):
            return getattr(p, key)
        if isinstance(p, dict):
            return p.get(key)
        return None

    def _safe_float(x, default=0.0):
        try:
            return float(x)
        except Exception:
            return default

    for p in product_list:
        qty = _get_attr_or_key(p, "quantity")
        qty = _safe_float(qty, 0.0)
        avg = _get_attr_or_key(p, "avg_daily_demand")
        sigma = _get_attr_or_key(p, "sigma_demand")
        lead = _get_attr_or_key(p, "lead_time")
        ro_level = get_field_value(p, "reorder")

        # use default lead time if not provided
        lead = default_lead_time if lead is None else _safe_float(lead, default_lead_time)
        sigma_f = 0.0 if sigma is None else _safe_float(sigma, 0.0)

        # if average daily demand missing or zero, fallback to static reorder_level
        if avg is None or (_safe_float(avg, 0.0) <= 0.0):
            if ro_level is not None and ro_level != "":
                try:
                    ro_val = _safe_float(ro_level)
                    if qty <= ro_val:
                        days = float("inf")  # no demand info
                        candidates.append((p, ro_val, days))
                except Exception:
                    # skip malformed values
                    continue
            # cannot compute ROP without demand info, skip otherwise
            continue

        avg_f = _safe_float(avg)
        # compute safety stock and reorder point
        safety = z * sigma_f * math.sqrt(max(0.0, lead))
        rp = lead * avg_f + safety

        # estimate days to stockout (qty / avg)
        days = float("inf")
        if avg_f > 0:
            days = qty / avg_f

        # candidate if current qty <= reorder point
        if qty <= rp:
            candidates.append((p, rp, days))

    # sort candidates by urgency (smaller days_to_stockout => more urgent)
    # treat inf as very large number so they appear at end
    candidates.sort(key=lambda tup: tup[2] if tup[2] != float("inf") else 1e12)

    return candidates
