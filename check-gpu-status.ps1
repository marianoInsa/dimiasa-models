<#
.SYNOPSIS
    Verifica que el entorno Windows esta listo para ejecutar
    notebooks/pipeline/01-Entrenamiento-GPU.ipynb.

.DESCRIPTION
    Chequea en orden: Python, GPU (NVIDIA/AMD/Intel), driver NVIDIA,
    TensorFlow con soporte GPU, datos oro en disco, espacio libre.
    Reporta [PASS] / [WARN] / [FAIL] con remediacion accionable.
    Exit code 0 si todo OK, 1 si hay bloqueantes.

.PARAMETER ProjectRoot
    Ruta raiz del proyecto. Por defecto: directorio del script.

.EXAMPLE
    .\check-gpu-status.ps1
    .\check-gpu-status.ps1 -ProjectRoot "D:\CARRERA\CINAPTIC\dimiasa-models"

.NOTES
    No requiere venv activado: detecta automaticamente python del PATH
    o .venv\Scripts\python.exe en el raiz del proyecto.
#>

[CmdletBinding()]
param(
    [string]$ProjectRoot
)

if (-not $ProjectRoot) {
    $scriptPath = $MyInvocation.MyCommand.Path
    if ($scriptPath) {
        $ProjectRoot = Split-Path -Parent $scriptPath
    } else {
        $ProjectRoot = (Get-Location).Path
    }
}

$ErrorActionPreference = "Continue"

# ---- Colores ----------------------------------------------------------------
function Title([string]$msg) {
    Write-Host ""
    Write-Host "=== $msg ===" -ForegroundColor Cyan
}
function Ok([string]$msg)   { Write-Host "  [PASS] $msg" -ForegroundColor Green }
function Warn([string]$msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Fail([string]$msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }
function Info([string]$msg) { Write-Host "  [INFO] $msg" -ForegroundColor Gray }

$BLOCKERS = 0  # contador de [FAIL] bloqueantes

# ---- Resolver ejecutable de Python --------------------------------------------
function Resolve-Python {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Cmd = "python"; Source = "PATH" }
    }
    $venvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) {
        return @{ Cmd = $venvPy; Source = ".venv" }
    }
    return $null
}

# ---- Cabecera ---------------------------------------------------------------
Clear-Host
Write-Host "==========================================================" -ForegroundColor White
Write-Host "  DiMIASA \u2014 Check GPU Status" -ForegroundColor White
Write-Host "  Proyecto: $ProjectRoot" -ForegroundColor Gray
Write-Host "  Fecha:    $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor White

# ---- 1. Sistema operativo ---------------------------------------------------
Title "Sistema operativo"
$os = (Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue).Caption
if ($os) {
    Ok "Windows detectado: $os"
    $osVer = [Environment]::OSVersion.Version
    Write-Host "         Version: $($osVer.Major).$($osVer.Minor) (Build $($osVer.Build))" -ForegroundColor Gray
} else {
    Warn "No se pudo leer el SO (Get-CimInstance fallo)"
    Write-Host "  Este script esta pensado para Windows. En Linux/macOS omitir." -ForegroundColor Yellow
}

# ---- 2. Python --------------------------------------------------------------
Title "Python"
$py = Resolve-Python
if (-not $py) {
    Fail "Python no encontrado. Instalar Python 3.11 o 3.12 desde python.org"
    Write-Host "        Marcá 'Add Python to PATH' durante la instalacion." -ForegroundColor Yellow
    $BLOCKERS++
} else {
    Write-Host "  Fuente: $($py.Source)" -ForegroundColor Gray
    $ver = & $py.Cmd --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Fail "Python encontrado pero no se pudo ejecutar: $($py.Cmd)"
        $BLOCKERS++
    } else {
        Ok "Python: $ver"
        $match = [regex]::Match($ver, "Python (\d+)\.(\d+)")
        if ($match.Success) {
            $major = [int]$match.Groups[1].Value
            $minor = [int]$match.Groups[2].Value
            $okVer = ($major -eq 3 -and $minor -ge 10 -and $minor -lt 12)
            # Aceptar 3.10, 3.11, 3.12, 3.13 (pyproject dice <3.14)
            $okVer = ($major -eq 3 -and $minor -ge 10 -and $minor -le 13)
            if ($okVer) {
                Ok "Version compatible con pyproject.toml (>=3.10, <3.14)"
            } else {
                Fail "Version fuera de rango. Requerido: 3.10.x a 3.13.x"
                Write-Host "        Recomendado: Python 3.11 o 3.12" -ForegroundColor Yellow
                $BLOCKERS++
            }
        }
    }
}

