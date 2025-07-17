# 🖼️ ИНСТРУКЦИЯ ПО ДОБАВЛЕНИЮ РЕАЛЬНОЙ HERO-КАРТИНКИ

## 📅 Для завершения оформления главной страницы

---

## 🎯 ЦЕЛЬ
Заменить CSS placeholder на реальную постапокалиптическую картинку в стиле Mad Max для hero-блока главной страницы.

---

## 📋 ШАГ ЗА ШАГОМ

### 1. 🖼️ Подготовка картинки

#### Требования к изображению:
- **Размер**: 800×600px (оптимально) или соотношение 4:3
- **Формат**: JPG или WebP
- **Размер файла**: до 500KB для быстрой загрузки
- **Стиль**: Постапокалиптический, автомобильная тематика

#### Рекомендуемые элементы:
- Ржавый автомобиль или его части
- Автозапчасти в брутальном стиле  
- Металлические поверхности
- Драматическое освещение
- Искры, дым, пыль
- Оранжево-коричневая цветовая гамма

### 2. 📁 Размещение файла

```bash
# Сохранить картинку в:
c:\Users\Professional\Desktop\shopapex\static\images\hero-autoparts-madmax.jpg
```

### 3. 🔧 Изменение шаблона

Заменить в файле `templates/cms/home.html` блок placeholder:

#### НАЙТИ (строки ~37-100):
```html
<!-- Mad Max Style Hero Placeholder -->
<div class="hero-image" style="...">
    <!-- весь CSS placeholder блок -->
</div>
```

#### ЗАМЕНИТЬ НА:
```html
<img src="{% static 'images/hero-autoparts-madmax.jpg' %}" 
     class="img-fluid rounded-3 shadow-lg hero-image" 
     alt="Автозапчасти APEX PARTS - Постапокалиптический стиль"
     style="max-height: 400px; object-fit: cover; width: 100%;">
```

### 4. 🎨 Опциональные улучшения

#### Добавление WebP поддержки:
```html
<picture>
    <source srcset="{% static 'images/hero-autoparts-madmax.webp' %}" type="image/webp">
    <img src="{% static 'images/hero-autoparts-madmax.jpg' %}" 
         class="img-fluid rounded-3 shadow-lg hero-image" 
         alt="Автозапчасти APEX PARTS - Постапокалиптический стиль"
         style="max-height: 400px; object-fit: cover; width: 100%;">
</picture>
```

#### Lazy Loading:
```html
<img src="{% static 'images/hero-autoparts-madmax.jpg' %}" 
     class="img-fluid rounded-3 shadow-lg hero-image" 
     alt="Автозапчасти APEX PARTS - Постапокалиптический стиль"
     style="max-height: 400px; object-fit: cover; width: 100%;"
     loading="lazy">
```

---

## 🔍 АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ

### Вариант A: Использование CSS background
```css
.hero-image-real {
    background-image: url('{% static "images/hero-autoparts-madmax.jpg" %}');
    background-size: cover;
    background-position: center;
    width: 100%;
    height: 400px;
    border-radius: 15px;
    border: 3px solid var(--madmax-orange);
}
```

### Вариант B: Комбинированный подход
```html
<div class="hero-image" style="
    background-image: url('{% static "images/hero-autoparts-madmax.jpg" %}');
    background-size: cover;
    background-position: center;
    /* остальные стили placeholder сохранить */
">
    <!-- Overlay контент поверх картинки -->
</div>
```

---

## 🖼️ ИСТОЧНИКИ КАРТИНОК

### Рекомендуемые ресурсы:
1. **Unsplash.com** - бесплатные HD изображения
2. **Pexels.com** - качественные фото
3. **Freepik.com** - иллюстрации и фото
4. **AI генераторы**:
   - DALL-E
   - Midjourney  
   - Stable Diffusion

### Поисковые запросы:
- "post apocalyptic car parts"
- "mad max vehicle parts"
- "rusty automotive parts"
- "industrial metal parts"
- "survival car workshop"

---

## 🧪 ТЕСТИРОВАНИЕ

После добавления картинки проверить:

1. **Загрузка**: `python manage.py runserver`
2. **Отображение**: Открыть http://127.0.0.1:8000/
3. **Hover эффекты**: Навести на картинку
4. **Мобильная версия**: Изменить размер окна
5. **Скорость загрузки**: Проверить в DevTools

---

## 🚀 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ

После добавления реальной картинки получится:
- ✅ Профессиональный hero-блок
- ✅ Брутальный Mad Max стиль  
- ✅ Отличные hover-эффекты
- ✅ Готовый к production дизайн

---

## ⚡ БЫСТРЫЙ СТАРТ

```bash
# 1. Скачать подходящую картинку
# 2. Переименовать в hero-autoparts-madmax.jpg
# 3. Поместить в static/images/
# 4. Заменить placeholder в home.html
# 5. Перезапустить сервер
# 6. Наслаждаться результатом! 🔥
```

---

*Главная страница ждет свою идеальную картинку! 🎨🚗⚡*
