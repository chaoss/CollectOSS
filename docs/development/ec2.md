## Configuring EC2 Instance

### Creating your EC2 Instance
1. Be sure you open the ports you need to. This includes the default for ssh, 22. But also 80, 5000 & 8000 from any IP.
2. Create a PEM Key. You will need to ensure it ends in .pem and if on a unix based system, issue a "chmod 600" mypem.pem command from the command line. Here are some more detailed instructions: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html
3. ssh -i software-engineering.pem ubuntu@ec2-52-3-231-155.compute-1.amazonaws.com

### If you have your repo on an UBUNTU EC2 Instance, you can run this command to get everything you need:
 - To Run Automatically and be Prompted:
    - login to you server
    - switch to wherever you are going to save the repo
    - This ASSUMES
      1. You have a repo on GitHub and
      2. You have a fresh EC2 instance
    - Run this:
      - bash <(curl -Ls https://www.dropbox.com/s/ttogu0p0kdo59c1/software-engineering-ghdata.sh?dl=1)

  - To step through it on your own, and inspect the shell script first, then you can follow this process
    - login to you server
    - switch to wherever you are going to save the repo
    - This ASSUMES
      1. You have a repo on GitHub and
      2. You have a fresh EC2 instance
    - Run this:
      - curl -L https://www.dropbox.com/s/ttogu0p0kdo59c1/software-engineering-ghdata.sh?dl=1 > install.sh
      - Then you can inspect the shell script
      - chmod +x install.sh
      - run the shell script: ./install.sh


=====
## Other Information of Use
### Working Example Sites
1. Test1: http://ec2-54-236-59-219.compute-1.amazonaws.com:5000/?owner=hadley&repo=devtools 
2. Test2: http://ec2-34-201-11-60.compute-1.amazonaws.com:5000/?owner=facebook&repo=folly  

### Instructions for installation
1. https://github.com/OSSHealth/ghdata/blob/master/devloperstartup.md

### Another project using the same style of developer environment
1. https://github.com/webpack/docs/wiki/hot-module-replacement-with-webpack
