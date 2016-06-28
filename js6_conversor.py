#!/usr/bin/python
import sys
from sys import argv
import re

from itens_js import Bank, JSClass, JSMethod, JSAtribute, JS_TYPE, Kinship

def create_js_method_on_the_bank(bank, kinships, name, id, modifier, parent_id):
    js_method = JSMethod(name, id, modifier)
    bank.insert_method(js_method)
    kinships.insert(parent_id, JS_TYPE().CLASS ,id, JS_TYPE().METHOD)


def create_js_structures_on_the_bank(bank=None, id=None, name=None, modifier=None, value=None, parent_id=None, sub_class=None, super_class=None, what_is_being_read=None, kinships=None):
    if not what_is_being_read:
        return

    if what_is_being_read == JS_TYPE().CLASS:
        js_class = JSClass(name, id)
        bank.insert_class(js_class)

    elif what_is_being_read == JS_TYPE().METHOD:
        create_js_method_on_the_bank(bank, kinships, name, id, modifier, parent_id)

    elif what_is_being_read == JS_TYPE().ATTRIBUTE:
        js_attribute = JSAtribute(name, id, value)
        bank.insert_attribute(js_attribute)
        kinships.insert(parent_id, JS_TYPE().METHOD_OR_CLASS, id, JS_TYPE().ATTRIBUTE)


    elif what_is_being_read == JS_TYPE().INHERITANCE:
        kinships.insert(super_class, JS_TYPE().CLASS, sub_class, JS_TYPE().CLASS)

    elif what_is_being_read == JS_TYPE().PACKAGE:
        pass

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
            elif "FAMIX.Package" in line:
                create_js_structures_on_the_bank(bank, id=id, name=name, modifier=modifier, value=value, parent_id=parent_type, sub_class=sub_class, super_class=super_class, what_is_being_read=what_is_being_read, kinships=kinships)
                what_is_being_read = JS_TYPE().PACKAGE

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
        bank.register_kinships(kinships)


def insert_code_into_the_bank(bank, structures, line_of_code, initial_code=False):
    if initial_code:
        bank.insert_initial_code(line_of_code)
    else:
        if not len(structures):
            bank.insert_external_code(line_of_code)
        else:
            bank.get_object_by_name(structures[len(structures)-1]).insert_code(line_of_code)

def see_if_is_an_init_of_conditional_or_loop_structure(line_of_file, ignore_block, bank, structures, line_with_comments, initial_code):
    javascript_conditional_and_loop_structures = ["if","else","while","for","switch","try","catch","case","return"]

    for st in javascript_conditional_and_loop_structures:
        temp_line_of_file = line_of_file.replace(" ","")

        if st in line_of_file:
            if (temp_line_of_file.index(st) + len(st)) < len(temp_line_of_file):
                prox_char_after_st = temp_line_of_file[temp_line_of_file.index(st)+len(st)]

                if prox_char_after_st == "(" and  ")" in line_of_file:
                    if "}" in line_of_file and "{" in line_of_file and line_of_file.index("}")<line_of_file.index("{"):
                        #Handling } else if (...){
                        if ignore_block:
                            ignore_block.pop()
                    if not "return" in line_of_file and not ";" == line_of_file[-2]:
                        ignore_block.append(True)
                    insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                    return True
                if (st == "return" or st == "try") and prox_char_after_st == "{":
                    if "}" in line_of_file:
                        if "}" in line_of_file[:line_of_file.index("}")]:
                            ignore_block.pop()

                    ignore_block.append(True)
                    insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                    return True

    return False

