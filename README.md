# lifespan event hook

- Inspired by the event-hook(callback) in javascript.
- Zero third-party dependencies, only requires `python>=3.10`
- Run lifespan functions, without mental burden of nested `async/await`
- Just define event hook functions with `async` or not, then run flow with `await` or not
- Lifespan functions can access the `Context` variable during the whole lifespan
- Execute the event hook functions sequentially, or customize the main-logic function
- Enjoy typing check/hint support

## usage:

### 1. **High Recommend 👍:** Define async hook functions, run flow with `await flow.run()`

```python
from hookio import Flow

 # Define Hook type and Ctx type
class MyHook:
    hook_one:Callable
    hook_two:Callable

@dataclass()
class MyCtx:
    state:str=''
    state_list:list=field(default_factory=list)

# Define some hooks
async def hook_one(ctx:MyCtx):
    print(f"start Hook One: ctx.state is {ctx.state}")
    ctx.state = "Completed"
    ctx.state_list.append({'hook1':ctx.state})
    print(f"leave Hook One: {ctx.state_list}")

async def hook_two(ctx:MyCtx):
    print(f"start Hook Two: ctx.state is {ctx.state}")
    ctx.state = "error"
    ctx.state_list.append({'hook2':ctx.state})
    print(f"leave Hook Two: {ctx.state_list}")

# Define main_logic
async def main_function(hooks:MyHook,ctx:MyCtx):
    print(f"Executing Main Function:{ctx.state}")
    # access ctx in main logic
    ctx.state='main_start'
    await hooks.hook_one(ctx)
    await hooks.hook_two(ctx)
    print("Main Function Completed")

# Create a Flow instance
flow = Flow(
    hooks=[hook_one, hook_two],
    ctx=MyCtx(state='init', state_list=[])
)
# Run with await flow.run()
await flow.run()
print(f'flow finished and before cleanup: {flow.ctx}')
flow.cleanup()
print(f'after cleanup: {flow.ctx}')

# start Hook One: ctx.state is init
# leave Hook One: [{'hook1': 'Completed'}]
# start Hook Two: ctx.state is Completed
# leave Hook Two: [{'hook1': 'Completed'}, {'hook2': 'error'}]
# flow finished and before cleanup: MyCtx(state='error', state_list=[{'hook1': 'Completed'}, {'hook2': 'error'}])
# after cleanup: {}
```

### 2. Define hook functions, run flow with `flow.safe_run()`

```python
from hookio import Flow

 # Define Hook type and Ctx type
class MyHook:
    hook_one:Callable
    hook_two:Callable

@dataclass()
class MyCtx:
    state:str=''
    state_list:list=field(default_factory=list)

# Define some hooks
await def hook_one(ctx:MyCtx):
    print(f"start Hook One: ctx.state is {ctx.state}")
    ctx.state = "Completed"
    ctx.state_list.append({'hook1':ctx.state})
    print(f"leave Hook One: {ctx.state_list}")

def hook_two(ctx:MyCtx):
    print(f"start Hook Two: ctx.state is {ctx.state}")
    ctx.state = "error"
    ctx.state_list.append({'hook2':ctx.state})
    print(f"leave Hook Two: {ctx.state_list}")

# Create a Flow instance
flow = Flow(
    hooks=[hook_one, hook_two],
    ctx=MyCtx(state='init', state_list=[])
)
# Run with flow.safe_run()
flow.safe_run()
print(f'flow finished and before cleanup: {flow.ctx}')
flow.cleanup()
print(f'after cleanup: {flow.ctx}')

# start Hook One: ctx.state is init
# leave Hook One: [{'hook1': 'Completed'}]
# start Hook Two: ctx.state is Completed
# leave Hook Two: [{'hook1': 'Completed'}, {'hook2': 'error'}]
# flow finished and before cleanup: MyCtx(state='error', state_list=[{'hook1': 'Completed'}, {'hook2': 'error'}])
# after cleanup: {}
```

### 3. **Advance Usage 😈**: mixing `async/sync` hook functions, run your own custom main_flow_logic function 

```python
from hookio import Flow

 # Define Hook type and Ctx type
class MyHook:
    hook_one:Callable
    hook_two:Callable

@dataclass()
class MyCtx:
    state:str=''
    state_list:list=field(default_factory=list)

# Define some hooks
async def hook_one(ctx:MyCtx):
    print(f"start Hook One: ctx.state is {ctx.state}")
    ctx.state = "Completed"
    ctx.state_list.append({'hook1':ctx.state})
    print(f"leave Hook One: {ctx.state_list}")

async def hook_two(ctx:MyCtx):
    print(f"start Hook Two: ctx.state is {ctx.state}")
    ctx.state = "error"
    ctx.state_list.append({'hook2':ctx.state})
    print(f"leave Hook Two: {ctx.state_list}")

# Define main_logic
async def main_function(hooks:MyHook,ctx:MyCtx):
    print(f"Executing Main Function:{ctx.state}")
    # access ctx in main logic
    ctx.state='main_start'
    await hooks.hook_one(ctx)
    hooks.hook_two(ctx)
    print("Main Function Completed")

# Create a Flow instance
flow = Flow(
    hooks=[hook_one, hook_two],
    logic=main_function,
    ctx=MyCtx(state='init', state_list=[])
)
# Run with await flow.run()
await flow.run()
print(f'flow finished and before cleanup: {flow.ctx}')
flow.cleanup()
print(f'after cleanup: {flow.ctx}')

# Executing Main Function:init
# start Hook One: ctx.state is main_start
# leave Hook One: [{'hook1': 'Completed'}]
# start Hook Two: ctx.state is Completed
# leave Hook Two: [{'hook1': 'Completed'}, {'hook2': 'error'}]
# Main Function Completed
# flow finished and before cleanup: MyCtx(state='error', state_list=[{'hook1': 'Completed'}, {'hook2': 'error'}])
# after cleanup: {}
```

## Typing check/hint for IDE 😊

```python
class Hook:
    hook_one:Callable
    hook_two:Callable
    ...
    
@dataclass()
class MyCtx:
    state:str=''
    state_list:list=field(default_factory=list)
    ...
```

