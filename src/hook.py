import inspect
import asyncio
from dataclasses import dataclass,field
from typing import Callable,Awaitable,Any,TypeVar,Generic


# 定义一个泛型变量
T = TypeVar('T')

@dataclass
class FuncArgs(Generic[T]):
    func: Callable[..., Awaitable[T] | T]
    args: tuple[Any, ...]

@dataclass
class Context(Generic[T]):
    data:T ## 用户可读写的字段
    info:dict=field(default_factory=lambda: dict()) ## 用户可读，内部flow内部可写的字段

class Flow(Generic[T]):
    def __init__(
        self,
        main_logic: FuncArgs,
        on_start: FuncArgs|None = None,
        on_end: FuncArgs|None = None,
        on_error: FuncArgs|None = None,
        data:T|None=None,
    ):
        
        if not self.check_hook_func(main_logic.func, ['context']):
            raise ValueError(f'main_logic.func:{main_logic.func} must have a param named context')
        else:
            self.main_logic = main_logic

        self.on_start = on_start if on_start and self.check_hook_func(on_start.func, ['context']) else None
        self.on_end = on_end if on_end and self.check_hook_func(on_end.func, ['context']) else None
        self.on_error = on_error if on_error and self.check_hook_func(on_error.func, ['context']) else None
        self.context = Context[T](data) if data else Context[dict]({})

    async def run(self):
        if self.on_start:
            await self._execute_func(self.on_start.func,self.on_start.args)
        try:
            await self._execute_func(self.main_logic.func,self.main_logic.args,)
        except Exception as e:
            if self.on_error:
                self.context.info['error'] = e
                should_raise = await self._execute_func(self.on_error.func, self.on_error.args)
                if should_raise:
                    raise
        finally:
            if self.on_end:
                await self._execute_func(self.on_end.func, self.on_end.args)

    ## flow可以安全的在同步或者异步的上下文执行
    def safe_run(self):
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(self.run())  # 事件循环已经在运行，使用create_task
            else:
                loop.run_until_complete(self.run())
        except RuntimeError:  # 没有正在运行的事件循环
            asyncio.run(self.run())

    
    ## 无感的运行同步和异步代码
    async def _execute_func(self,func,args):
        if inspect.iscoroutinefunction(func):
            await func(*args, context=self.context)
        else:
            func(*args, context=self.context)

    ## 检查回调函数是否还有关键字参数
    @staticmethod
    def check_hook_func(func: Callable, expected_args: list[str]):
        sig = inspect.signature(func)
        params = sig.parameters
        return all(p in params for p in expected_args)
    

if __name__ =='__main__':
    def main_func(x,y, context:Context[dict]):
        result=x/y
        context.data['result']=result
        context.data['params']={'x':x, 'y':y}
        return result
    
    async def on_start(msg:str, context:Context[dict]):
        print(f'start:{msg}; context:{context}')
    
    def on_error(msg:str, context:Context[dict]):
        print(f'error: {msg}; {context.info["error"]}')
    
    def on_end(msg:str, context:Context[dict]):
        print(f'msg:{msg}; state: {context.data.get("result","null")}')

    flow=Flow[dict](
        main_logic = FuncArgs(main_func,(1,0)),
        on_start = FuncArgs(on_start,('start',)),
        on_end = FuncArgs(on_end,('end',)),
        on_error=FuncArgs(on_error,('find_error',))
    )

    asyncio.run(flow.run())