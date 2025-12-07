# Скрипт для зупинки всіх БД Docker
# Виконайте: .\stop-docker.ps1

param(
    [switch]$RemoveData
)

Write-Host "🛑 Зупинка баз даних Docker..." -ForegroundColor Cyan
Write-Host ""

if ($RemoveData) {
    Write-Host "⚠️  УВАГА: Дані будуть ВИДАЛЕНІ!" -ForegroundColor Red
    $confirm = Read-Host "Ви впевнені? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "Скасовано." -ForegroundColor Yellow
        exit 0
    }
    docker-compose down -v
    Write-Host "✅ Контейнери та дані видалені" -ForegroundColor Green
} else {
    docker-compose stop
    Write-Host "✅ Контейнери зупинені (дані збережені)" -ForegroundColor Green
}

Write-Host ""
Write-Host "📊 Статус:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "💡 Команди:" -ForegroundColor Yellow
Write-Host "  Запустити знову:    .\start-docker.ps1" -ForegroundColor White
Write-Host "  Запустити вручну:   docker-compose start" -ForegroundColor White
Write-Host "  Видалити все:       .\stop-docker.ps1 -RemoveData" -ForegroundColor White
Write-Host ""
