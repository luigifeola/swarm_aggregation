rm -rf build
mkdir build
cd build
cmake ../ARGoS_simulation
make
cd ../ARGoS_simulation/data_generation_scripts
argos3 -c ../experiment/social_behavior.argos
