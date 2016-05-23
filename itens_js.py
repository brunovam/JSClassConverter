class JS_TYPE:
    CLASS = 1
    METHOD = 2
    ATTRIBUTE = 3
    INHERITANCE = 4
    METHOD_OR_CLASS = 5


class Kinship:
    kinships = None

    def __init__(self):
        self.kinships = []

    def insert(self, parent_object_id, parent_object_type, son_object_id, son_object_type):
        self.kinships.append({"PARENT":int(parent_object_id), "PARENT_TYPE": int(parent_object_type),
            "SON": int(son_object_id), "SON_TYPE": int(son_object_type)})

    def get_itens(self):
        return self.kinships

    def print_obj(self):
        for k in self.kinships:
            print(k)


class Bank:
    js_classes = None
    js_methods = None
    js_attributes = None
    js_external_code = None

    def __init__(self):
        self.js_classes = []
        self.js_methods = []
        self.js_attributes = []
        self.js_external_code = ""

    def insert_class(self, js_class):
        js_class.insert_bank_id(len(self.js_classes))
        self.js_classes.append(js_class)

    def insert_method(self, js_method):
        js_method.insert_bank_id(len(self.js_methods))
        self.js_methods.append(js_method)

    def insert_attribute(self, js_attribute):
        js_attribute.insert_bank_id(len(self.js_attributes))
        self.js_attributes.append(js_attribute)

    def register_method_into_class(self, class_id, method_id):
        class_bank_id = self.get_class(id=class_id)[0]
        method_bank_id, method = self.get_method(id=method_id)
        self.js_classes[class_bank_id].register_method(method)

    def register_attribute_into_class(self, class_id, attribute_id):
        class_bank_id = self.get_class(id=class_id)[0]
        attribute_bank_id, attribute = self.get_attribute(id=attribute_id)
        self.js_classes[class_bank_id].register_attribute(attribute)

    def register_attribute_into_method(self, method_id, attribute_id):
        method_bank_id = self.get_method(id=method_id)[0]
        attribute_bank_id, attribute = self.get_attribute(id=attribute_id)
        self.js_methods[method_bank_id].register_attribute(attribute)

    def register_subclass_into_class(self, class_id, subclass_id):
        class_bank_id, js_class = self.get_class(id=class_id)
        subclass_bank_id, js_subclass = self.get_class(id=subclass_id)
        self.js_classes[class_bank_id].register_subclass(js_subclass)
        self.js_classes[subclass_bank_id].register_superclass(js_class)

    def get_object_by_name(self, object_name):
        for c in self.js_classes:
            if c.name == object_name:
                return c #see if this is returning the object by reference

        for m in self.js_methods:
            if m.name == object_name:
                return m #see if this is returning the object by reference

        for a in self.js_attributes:
            if a.name == object_name:
                return a #see if this is returning the object by reference

        return None

    def insert_external_code(self, code):
        self.js_external_code += code

    def print_external_code(self):
        all_code = ""
        all_code += self.js_external_code
        return all_code

    def get_all_classes(self):
        return self.js_classes

    def get_all_methods(self):
        return self.js_methods

    def get_all_attributes(self):
        return self.js_attributes

    def get_all_classes_ordered_by_kinship(self):
        ordered_classes = []
        aux = list(self.js_classes)

        count = 0
        for c in aux:
            if c.superclass_of and not c.subclass_of:
                ordered_classes.append(c)
                aux.pop(count)
            count += 1

        count = 0
        for c in aux:
            if c.superclass_of:
                ordered_classes.append(c)
                aux.pop(count)
            count += 1

        for item in aux:
            ordered_classes.append(item)

        return ordered_classes

    def get_class(self, id=None,name=None,bank_id=None):
        if not bank_id:
            return self.get_bank_id(id,name, JS_TYPE().CLASS)
        return self.js_classes[bank_id]

    def get_method(self, id=None,name=None,bank_id=None):
        if not bank_id:
            return self.get_bank_id(id,name, JS_TYPE().METHOD)
        return self.js_methods[bank_id]

    def get_attribute(self, id=None,name=None,bank_id=None):
        if not bank_id:
            return self.get_bank_id(id,name, JS_TYPE().ATTRIBUTE)
        return self.js_attributes[bank_id]

    def get_bank_id(self, id=None,name=None, structure_id=None):
        if type(id) is str:
            id = int(id)
        if structure_id == JS_TYPE().CLASS:
            JS_STRUCTURE = self.js_classes
        elif structure_id == JS_TYPE().METHOD:
            JS_STRUCTURE = self.js_methods
        elif structure_id == JS_TYPE().ATTRIBUTE:
            JS_STRUCTURE = self.js_attributes

        if id:
            for j in JS_STRUCTURE:
                if j.id == id:
                    return j.bank_id,j
        elif name:
            for j in JS_STRUCTURE:
                if j.name == name:
                    return j.bank_id,j
        else:
            print("You have to pass an id or a name to get a bank id class")
            return None


    def register_kinships(self, kinships):
        for k in kinships.get_itens():
            if k["PARENT_TYPE"] == JS_TYPE().CLASS and k["SON_TYPE"] == JS_TYPE().CLASS:
                self.register_subclass_into_class(k["PARENT"], k["SON"])
            elif k["PARENT_TYPE"] == JS_TYPE().CLASS and k["SON_TYPE"] == JS_TYPE().METHOD:
                self.register_method_into_class(k["PARENT"], k["SON"])
            # elif k["PARENT_TYPE"] == JS_TYPE().CLASS and k["SON_TYPE"] == JS_TYPE().ATTRIBUTE:
            #     self.register_attribute_into_class(k["PARENT"], k["SON"])
            elif k["PARENT_TYPE"] == JS_TYPE().METHOD_OR_CLASS and k["SON_TYPE"] == JS_TYPE().ATTRIBUTE:
                found = 0
                for c in self.js_classes:
                    if c.id == k["PARENT"]:
                        k["PARENT_TYPE"] = JS_TYPE().CLASS
                        self.register_attribute_into_class(k["PARENT"], k["SON"])
                        found = 1
                if not found:
                    k["PARENT_TYPE"] = JS_TYPE().METHOD
                    self.register_attribute_into_method(k["PARENT"], k["SON"])
            else:
                print("Algo deu muito errado!")
                exit(1)

    def print_bank(self):
        print("The bank has %d classes, %d methods and %d attributes" % (len(self.js_classes), len(self.js_methods), len(self.js_attributes)))
        for c in self.js_classes:
            print("Class")
            c.print_obj()
            methods = c.get_methods()
            for m_id in methods:
                print("Method of class")
                self.js_methods[m_id].print_obj()
                attributes_of_method = self.js_methods[m_id].get_attributes()
                for attr_id in attributes_of_method:
                    print("Attribute of method")
                    self.js_attributes[attr_id].print_obj()
            attributes_of_class = c.get_attributes()
            for attr_id in attributes_of_class:
                print("Attribute of class")
                self.js_attributes[attr_id].print_obj()
        print("\nExternal code")
        print(self.js_external_code)



