test
Server     Description       Log                   Monitoring                   PID                        
------------------------------------------------------------------------------------------                 
Frontend   Brunch            logs/frontend.log     make monitor-backend         8480 
Backend    Augur/Gunicorn    logs/backend.log      make monitor-frontend        8440 

Monitor both:  make monitor  
Restart and monitor: make dev
Restart servers:  make dev-start 
Stop servers:  make dev-stop 
