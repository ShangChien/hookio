import inspect
import asyncio
from dataclasses import dataclass,field
from typing import Callable,TypeVar,Generic,Any


@dataclass
class Hooks:
    pass

# 定义泛型变量
T = TypeVar('T')

@dataclass
class Flow(Generic[T]):
    hooks: list[Callable[...,Any]] = field(default_factory = lambda : list())
    logic: Callable[..., Any]| None = None
    ctx: T | dict = field(default_factory = lambda : dict())
    inner_hooks: Hooks = field(default_factory= lambda : Hooks())


    def __post_init__(self):
        for i in self.hooks:
            setattr(self.inner_hooks, i.__name__, i)
    

    async def run(self):
        # 如果用户有自定义逻辑则执行自定义逻辑，否则顺序执行hooks
        if self.logic:
            await self._execute_logic(self.logic)

        else:
            for hook in self.hooks:
                await self._execute_hook(hook)

    
    ## 无感的运行同步和异步的自定义逻辑
    async def _execute_logic(self,func):
        #检查函数是否为异步
        is_async = inspect.iscoroutinefunction(func)
        
        # 确定params是否传递 ctx, hooks
        kwargs={}
        sig = inspect.signature(func)
        params=sig.parameters
        params_length = len(params)

        if params_length > 2:
            raise ValueError(f"HOOKIO ERROR: Function '{func.__name__}' can only pass in two parameters at most, named 'ctx' and 'hooks'.")
        
        if params_length == 2:
            if set(params.keys()) == set(['ctx','hooks']):
                kwargs['ctx'] = self.ctx
                kwargs['hooks'] = self.inner_hooks
            else:
                raise ValueError(f"HOOKIO ERROR: Function '{func.__name__}' can only pass in two parameters at most, named 'ctx' and 'hooks'.")

        if params_length == 1:
            if 'ctx' in params:
                kwargs['ctx'] = self.ctx
            elif 'hooks' in params:
                kwargs['hooks'] = self.inner_hooks
            else:
                raise ValueError(f"HOOKIO ERROR: Function '{func.__name__}' can only pass in two parameters at most, named 'ctx' and 'hooks'.")

        if len(sig.parameters) == 0:
            pass

        # 根据是否异步和是否传递 ctx 来调用函数
        if is_async:
            await func(**kwargs) 
        else:
            func(**kwargs)


    ## 无感的运行同步或异步hook
    async def _execute_hook(self,func):
        #检查函数签名
        is_async = inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)

        # 确定是否传递 ctx
        if len(sig.parameters) == 1 and 'ctx' in sig.parameters:
            pass_ctx=True
        elif len(sig.parameters) == 0:
            pass_ctx=False
        else:
            raise ValueError(f"HOOKIO ERROR: Function '{func.__name__}' must have either zero parameters or one parameter named 'ctx'.")
        
        # 根据是否异步和是否传递 ctx 来调用函数
        if is_async:
            if pass_ctx:
                await func(self.ctx) 
            else:
                await func() 
        else:
            if pass_ctx:
                func(self.ctx) 
            else:
                func()


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
        except Exception as e:
            print(f"An error occurred: {e}")  # 处理其他异常


        
if __name__ =='__main__':

    #定义类型
    class MyHook(Hooks):
        hook_one:Callable
        hook_two:Callable
    
    @dataclass()
    class MyCtx:
        state:str=''
        state_list:list=field(default_factory=list)

    # Define some hooks
    async def hook_one(ctx:MyCtx):
        print("Executing Hook One")
        ctx.state = "Completed"
        ctx.state_list.append({'hook1':ctx.state})

    def hook_two(ctx:MyCtx):
        print("Executing Hook Two")
        ctx.state = "Completed"
        ctx.state_list.append({'hook2':ctx.state})
        print(ctx)
    
    async def main_function(hooks:MyHook,ctx:MyCtx):
        print("Executing Main Function")
        await hooks.hook_one(ctx)
        hooks.hook_two(ctx)
        print("Main Function Completed")

    # Create a Flow instance
    flow = Flow(hooks=[hook_one, hook_two],logic=main_function,ctx=MyCtx(state='',state_list=[]))

    # Run the flow
    flow.safe_run()
    print(flow.ctx)