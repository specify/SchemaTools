from .orderedclass import OrderedMeta
from . import to_sqlalchemy as sql_mixin

def is_field(obj):
    return isinstance(obj, Field)

def is_record(obj):
    return isinstance(obj, type) and issubclass(obj, Record)

def is_tree(obj):
    return is_record(obj) and issubclass(obj, TreeRecord)

def is_schema(obj):
    return isinstance(obj, type) and issubclass(obj, Schema)

class Field(sql_mixin.Field):
    _record = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_name(self):
        return self._name

class RecordMeta(OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        record = super().__new__(meta, name, bases, clsdict)
        values = [getattr(record, key) for key in record._keys]
        record._children = [v for v in values if is_record(v)]
        for child in record._children:
            child._parent = record

        record._fields = []
        for name, field in ((k, v)
                            for k, v in zip(record._keys, values)
                            if is_field(v)):
            field._record = record
            field._name = name
            record._fields.append(field)
        return record

class Record(sql_mixin.Record, metaclass=RecordMeta):
    _parent = None

    @classmethod
    def get_schema(cls):
        if cls._parent is None:
            return cls._schema.get_name()
        else:
            return cls._parent.get_schema()

    @classmethod
    def get_name(cls):
        return cls.__name__

class SchemaMeta(OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        schema = super().__new__(meta, name, bases, clsdict)
        values = [getattr(schema, key) for key in schema._keys]
        schema._records = [v for v in values if is_record(v)]
        for record in schema._records:
            record._schema = schema
        return schema

class Schema(sql_mixin.Schema, metaclass=SchemaMeta):
    @classmethod
    def get_name(cls):
        return cls.__name__

class TreeRecord(sql_mixin.TreeRecord, Record):
    pass

def make_tree(ranks_for_tree):
    class Tree(TreeRecord):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return Tree
