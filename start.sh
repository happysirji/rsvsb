echo "Cloning Repo, Please Wait..."
git clone https://github.com/happysirji/rsvsb.git /rsvsb
cd /rsvsb
echo "Installing Requirements..."
pip3 install -U -r requirements.txt
echo "Starting Bot, Please Wait..."
python3 main.py
