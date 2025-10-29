[CmdletBinding()]
Param(
	# Clean up all files and directories
	[switch]$clean,

  # Commands
  [switch]$all,
  [switch]$copyall,

  [switch]$doc,
  [switch]$livedoc,
  [switch]$doccov,

  [switch]$unit,
  [switch]$liveunit,
  [switch]$copyunit,

  [switch]$cov,
  [switch]$livecov,
  [switch]$copycov,

  [switch]$type,
  [switch]$livetype,
  [switch]$copytype,

  [switch]$nooutput,

  [switch]$build,
  [switch]$install,

	# Display this help"
	[switch]$help
)

$PackageName = "pyVHDLModel"
$PackageVersion = "0.33.0"

# set default values
$EnableDebug =        [bool]$PSCmdlet.MyInvocation.BoundParameters["Debug"]
$EnableVerbose =      [bool]$PSCmdlet.MyInvocation.BoundParameters["Verbose"] -or $EnableDebug

# Display help if no command was selected
$help = $help -or ( -not(
  $all -or $copyall -or
    $clean -or
    $doc -or $livedoc -or $doccov -or
    $unit -or $liveunit -or $copyunit -or
    $cov -or $livecov -or $copycov -or
    $type -or $livetype -or $copytype -or
    $build -or $install
  )
)

Write-Host "================================================================================" -ForegroundColor Magenta
Write-Host "$PackageName Documentation Compilation and Assembly Tool"                         -ForegroundColor Magenta
Write-Host "================================================================================" -ForegroundColor Magenta

if ($help)
{	Get-Help $MYINVOCATION.MyCommand.Path -Detailed
	exit 0
}

if ($all)
{	$doc =      $true
	$unit =     $true
#	$copyunit = $true
	$cov =      $true
#	$copycov =  $true
	$type =     $true
	$copytype = $true
}
if ($copyall)
{# $copyunit = $true
#  $copycov =  $true
  $copytype = $true
}

if ($clean)
{ Write-Host -ForegroundColor DarkYellow    "[live][DOC]        Cleaning documentation directories ..."
  rm -Force .\doc\$PackageName\*
  .\doc\make.bat clean
  Write-Host -ForegroundColor DarkYellow   "[live][BUILD]      Cleaning build directories ..."
  rm -Force .\build\bdist.win-amd64
  rm -Force .\build\lib
}

if ($build)
{ Write-Host -ForegroundColor Yellow        "[live][BUILD]      Cleaning build directories ..."
  rm -Force .\build\bdist.win-amd64
  rm -Force .\build\lib
  Write-Host -ForegroundColor Yellow        "[live][BUILD]      Building $PackageName package as wheel ..."
  py -3.14 -m build --wheel --no-isolation

  Write-Host -ForegroundColor Yellow        "[live][BUILD]      Building wheel finished"
}
if ($install)
{ if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
  { Write-Host -ForegroundColor Yellow      "[live][INSTALL]    Installing $PackageName with administrator rights ..."
    $proc = Start-Process pwsh.exe "-NoProfile -ExecutionPolicy Bypass -WorkingDirectory `"$PSScriptRoot`" -File `"$PSCommandPath`" `"-install`"" -Verb RunAs -Wait

#    Write-Host -ForegroundColor Yellow   "[live][INSTALL]    Wait on administrator console ..."
#    Wait-Process -Id $proc.Id
  }
  else
  { Write-Host -ForegroundColor Cyan        "[ADMIN][UNINSTALL] Uninstalling $PackageName ..."
    py -3.14 -m pip uninstall -y $PackageName
    Write-Host -ForegroundColor Cyan        "[ADMIN][INSTALL]   Installing $PackageName from wheel ..."
    py -3.14 -m pip install .\dist\$($PackageName.Replace(".", "_").ToLower())-$PackageVersion-py3-none-any.whl

    Write-Host -ForegroundColor Cyan        "[ADMIN][INSTALL]   Closing window in 5 seconds ..."
    Start-Sleep -Seconds 5
  }
}

$jobs = @()

if ($livedoc)
{ Write-Host -ForegroundColor DarkYellow    "[live][DOC]       Building documentation using Sphinx ..."

  .\doc\make.bat html --verbose

  Write-Host -ForegroundColor DarkYellow    "[live][DOC]       Documentation finished"
}
elseif ($doc)
{ Write-Host -ForegroundColor DarkYellow    "[Job1][DOC]       Building documentation using Sphinx ..."
  Write-Host -ForegroundColor DarkGreen     "[SCRIPT]          Starting Documentation job ..."

  # Compile documentation
  $compileDocFunc = {
    .\doc\make.bat html --verbose
  }
  $docJob = Start-Job -Name "Documentation" -ScriptBlock $compileDocFunc
#  $jobs += $docJob
}


