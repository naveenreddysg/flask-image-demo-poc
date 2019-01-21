from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.mapper import class_mapper
from sqlalchemy import inspect

db = SQLAlchemy()

# To be initialized with the Flask app object in app.py.

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String)
    img_filename = db.Column('img_filename', db.String)
    img_data = db.Column('img_data', db.LargeBinary)

    # def __repr__(self):
    #     return '<image id={},name={}>'.format(self.id, self.name)


def get_image(the_id):
    #return Image.query.filter(Image.id == the_id).first()
    return Image.query.get_or_404(the_id)


def get_images(params=None):
    if not params:
        return Image.query.all()
    else:
        raise Exception('Filtering not implemented yet.')


def add_image(image_dict):
    new_image = Image(name=image_dict['name'],
                        img_filename=image_dict['img_filename'],
                        img_data=image_dict['img_data'])
    db.session.add(new_image)
    db.session.commit()

def model_to_dict(obj, visited_children=None, back_relationships=None):
    if visited_children is None:
        visited_children = set()
    if back_relationships is None:
        back_relationships = set()
    serialized_data = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    relationships = class_mapper(obj.__class__).relationships
    visitable_relationships = [(name, rel) for name, rel in relationships.items() if name not in back_relationships]
    for name, relation in visitable_relationships:
        if relation.backref:
            back_relationships.add(relation.backref)
        relationship_children = getattr(obj, name)
        if relationship_children is not None:
            if relation.uselist:
                children = []
                for child in [c for c in relationship_children if c not in visited_children]:
                    visited_children.add(child)
                    children.append(model_to_dict(child, visited_children, back_relationships))
                serialized_data[name] = children
            else:
                serialized_data[name] = model_to_dict(relationship_children, visited_children, back_relationships)
    return serialized_data
