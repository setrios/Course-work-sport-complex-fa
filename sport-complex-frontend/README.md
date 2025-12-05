# SportComplex Frontend

Сучасний веб-інтерфейс для SportComplex API.

## 🚀 Швидкий старт

1. Переконайтесь що backend запущено:
```bash
cd ../sport-complex-api
python -m uvicorn app.main:app --reload
```

2. Відкрийте `index.html` у браузері:
```bash
# У Windows
start index.html

# Або просто двічі клікніть на index.html
```

## 📋 Функціонал

### 🏠 Головна сторінка
- Статистика (бестселери, тренери, товари)
- Рекомендовані продукти
- Список тренерів

### 🛒 Магазин
- Каталог продуктів
- Додавання в кошик
- Оформлення замовлення
- Автоматичне оновлення запасів

### 👤 Тренери
- Список всіх тренерів
- Профілі з рейтингом
- Спеціалізація та досвід

### 📋 Клієнти (Адмін панель)
- Список клієнтів
- Додавання нових клієнтів
- Перегляд деталей

### 📊 Аналітика
- Топ-10 бестселерів (з Redis)
- Останні замовлення
- Статистика продажів

## 🎨 Дизайн

- **Тема**: Dark theme з градієнтами
- **Кольори**: Indigo + Purple + Pink
- **Шрифт**: Inter (Google Fonts)
- **Адаптивність**: Mobile, Tablet, Desktop
- **Анімації**: Плавні переходи та ефекти

## 🛠️ Технології

- **HTML5** - Сучасна розмітка
- **CSS3** - Градієнти, анімації, grid/flexbox
- **Vanilla JavaScript** - Без фреймворків
- **Fetch API** - Інтеграція з backend

## 📁 Структура

```
sport-complex-frontend/
├── index.html           # Головна сторінка
├── css/
│   └── style.css        # Стилі
├── js/
│   ├── api.js           # API виклики
│   ├── components.js    # UI компоненти
│   └── app.js           # Основна логіка
└── README.md
```

## 🔗 API Endpoints

Фронтенд підключається до:
```
http://localhost:8000/api/v1
```

Використовує:
- `/products` - Каталог товарів
- `/trainers` - Тренери
- `/clients` - Клієнти
- `/orders` - Замовлення
- `/analytics/bestsellers` - Бестселери
- `/recommendations/*` - Рекомендації

## ✨ Особливості

- ✅ SPA (Single Page Application)
- ✅ Hash-based routing
- ✅ Shopping cart
- ✅ Modal windows
- ✅ Toast notifications
- ✅ Loading states
- ✅ Error handling
- ✅ Responsive design

## 📱 Підтримка браузерів

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 🎯 Використання

### Перегляд магазину
1. Клікніть "🛒 Магазин"
2. Оберіть товар
3. Натисніть "Додати в кошик"

### Оформлення замовлення
1. Клікніть "🛒 Кошик" у header
2. Перевірте товари
3. Натисніть "Оформити замовлення"

### Додавання клієнта
1. Перейдіть "📋 Клієнти"
2. Натисніть "➕ Додати клієнта"
3. Заповніть форму

---

**Розроблено для курсової роботи** 🎓
