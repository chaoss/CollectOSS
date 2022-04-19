# Example Certificate Response Using Certbot

Which names would you like to activate HTTPS for?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1: augur.augurlabs.io
2: new.augurlabs.io
3: old.augurlabs.io
4: augur.chaoss.io
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Select the appropriate numbers separated by commas and/or spaces, or leave input
blank to select all options shown (Enter 'c' to cancel): 4
Requesting a certificate for augur.chaoss.io

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/augur.chaoss.io/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/augur.chaoss.io/privkey.pem
This certificate expires on 2022-07-12.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

Deploying certificate
Successfully deployed certificate for augur.chaoss.io to /etc/nginx/sites-enabled/augur.chaoss.io
Congratulations! You have successfully enabled HTTPS on https://augur.chaoss.io

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
