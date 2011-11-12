PKGS="nginx python-flup python-rrdtool rrdtool spawn-fcgi"

sudo apt-get -y install $PKGS
id -u bogomon || sudo useradd bogomon || exit 1
sudo mkdir -p /usr/lib/bogomon /var/lib/bogomon /var/run/bogomon
REPO=https://raw.github.com/jjo/bogomon/master
for f in etc/nginx/sites-available/bogomon usr/lib/bogomon/bogomon.fcgi.py etc/init.d/spawn-fcgi;do
	sudo wget -O /$f $REPO/$f || exit 1
done
sudo ln -sf ../sites-available/bogomon /etc/nginx/sites-enabled/bogomon
sudo chmod +x /etc/init.d/spawn-fcgi
sudo /etc/init.d/spawn-fcgi restart
sudo /etc/init.d/nginx configtest || exit 1
sudo /etc/init.d/nginx status && sudo /etc/init.d/nginx start || sudo /etc/init.d/nginx restart
