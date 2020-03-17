from pipeline import Pipeline
import time


class StepA:
    def __init__(self, base_value):
        self.base_value = base_value

    def add_value(self, value):
        self.base_value += value
        return self.base_value

    def __str__(self):
        return "<object StepA>"


class StepB:
    def __init__(self, base_value):
        self.base_value = base_value

    def minus_value(self, value):
        self.base_value = self.base_value - value
        return self.base_value

    def multi_val(self, value):
        self.base_value = self.base_value * value
        return self.base_value

    def self_double(self):
        self.base_value *= 2
        return self.base_value

    def add_two(self, value_one, value_two):
        return value_one + value_two

    def __str__(self):
        return "<object StepB>"


def example_zero():
    # 测试用例零： task2用task1的结果。task3用task2的结果。
    # test_case_zero: task2 use task1 result, task3 use task2 result.
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
    result = pipeline.get_results()
    print(result)


def example_one():
    # 测试用例一: task3只使用task1的输出。
    # test_case_one: task3 use task1 result.
    a_ins = StepA(66)
    b_ins = StepB(200)
    pipeline = Pipeline(
        [('name_a', a_ins, "add_value"), ("name_b", b_ins, "multi_val"), ('name_c', b_ins, "minus_value")])
    parameters = {
        'name_a__value': 100,
        'name_b__value': 2,
        'name_c__value': "name_a.output"
    }
    pipeline.set_params(parameters)
    pipeline.run()
    pipeline.get_results()


def example_two():
    # 测试用例二： task3直接使用task2和task1的结果。task4用task3结果。
    # test case two: task3 use both task1 and task2 results。task4 use task3 result。
    a_ins = StepA(66)
    b_ins = StepB(200)
    pipeline = Pipeline(
        [('name_a', a_ins, "add_value"), ("name_b", b_ins, "self_double"),
         ('name_c', b_ins, "add_two"), ('name_d', a_ins, "add_value")])
    parameters = {
        'name_a__value': 100,
        'name_c__value_one': "name_a.output",
        'name_c__value_two': "name_b.output",
        'name_d__value': "name_c.output",
    }
    pipeline.set_params(parameters)
    pipeline.run()
    pipeline.get_results()


def example_three():
    # 测试用例三： task1有参数，task2没有参数，task3用task1的结果。
    # test case three： task1 has parameters，task2 not，task3 use task1 result。
    a_ins = StepA(100)
    b_ins = StepB(200)
    pipeline = Pipeline(
        [('name_a', a_ins, "add_value"), ("name_b", b_ins, "self_double"), ('name_c', b_ins, "minus_value")])
    parameters = {
        'name_a__value': 100,
        'name_c__value': "name_a.output"
    }
    pipeline.set_params(parameters)
    pipeline.run()
    pipeline.get_results()


def example_four():
    # 多线程跑，一共十个任务，每个任务执行都是2秒左右。多线程跑。
    # 之所以说每个任务都是2秒左右，是因为测试的时候在Pipeline的run函数的开头添加了sleep(2)。
    # test case four：multi process, every one will cost 2 seconds。
    threads = []
    start_time = time.time()
    for idx in range(10):
        base = idx * 10
        a_ins = StepA(base)
        b_ins = StepB(200)
        pipeline = Pipeline(
            [('name_a', a_ins, "add_value"), ("name_b", b_ins, "self_double"),
             ('name_c', b_ins, "add_two"), ('name_d', a_ins, "add_value")], thread_name="id_{}".format(idx))
        parameters = {
            'name_a__value': 100,
            'name_c__value_one': "name_a.output",
            'name_c__value_two': "name_b.output",
            'name_d__value': "name_c.output",
        }
        pipeline.set_params(parameters)
        threads.append(pipeline)
    for each_thread in threads:
        # import ctypes, threading
        each_thread.setDaemon(True)  # 主线程结束后就不要在后台继续跑了
        each_thread.start()
        print("thread name:{}".format(each_thread.name))
        # print(threading.currentThread().ident)  # 这个只会打印出主线程的id。
        # print("thread id: ", ctypes.CDLL('libc.so.6').syscall(186))  # 这个windows下没法用，186,224,178三个数都不行
    for each_thread in threads:
        each_thread.join()  # 会等待每一个都执行ok的。
    for each_thread in threads:
        print(each_thread.get_results())  # 看一下每一个的结果是不是都是ok的。
    print("total cost: {} seconds".format(time.time() - start_time))


if __name__ == '__main__':
    # print("=" * 20)
    example_zero()  # 测试用例零： task2用task1的结果。task3用task2的结果。
    # print("=" * 20)
    # example_one()   # 测试用例一:  task3只使用task1的输出。
    # print("=" * 20)
    # example_two()   # 测试用例二： task3直接使用task2和task1的结果。task4用task3结果。
    # print("=" * 20)
    # example_three() # 测试用例三： task1有参数，task2没有参数，task3用task1的结果。
    # print("=" * 20)
    # example_four()    # 测试用例四：十个任务并行跑，每个任务2秒左右，并行之后总时间还是2秒左右。
