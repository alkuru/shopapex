"""
Web views для CMS страниц
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import News, HTMLBlock


def contacts(request):
    """Страница контактов"""
    # Получаем HTML блок с контактной информацией
    contact_block = None
    try:
        contact_block = HTMLBlock.objects.get(position='contacts', is_active=True)
    except HTMLBlock.DoesNotExist:
        pass
    
    context = {
        'contact_block': contact_block,
        'page_title': 'Контакты'
    }
    return render(request, 'cms/contacts.html', context)


def about(request):
    """Страница о компании"""
    # Получаем HTML блок с информацией о компании
    about_block = None
    try:
        about_block = HTMLBlock.objects.get(position='about', is_active=True)
    except HTMLBlock.DoesNotExist:
        pass
    
    context = {
        'about_block': about_block,
        'page_title': 'О компании'
    }
    return render(request, 'cms/about.html', context)


def news_list(request):
    """Список новостей"""
    news_list = News.objects.filter(is_published=True).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'news': page_obj,
        'page_title': 'Новости'
    }
    return render(request, 'cms/news_list.html', context)


def news_detail(request, news_id):
    """Детальная страница новости"""
    news = get_object_or_404(News, id=news_id, is_published=True)
    
    # Другие новости
    other_news = News.objects.filter(
        is_published=True
    ).exclude(id=news.id).order_by('-created_at')[:5]
    
    context = {
        'news': news,
        'other_news': other_news,
        'page_title': news.title
    }
    return render(request, 'cms/news_detail.html', context)