class JSClass:
    name = None
    id = None # que aparece no arquivo
    type_ = None
    superclass_of = None
    subclass_of = None
    methods = None
    attributes = None
    code = None
    attributes_of_structure = None
    inheritance_attributes = None

    bank_id = None

    def __init__(self, name, id):
        self.name = name
        self.id = int(id)
        self.superclass_of = [] #integer referencing the superclass at the bank
        self.subclass_of = []
        self.methods = []
        self.attributes = []
        self.code = ""
        self.inheritance_attributes = []
        self.attributes_of_structure = []

    def insert_bank_id(self, id):
        self.bank_id = int(id)

    def register_superclass(self, super_class):
        self.subclass_of.append(super_class.bank_id)

    def register_subclass(self, sub_class):
        self.superclass_of.append(sub_class.bank_id)

    def register_method(self, method):
        self.methods.append(method.bank_id)

    def register_attribute(self, attribute):
        self.attributes.append(attribute.bank_id)

    def insert_inheritance_attributes(self, attributes):
        self.inheritance_attributes = attributes

    def insert_attributes_of_structure(self, attrs):
        self.attributes_of_structure = attrs

    def insert_code(self, line_of_code):
        self.code += line_of_code

    def get_attributes_of_structure(self):
        return self.attributes_of_structure

    def get_attributes_of_superclass(self, bank):
        if self.subclass_of:
            attrs_of_parent_structure = bank.get_class(bank_id=self.subclass_of[0]).get_attributes_of_structure()
            if not self.inheritance_attributes:
                return attrs_of_parent_structure

            count = 0
            attrs_of_parent_structure_with_inheritance = list(attrs_of_parent_structure)
            for attr in attrs_of_parent_structure_with_inheritance:
                if len(self.inheritance_attributes)> count:
                    attrs_of_parent_structure_with_inheritance[count] += "=%s" % self.inheritance_attributes[count]
                count += 1
            return attrs_of_parent_structure_with_inheritance
        return []

    def get_methods(self):
        return self.methods

    def get_attributes(self):
        return self.attributes

    def get_type(self):
        return JS_TYPE().CLASS

    def print_js6_code(self, bank):
        all_code = ""
        attributes_of_superclass = self.get_attributes_of_superclass(bank)
        if len(self.subclass_of):
            all_code += "class %s extends %s{\n" % (self.name, bank.get_class(bank_id=self.subclass_of[0]).name)
        else:
            all_code += "class %s {\n" % self.name
        all_code += "constructor (%s) {\n"% ",".join(attributes_of_superclass + self.attributes_of_structure)
        if attributes_of_superclass:
            count = 0
            for attr in attributes_of_superclass:
                attributes_of_superclass[count] = attr[0:attr.find("=")]
                count += 1
            all_code += "super(%s)\n"% ",".join(attributes_of_superclass)
        all_code += self.code
        for attr_id in self.attributes:
            all_code += bank.js_attributes[attr_id].print_js6_code()
        for m_id in self.methods:
            all_code += "this.%s" % bank.js_methods[m_id].print_signature()
        all_code += "}\n"

        for meth_id in self.methods:
            all_code += bank.js_methods[meth_id].print_js6_code(bank)

        all_code += "}\n"
        return all_code


    def print_obj(self):
        print("Name: %s\nId: %d" % (self.name, self.id))
        print("Superclasses number: %d Subclasses number: %d" % (len(self.subclass_of),len(self.superclass_of)))
        print("Bank id: %d" % self.bank_id,)
        print("Code:")
        print(self.code)
        print("\n")


