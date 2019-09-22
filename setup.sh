sudo apt update &&
sudo apt install -y nodejs npm python3 python3-pip &&
pip install -r requirements.txt &&
npm install geckodriver &&

sudo apt install -y firefox=59.0.2 &&
wget https://raw.githubusercontent.com/mukulhase/WebWhatsapp-Wrapper/master/webwhatsapi/js/wapi.js &&
mv wapi.js ~/.local/lib/python3.7/site-packages/webwhatsapi/js/wapi.js
