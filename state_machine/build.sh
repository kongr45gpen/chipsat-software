rm -rf build
cp -r $1 build
cp frame/main.py build/
cp frame/state_machine.py build/
cp -r frame/lib build/
cp -r frame/tasko build/

# state machine visualization generation

export PYTHONDONTWRITEBYTECODE=1
cp buildtools/chart.py build/
cd build
python3 chart.py
dot -Tsvg graph.dot > state_machine.svg
convert -density 600 state_machine.svg state_machine.png
rm chart.py
cd - 