rm -rf build
mkdir build
cd build
cmake ../ARGoS_simulation
make
cd ../ARGoS_simulation/data_generation_scripts
for i in {1..10}
do
  argos3 -c ../experiment/social_behavior.argos
  mv robot_positions.csv Results/robot_positions_$i.csv
done
