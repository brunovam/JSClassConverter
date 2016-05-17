#!/usr/bin/python
import sys
from sys import argv
import re

from itens_js import Bank, JSClass, JSMethod, JSAtribute, JS_TYPE, Kinship

def create_js_structures_on_the_bank(bank=None, id=None, name=None, modifier=None, value=None, parent_id=None, sub_class=None, super_class=None, what_is_being_read=None, kinships=None):
    if not what_is_being_read:
        return

    if what_is_being_read == JS_TYPE().CLASS:
        js_class = JSClass(name, id)
        bank.insert_class(js_class)

    elif what_is_being_read == JS_TYPE().METHOD:
        js_method = JSMethod(name, id, modifier)
        bank.insert_method(js_method)
        #bank.register_method_into_class(parent_type, js_method)
        kinships.insert(parent_id, JS_TYPE().CLASS ,id, JS_TYPE().METHOD)

    elif what_is_being_read == JS_TYPE().ATTRIBUTE:
        js_attribute = JSAtribute(name, id, value)
        bank.insert_attribute(js_attribute)
        #bank.register_attribute_into_method(parent_type, js_attribute)
        kinships.insert(parent_id, JS_TYPE().METHOD_OR_CLASS, id, JS_TYPE().ATTRIBUTE)


    elif what_is_being_read == JS_TYPE().INHERITANCE:
        #js_attribute = JSAtribute(name, id, value)
        #bank.insert_attribute(js_attribute)
        #bank.register_attribute_into_method(parent_type, js_attribute)
        kinships.insert(super_class, JS_TYPE().CLASS, sub_class, JS_TYPE().CLASS)

def read_mse_file(filename, bank):
    kinships = Kinship()
    with open(filename) as f:
        what_is_being_read = None
        id = None
        name = None
        modifier = None
        value = None
        parent_type = None
        sub_class = None
        super_class = None

        all_mse_file_content = f.readlines()
        for line_of_file in all_mse_file_content:
            line = line_of_file.replace("\n","")
            if "FAMIX.Class" in line:
                create_js_structures_on_the_bank(bank, id=id, name=name, modifier=modifier, value=value, parent_id=parent_type, sub_class=sub_class, super_class=super_class, what_is_being_read=what_is_being_read, kinships=kinships)
                what_is_being_read = JS_TYPE().CLASS
                id = re.sub("[\s\(\)\:A-Za-z.]","",line)
            elif "FAMIX.Method" in line:
                create_js_structures_on_the_bank(bank, id=id, name=name, modifier=modifier, value=value, parent_id=parent_type, sub_class=sub_class, super_class=super_class, what_is_being_read=what_is_being_read, kinships=kinships)
                what_is_being_read = JS_TYPE().METHOD
                id = re.sub("[\s\(\)\:A-Za-z.]","",line)
            elif "FAMIX.Attribute" in line:
                create_js_structures_on_the_bank(bank, id=id, name=name, modifier=modifier, value=value, parent_id=parent_type, sub_class=sub_class, super_class=super_class, what_is_being_read=what_is_being_read, kinships=kinships)
                what_is_being_read = JS_TYPE().ATTRIBUTE
                id = re.sub("[\s\(\)\:A-Za-z.]","",line)
            elif "FAMIX.Inheritance" in line:
                create_js_structures_on_the_bank(bank, id=id, name=name, modifier=modifier, value=value, parent_id=parent_type, sub_class=sub_class, super_class=super_class, what_is_being_read=what_is_being_read, kinships=kinships)
                what_is_being_read = JS_TYPE().INHERITANCE

            if "name" in line:
                name = line[line.find("'")+1:line[line.find("'")+1].find("'")-1]
            elif "modifiers" in line:
                modifier = line[line.find("'")+1:line[line.find("'")+1].find("'")-1]
            elif "parentType" in line:
                parent_type = re.sub("[\s\(\)\:A-Za-z.]","",line)
            elif "subclass" in line:
                sub_class = re.sub("[\s\(\)\:A-Za-z.]","",line)
            elif "superclass" in line:
                super_class = re.sub("[\s\(\)\:A-Za-z.]","",line)

        #Create the last structure after the last line be read
        create_js_structures_on_the_bank(bank, id=id, name=name, modifier=modifier, value=value, parent_id=parent_type, sub_class=sub_class, super_class=super_class, what_is_being_read=what_is_being_read, kinships=kinships)
        #kinships.print_obj()
        bank.register_kinships(kinships)

def read_js_file(filename, bank):
    with open(filename) as f:
        all_mse_file_content = f.readlines()
        name = None
        attributes = []
        next_word_is_name = False
        next_word_is_method = False
        next_word_is_attribute = False
        structures = []
        for line_of_file in all_mse_file_content:
            if "function" in line_of_file:
                if not "prototype" in line_of_file:
                    if "this" in line_of_file:
                        line_without_this = line_of_file.split(".")[1]
                        name = line_without_this.split("=")[0]
                    else:
                        name = line_of_file.replace("function","").split("(")[0].replace(" ","")

                    structures.append(name)
                    attrs = line_of_file[line_of_file.find("(")+1:line_of_file.find(")")]
                    attributes_of_method_or_class = []
                    for a in attrs.replace(" ","").split(","):
                        attributes_of_method_or_class.append(a)
                    bank.get_object_by_name(name).insert_attributes_of_structure(attributes_of_method_or_class)
                    continue

            if "}" in line_of_file:
                structures.pop()
                continue
            if "prototype" in line_of_file:
                if "new" in line_of_file:
                    line = line_of_file.split(".")
                    subclass = line[0]
                    super_class_info = line[1].replace("new ","").replace(" ","").replace("{","").replace("prototype=","").split("(")
                    super_class_name = super_class_info[0]
                    super_class_attributes = super_class_info[1].replace(")","").replace(";","").replace("\n","").split(",")
                    bank.get_object_by_name(subclass).insert_inheritance_attributes(super_class_attributes)
                    continue
                else:
                    line = line_of_file.split(".")
                    class_name = line[0]
                    method_name, attributes = line[2].replace(" ","").replace("{","").split("=function")
                    attributes = attributes.replace("(","").replace(")","").split(",")#TODO Treat the methods attributes
                    structures.append(method_name)
                    continue
            if not len(structures):
                bank.insert_external_code(line_of_file)
            else:
                bank.get_object_by_name(structures[len(structures)-1]).insert_code(line_of_file)#create a stack to store the different levels of the structures tree


def write_js6_code(bank):
    all_code = ""
    for c in bank.get_all_classes():
        all_code += c.print_js6_code(bank)

    all_code += bank.print_external_code()
    improved_code = improve_code(all_code)
    print(improved_code)

def improve_code(all_code):
    """
    identation and others interface improvements
    """
    code_lines = list(all_code.splitlines())
    level = 0
    identation_chars = "  "
    for i in range(0,len(code_lines)):
        code_lines[i] = level*identation_chars + code_lines[i].lstrip().rstrip() + "\n"
        if "{" in code_lines[i]:
            level += 1
        if "}" in code_lines[i]:
            level -= 1
            code_lines[i] += "\n"
    return "".join(code_lines)


def main(argv):
    if not len(sys.argv) == 3:
        print "Usage: python js6_conversor.py FILE.js FILE.mse"
        exit(0)

    bank = Bank()
    read_mse_file(argv[2], bank)
    read_js_file(argv[1], bank)
    #bank.print_bank()
    write_js6_code(bank)

    #write_js6_code(js6_converter(bank)):

    # Look at line ending of input files
if __name__ == '__main__':
    main(argv)