if ($doccov)
{
  .\doc\make.bat coverage
}

if ($liveunit)
{ Write-Host -ForegroundColor DarkYellow    "[live][UNIT]      Running Unit Tests using pytest ..."

  $env:GHDL_PREFIX = "C:\Tools\GHDL\6.0.0.dev0-ucrt64-mcode\lib\ghdl"
  $env:ENVIRONMENT_NAME = "Windows (x86-64)"
  pytest -raP --color=yes --junitxml=report/unit/TestReportSummary.xml --template=html1/index.html --report=report/unit/html/index.html --split-report tests/unit

  pyedaa-reports -v unittest "--merge=pyTest-JUnit:report/unit/TestReportSummary.xml" "--name=$PackageName" "--pytest=rewrite-dunder-init;reduce-depth:pytest.tests.unit" "--output=pyTest-JUnit:report/unit/unittest.xml"

  if ($copyunit)
  { cp -Recurse -Force .\report\unit\html\* .\doc\_build\html\unittests
    Write-Host -ForegroundColor DarkBlue    "[live][UNIT]      Copyed unit testing report to 'unittests' directory in HTML directory"
  }

  Write-Host -ForegroundColor DarkYellow    "[live][UNIT]      Unit Tests finished"
}
elseif ($unit)
{ Write-Host -ForegroundColor DarkYellow    "[Job2][UNIT]      Running Unit Tests using pytest ..."
  Write-Host -ForegroundColor DarkGreen     "[SCRIPT]          Starting UnitTests jobs ..."

  # Run unit tests
  $runUnitFunc = {
    $env:GHDL_PREFIX = "C:\Tools\GHDL\6.0.0.dev0-ucrt64-mcode\lib\ghdl"
    $env:ENVIRONMENT_NAME = "Windows (x86-64)"
    pytest -raP --color=yes --junitxml=report/unit/TestReportSummary.xml --template=html1/index.html --report=report/unit/html/index.html --split-report tests/unit

    pyedaa-reports -v unittest "--merge=pyTest-JUnit:report/unit/TestReportSummary.xml" "--name=$PackageName" "--pytest=rewrite-dunder-init;reduce-depth:pytest.tests.unit" "--output=pyTest-JUnit:report/unit/unittest.xml"
  }
  $unitJob = Start-Job -Name "UnitTests" -ScriptBlock $runUnitFunc
  $jobs += $unitJob
}

if ($livecov)
{ Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Running Unit Tests with coverage ..."

  $env:GHDL_PREFIX = "C:\Tools\GHDL\6.0.0.dev0-ucrt64-mcode\lib\ghdl"
  $env:ENVIRONMENT_NAME = "Windows (x86-64)"
  coverage run --data-file=.coverage --rcfile=pyproject.toml -m pytest -ra --tb=line --color=yes tests/unit

  Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Convert coverage report to HTML ..."
  coverage html

  Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Convert coverage report to XML (Cobertura) ..."
  coverage xml

  Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Convert coverage report to JSON ..."
  coverage json

  Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Write coverage report to console ..."
  coverage report

  if ($copycov)
  { cp -Recurse -Force .\report\coverage\html\* .\doc\_build\html\coverage
    Write-Host -ForegroundColor DarkMagenta "[live][COV]       Copyed code coverage report to 'coverage' directory in HTML directory"
  }

  Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Coverage finished"
}
elseif ($cov)
{ Write-Host -ForegroundColor DarkMagenta   "[live][COV]       Running Unit Tests with coverage ..."
  Write-Host -ForegroundColor DarkMagenta   "[SCRIPT]          Starting Coverage jobs ..."

  # Collect coverage
  $collectCovFunc = {
    $env:GHDL_PREFIX = "C:\Tools\GHDL\6.0.0.dev0-ucrt64-mcode\lib\ghdl"
    $env:ENVIRONMENT_NAME = "Windows (x86-64)"
    coverage run --data-file=.coverage --rcfile=pyproject.toml -m pytest -ra --tb=line --color=yes tests/unit

    Write-Host -ForegroundColor DarkMagenta "[Job3][COV]       Convert coverage report to HTML ..."
    coverage html

    Write-Host -ForegroundColor DarkMagenta "[Job3][COV]       Convert coverage report to XML (Cobertura) ..."
    coverage xml

    Write-Host -ForegroundColor DarkMagenta "[Job3][COV]       Convert coverage report to JSON ..."
    coverage json
  }
  $covJob = Start-Job -Name "Coverage" -ScriptBlock $collectCovFunc
  $jobs += $covJob
}

