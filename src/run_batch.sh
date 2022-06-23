config_file="../config/config.txt"
config_file_mod="../config/config_mod.txt"
for i in {1..10}
do
  touch "../results/log$i.csv"
  log_path="../results/log$i.csv"
  cp $config_file $config_file_mod
  sed -i "s|__logpath__|$log_path|g" $config_file_mod
  python3 rw_gradient_follower.py ../config/config_mod.txt
done
