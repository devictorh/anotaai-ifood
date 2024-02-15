from djongo import models


class Category(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    ownerid = models.CharField(max_length=25)

    def __str__(self) -> str:
        return f'{self.title}: {self.description}'


class Product(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.EmbeddedField(Category)
    ownerid = models.CharField(max_length=25)

    def __str__(self) -> str:
        return f'{self.title}: {self.description}'
