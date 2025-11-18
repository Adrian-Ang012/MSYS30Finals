def merge_sort(product_list, field):
    # base case
    if len(product_list) <= 1:
        return product_list

    midpoint = len(product_list) // 2

    left_half = merge_sort(product_list[:midpoint], field)
    right_half = merge_sort(product_list[midpoint:], field)

    return merge_lists(left_half, right_half, field)


def get_field_value(product, field):
    if field == "name":
        return product.name.lower()
    if field == "sku":
        return product.sku.lower()
    if field == "category":
        return product.category.lower()
    if field == "supplier":
        return product.supplier.name.lower()
    if field == "quantity":
        return product.quantity
    if field == "reorder":
        return product.reorder_level
    if field == "price":
        return product.unit_price
    if field == 'contact_person':
        return product.contact_person.lower()

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

def binary_search():
    pass 
    