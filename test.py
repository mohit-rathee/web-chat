import hashlib
import asyncio
async def updateHash():
    hasher=hashlib.sha256()
    while True:
        arg = yield hasher.hexdigest()
        await asyncio.sleep(3)
        print((hasher.hexdigest() + arg).encode())
        hasher.update((hasher.hexdigest() + arg).encode())
async def wait(s):
    await asyncio.sleep(s)
    return "took "+str(s)+" sec" 
async def main():
    hash_generator = updateHash()
    await hash_generator.asend(None)
    result1 = await asyncio.gather(wait(1),hash_generator.asend("arg1"))
    print(result1)
    result2 = await asyncio.gather(hash_generator.asend("arg2"),wait(2))
    print(result2)  
    result3 = h
    print(result3)
asyncio.run(main())
