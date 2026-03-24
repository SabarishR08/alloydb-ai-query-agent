param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$queryEndpoint = "$BaseUrl/query"
$healthEndpoint = "$BaseUrl/health"

Write-Host "Checking health endpoint: $healthEndpoint"
try {
    $health = Invoke-RestMethod -Uri $healthEndpoint -Method Get
    Write-Host "Health response:" ($health | ConvertTo-Json -Depth 5)
} catch {
    Write-Error "Health check failed: $($_.Exception.Message)"
    exit 1
}

$requests = @(
    @{ query = "Top DevOps tools" },
    @{ query = "List vector databases" },
    @{ query = "Top backend tools" }
)

foreach ($req in $requests) {
    Write-Host "`nQuery: $($req.query)"
    try {
        $payload = $req | ConvertTo-Json
        $response = Invoke-RestMethod -Uri $queryEndpoint -Method Post -ContentType "application/json" -Body $payload

        Write-Host "Generated SQL:"
        Write-Host $response.sql

        $rows = @($response.results)
        if ($rows.Count -eq 0) {
            Write-Host "No rows returned."
            continue
        }

        Write-Host "Top rows:"
        $rows | Select-Object -First 5 | Format-Table id, name, category, popularity_score -AutoSize
    } catch {
        Write-Error "Query failed: $($_.Exception.Message)"
    }
}
