from django import forms
from django.core.exceptions import ValidationError
from .models import Status, Type, Category, Subcategory, CashFlowRecord

# Форма для создания и редактирования записей 
class CashFlowRecordForm(forms.ModelForm):
    class Meta:
        model = CashFlowRecord
        fields = ['date', 'status', 'operation_type', 'category', 'subcategory', 'amount', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'operation_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_operation_type'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'subcategory': forms.Select(attrs={'class': 'form-select', 'id': 'id_subcategory'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'date': 'Дата',
            'status': 'Статус',
            'operation_type': 'Тип',
            'category': 'Категория',
            'subcategory': 'Подкатегория',
            'amount': 'Сумма (руб.)',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Обяз. поля
        for field in ['status', 'operation_type', 'category', 'subcategory', 'amount']:
            self.fields[field].required = True
        
        self.fields['category'].empty_label = "-- Выберите категорию --"
        self.fields['subcategory'].empty_label = "-- Выберите подкатегорию --"
        
        # Если ред. запись - фильтр связанных данных
        if self.instance and self.instance.pk:
            if self.instance.operation_type:
                self.fields['category'].queryset = Category.objects.filter(
                    operation_type=self.instance.operation_type
                )
            if self.instance.category:
                self.fields['subcategory'].queryset = Subcategory.objects.filter(
                    category=self.instance.category
                )

    def clean(self):
        cleaned_data = super().clean()
        operation_type = cleaned_data.get('operation_type')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')

        # Категория должна принадлежать выбранному типу
        if operation_type and category:
            if category.operation_type != operation_type:
                self.add_error('category', 'Категория не относится к выбранному типу')

        # Подкатегория должна принадлежать выбранной категории
        if category and subcategory:
            if subcategory.category != category:
                self.add_error('subcategory', 'Подкатегория не относится к выбранной категории')

        return cleaned_data

# Формы для справочников
class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'name': 'Название статуса'}


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'name': 'Название типа'}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'operation_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'operation_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Название категории',
            'operation_type': 'Тип',
        }


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Название подкатегории',
            'category': 'Категория',
        }