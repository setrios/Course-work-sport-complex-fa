// ============================================
// Neo4j Cypher запити для інтернет-магазину
// Відкрийте Neo4j Browser: http://localhost:7474
// ============================================

// ============================================
// 1. ПЕРЕГЛЯД СТРУКТУРИ ГРАФА
// ============================================

// Показати всі ноди та зв'язки
MATCH (n) RETURN n LIMIT 50;

// Підрахунок нод по типах
MATCH (n)
RETURN labels(n) AS Type, count(n) AS Count
ORDER BY Count DESC;

// Підрахунок зв'язків по типах
MATCH ()-[r]->()
RETURN type(r) AS RelationType, count(r) AS Count
ORDER BY Count DESC;


// ============================================
// 2. ПОСТАЧАЛЬНИКИ (SUPPLIERS)
// ============================================

// Всі постачальники
MATCH (s:Supplier)
RETURN s.name AS Supplier, s.city AS City, s.country AS Country;

// Постачальники по містах
MATCH (s:Supplier)
RETURN s.city AS City, collect(s.name) AS Suppliers, count(s) AS Count
ORDER BY Count DESC;

// Постачальники конкретного міста
MATCH (s:Supplier {city: "Київ"})
RETURN s.name AS Supplier, s.country AS Country;


// ============================================
// 3. ТОВАРИ (PRODUCTS)
// ============================================

// Всі товари
MATCH (p:Product)
RETURN p.article AS Article, p.name AS Product;

// Товари з категоріями
MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
RETURN p.article AS Article, p.name AS Product, c.name AS Category;

// Товари конкретної категорії
MATCH (p:Product)-[:BELONGS_TO]->(c:Category {name: "Електроніка"})
RETURN p.article AS Article, p.name AS Product;


// ============================================
// 4. ЗВ'ЯЗКИ МІЖ ПОСТАЧАЛЬНИКАМИ ТА ТОВАРАМИ
// ============================================

// Постачальники та їхні товари
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)
RETURN s.name AS Supplier, collect(p.name) AS Products, count(p) AS ProductCount
ORDER BY ProductCount DESC;

// Товари від конкретного постачальника
MATCH (s:Supplier {name: "GlobalTech"})-[:SUPPLIES]->(p:Product)
RETURN p.article AS Article, p.name AS Product;

// Повний ланцюг: Постачальник -> Товар -> Категорія
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)-[:BELONGS_TO]->(c:Category)
RETURN s.name AS Supplier, s.city AS City, 
       p.article AS Article, p.name AS Product,
       c.name AS Category;


// ============================================
// 5. АНАЛІТИКА ТА СТАТИСТИКА
// ============================================

// Топ постачальників за кількістю товарів
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)
RETURN s.name AS Supplier, s.city AS City, count(p) AS TotalProducts
ORDER BY TotalProducts DESC;

// Розподіл товарів по категоріях
MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
RETURN c.name AS Category, count(p) AS ProductCount
ORDER BY ProductCount DESC;

// Постачальники з товарами в конкретній категорії
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)-[:BELONGS_TO]->(c:Category {name: "Електроніка"})
RETURN s.name AS Supplier, collect(p.name) AS Products, count(p) AS Count;

// Міста з найбільшою кількістю постачальників
MATCH (s:Supplier)
WITH s.city AS City, count(s) AS SupplierCount
RETURN City, SupplierCount
ORDER BY SupplierCount DESC;


// ============================================
// 6. ПОШУК АЛЬТЕРНАТИВНИХ ПОСТАЧАЛЬНИКІВ
// ============================================

// Знайти постачальників товарів тієї ж категорії
MATCH (p:Product {article: "LAPTOP-001"})-[:BELONGS_TO]->(c:Category),
      (other:Product)-[:BELONGS_TO]->(c),
      (s:Supplier)-[:SUPPLIES]->(other)
RETURN DISTINCT s.name AS AlternativeSupplier, 
                s.city AS City, 
                collect(DISTINCT other.name) AS Products;

// Постачальники з міст України
MATCH (s:Supplier)
WHERE s.country = "Україна"
RETURN s.name AS Supplier, s.city AS City;


// ============================================
// 7. СКЛАДНІ ЗАПИТИ
// ============================================

// Топ-5 категорій з найбільшою кількістю постачальників
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)-[:BELONGS_TO]->(c:Category)
RETURN c.name AS Category, 
       count(DISTINCT s) AS UniqueSuppliers,
       count(p) AS TotalProducts
ORDER BY UniqueSuppliers DESC, TotalProducts DESC
LIMIT 5;

// Постачальники, що поставляють товари в кількох категоріях
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)-[:BELONGS_TO]->(c:Category)
WITH s, collect(DISTINCT c.name) AS Categories
WHERE size(Categories) > 1
RETURN s.name AS Supplier, Categories, size(Categories) AS CategoryCount
ORDER BY CategoryCount DESC;

// Найближчі постачальники (по алфавіту міст)
MATCH (s:Supplier)
RETURN s.name AS Supplier, s.city AS City, s.country AS Country
ORDER BY s.city;


// ============================================
// 8. ВІЗУАЛІЗАЦІЯ
// ============================================

// Граф: всі постачальники та їхні товари
MATCH (s:Supplier)-[r:SUPPLIES]->(p:Product)
RETURN s, r, p
LIMIT 50;

// Граф: товари та категорії
MATCH (p:Product)-[r:BELONGS_TO]->(c:Category)
RETURN p, r, c;

// Повний граф (обережно з великими даними!)
MATCH path = (s:Supplier)-[:SUPPLIES]->(p:Product)-[:BELONGS_TO]->(c:Category)
RETURN path
LIMIT 25;


// ============================================
// 9. СТВОРЕННЯ ДАНИХ (якщо потрібно вручну)
// ============================================

// Створення постачальника
CREATE (s:Supplier {
  mysql_id: 100,
  name: "TestSupplier",
  city: "Харків",
  country: "Україна"
});

// Створення товару
CREATE (p:Product {
  mysql_id: 200,
  article: "TEST-001",
  name: "Тестовий товар"
});

// Створення категорії
CREATE (c:Category {name: "Тестові товари"});

// Створення зв'язків
MATCH (s:Supplier {name: "TestSupplier"}),
      (p:Product {article: "TEST-001"}),
      (c:Category {name: "Тестові товари"})
CREATE (s)-[:SUPPLIES]->(p)-[:BELONGS_TO]->(c);


// ============================================
// 10. ОЧИЩЕННЯ (ОБЕРЕЖНО!)
// ============================================

// Видалити всі зв'язки SUPPLIES
MATCH ()-[r:SUPPLIES]->()
DELETE r;

// Видалити всі зв'язки BELONGS_TO
MATCH ()-[r:BELONGS_TO]->()
DELETE r;

// Видалити всі ноди Product
MATCH (p:Product)
DETACH DELETE p;

// Видалити всі ноди Supplier
MATCH (s:Supplier)
DETACH DELETE s;

// Видалити всі ноди Category
MATCH (c:Category)
DETACH DELETE c;

// Видалити ВСЕ (ОБЕРЕЖНО!!!)
// MATCH (n)
// DETACH DELETE n;


// ============================================
// 11. КОРИСНІ КОМАНДИ
// ============================================

// Показати схему бази
CALL db.schema.visualization();

// Статистика бази
CALL apoc.meta.stats();

// Індекси
SHOW INDEXES;

// Обмеження
SHOW CONSTRAINTS;
