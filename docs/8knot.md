# 8Knot Configuration
## Required Ubuntu Packages
```shell
sudo apt install docker &&
sudo apt install docker compose 
```

If you are running Augur on the same computer, you should already have Python3.x installed. If not, for an Ubuntu 22.x Server also issue this command: 
```shell
sudo apt install python3-dev && 
sudo apt install python3.10-venv &&
```

## Clone 8Knot
```shell
git clone https://github.com/oss-aspen/8knot &&
git checkout redis-remap
```


## Start 8knot
To see if everything works: 
```shell
sudo docker compose up --build
```

If you want to run 8Knot in the background: 
```shell
(nohup sudo docker compose up --build &)
```

