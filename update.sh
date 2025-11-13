echo "Updating Git"
git pull
echo "Restarting service"
sudo systemctl restart keep-server-awake
echo "Done"