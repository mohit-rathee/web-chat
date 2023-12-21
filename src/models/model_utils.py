from .. import db

def create_channel(table_number,base,users):
    attrs = {
        '__tablename__': str(table_number),
        'id': db.Column(db.Integer, primary_key=True),
        'data': db.Column(db.String, nullable=False),
        'sender_id': db.Column(db.Integer, db.ForeignKey(users.id)),
        'user': db.relationship(users)
    }
    channel_class = type(str(table_number), (base,), attrs)
    return channel_class