class JSMethod:
    name = None
    id = None
    modifier = None
    attributes = []
    code = None
    attributes_of_structure = None

    bank_id = None

    def __init__(self, name, id, modifier):
        self.name = name
        self.id = int(id)
        self.modifier = modifier
        self.code = ""
        self.attributes_of_structure = []

    def insert_bank_id(self, id):
        self.bank_id = id

    def insert_attributes_of_structure(self, attrs):
        self.attributes_of_structure = attrs

    def register_attribute(self, attribute):
        self.attributes.append(attribute.bank_id)

    def insert_code(self, line_of_code):
        self.code += line_of_code

    def get_attributes(self):
        return self.attributes

    def get_type(self):
        return JS_TYPE().METHOD

    def print_signature(self):
        all_code = ""
        all_code += "%s(%s);\n" % (self.name, ",".join(self.attributes_of_structure))
        return all_code

    def print_js6_code(self, bank):
        all_code = ""
        all_code += "%s (%s){\n" % (self.name, ",".join(self.attributes_of_structure))
        all_code += self.code
        for attr_id in self.attributes:
            all_code += bank.js_attributes[attr_id].print_js6_code()
        all_code += "}\n"

        return all_code

    def print_obj(self):
        print("Name: %s\nId: %d" % (self.name, self.id))
        print("Modifier: %s" % self.modifier,)
        print("Bank id: %d" % self.bank_id,)
        print("Code:")
        print(self.code)
        print("\n")


class JSAtribute:
    name = None
    value = None
    id = None
    code = None

    bank_id = None

    def __init__(self, name, id, value):
        self.name = name
        self.id = int(id)
        self.value = value
        self.code = ""

    def insert_bank_id(self, id):
        self.bank_id = id

    def insert_code(self, line_of_code):
        self.code += line_of_code

    def get_type(self):
        return JS_TYPE().ATTRIBUTE

    def print_js6_code(self):
        all_code = ""
        all_code += self.code
        return all_code

    def print_obj(self):
        print("Name: %s\nId: %d" % (self.name, self.id))
        print("Value: %s" % self.value,)
        print("Bank id: %d" % self.bank_id,)
        print("Code:")
        print(self.code)
        print("\n")
