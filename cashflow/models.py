from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# СТатус
class Status(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['name']

    def __str__(self):
        return self.name

# Типы операций
class Type(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Тип'
        verbose_name_plural = 'Типы'
        ordering = ['name']

    def __str__(self):
        return self.name

# Категории
class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    operation_type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        verbose_name='Тип',
        related_name='categories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
        unique_together = ['name', 'operation_type']

    def __str__(self):
        return f"{self.name} ({self.operation_type.name})"

# Подкатегории
class Subcategory(models.Model):
    name = models.CharField('Название', max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

# Запись ДДС
class CashFlowRecord(models.Model):
    date = models.DateField('Дата', default=timezone.now)
    
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name='Статус'
    )
    operation_type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        verbose_name='Тип'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='Категория'
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        verbose_name='Подкатегория'
    )
    
    amount = models.DecimalField(
        'Сумма (руб.)',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    comment = models.TextField('Комментарий', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.operation_type.name} - {self.amount} руб."

    def clean(self):
        """Валидация связей между полями (используем ValidationError)"""
        # Категория должна принадлежать выбранному типу
        if self.category and self.operation_type:
            if self.category.operation_type != self.operation_type:
                raise ValidationError({
                    'category': 'Категория не относится к выбранному типу'
                })
        
        # Подкатегория должна принадлежать выбранной категории
        if self.subcategory and self.category:
            if self.subcategory.category != self.category:
                raise ValidationError({
                    'subcategory': 'Подкатегория не относится к выбранной категории'
                })

    def save(self, *args, **kwargs):
        """Вызываем clean() перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)