from django.shortcuts import render, redirect
from .models import *
from django.forms import inlineformset_factory
from .forms import *
from django.contrib import messages
from .filters import OrderFilter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import *
from django.contrib.auth.models import Group


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    context = {'form': form}

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account created for ' + username)
            return redirect('login')
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    cust = Customer.objects.all()
    order = Order.objects.all()
    total_orders = order.count()
    delivered = order.filter(status='Delivered').count()
    pending = order.filter(status='Pending').count()
    context = {'cust': cust, 'order': order, 'total_orders': total_orders, 'delivered': delivered, 'pending': pending}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {'orders': orders, 'total_orders': total_orders, 'delivered': delivered, 'pending': pending}

    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    context = {'form': form}
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    product = Product.objects.all()
    return render(request, 'accounts/products.html', {'prod': product})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    cust = Customer.objects.get(id=pk)
    orders = cust.order_set.all()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {'customer': cust, 'orders': orders, 'myFilter': myFilter}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=3)
    custom = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=custom)
    # form = OrderForm(initial={'customer': custom})
    if request.method == "POST":
        formset = OrderFormSet(request.POST, instance=custom)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset': formset, 'customer': customer}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    context = {'order': order}
    if request.method == "POST":
        order.delete()
        return redirect('/')
    return render(request, 'accounts/delete.html', context)
