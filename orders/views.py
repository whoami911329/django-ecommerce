from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.contrib import messages


def order_create(request):
    cart = Cart(request)
    if cart.__len__() > 0:
        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                if cart.coupon:
                    order.coupon = cart.coupon
                    order.discount = cart.coupon.discount
                order.save()
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity'])
                    # clear the cart
                    cart.clear()
                    # launch asynchronous task
                    order_created.delay(order.id)
                    messages.success(
                        request, 'Your order has been successfully send. we have send you a later.')
                    return redirect("/")
        else:
            form = OrderCreateForm()
        return render(request,
                      'orders/order_create.html',
                      {'cart': cart, 'form': form})
    else:
        messages.success(
                        request, 'You aint got products in cart to proceed the order')
        return redirect("/")
