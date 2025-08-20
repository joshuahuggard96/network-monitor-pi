import time 

current_time = time.strftime("%d %b %Y %H:%M:%S")
print(current_time)


router = {
        "ip": "192.168.0.1",
        "status": None, 
        "last_online": None
    },

ip = router.get("ip")
print(ip)