if ($livetype)
{ Write-Host -ForegroundColor DarkCyan      "[live][TYPE]      Running static type analysis using mypy ..."

  $env:MYPY_FORCE_COLOR = 1
  mypy.exe -p $PackageName

  if ($copytype)
  { cp -Recurse -Force .\report\typing\* .\doc\_build\html\typing
    Write-Host -ForegroundColor DarkCyan    "[live][TYPE]      Copyed typing report to 'typing' directory in HTML directory."
  }

  Write-Host -ForegroundColor DarkCyan      "[live][TYPE]      Static type analysis finished"
}
elseif ($type)
{ Write-Host -ForegroundColor DarkCyan      "[live][TYPE]      Running static type analysis using mypy ..."
  Write-Host -ForegroundColor DarkCyan      "[SCRIPT]          Starting Typing jobs ..."

  # Analyze types
  $analyzeTypesFunc = {
    $env:MYPY_FORCE_COLOR = 1
    mypy.exe -p $PackageName
  }
  $typeJob = Start-Job -Name "Typing" -ScriptBlock $analyzeTypesFunc
  $jobs += $typeJob
}


if ($doc)
{ Write-Host -ForegroundColor DarkGreen     "[SCRIPT]          Waiting on Documentation job ..."
  Wait-Job -Job $docJob
  Write-Host -ForegroundColor DarkYellow    "[Job1][DOC]       Documentation finished"
}
if ($jobs.Count -ne 0)
{
  Write-Host -ForegroundColor DarkGreen (   "[SCRIPT]          Waiting on {0} jobs ({1}) ..." -f $jobs.Count, (($jobs | %{ $_.Name }) -join ", "))
  Wait-Job -Job $jobs
}


if (-not $liveunit -and $copyunit)
{
#  if ($unit)
#  { Wait-Job -Job $unitJob
#    Write-Host -ForegroundColor DarkBlue "[Job2][UNIT] Unit tests finished"
#  }
  cp -Recurse -Force .\report\unit\html\* .\doc\_build\html\unittests
  Write-Host -ForegroundColor DarkBlue      "[post][UNIT]      Copyed unit testing report to 'unittests' directory in HTML directory"
}
if (-not ($livecov -or $cov) -and $copycov)
{
#  if ($cov)
#  { Wait-Job -Job $unitJob
#    Write-Host -ForegroundColor DarkMagenta "[Job3][UNIT] Coverage collection finished"
#  }
  cp -Recurse -Force .\report\coverage\html\* .\doc\_build\html\coverage
  Write-Host -ForegroundColor DarkMagenta   "[post][COV]       Copyed code coverage report to 'coverage' directory in HTML directory"
}
if (-not $livetype -and $copytype)
{
#  if ($type)
#  { Wait-Job -Job $typeJob
#    Write-Host -ForegroundColor DarkCyan "[Job4][UNIT] Static type analysis finished"
#  }
  cp -Recurse -Force .\report\typing\* .\doc\_build\html\typing
  Write-Host -ForegroundColor DarkCyan      "[post][TYPE]      Copyed typing report to 'typing' directory in HTML directory."
}


if ($type)
{ Write-Host -ForegroundColor DarkCyan      "================================================================================"
  if (-not $nooutput)
  { Receive-Job -Job $typeJob
  }
  Remove-Job  -Job $typeJob
}
if ($doc)
{ Write-Host -ForegroundColor DarkYellow    "================================================================================"
  if (-not $nooutput)
  { Receive-Job -Job $docJob
  }
  Remove-Job  -Job $docJob
}
if ($unit)
{ Write-Host -ForegroundColor DarkBlue      "================================================================================"
  if (-not $nooutput)
  { Receive-Job -Job $unitJob
  }
  Remove-Job  -Job $unitJob
}
if ($cov)
{ Write-Host -ForegroundColor DarkMagenta   "================================================================================"
  if (-not $nooutput)
  { Receive-Job -Job $covJob
  }
  Remove-Job  -Job $covJob

  if ($copycov)
  { cp -Recurse -Force .\report\coverage\html\* .\doc\_build\html\coverage
    Write-Host -ForegroundColor DarkMagenta "[post][COV]       Copyed code coverage report to 'coverage' directory in HTML directory"
  }
}
Write-Host -ForegroundColor DarkGreen       "================================================================================"
Write-Host -ForegroundColor DarkGreen       "[SCRIPT]          Finished"
