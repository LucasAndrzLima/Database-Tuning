$ErrorActionPreference = 'Stop'
$n2Raiz = Split-Path -Parent $PSScriptRoot
$n2Env = Join-Path $n2Raiz '.env'
if (-not (Test-Path -LiteralPath $n2Env)) {
    $n2Rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    $n2Bytes = New-Object byte[] 32
    $n2Rng.GetBytes($n2Bytes)
    $n2Cookie = [Convert]::ToBase64String($n2Bytes)
    $n2Rng.GetBytes($n2Bytes)
    $n2Secret = [Convert]::ToBase64String($n2Bytes)
    $n2Rng.Dispose()
    [IO.File]::WriteAllText($n2Env, "MYSQL_PASSWORD=root`nREDASH_COOKIE_SECRET=$n2Cookie`nREDASH_SECRET_KEY=$n2Secret`n", [Text.UTF8Encoding]::new($false))
    Write-Host 'Arquivo .env local criado. As chaves não serão mostradas.'
} else {
    Write-Host '.env já existe; configuração preservada.'
}
Write-Host 'Agora execute os comandos Docker do README.'
