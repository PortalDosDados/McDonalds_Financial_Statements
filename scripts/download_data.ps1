#!/usr/bin/env pwsh
<#
Script para baixar os dados do Kaggle usando a CLI.
Pré-requisitos:
- Colocar o arquivo kaggle.json em $env:USERPROFILE\.kaggle\kaggle.json
- Ter a CLI `kaggle` instalada e configurada (vem com o pacote `kaggle` no Python)
#>

if (-not (Test-Path "$env:USERPROFILE\.kaggle\kaggle.json")) {
    Write-Host "Arquivo kaggle.json não encontrado em $env:USERPROFILE\\.kaggle\\kaggle.json" -ForegroundColor Yellow
    Write-Host "Coloque seu kaggle.json lá (baixado da sua conta Kaggle -> Account -> Create New API Token)." -ForegroundColor Yellow
    exit 1
}

mkdir -Force data | Out-Null
Write-Host "Baixando dataset do Kaggle para ./data..." -ForegroundColor Green
kaggle datasets download -d mikhail1681/mcdonalds-financial-statements-2002-2022 -p data --unzip

Write-Host "Download concluído (verifique ./data)." -ForegroundColor Green
