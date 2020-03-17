# python-Pipeline
design a simple pipeline for daily job, freer than Pipeline in sklearn

主要为了提供一种类似于sklearn的pipeline，但又没有fit、transform函数统一、以及输出格式为numpy等限制的pipeline。

可用于一般任务的流水线，也同样可以用于多算法模块的流水线。

用法参考下面示例。

example:
``````
class StepA:
    def __init__(self, base_value):
        self.base_value = base_value

    def add_value(self, value):
        self.base_value += value
        return self.base_value

class StepB:
    def __init__(self, base_value):
        self.base_value = base_value

    def minus_value(self, value):
        self.base_value = self.base_value - value
        return self.base_value

    def multi_val(self, value):
        self.base_value = self.base_value * value
        return self.base_value

a_ins = StepA(1)
b_ins = StepB(100)
pipeline = Pipeline(
    [('name_a', a_ins, "add_value"), ("name_b", b_ins, "multi_val"), ('name_c', a_ins, "add_value")])
parameters = {
    'name_a__value': 1,  # 1+1 = 2
    'name_b__value': "name_a.output",  # 100 * 2 = 200
    'name_c__value': "name_b.output"  # 200 + 2 = 202
}
pipeline.set_params(parameters)
pipeline.run()
results = pipeline.get_results()
print(results)          # return： [2, 200, 202]
``````
说明：
```
1、Pipeline初始化必须传任务列表。

2、列表中每个元组必须是三个元素，即(任务别名，实例，函数名), 其中任务别名和函数名必须是字符串形式。

3、参数形式类同Sklearn，别名之后双下划线，然后输入函数所需参数的key，value。

4、在初始化以后，每个别名都自带有output属性，在参数中可以写“别名.output”来表示获取对应任务的输出。此处必须以字符串形式。

```
特点：
``````
1、可以单起一个线程跑。当然，也可以是使用函数调用run()方法来运行。

2、会保留每一步的执行结果、函数名、对应参数和实例名。每步执行之后会删除本步骤对应实例。

3、对应函数可以自己任意指定，只需要保证该函数是该实例拥有的就行。必须以字符串形式指定。

4、可以使用前面任意一步或者多步的结果输出，即以 “别名.output” 的形式写到参数里即可。

5、日志体系自我感觉做得比较优雅。每一步都比较清晰地看到开始结束，以及中间经历。
``````
测试用例：
``````
测试用例零： task2用task1的结果。task3用task2的结果。

测试用例一:  task3只使用task1的输出。

测试用例二： task3直接使用task2和task1的结果。task4用task3结果。

测试用例三： task1有参数，task2没有参数，task3用task1的结果。

测试用例四：十个任务并行跑，每个任务2秒左右，并行之后总时间还是2秒左右，结果都正确。
``````
日志输出示例：
``````
task list start building
task add: <object EachObject, name:name_a,ins:<object StepA>,func:add_value,output:None,params:{}>
task add: <object EachObject, name:name_b,ins:<object StepB>,func:multi_val,output:None,params:{}>
task add: <object EachObject, name:name_c,ins:<object StepA>,func:add_value,output:None,params:{}>
task list build finished
----------
task params start setting
task name_b, initial parameters:{'value': 'name_a.output', '88494a8a-6830-11ea-afe6-0205857feb80': 1}
task name_b, set parameters: {'value': 'name_a.output'}
task name_c, initial parameters:{'value': 'name_b.output', '88494a8a-6830-11ea-afe6-0205857feb80': 1}
task name_c, set parameters: {'value': 'name_b.output'}
task name_a, initial parameters:{'value': 1}
task name_a, set parameters: {'value': 1}
task params set finished
----------
task jobs start executing:
task_list: ['name_a', 'name_b', 'name_c']
executing task: name_a
name_a finished
executing task: name_b
params before update:{'value': 'name_a.output'}
params after update:{'value': 2}
name_b finished
executing task: name_c
params before update:{'value': 'name_b.output'}
params after update:{'value': 200}
name_c finished
task jobs execute finished
----------
task results:
task_list:['name_a', 'name_b', 'name_c']
functions:['<object StepA>:add_value', '<object StepB>:multi_val', '<object StepA>:add_value']
results:[2, 200, 202]
----------
[2, 200, 202]
``````
