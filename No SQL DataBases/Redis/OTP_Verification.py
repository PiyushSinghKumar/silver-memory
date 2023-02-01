import redis
redis = redis.Redis(
    host='localhost',
    port='6379')

OTP_Driver = redis.get("OTP_Driver")
print("OTP for Driver: ", OTP_Driver)

OTP_Customer = redis.get("OTP_Customer")
print("OTP for Customer: ", OTP_Customer)

if OTP_Driver == OTP_Customer != None:
    print("OTP Verification Successfull")
    redis.expire("OTP_Driver", 10)
    redis.expire("OTP_Customer", 10)
else:
    print("OTP Verification Failed")
