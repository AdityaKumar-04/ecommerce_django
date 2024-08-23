from django.db import models
from store.models import Product,Variation 


# Create your models here.
class Cart(models.Model):
    cart_id= models.CharField(max_length=255)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(Variation)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.product.product_name

    def get_total(self):
        return self.product.price * self.quantity