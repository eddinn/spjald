"""adding tables User and Spjald

Revision ID: 1b7b3431e921
Revises: 
Create Date: 2019-11-06 12:50:17.060585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b7b3431e921'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('spjald',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clientname', sa.String(length=64), nullable=True),
    sa.Column('clientemail', sa.String(length=128), nullable=True),
    sa.Column('clientphone', sa.String(length=24), nullable=True),
    sa.Column('clientaddress', sa.String(length=100), nullable=True),
    sa.Column('clientcity', sa.String(length=32), nullable=True),
    sa.Column('clientzip', sa.String(length=8), nullable=True),
    sa.Column('userid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['userid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spjald_clientaddress'), 'spjald', ['clientaddress'], unique=False)
    op.create_index(op.f('ix_spjald_clientcity'), 'spjald', ['clientcity'], unique=False)
    op.create_index(op.f('ix_spjald_clientemail'), 'spjald', ['clientemail'], unique=True)
    op.create_index(op.f('ix_spjald_clientname'), 'spjald', ['clientname'], unique=False)
    op.create_index(op.f('ix_spjald_clientphone'), 'spjald', ['clientphone'], unique=False)
    op.create_index(op.f('ix_spjald_clientzip'), 'spjald', ['clientzip'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_spjald_clientzip'), table_name='spjald')
    op.drop_index(op.f('ix_spjald_clientphone'), table_name='spjald')
    op.drop_index(op.f('ix_spjald_clientname'), table_name='spjald')
    op.drop_index(op.f('ix_spjald_clientemail'), table_name='spjald')
    op.drop_index(op.f('ix_spjald_clientcity'), table_name='spjald')
    op.drop_index(op.f('ix_spjald_clientaddress'), table_name='spjald')
    op.drop_table('spjald')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
