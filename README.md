# lifespan event hook

- Inspired by the event-hook(callback) in javascript.
- Zero third-party dependencies, only requires `python>=3.10`
- Run lifespan functions, without mental burden of nested `async/await`
- Just define event hook functions with `async` or not, then run flow with `await` or not
- Lifespan functions can access the `Context` variable during the whole lifespan
- Enjoy typing hint/check support

## usage:

### 1. （**Highly recommended**）define `async` lifespan functions, run flow with `await flow.run()`:

```python
from hookio import FuncArgs,Context,Flow
import asyncio

async def main_func(x,y, context:Context[dict]):
        context.data['params']={'x':x, 'y':y}
        result=x/y
        print('main get result, but block 2s')
        await asyncio.sleep(2)
        context.data['result']=result
        print('main finished')
        return result
    
async def on_start(msg:int, context:Context[dict]):
    print(f'start: time:{msg}; ')
    await asyncio.sleep(2)
    print(f'start: context:{context} after 2s')

async def on_error(msg:str, context:Context[dict]):
    print(f'error: {context.info["error"]}; msg from user: {msg} ')

async def on_end(context:Context[dict]):
    print(f'end: get result from context: {context.data.get("result", None)}')
    print(f'end: full context: {context}')
    
flow=Flow[dict](
    main_logic = FuncArgs(main_func,(1,2)),
    on_start = FuncArgs(on_start,(0,)),
    on_end = FuncArgs(on_end,()),
    on_error=FuncArgs(on_error,('red',))
)

await flow.run()

# start: time:0; 
# start: context:Context(data={}, info={}) after 2s
# main get result, but block 2s
# main finished
# end: get result from context: 0.5
# end: full context: Context(data={'params': {'x': 1, 'y': 2}, 'result': 0.5}, info={})
```

### 2. define normal `sync` lifespan functions, run flow with `flow.safe_run()`:

```python
from hookio import FuncArgs,Context,Flow
import time

def main_func(x,y, context:Context[dict]):
        context.data['params']={'x':x, 'y':y}
        result=x/y
        print('main get result, but block 2s')
        time.sleep(2)
        context.data['result']=result
        print('main finished')
        return result
    
def on_start(msg:int, context:Context[dict]):
    print(f'start: time:{msg}; ')
    time.sleep(2)
    print(f'start: context:{context} after 2s')

def on_error(msg:str, context:Context[dict]):
    print(f'error: {context.info["error"]}; msg from user: {msg} ')

def on_end(context:Context[dict]):
    print(f'end: get result from context: {context.data.get("result", None)}')
    print(f'end: full context: {context}')
    
flow=Flow[dict](
    main_logic = FuncArgs(main_func,(1,2)),
    on_start = FuncArgs(on_start,(0,)),
    on_end = FuncArgs(on_end,()),
    on_error=FuncArgs(on_error,('red',))
)

flow.safe_run()

# start: time:0; 
# start: context:Context(data={}, info={}) after 2s
# main get result, but block 2s
# main finished
# end: get result from context: 0.5
# end: full context: Context(data={'params': {'x': 1, 'y': 2}, 'result': 0.5}, info={})
```

### 3. Mixing `async/sync` functions lifespan functions, run flow with `flow.safe_run()`:
```python
from hookio import FuncArgs,Context,Flow
import time
import asyncio

async def main_func(x,y, context:Context[dict]):
        context.data['params']={'x':x, 'y':y}
        result=x/y
        print('main get result, but block 2s')
        await asyncio.sleep(2)
        context.data['result']=result
        print('main finished')
        return result
    
def on_start(msg:int, context:Context[dict]):
    print(f'start: time:{msg}; ')
    time.sleep(2)
    print(f'start: context:{context} after 2s')

def on_error(msg:str, context:Context[dict]):
    print(f'error: {context.info["error"]}; msg from user: {msg} ')

def on_end(context:Context[dict]):
    print(f'end: get result from context: {context.data.get("result", None)}')
    print(f'end: full context: {context}')
    
flow=Flow[dict](
    main_logic = FuncArgs(main_func,(1,2)),
    on_start = FuncArgs(on_start,(0,)),
    on_end = FuncArgs(on_end,()),
    on_error=FuncArgs(on_error,('red',))
)

flow.safe_run()

# start: time:0; 
# start: context:Context(data={}, info={}) after 2s
# main get result, but block 2s
# main finished
# end: get result from context: 0.5
# end: full context: Context(data={'params': {'x': 1, 'y': 2}, 'result': 0.5}, info={})
```

### 4. let's trigger the function of `on_error()`:
```python
from hookio import FuncArgs,Context,Flow
import asyncio

async def main_func(x,y, context:Context[dict]):
        context.data['params']={'x':x, 'y':y}
        result=x/y
        print('main get result, but block 2s')
        await asyncio.sleep(2)
        context.data['result']=result
        print('main finished')
        return result
    
async def on_start(msg:int, context:Context[dict]):
    print(f'start: time:{msg}; ')
    await asyncio.sleep(2)
    print(f'start: context:{context} after 2s')

async def on_error(msg:str, context:Context[dict]):
    print(f'error: {context.info["error"]}; msg from user: {msg} ')

async def on_end(context:Context[dict]):
    print(f'end: get result from context: {context.data.get("result", None)}')
    print(f'end: full context: {context}')
    
flow=Flow[dict](
    main_logic = FuncArgs(main_func,(1,0)), ## this will raise error
    on_start = FuncArgs(on_start,(0,)),
    on_end = FuncArgs(on_end,()),
    on_error=FuncArgs(on_error,('red',))
)

await flow.run()

# start: time:0; 
# start: context:Context(data={}, info={}) after 2s
# error: division by zero; msg from user: red 
# end: get result from context: None
# end: full context: Context(data={'params': {'x': 1, 'y': 0}}, info={'error': ZeroDivisionError('division by zero')})
```
## typing support

- `Context`support Generic('T'), and shared by all event-hook functions during while lifespan:
    - `Context` have two properties: 
        - `data`
            - for user to read/write, (eg: record state, share msg)
            - can specify `context.data`'s type by `Context[int]` or `Context[dict[str,Any]]`
        - `info`
            - this is an internally reserved field attribute, 
            - initial value is a empty dict `{}`
            - **waring**: just read but not change it

```python
from hookio import Context

async def on_end(context:Context[dict]):
    print(f'end: get result from context: {context.data.get("result", None)}')
    print(f'end: full context: {context}')

## `Flow` can also specify Generic
flow = Flow[dict](
    ...
    on_error=FuncArgs(on_error,('find_error',))
)
```

## lifespan function definition

- `FuncArgs()` accept two params
    - func: function name
    - args: tuple without `context`. if `func` only accept `context`, should passing it with a empty tuple `()`

```python
from hookio import FuncArgs

async def on_start(msg:int, context:Context[dict]):
    print(f'start: time:{msg}; ')
    await asyncio.sleep(2)
    print(f'start: context:{context} after 2s')

on_start = FuncArgs(on_start, (0,))
```

