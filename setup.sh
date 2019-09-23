# Make sure to have all the packages to proceed
sudo apt update &&
sudo apt install -y nodejs npm python3 python3-pip wget &&

# Install python and node requirements
pip3 install -r requirements.txt &&
npm install --prefix ~ geckodriver &&

# Add geckodriver to the environment variables
echo -e '\n\nPATH="$PATH:$HOME/node_modules/geckodriver/bin"' >> ~/.profile

# Modify the python library due to a bug of the library developer
wget https://raw.githubusercontent.com/mukulhase/WebWhatsapp-Wrapper/master/webwhatsapi/js/wapi.js &&
mv wapi.js $(pip3 show webwhatsapi | grep Location: | awk '{print $2}')/webwhatsapi/js/wapi.js &&

# Due to a bug of the developer the firefox version should be lower than 61.0.2
# Detect the system and proced with the downgrade
if  uname -r | grep -q raspi2; then
	echo -e "\nThe device is a raspberry\n" &&
	sudo apt remove firefox
	wget http://security.debian.org/debian-security/pool/updates/main/f/firefox-esr/firefox-esr_60.9.0esr-1~deb8u1_armhf.deb &&
	sudo dpkg -i firefox-esr_60.9.0esr-1~deb8u1_armhf.deb &&
	sudo apt install -yf &&
	sudo rm firefox-esr_60.9.0esr-1~deb8u1_armhf.deb
else
	echo -e "\nCannot detect the system to downgrade firefox, you must manually downgrade firefox to a version <= 61.0.2"
fi