# ---- 3. Hardware GPU ---------------------------------------------------------
Title "Hardware GPU (via WMI)"
$gpus = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -and $_.AdapterCompatibility -match "NVIDIA|AMD|Intel" }
if (-not $gpus -or $gpus.Count -eq 0) {
    Fail "No se detectaron GPUs dedicadas NVIDIA/AMD/Intel"
    Write-Host "        Entrenar el modelo en CPU es posible pero muy lento (~12h)." -ForegroundColor Yellow
    $BLOCKERS++
} else {
    $totalVramGB = 0
    foreach ($gpu in $gpus) {
        $vramGB = if ($gpu.AdapterRAM -and $gpu.AdapterRAM -gt 0) {
            [math]::Round($gpu.AdapterRAM / 1GB, 1)
        } else { 0 }
        $totalVramGB += $vramGB
        Write-Host "  GPU: $($gpu.Name)" -ForegroundColor Gray
        Write-Host "       Fabricante: $($gpu.AdapterCompatibility) | VRAM: ~${vramGB} GB" -ForegroundColor Gray
    }
    if ($totalVramGB -lt 4) {
        Warn "VRAM total ~${totalVramGB} GB < 4 GB recomendado."
        Write-Host "        En el notebook bajar BATCH_SIZE de 512 a 128." -ForegroundColor Yellow
    } else {
        Ok "VRAM total ~${totalVramGB} GB (suficiente para BATCH_SIZE=512)"
    }
}

# ---- 4. Driver NVIDIA (solo si hay NVIDIA) -----------------------------------
Title "Driver NVIDIA (nvidia-smi)"
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
$nvidiaPresent = $false
if ($nvidiaSmi) {
    $smiOut = nvidia-smi --query-gpu=driver_version,name,memory.total --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        $nvidiaPresent = $true
        Ok "nvidia-smi OK"
        foreach ($line in $smiOut) {
            Write-Host "         $line" -ForegroundColor Gray
        }
    } else {
        Warn "nvidia-smi fallo al ejecutar. Driver NVIDIA posiblemente danado."
    }
} else {
    # Verificar si hay GPU NVIDIA aunque nvidia-smi no este
    $hasNvidiaGpu = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "NVIDIA" }
    if ($hasNvidiaGpu) {
        Warn "GPU NVIDIA detectada pero nvidia-smi no esta en PATH."
        Write-Host "        Instalar driver desde https://www.nvidia.com/Download/index.aspx" -ForegroundColor Yellow
        Write-Host "        O usar WSL2 (drivers NVIDIA de Windows son visibles desde WSL2)." -ForegroundColor Yellow
    } else {
        Info "Sin GPU NVIDIA \u2014 se evaluara stack alternativo (DirectML)."
    }
}

# ---- 5. TensorFlow y soporte GPU ---------------------------------------------
Title "TensorFlow + soporte GPU"
$tfBlock = @"
import sys, json
try:
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    cuda = tf.test.is_built_with_cuda()
    print(json.dumps({'ok': True, 'version': tf.__version__,
                      'n_gpus': len(gpus), 'gpus': [g.name for g in gpus],
                      'built_cuda': bool(cuda)}))
