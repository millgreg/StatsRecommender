@echo off
echo Starting StatsRecommender Audit Pipeline...

REM Activate Environment (assuming Miniforge/Conda)
call C:\Users\Greg\miniforge3\condabin\conda.bat activate stats_rec_env

if errorlevel 1 (
    echo Error: Could not activate conda environment 'stats_rec_env'.
    echo Please make sure you have installed it: conda env create -f environment.yml
    pause
    exit /b
)

echo.
echo Environment activated.
echo.

echo --- STEP 1: Running Audit Pipeline ---
echo (This will ingest PDFs, parse XMLs, extract features, and generate feedback)
python src/run_pipeline.py

if errorlevel 1 (
    echo Pipeline execution failed!
    pause
    exit /b
)

echo.
echo --- Pipeline Complete ---
echo.
echo Opening Dashboard...
start reports/rigor_dashboard.html

pause