def read_js_file(filename, bank):
    with open(filename) as f:
        all_mse_file_content = f.readlines()
        name = None
        attributes = []
        next_word_is_name = False
        next_word_is_method = False
        next_word_is_attribute = False
        structures = [] #List to store the different levels of the structures tree
        comment_chars = "//"
        is_comment = False
        ignore_block = []
        line_count = 0
        initial_code = True
        line_has_comment = False

        for line_of_file in all_mse_file_content:
            line_count += 1
            line_of_file = line_of_file.replace("\t","")
            line_with_comments = ""+line_of_file
            line_has_comment = False
            if comment_chars in line_of_file:
                line_of_file = line_of_file.split(comment_chars, 1)[0]
                line_has_comment = True
                if line_of_file.replace(" ","") == "":
                    insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                    continue

            if "/*" in line_of_file:
                is_comment = True
            if "*/" in line_of_file:
                is_comment = False
                insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                continue
            if is_comment:
                insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                continue;



            if see_if_is_an_init_of_conditional_or_loop_structure(line_of_file, ignore_block, bank, structures, line_with_comments, initial_code):
                continue

            if "{" in line_of_file and "}" in line_of_file:
                if "function" in line_of_file and not line_of_file.replace(" ","")[-2] == ";":

                    ignore_block.append(True)
                    insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                    continue
                insert_code_into_the_bank(bank, structures, line_with_comments)
                continue


            if "function" in line_of_file and line_of_file[-2] != ";":# and not structures:
                if not ".prototype" in line_of_file:
                    if "this" in line_of_file:
                        line_without_this = line_of_file.split(".")[1]
                        name = line_without_this.split("=")[0]
                    else:
                        name = line_of_file.replace("function","").split("(")[0].replace(" ","").replace(";","")

                    if not name:
                        if initial_code:
                            bank.insert_initial_code(line_with_comments)
                        else:
                            bank.insert_external_code(line_with_comments)
                        continue

                    attrs = line_of_file[line_of_file.find("(")+1:line_of_file.find(")")]
                    attributes_of_method_or_class = []
                    for a in attrs.replace(" ","").split(","):
                        attributes_of_method_or_class.append(a)

                    if not bank.get_object_by_name(name):
                        temp_line = line_of_file.split(".")
                        obj = bank.get_object_by_name(temp_line[0].replace(" ",""))

                        if obj and obj.get_type() == JS_TYPE().CLASS:
                            name = temp_line[1].split("=")[0].replace(" ","")
                            attrs = temp_line[1][temp_line[1].find("(")+1:temp_line[1].find(")")]
                            attributes_of_method_or_class = []
                            for a in attrs.replace(" ","").split(","):
                                attributes_of_method_or_class.append(a)

                            if ("(" in name and "[" in name) or "{" in name or (ignore_block or "})." in line_of_file):
                                ignore_block.append(True)
                                insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                                continue
                            if "\"" in name or "'" in name:

                                ignore_block.append(True)
                                insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                                continue

                            #Static method
                            kinships = Kinship()
                            create_js_method_on_the_bank(bank, kinships, name, bank.get_higher_id()+1, "static", obj.id)
                            bank.register_kinships(kinships)
                        else:
                            # In this case, the code has a function into a class by compatibility.
                            ignore_block.append(True)
                            insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                            continue

                    if not ("(function".replace(" ","") in line_of_file or ",function" in line_of_file.replace(" ","") or ignore_block or "})." in line_of_file):
                        if "each" in line_of_file:
                            pass
                        initial_code = False
                        structures.append(name)
                    bank.get_object_by_name(name).insert_attributes_of_structure(attributes_of_method_or_class)
                    continue

            if "}" in line_of_file and "{" not in line_of_file:
                if ignore_block:
                    ignore_block.pop()
                else:
                    if structures:
                        structures.pop()
                    elif not structures and len(line_of_file.replace(" ","")) > 3 and "(" in line_of_file and ")" in line_of_file:
                        bank.insert_external_code(line_with_comments)
                    continue

            if ".prototype" in line_of_file:
                if "new" in line_of_file:
                    # Subclass
                    line = line_of_file.split(".")
                    subclass = line[0]
                    super_class_info = line[1].replace("new ","").replace(" ","").replace("{","").replace("prototype=","").split("(")
                    super_class_name = super_class_info[0]
                    super_class_attributes = super_class_info[1].replace(")","").replace(";","").replace("\n","").split(",")
                    bank.get_object_by_name(subclass).insert_inheritance_attributes(super_class_attributes)
                    initial_code = False
                    continue
                else:
                    if "function" in line_of_file and ".prototype." in line_of_file:
                        # Method
                        line = line_of_file.split(".")
                        class_name = line[0].replace(" ","")
                        method_name, attributes = line[2].replace(" ","").replace("{","").replace("\n","").split("=function")
                        attributes = attributes.replace("(","").replace(")","").split(",")
                        bank.get_object_by_name(method_name).insert_attributes_of_structure(attributes)
                        structures.append(method_name)

                        initial_code = False
                        continue
                    elif "function" in line_of_file and ".prototype[" in line_of_file:
                        ignore_block.append(True)

                    else:
                        #TODO handle static attributes
                        pass
            if ignore_block:
                insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)
                continue

            if "=" in line_of_file and "{" == line_of_file[-2]:
                if "}" in line_of_file:
                    if "}" in line_of_file[:line_of_file.index("}")]:
                        ignore_block.pop()

                ignore_block.append(True)
                insert_code_into_the_bank(bank, structures, line_with_comments)

            insert_code_into_the_bank(bank, structures, line_with_comments, initial_code)


def write_js6_code(bank):
    all_code = ""
    all_code += bank.print_initial_code()
    for c in bank.get_all_classes_ordered_by_kinship():
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
            if level <0:
                level = 0
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

    # TODO Look at line ending of input files
if __name__ == '__main__':
    main(argv)
