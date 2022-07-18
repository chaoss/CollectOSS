# Instructions for macOS SetUp:
####  While running Augur on macOS, we strongly recommend updating your shell’s initialization script as follows:

1. Open a terminal:
   -  `nano .bash_profile`
2. Add the following line to the end of the file:
   -  `export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`



### Issue Resolved

Users faced the issue that in the installation page, it says:

- If you’re running Augur on macOS, we strongly suggest adding the following line to your shell’s initialization script:
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES 

