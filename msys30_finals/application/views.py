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

def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.name = request.POST.get("name")
        supplier.contact_person = request.POST.get("contact_person")
        supplier.phone = request.POST.get("phone")
        supplier.email = request.POST.get("email")
        supplier.address = request.POST.get("address")
        supplier.save()
        return redirect('supplier_list')
    return render(request, "myapp/edit_supplier.html", {"supplier": supplier})


def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        return redirect('supplier_list')
    return render(request, "myapp/delete_supplier.html", {"supplier": supplier})


def inventory_list(request):
    # get all products
    product_list = list(Product.objects.all())

    # SORT DROPDOWN
    sort_field = request.GET.get("sort", "name")
    sorted_products = merge_sort(product_list, sort_field)

    # SEARCH DROPDOWN
    selected_field = request.GET.get("search_field", "name")

    # SEARCH TEXT
    search_text = request.GET.get("search_query", "").strip()

    # HASH MAP for SKU lookup
    product_map = {p.sku.upper(): p for p in sorted_products}

    # NO SEARCH → show sorted list
    if search_text == "":
        return render(request, "myapp/inventory_list.html", {
            "products": sorted_products,
            "selected_field": selected_field,
            "sort_field": sort_field
        })

    # CASE 1: SKU SEARCH (O(1))
    if selected_field == "sku":
        key = search_text.upper()
        found_item = product_map.get(key)
        results = [found_item] if found_item else []

        return render(request, "myapp/inventory_list.html", {
            "products": results,
            "selected_field": selected_field,
            "sort_field": sort_field
        })

    # CASE 2: BINARY SEARCH (name, category, supplier)
    # SORT BY SEARCH FIELD FIRST
    sorted_for_search = merge_sort(product_list, selected_field)

    # Lowercase target
    target = search_text.lower()
    results = binary_search(sorted_for_search, target, selected_field)


    return render(request, "myapp/inventory_list.html", {
        "products": results,
        "selected_field": selected_field,
        "sort_field": sort_field
    })

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



def supplier_list(request):
    # get all products
    supplier_list = list(Supplier.objects.all())
    # SORT DROPDOWN
    sort_field = request.GET.get("sort", "name")
    sorted_products = merge_sort(supplier_list, sort_field)

    # SEARCH DROPDOWN
    selected_field = request.GET.get("search_field", "name")

    # SEARCH TEXT
    search_text = request.GET.get("search_query", "").strip()

    # NO SEARCH → show sorted list
    if search_text == "":
        return render(request, "myapp/supplier_list.html", {
            "suppliers": sorted_products,
            "selected_field": selected_field,
            "sort_field": sort_field
        })
    
    #BINARY SEARCH (name, category, supplier)
    # SORT BY SEARCH FIELD FIRST
    sorted_for_search = merge_sort(supplier_list, selected_field)

    # Lowercase target
    target = search_text.lower()
    results = binary_search(sorted_for_search, target, selected_field)


    return render(request, "myapp/supplier_list.html", {
        "suppliers": results,
        "selected_field": selected_field,
        "sort_field": sort_field
    })




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
