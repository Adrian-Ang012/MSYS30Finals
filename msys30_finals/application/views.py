from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Product, Supplier, ReorderAlert
from .algorithms import merge_sort, binary_search



# DASHBOARD PAGE
def dashboard(request):
    products = Product.objects.all()
    low_stock_items = [p for p in products if p.is_low_stock()]

    context = {
        'total_products': products.count(),
        'low_stock_count': len(low_stock_items),
        'supplier_count': Supplier.objects.count(),
        'last_update': timezone.now().strftime("%b %d, %Y"),
        'low_stock_items': low_stock_items,
    }
    return render(request, 'myapp/dashboard.html', context)



def inventory_list(request):
    # get all products
    product_list = list(Product.objects.all())

    # sort the list using merge sort
    sort_field = request.GET.get("sort", "name")
    sorted_products = merge_sort(product_list, sort_field)

    # CREATE THE HASH MAP (SKU -> Product)
    product_map = {}
    for product in sorted_products:
        product_map[product.sku.upper()] = product

    # get search text
    search_text = request.GET.get("search_query", "").strip().upper()

    # CASE 1: no search
    if search_text == "":
        context = {
            "products": sorted_products,
            "product_map": product_map  
        }
        return render(request, "myapp/inventory_list.html", context)
    
    # CASE 2: exact search
    # First check SKU using hash map (O(1))
    if search_text in product_map:
        context = {"products": [product_map[search_text]]}
        return render(request, "myapp/inventory_list.html", context)

    # If not SKU, try name using binary search (O(log n))
    search_result = binary_search(sorted_products, search_text)

    if search_result:
        context = {"products": [search_result]}
    else:
        context = {"products": []}

    return render(request, "myapp/inventory_list.html", context)






# ADD PRODUCT PAGE
def add_product(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        name = request.POST.get('name')
        category = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        quantity = int(request.POST.get('quantity'))
        reorder_level = int(request.POST.get('reorder_level'))
        unit_price = float(request.POST.get('unit_price'))

        supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None

        Product.objects.create(
            sku=sku,
            name=name,
            category=category,
            supplier=supplier,
            quantity=quantity,
            reorder_level=reorder_level,
            unit_price=unit_price
        )
        return redirect('inventory_list')

    suppliers = Supplier.objects.all()
    return render(request, 'myapp/add_product.html', {'suppliers': suppliers})


# EDIT PRODUCT PAGE
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.sku = request.POST.get('sku')
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        product.supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None
        product.quantity = int(request.POST.get('quantity'))
        product.reorder_level = int(request.POST.get('reorder_level'))
        product.unit_price = float(request.POST.get('unit_price'))
        product.save()
        return redirect('inventory_list')

    suppliers = Supplier.objects.all()
    return render(request, 'myapp/edit_product.html', {'product': product, 'suppliers': suppliers})


# DELETE PRODUCT
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('inventory_list')
    return render(request, 'myapp/delete_product.html', {'product': product})


# SUPPLIER LIST PAGE
def supplier_list(request):

    supplier_list = list(Supplier.objects.all())

    # sort using the SAME merge_sort as products
    sort_field = request.GET.get("sort", "name")
    sorted_suppliers = merge_sort(supplier_list, sort_field)

    # hash map for name → supplier
    supplier_map = {sup.name.upper(): sup for sup in sorted_suppliers}

    search_text = request.GET.get("search_query", "").strip().upper()

    # no search
    if search_text == "":
        return render(request, "myapp/supplier_list.html", {"suppliers": sorted_suppliers})

    # hash map (O(1) name lookup)
    if search_text in supplier_map:
        return render(request, "myapp/supplier_list.html", {"suppliers": [supplier_map[search_text]]})

    # fallback: binary search (name only)
    result = binary_search(sorted_suppliers, search_text)

    if result:
        final_list = [result]
    else:
        final_list = []

    return render(request, "myapp/supplier_list.html", {"suppliers": final_list})






def add_supplier(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        Supplier.objects.create(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address
        )
        return redirect('supplier_list')

    return render(request, 'myapp/add_supplier.html')

# REORDER SUGGESTIONS PAGE
def reorder_suggestions(request):
    products = Product.objects.all()
    reorder_items = [p for p in products if p.is_low_stock()]
    return render(request, 'myapp/reorder_suggestions.html', {'reorder_items': reorder_items})
