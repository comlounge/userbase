import pymongo
import colander
import uuid
import starflyer
import mongoquery

__all__ = ['Record', 'Collection', 'Error', 'InvalidData', 'ObjectNotFound', 'DateTime']

class DateTime(colander.SchemaType):
    """our own date time type which does not serialize to a string but keeps the datetime for mongo"""

    err_template =  colander._('Invalid date')

    def serialize(self, node, appstruct):
        if appstruct is colander:
            return colander

        if not isinstance(appstruct, datetime.datetime):
            raise colande.Invalid(node,
                          _('"${val}" is not a datetime object',
                            mapping={'val':appstruct})
                          )

        return appstruct

    def deserialize(self, node, cstruct):
        if not cstruct:
            return colander.null
        return cstruct

class Error(Exception):
    """base class for all data related exceptions"""

class InvalidData(Error):
    """exception raised if the data is invalid on serialize"""

    def __init__(self, errors):
        """initialize the exception"""
        self.errors = errors

    def __str__(self):
        """return a printable representation of the errors"""
        fs = ["%s: %s" %(a,v) for a,v in self.errors.items()]
        return """<Invalid Data: %s>""" %", ".join(fs)

class ObjectNotFound(Error):
    """exception raised if an object was not found"""

    def __init__(self, _id):
        """initialize the exception"""
        self._id = _id

class Record(object):
    
    schema = None
    create_id = True

    def __init__(self, data, from_db = False, collection = None, config = {}):
        """initialize a user with data

        :param data: The data in dict form to store in this object which will be available as obj.d
        :param collection: the collection instance this data object belongs to
        :param from_db: flag if this object was loaded from the database or not, meaning if it's new or not
        """
        # TODO: We want some mapper with remembering old values when values change
        self.d = starflyer.AttributeMapper(data)
        self._id = self.d.get("_id", None)
        self.collection = collection
        self.from_db = from_db

    def gen_id(self):
        """create a new unique id"""
        return unicode(uuid.uuid4())

    @property
    def exists(self):
        """check if this is an existing object, meaning if it has an _id attached"""
        return self.d.get('_id') is not None

    def serialize(self):
        """serialize the data into a structure"""

        # check if data is valid (strangely we need to call colander's deserialize()
        # because otherwise it would make strings out of everything
        # we only want the validators though
        print self.d
        try:
            data = self.schema.deserialize(self.d)
        except colander.Invalid, e:
            raise InvalidData(e.asdict())

        # now check if we have an _id and if not create one
        if not self.exists and self.create_id:
            data['_id'] = self.gen_id()
        else:
            data['_id'] = self.d.get("_id")

        return self.on_serialize(data)

    def on_serialize(self, data):
        """hook for adding your own serialize processing"""
        return data

    @classmethod
    def on_deserialize(cls, d):
        """hook for adding your own deserialize processing"""
        return d

    def put(self):
        """save the object"""
        self.collection.put(self)

    @classmethod
    def deserialize(cls, data, collection = None):
        """create a new instance of this class"""
        data = cls.on_deserialize(data)
        return cls(data, from_db=True, collection = collection)
        

class Collection(object):
    
    data_class = None
    use_objectids = False # does the mongodb collection use object ids?

    def __init__(self, collection, config = {}):
        """initialize the collection"""
        self.collection = collection
        self.config = config

    def put(self, obj):
        """store an object"""
        # TODO: handle automatically generated objectids
        data = obj.serialize()
        self.collection.save(data, True)
        obj.d = starflyer.AttributeMapper(data)
        obj.from_db = True
        return obj

    def get(self, _id):
        """return an object by it's id"""
        data = self.collection.find_one({'_id' : _id})
        if data is None:
            raise ObjectNotFound(_id)

        return self.data_class.deserialize(data)

    __getitem__ = get

    @property
    def all(self):
        """return all objects"""
        return self.query()

    @property
    def query(self):
        """return a mongoquery.Query object with collection and instantiation pre-filled"""
        return mongoquery.Query().coll(self.collection).call(self.data_class.deserialize, collection=self)







