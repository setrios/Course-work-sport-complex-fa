# Скрипт для швидкого запуску всіх БД через Docker
# Виконайте: .\start-docker.ps1

Write-Host "🐳 Запуск баз даних через Docker..." -ForegroundColor Cyan
Write-Host ""

# Перевірка чи Docker запущений
Write-Host "Перевірка Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker не запущений! Запустіть Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker працює" -ForegroundColor Green
Write-Host ""

# Запуск контейнерів
Write-Host "🚀 Запуск контейнерів..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Помилка при запуску контейнерів!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏳ Очікування ініціалізації БД (30 секунд)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "📊 Статус контейнерів:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "🔍 Перевірка підключень..." -ForegroundColor Yellow

# MySQL
Write-Host -NoNewline "  MySQL (3306)... "
$mysqlTest = docker exec shop-mysql mysqladmin ping -h localhost -u root -prootpassword 2>$null
if ($mysqlTest -match "alive") {
    Write-Host "✅" -ForegroundColor Green
} else {
    Write-Host "❌" -ForegroundColor Red
}

# Redis
Write-Host -NoNewline "  Redis (6379)... "
$redisTest = docker exec shop-redis redis-cli ping 2>$null
if ($redisTest -eq "PONG") {
    Write-Host "✅" -ForegroundColor Green
} else {
    Write-Host "❌" -ForegroundColor Red
}

# CouchDB
Write-Host -NoNewline "  CouchDB (5984)... "
try {
    $couchTest = Invoke-RestMethod -Uri "http://localhost:5984/" -ErrorAction SilentlyContinue
    if ($couchTest.couchdb) {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌" -ForegroundColor Red
}

# Neo4j
Write-Host -NoNewline "  Neo4j (7474, 7687)... "
try {
    $neo4jTest = Invoke-RestMethod -Uri "http://localhost:7474/" -ErrorAction SilentlyContinue
    if ($neo4jTest) {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Бази даних запущені!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Корисні посилання:" -ForegroundColor Cyan
Write-Host "  - CouchDB: http://localhost:5984/_utils/ (couchdb / couchdb)"
Write-Host "  - Neo4j: http://localhost:7474 (neo4j / neo4jneo4j)"
Write-Host ""
Write-Host "🚀 Тепер запустіть FastAPI:" -ForegroundColor Yellow
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Або запустіть тести:" -ForegroundColor Yellow
Write-Host "  python test_requests.py" -ForegroundColor White
Write-Host ""
