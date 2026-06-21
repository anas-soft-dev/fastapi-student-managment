import time
import asyncio

async def task1():
    print("task 1 started")
    await asyncio.sleep(3)
    return "task 1 done"
async def task2():
    print("task 2 started")
    await asyncio.sleep(3)
    return "task 2 done"

async def main():
    res1, res2 = await asyncio.gather(
        task1(),
        task2()
    )
    print(res1)
    print(res2)

# asyncio.run(main())



class Book():
    def __init__(self, title):
        self.title = title
    def __call__(self, *args, **kwds):
        print(self.title)

Book("python")()