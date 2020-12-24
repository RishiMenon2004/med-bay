from django.contrib.auth.decorators import login_required
from .models import Stock, Order, Bill, BillUnit
from django.shortcuts import render, redirect
from admins.utils import validate_access
from .forms import StockForm, BillForm
from django.http import HttpResponse
from django.utils import timezone


# Create your views here.
@login_required
def shop(request):

    # Checking if user is allowed visit the site
    validate_access(request, 'p')

    # Getting the list of stocks
    items = Stock.objects.filter(deleted=False)
    items = list(items)
    for item in items:

        # Removing out of stock items
        if item.quantity < 1:
            items.remove(item)

    return render(request, "pharma/shop.html", context={'items': items})


# Placing order when order button is pressed
@login_required()
def place(request):

    user = validate_access(request, 'p')
    if request.method == "GET":
        ID = request.GET['product_id']
        qty = int(request.GET['product_amount'])
        item = Stock.objects.filter(id=ID)[0]
        orders = user.staff.order_set.all()

        # Checking if item already in cart
        in_cart = False
        for order in orders:
            if order.item.id == item.id:
                in_cart = True

        # If the item is already in cart
        if in_cart:
            order = user.staff.order_set.filter(item__id=item.id)[0]
            order.quantity += qty

        # Creating a new order if not already there
        else:
            order = Order(user=user.staff, item=item, quantity=qty)

        # Updating the item stock and saving changes
        item.quantity -= qty
        order.save()
        item.save()

        return HttpResponse("success")


@login_required()
def remove(request):
    user = validate_access(request, 'p')
    if request.method == "GET":
        ID = int(request.GET['product_id'])
        reduce = int(request.GET['remove_amount'])
        item = Stock.objects.filter(id=ID)[0]
        order = user.staff.order_set.filter(item__id=item.id)[0]

        # Checking if the quantity in order will be 0
        if order.quantity == reduce:
            order.delete()
        else:
            order.quantity -= reduce
            order.save()

        # Updating item quantity and saving changes
        item.quantity += reduce
        item.save()

    return render(request, "pharma/cart.html", {'cart': cart})


@login_required()
def add_one(request):

    user = validate_access(request, "p")
    if request.method == "GET":
        ID = int(request.GET['product_id'])
        increase = 1
        item = Stock.objects.get(id=ID)
        order = user.staff.order_set.get(item__id=item.id)
        order.quantity += increase
        item.quantity -= increase
        order.save()
        item.save()
    return render(request, "pharma/cart.html", {'cart': cart})


@login_required()
def cart(request):

    user = validate_access(request, 'd')
    if request.method == "POST":
        cq = int(request.POST['qty'])
        order = Order.objects.filter(id=request.POST['order_id'])[0]
        item = Stock.objects.filter(id=order.product.id)[0]

        print(order, item)
        if item.quantity > cq > 1:
            change = int(request.Post['qty']) - order.quantity
            order.quantity = int(request.Post['qty'])
            item.quantity -= change
            order.save()
            item.save()
        
        else:
            print(user)
            cart = user.staff.order_set.all()
            print(cart)
            
            return render(request, "pharma/cart.html", {'cart': cart})

    cart = user.staff
    orders = cart.order_set.all()
    print(cart)
    total = get_total(cart)
    return render(request, "pharma/cart.html", {'cart': orders, 'total': total})


# Getting cart total
def get_total(cart):
    total = 0
    # looping through all the orders in the cart and summing the prices
    for order in cart.order_set.all():
        total += order.quantity * order.item.price
    return total


# Getting the name and phone number for bill
@login_required()
def bill_info(request):

    # Getting the orders
    user = validate_access(request, 'p')
    orders = user.staff.order_set.all()
    print(orders)
    print(request.GET)

    # Redirecting back to home if there are no orders
    if not orders:
        return redirect("pharma:shop")

    # Checking if the form data is recieved
    if request.method == "POST":
        form = BillForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']

            # Redirecting user to prescription page
            response = redirect('pharma:bill')
            response['Location'] += f'?name={name}&phone={phone}'
            return response

    else:
        form = BillForm()

    return render(request, "pharma/bill_info.html", context={'form':form})


# showing the bill after purchase
@login_required()
def bill(request):
    
    # Getting the orders
    user = validate_access(request, 'p')
    orders = user.staff.order_set.all()
    print(orders)
    print(request.GET)

    # Redirecting back to home if there are no orders
    if not orders:
        return redirect("pharma:shop")

    # Generating the bill objects
    bill = Bill(name=request.GET["name"], contact_num=request.GET["phone"], date=timezone.now())
    bill.save()
    total = 0

    # Creating the billunits and removing orders
    for order in orders:
        unit = BillUnit(name=order.item.name, quantity=order.quantity,
                        desc=order.item.desc, price=order.item.price,
                        bill=bill)
        
        total += order.item.price * order.quantity
        
        unit.save()
        order.delete()

    # getting all the bill units to send in context
    bill_units = bill.billunit_set.all()
    print(bill_units, bill)

    return render(request, 'pharma/bill.html', context={'bill': bill, 'bill_unit': bill_units, 'total':total})


@login_required()
def add_stock(request):
    validate_access(request, 'p')
    if request.method == "POST":
        form = StockForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']

            stock = Stock.objects.create(name=name, desc="med", price=price, quantity=quantity)
            stock.save()

            return redirect("pharma:shop")

    return render(request, 'pharma/add_stock.html')


@login_required()
def remove_stock(request):

    # making sure the user is a pharmacist
    validate_access(request, "p")

    # Deleting the product if product_id is sent
    if 'product_id' in request.GET:
        print(f"deleting {request.GET['product_id']}")
        id = int(request.GET['product_id'])
        item = Stock.objects.get(id=id)
        item.deleted = True
        item.save()

    # loading the list of stocks
    items = Stock.objects.filter(deleted=False)

    return render(request, 'pharma/remove_stock.html', context={'items': items})


# Bill archive
def bill_archive(request):
    validate_access(request, 'p')
    return render(request, 'pharma/bill_archive.html')
