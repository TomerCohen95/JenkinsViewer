import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from alembic import op
import sqlalchemy as sa
from app import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db, compare_type=True)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


# def upgrade():
#     op.alter_column('results', 'last_result', existing_type=sa.Integer(), type_=sa.String())


if __name__ == '__main__':
    manager.run()