except ImportError as e:
    print(json.dumps({'ok': False, 'error': 'ImportError: ' + str(e)}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': type(e).__name__ + ': ' + str(e)}))
"@
if (-not $py) {
    Fail "Python no disponible, no puedo verificar TensorFlow"
    $BLOCKERS++
} else {
    $tfJson = & $py.Cmd -c $tfBlock 2>&1 | Where-Object { $_ -match "^\{" } | Select-Object -First 1
    if (-not $tfJson) {
        Fail "TensorFlow no instalado o no se pudo importar"
        Write-Host "        Instalar con:" -ForegroundColor Yellow
        Write-Host "          pip install 'tensorflow[and-cuda]==2.18.*'   # NVIDIA + CUDA" -ForegroundColor Yellow
        Write-Host "          pip install tensorflow-directml              # AMD/Intel o NVIDIA sin CUDA" -ForegroundColor Yellow
        $BLOCKERS++
    } else {
        try {
            $info = $tfJson | ConvertFrom-Json
        } catch {
            Fail "Salida inesperada de TensorFlow: $tfJson"
            $BLOCKERS++
            $info = $null
        }
        if ($info -and $info.ok) {
            Ok "TensorFlow $($info.version) instalado"
            if ($info.built_cuda) {
                Ok "Compilado con soporte CUDA"
            } else {
                Info "No compilado con CUDA (build CPU o tensorflow-directml)"
            }
            if ($info.n_gpus -gt 0) {
                Ok "$($info.n_gpus) GPU(s) visible(s) para TensorFlow: $($info.gpus -join ', ')"
            } else {
                Fail "TensorFlow no detecta ninguna GPU."
                if ($nvidiaPresent) {
                    Write-Host "        CUDA/cuDNN probablemente no compatibles con TF $($info.version)." -ForegroundColor Yellow
                    Write-Host "        Ver: https://www.tensorflow.org/install/pip#hardware_requirements" -ForegroundColor Yellow
                } else {
                    Write-Host "        pip install tensorflow-directml (provee backend DirectX 12)." -ForegroundColor Yellow
                }
                $BLOCKERS++
            }
        } elseif ($info) {
            Fail "TensorFlow error: $($info.error)"
            $BLOCKERS++
        }
    }
}

# ---- 6. Datos oro en disco --------------------------------------------------
Title "Datos Oro (capa oro/falls/)"
$setA = Join-Path $ProjectRoot "notebooks\data\oro\falls\set_a.parquet"
$setB = Join-Path $ProjectRoot "notebooks\data\oro\falls\set_b.parquet"
foreach ($pair in @(@("set_a", $setA), @("set_b", $setB))) {
    $name = $pair[0]; $path = $pair[1]
    if (Test-Path $path) {
        $sizeMB = [math]::Round((Get-Item $path).Length / 1MB, 1)
        Ok "$name.parquet existe ($sizeMB MB)"
    } else {
        Fail "$name.parquet no encontrado en notebooks\data\oro\falls\"
        Write-Host "        Ejecutar primero notebooks/pipeline/00_Preprocesamiento.ipynb" -ForegroundColor Yellow
        $BLOCKERS++
    }
}

# ---- 7. Espacio en disco -----------------------------------------------------
Title "Espacio en disco"
try {
    $drv = (Get-Item $ProjectRoot).PSDrive
    $freeGB = [math]::Round($drv.Free / 1GB, 1)
    $usedPct = [math]::Round(($drv.Used / ($drv.Used + $drv.Free)) * 100, 1)
    Write-Host "  Unidad $($drv.Name):  ${freeGB} GB libres de $([math]::Round(($drv.Used + $drv.Free)/1GB,1)) GB (${usedPct}% usada)" -ForegroundColor Gray
    if ($freeGB -ge 5) {
        Ok "Espacio libre >= 5 GB (suficiente para modelos + outputs)"
    } elseif ($freeGB -ge 3) {
        Warn "Espacio libre ~${freeGB} GB (apenas suficiente)."
    } else {
        Fail "Espacio libre < 3 GB. Modelos + visualizaciones + logs pueden fallar."
        $BLOCKERS++
    }
} catch {
    Warn "No se pudo consultar el espacio en disco."
}

# ---- 8. Notebook GPU presente -----------------------------------------------
Title "Notebook GPU"
$gpuNb = Join-Path $ProjectRoot "notebooks\pipeline\01-Entrenamiento-GPU.ipynb"
if (Test-Path $gpuNb) {
    $sizeKB = [math]::Round((Get-Item $gpuNb).Length / 1KB, 1)
    Ok "01-Entrenamiento-GPU.ipynb presente ($sizeKB KB)"
} else {
    Fail "01-Entrenamiento-GPU.ipynb no encontrado en notebooks\pipeline\"
    $BLOCKERS++
}

# ---- Veredicto final --------------------------------------------------------
Title "Veredicto"
Write-Host ""
if ($BLOCKERS -eq 0) {
    Write-Host "  +---------------------------------------------------------+" -ForegroundColor Green
    Write-Host "  |  ENTORNO LISTO \u2014 puedes correr el notebook GPU          |" -ForegroundColor Green
    Write-Host "  +---------------------------------------------------------+" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Estimacion de tiempo (RTX 3060/4060):" -ForegroundColor Gray
    Write-Host "    - ~7-12 min por modelo, ~15-25 min totales (2 configs)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Siguiente paso:" -ForegroundColor Cyan
    Write-Host "    jupyter nbconvert --to notebook --execute --inplace notebooks\pipeline\01-Entrenamiento-GPU.ipynb" -ForegroundColor White
    exit 0
} else {
    Write-Host "  +---------------------------------------------------------+" -ForegroundColor Red
    Write-Host "  |  ENTORNO NO LISTO: $BLOCKERS bloqueante(s)                                |" -ForegroundColor Red
    Write-Host "  +---------------------------------------------------------+" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Resolvi los [FAIL] arriba y volve a correr este script." -ForegroundColor Yellow
    Write-Host "  Guias de setup rapidas:" -ForegroundColor Cyan
    Write-Host "    - NVIDIA:  pip install 'tensorflow[and-cuda]==2.18.*'" -ForegroundColor White
    Write-Host "    - AMD/Intel/NVIDIA sin CUDA:  pip install tensorflow-directml" -ForegroundColor White
    Write-Host "    - Datos:  ejecutar 00_Preprocesamiento.ipynb" -ForegroundColor White
    exit 1
}
