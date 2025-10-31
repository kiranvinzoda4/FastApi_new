"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    # Start explicit transaction
    connection = op.get_bind()
    trans = connection.begin()
    
    try:
        ${upgrades if upgrades else "pass"}
        
        # Commit if all successful
        trans.commit()
        
    except Exception as e:
        # Rollback on any error
        trans.rollback()
        raise e


def downgrade():
    # Start explicit transaction
    connection = op.get_bind()
    trans = connection.begin()
    
    try:
        ${downgrades if downgrades else "pass"}
        
        # Commit if all successful
        trans.commit()
        
    except Exception as e:
        # Rollback on any error
        trans.rollback()
        raise e