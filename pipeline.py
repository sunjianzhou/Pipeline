import threading
import re
from operator import methodcaller
import logging
import gc
import uuid


class EachObject:
    def __init__(self, task_name, ins, func):
        self.task_name = task_name
        self.ins = ins
        self.ins_name = str(ins)
        self.func = str(func)
        self.output = None
        self.params = dict()
        self.output_update_tag = 0

    def set_output_update_tag(self, tag):
        self.output_update_tag = tag

    def get_output_update_tag(self):
        return self.output_update_tag

    def get_task_name(self):
        return self.task_name

    def set_ins(self, ins):
        self.ins = ins

    def get_ins(self):
        return self.ins

    def get_ins_name(self):
        return self.ins_name

    def set_func(self, func):
        self.func = str(func)

    def get_func(self):
        return self.func

    def set_output(self, value):
        self.output = value

    def set_param(self, key, value):
        self.params.update({key: value})

    def set_params(self, params_dict):
        self.params.update(params_dict)

    def get_params(self):
        return self.params

    def __str__(self):
        return "<object EachObject, name:{},ins:{},func:{},output:{},params:{}>". \
            format(self.task_name, str(self.ins), str(self.func), str(self.output), str(self.params))


class Pipeline(threading.Thread):
    def __init__(self, object_list, thread_name=None):
        threading.Thread.__init__(self, name=thread_name)
        self.task_list = []
        logging.info("task list start building")
        for task_name, ins, func in object_list:
            new_task = EachObject(task_name, ins, func)
            setattr(self, task_name, new_task)
            self.task_list.append(task_name)
            logging.info("task add: {}".format(getattr(self, task_name)))
        logging.info("task list build finished")

    def set_params(self, params_dict):
        names_params_dict = {}
        task_output_update_tag = str(uuid.uuid1())  # make sure unique
        for key, value in params_dict.items():
            obj_param_name_list = key.split("__")
            obj_name, param_name = obj_param_name_list[0], obj_param_name_list[1]
            if not names_params_dict.get(obj_name):
                names_params_dict.update({obj_name: {}})

            pattern = re.compile(r".*\.output$")
            if isinstance(value, str) and re.search(pattern, value):
                names_params_dict.get(obj_name).update({task_output_update_tag: 1})

            names_params_dict.get(obj_name).update({param_name: value})

        logging.info("-" * 10)
        logging.info("task params start setting")
        for name in names_params_dict:
            cur_parameters = names_params_dict.get(name)
            logging.info("task {}, initial parameters:{}".format(name, cur_parameters))
            if cur_parameters.get(task_output_update_tag):
                getattr(self, name).set_output_update_tag(cur_parameters.pop(task_output_update_tag))
            getattr(self, name).set_params(cur_parameters)
            logging.info("task {}, set parameters: {}".format(name, cur_parameters))
        logging.info("task params set finished")
        logging.info("-" * 10)

    def get_result(self, object_name):
        return getattr(self, object_name).output

    def get_results(self):
        res_list = []
        func_list = []
        logging.info("task results:")
        logging.info("task_list:{}".format(self.task_list))
        for each in self.task_list:
            each_task = getattr(self, each)
            func_list.append(str(each_task.ins_name) + ":" + each_task.func)
            res_list.append(each_task.output)
        logging.info("functions:{}".format(func_list))
        logging.info("results:{}".format(res_list))
        logging.info("-" * 10)
        return res_list

    def _set_output(self, key, value):
        logging.info("set {} to {}".format(key, value))
        getattr(self, key).set_output(value)

    def get_task_list(self):
        logging.info("task_list:")
        logging.info("  ==>  ".join(self.task_list))
        return self.task_list

    def get_params(self):
        params_list = []
        logging.info("task_list:{}".format(self.task_list))
        for each in self.task_list:
            params = getattr(self, each).get_params()
            logging.info(params)
            params_list.append(params)
        return params_list

    def update_params(self, params_dict):
        for each in params_dict:
            value = params_dict.get(each)
            pattern = re.compile(r".*\.output$")
            if isinstance(value, str) and re.search(pattern, value):
                task_name = value.split(".output")[0]
                if task_name not in set(self.task_list):
                    logging.info("all tasks are: {}".format(self.task_list))
                    logging.info("task_name: {} is not a member of existing task")
                    return
                value = "self." + value
                params_dict.update({each: eval(value)})

    def run(self):
        # import time
        # time.sleep(2)  # just for multi process test
        logging.info("task jobs start executing:")
        logging.info("task_list: {}".format(self.task_list))
        for task_name in self.task_list:
            logging.info("executing task: {}".format(task_name))
            each_object = getattr(self, task_name)

            # update the params if the value of output_tag is one
            output_update_tag = each_object.get_output_update_tag()
            if output_update_tag:
                params = each_object.get_params()
                logging.info("params before update:{}".format(params))
                self.update_params(params)
                logging.info("params after update:{}".format(params))
                each_object.set_params(params)

            obj_ins = each_object.get_ins()
            func_name = each_object.get_func()
            params = each_object.get_params()

            out_put = methodcaller(func_name, **params)(obj_ins)
            each_object.set_output(out_put)
            del obj_ins
            gc.collect()
            logging.info("{} finished".format(task_name))
        logging.info("task jobs execute finished")
        logging.info("-" * 10)
