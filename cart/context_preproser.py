from .models import CartItem

def cart_item_count(request):
    total_item=CartItem.objects.all().count()

    return {'cart_total_item':total_item}