from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from .models import Status, Type, Category, Subcategory, CashFlowRecord
from .forms import CashFlowRecordForm, StatusForm, TypeForm, CategoryForm, SubcategoryForm

# Управление ДДС
def index(request):
    records = CashFlowRecord.objects.all().select_related(
        'status', 'operation_type', 'category', 'subcategory'
    )
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        records = records.filter(date__gte=date_from)
    if date_to:
        records = records.filter(date__lte=date_to)
    
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('operation_type')
    category_filter = request.GET.get('category')
    subcategory_filter = request.GET.get('subcategory')
    
    if status_filter:
        records = records.filter(status_id=status_filter)
    if type_filter:
        records = records.filter(operation_type_id=type_filter)
    if category_filter:
        records = records.filter(category_id=category_filter)
    if subcategory_filter:
        records = records.filter(subcategory_id=subcategory_filter)
    
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'statuses': Status.objects.all(),
        'types': Type.objects.all(),
        'categories': Category.objects.all(),
        'subcategories': Subcategory.objects.all(),
        'filter_data': {
            'date_from': date_from or '',
            'date_to': date_to or '',
            'status': status_filter or '',
            'operation_type': type_filter or '',
            'category': category_filter or '',
            'subcategory': subcategory_filter or '',
        }
    }
    return render(request, 'cashflow/index.html', context)


# Добавлние записи
def record_create(request):
    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Запись успешно создана!')
                return redirect('cashflow:index')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                messages.error(request, 'Ошибка при создании записи.')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CashFlowRecordForm()
    
    return render(request, 'cashflow/record_form.html', {
        'form': form,
        'title': 'Создание записи'
    })

# Редактирование записи
def record_edit(request, pk):
    record = get_object_or_404(CashFlowRecord, pk=pk)
    
    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST, instance=record)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Запись успешно обновлена!')
                return redirect('cashflow:index')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                messages.error(request, 'Ошибка при обновлении записи.')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CashFlowRecordForm(instance=record)
    
    return render(request, 'cashflow/record_form.html', {
        'form': form,
        'title': 'Редактирование записи'
    })

# Удаление записи
def record_delete(request, pk):
    record = get_object_or_404(CashFlowRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Запись успешно удалена!')
        return redirect('cashflow:index')
    return render(request, 'cashflow/record_confirm_delete.html', {'record': record})


# Получение категорий по типу
def get_categories_by_type(request):
    type_id = request.GET.get('type_id')
    if type_id:
        categories = Category.objects.filter(
            operation_type_id=type_id
        ).values('id', 'name')
        return JsonResponse(list(categories), safe=False)
    return JsonResponse([], safe=False)

# Получение подкатегорий по категории
def get_subcategories_by_category(request):
    category_id = request.GET.get('category_id')
    if category_id:
        subcategories = Subcategory.objects.filter(
            category_id=category_id
        ).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)


# Управление справочниками

def directory_list(request):
    context = {
        'statuses': Status.objects.all(),
        'types': Type.objects.all(),
        'categories': Category.objects.all().select_related('operation_type'),
        'subcategories': Subcategory.objects.all().select_related('category'),
    }
    return render(request, 'cashflow/directory_list.html', context)


# Добавлние
def directory_create(request, model, form_class, template, redirect_url, success_msg):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, success_msg)
            return redirect(redirect_url)
    else:
        form = form_class()
    return render(request, template, {'form': form, 'title': 'Добавление'})

# Редактирование
def directory_edit(request, pk, model, form_class, template, redirect_url, success_msg):
    instance = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, success_msg)
            return redirect(redirect_url)
    else:
        form = form_class(instance=instance)
    return render(request, template, {'form': form, 'title': 'Редактирование'})

# Удаление
def directory_delete(request, pk, model, redirect_url, success_msg, error_msg=None):
    instance = get_object_or_404(model, pk=pk)
    
    if request.method == 'POST':
        try:
            instance.delete()
            messages.success(request, success_msg)
            return redirect(redirect_url)
        except models.ProtectedError:
            # Ошибка - объект используется
            error_message = error_msg or f'Невозможно удалить "{instance.name}", так как он используется в записях.'
            return render(request, 'cashflow/directory_confirm_delete.html', {
                'object': instance,
                'type_name': model._meta.verbose_name,
                'error_message': error_message,
            })
        except Exception as e:
            error_message = f'Ошибка при удалении: {str(e)}'
            return render(request, 'cashflow/directory_confirm_delete.html', {
                'object': instance,
                'type_name': model._meta.verbose_name,
                'error_message': error_message,
            })
    
    # GET запрос - показывает страницу подтверждения
    return render(request, 'cashflow/directory_confirm_delete.html', {
        'object': instance,
        'type_name': model._meta.verbose_name,
    })

# Статусы
def status_create(request):
    return directory_create(request, Status, StatusForm, 'cashflow/directory_form.html',
                           'cashflow:directory_list', 'Статус успешно добавлен!')

def status_edit(request, pk):
    return directory_edit(request, pk, Status, StatusForm, 'cashflow/directory_form.html',
                         'cashflow:directory_list', 'Статус успешно обновлен!')

def status_delete(request, pk):
    return directory_delete(request, pk, Status, 'cashflow:directory_list',
                           'Статус успешно удален!', 
                           'Невозможно удалить статус, он используется в записях.')


# Типы
def type_create(request):
    return directory_create(request, Type, TypeForm, 'cashflow/directory_form.html',
                           'cashflow:directory_list', 'Тип успешно добавлен!')

def type_edit(request, pk):
    return directory_edit(request, pk, Type, TypeForm, 'cashflow/directory_form.html',
                         'cashflow:directory_list', 'Тип успешно обновлен!')

def type_delete(request, pk):
    return directory_delete(request, pk, Type, 'cashflow:directory_list',
                           'Тип успешно удален!', 
                           'Невозможно удалить тип, он используется в записях или категориях.')


# Категории
def category_create(request):
    return directory_create(request, Category, CategoryForm, 'cashflow/directory_form.html',
                           'cashflow:directory_list', 'Категория успешно добавлена!')

def category_edit(request, pk):
    return directory_edit(request, pk, Category, CategoryForm, 'cashflow/directory_form.html',
                         'cashflow:directory_list', 'Категория успешно обновлена!')

def category_delete(request, pk):
    return directory_delete(request, pk, Category, 'cashflow:directory_list',
                           'Категория успешно удалена!', 
                           'Невозможно удалить категорию, она используется в записях или подкатегориях.')


# Подкатегории
def subcategory_create(request):
    return directory_create(request, Subcategory, SubcategoryForm, 'cashflow/directory_form.html',
                           'cashflow:directory_list', 'Подкатегория успешно добавлена!')

def subcategory_edit(request, pk):
    return directory_edit(request, pk, Subcategory, SubcategoryForm, 'cashflow/directory_form.html',
                         'cashflow:directory_list', 'Подкатегория успешно обновлена!')

def subcategory_delete(request, pk):
    return directory_delete(request, pk, Subcategory, 'cashflow:directory_list',
                           'Подкатегория успешно удалена!', 
                           'Невозможно удалить подкатегорию, она используется в записях.')