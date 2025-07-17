# 🖼️ ПОШАГОВАЯ ИНСТРУКЦИЯ ПО ЗАМЕНЕ КАРТИНКИ

## 🎯 Текущее состояние
Сейчас у нас CSS placeholder (строки 39-95 в home.html) - большой блок с градиентами и иконкой шестеренки.

## 📋 ШАГ 1: Получить картинку

### Вариант A: Скачать готовую
1. Идти на https://unsplash.com/
2. Поиск: "post apocalyptic car" или "mad max vehicle"
3. Скачать понравившуюся картинку
4. Переименовать в `hero-autoparts-madmax.jpg`

### Вариант B: AI генерация
Промпт для AI:
```
"Post-apocalyptic car workshop, rusty automotive parts scattered around, 
orange and brown color scheme, dramatic lighting, Mad Max style, 
industrial metal textures, survival garage scene"
```

## 📋 ШАГ 2: Сохранить файл

```
📁 c:\Users\Professional\Desktop\shopapex\
  📁 static\
    📁 images\
      🖼️ hero-autoparts-madmax.jpg  ← СЮДА!
```

## 📋 ШАГ 3: Заменить код

### НАЙТИ в home.html (строки ~39-95):
```html
<!-- Mad Max Style Hero Placeholder -->
<div class="hero-image" style="
    width: 100%; 
    max-width: 500px; 
    height: 400px; 
    background: linear-gradient(...);
    ...весь длинный блок с градиентами...
</div>
```

### ЗАМЕНИТЬ НА:
```html
<img src="{% static 'images/hero-autoparts-madmax.jpg' %}" 
     class="img-fluid rounded-3 shadow-lg hero-image" 
     alt="Автозапчасти APEX PARTS - Постапокалиптический стиль"
     style="max-height: 400px; object-fit: cover; width: 100%;">
```

## 📋 ШАГ 4: Проверить результат

1. Перезапустить сервер: `python manage.py runserver`
2. Открыть http://127.0.0.1:8000/
3. Наслаждаться результатом! 🔥

---

## 🎨 АЛЬТЕРНАТИВНЫЙ СПОСОБ (если хочется сохранить эффекты)

Можно заменить только CSS background, оставив overlay:

```html
<div class="hero-image" style="
    width: 100%; 
    max-width: 500px; 
    height: 400px; 
    background-image: url('{% static 'images/hero-autoparts-madmax.jpg' %}');
    background-size: cover;
    background-position: center;
    border-radius: 15px;
    border: 3px solid #ff5722;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
    margin: 0 auto;
">
    <!-- Можно оставить overlay эффекты поверх картинки -->
</div>
```

---

## ⚠️ ВАЖНО:

1. **Имя файла** должно быть точно `hero-autoparts-madmax.jpg`
2. **Путь** должен быть точно `static/images/`
3. **Размер** картинки желательно не больше 500KB
4. После изменений **перезапустить сервер**

---

## 🚀 РЕЗУЛЬТАТ

После замены получится:
- ✅ Реальная крутая картинка вместо placeholder'а
- ✅ Все hover-эффекты и overlay сохранятся
- ✅ Адаптивный дизайн останется
- ✅ Mad Max атмосфера усилится!

**Готово к бою! 🔥🚗⚡**
