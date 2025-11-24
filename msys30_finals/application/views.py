from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Supplier, ReorderAlert
from .algorithms import merge_sort, binary_search, safety_stock, reorder_point


def dashboard(request):
    products = list(Product.objects.all())

    total_products = len(products)
    supplier_count = Supplier.objects.count()
    low_stock_items = [p for p in products if p.quantity <= p.reorder_level]
    low_stock_count = len(low_stock_items)
    recent_products = Product.objects.order_by('-id')[:10]

    return render(request, "myapp/dashboard.html", {
        "total_products": total_products,
        "supplier_count": supplier_count,
        "low_stock_items": low_stock_items,
        "low_stock_count": low_stock_count,
        "recent_products": recent_products,
    })



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
    product_list = list(Product.objects.all())


    sort_field = request.GET.get("sort", "name")
    sorted_products = merge_sort(product_list, sort_field)


    selected_field = request.GET.get("search_field", "name")
    search_text = request.GET.get("search_query", "").strip()

    product_map = {p.sku.upper(): p for p in sorted_products}

    # if no search, show sorted list
    if search_text == "":
        return render(request, "myapp/inventory_list.html", {
            "products": sorted_products,
            "selected_field": selected_field,
            "sort_field": sort_field
        })

    # if sku was selected, do direct lookup 
    if selected_field == "sku":
        key = search_text.upper()
        found_item = product_map.get(key)
        results = [found_item] if found_item else []

        return render(request, "myapp/inventory_list.html", {
            "products": results,
            "selected_field": selected_field,
            "sort_field": sort_field
        })

    # sort field by merge sort 
    sorted_for_search = merge_sort(product_list, selected_field)
    # Lowercase target, then do binary  
    target = search_text.lower()
    results = binary_search(sorted_for_search, target, selected_field)


    return render(request, "myapp/inventory_list.html", {
        "products": results,
        "selected_field": selected_field,
        "sort_field": sort_field
    })


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

    # if no search, show sorted list 
    if search_text == "":
        return render(request, "myapp/supplier_list.html", {
            "suppliers": sorted_products,
            "selected_field": selected_field,
            "sort_field": sort_field
        })
    
    # do merge sort first then do binary search
    sorted_for_search = merge_sort(supplier_list, selected_field)
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


def reorder_suggestions(request):
    products = Product.objects.all()

    reorder_items = []

    for p in products:
        lead_time = 7
        avg_daily_demand = max(1, p.quantity // 30)  
        sigma_demand = avg_daily_demand * 0.25       
        z = 1.65  # 95 percent service level

        ss = safety_stock(z, sigma_demand, lead_time)
        rp = reorder_point(lead_time, avg_daily_demand, z, sigma_demand)

        reorder_items.append({
            "product": p,
            "safety_stock": round(ss, 2),
            "reorder_point": round(rp, 2),
            "needs_reorder": p.quantity <= rp
        })

    return render(request, "myapp/reorder_suggestions.html", {
        "reorder_items": reorder_items
    })

